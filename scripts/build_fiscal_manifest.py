#!/usr/bin/env python3
"""Build the cross-runtime fiscal data manifest.

The manifest intentionally distinguishes verified authority data from legacy
historical snapshots that remain available but have not yet completed a
source-by-source audit. Hashes cover the canonical JSON value payload for each
(table, exercise) entry so consumers can pin or reject fiscal inputs.

Normal generation is additive with respect to history: an exercise that already
exists in the checked-in manifest may be corrected, but it may not silently
disappear. Deliberate history removal therefore requires changing this policy,
not merely editing a source JSON file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal, TypeAlias, TypedDict, cast

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "packages" / "shared-data"
MANIFEST_PATH = SHARED / "fiscal-manifest.json"
PYTHON_MANIFEST_PATH = (
    ROOT / "packages" / "python" / "catalogmx" / "data" / "fiscal-manifest.json"
)
PYTHON_IDS_PATH = ROOT / "packages" / "python" / "catalogmx" / "_fiscal_ids.py"
TS_PATH = ROOT / "packages" / "typescript" / "src" / "fiscal" / "manifest.generated.ts"

VERIFIED_YEARS = {2024, 2025, 2026}

FiscalDataStatus: TypeAlias = Literal["verified", "pending_review", "legacy_unverified"]
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


class FiscalSource(TypedDict, total=False):
    authority: str
    title: str
    published_at: str
    url: str


class _FiscalManifestEntryRequired(TypedDict):
    exercise: int
    status: FiscalDataStatus
    valid_from: str | None
    valid_to: str | None
    source_ids: list[str]
    values: JsonValue
    sha256: str


class FiscalManifestEntry(_FiscalManifestEntryRequired, total=False):
    notes: str


class FiscalDataset(TypedDict):
    owner: str
    kind: str
    entries: dict[str, FiscalManifestEntry]


class FiscalManifest(TypedDict):
    schema_version: int
    manifest_id: str
    policy: dict[FiscalDataStatus, str]
    sources: dict[str, FiscalSource]
    datasets: dict[str, FiscalDataset]
    content_sha256: str


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def entry(
    exercise: int,
    status: FiscalDataStatus,
    valid_from: str | None,
    valid_to: str | None,
    source_ids: list[str],
    values: JsonValue,
    *,
    notes: str | None = None,
) -> FiscalManifestEntry:
    result: FiscalManifestEntry = {
        "exercise": exercise,
        "status": status,
        "valid_from": valid_from,
        "valid_to": valid_to,
        "source_ids": source_ids,
        "values": values,
        "sha256": digest(values),
    }
    if notes:
        result["notes"] = notes
    return result


def ensure_imss_parameter_parity(
    uma_rows: list[dict[str, Any]],
    wage_rows: list[dict[str, Any]],
    imss: dict[str, Any],
) -> None:
    """Ensure canonical fiscal parameters match the IMSS runtime copy."""
    canonical_uma = {int(row["año"]): row for row in uma_rows}
    canonical_wages = {int(row["año"]): row for row in wage_rows}
    errors: list[str] = []

    for year in sorted(VERIFIED_YEARS):
        runtime_uma = imss.get("uma", {}).get(str(year))
        source_uma = canonical_uma.get(year)
        if runtime_uma is None or source_uma is None:
            errors.append(f"UMA {year}: missing canonical/runtime row")
        else:
            for source_key, runtime_key in (
                ("valor_diario", "diaria"),
                ("valor_mensual", "mensual"),
                ("valor_anual", "anual"),
                ("vigencia_inicio", "vigencia_desde"),
                ("vigencia_fin", "vigencia_hasta"),
            ):
                if source_uma.get(source_key) != runtime_uma.get(runtime_key):
                    errors.append(
                        f"UMA {year}:{runtime_key} canonical={source_uma.get(source_key)!r} "
                        f"runtime={runtime_uma.get(runtime_key)!r}"
                    )

        runtime_wage = imss.get("salario_minimo", {}).get(str(year))
        source_wage = canonical_wages.get(year)
        if runtime_wage is None or source_wage is None:
            errors.append(f"Salario mínimo {year}: missing canonical/runtime row")
        else:
            for source_key, runtime_key in (
                ("resto_pais", "general"),
                ("zona_frontera_norte", "frontera"),
                ("vigencia_inicio", "vigencia_desde"),
            ):
                if source_wage.get(source_key) != runtime_wage.get(runtime_key):
                    errors.append(
                        f"Salario mínimo {year}:{runtime_key} "
                        f"canonical={source_wage.get(source_key)!r} "
                        f"runtime={runtime_wage.get(runtime_key)!r}"
                    )

    if errors:
        raise SystemExit("IMSS canonical/runtime parameter drift: " + "; ".join(errors))


def build_manifest() -> FiscalManifest:
    uma_rows = cast(
        list[dict[str, Any]],
        json.loads((SHARED / "mexico" / "uma.json").read_text(encoding="utf-8")),
    )
    wage_rows = cast(
        list[dict[str, Any]],
        json.loads(
            (SHARED / "mexico" / "salarios_minimos.json").read_text(encoding="utf-8")
        ),
    )
    imss = cast(
        dict[str, Any],
        json.loads((SHARED / "imss-tables.json").read_text(encoding="utf-8")),
    )
    isr = cast(
        dict[str, Any],
        json.loads((SHARED / "isr-tables.json").read_text(encoding="utf-8")),
    )

    ensure_imss_parameter_parity(uma_rows, wage_rows, imss)

    sources = cast(
        dict[str, FiscalSource], dict(imss.get("_meta", {}).get("sources", {}))
    )
    sources["legacy_snapshot"] = {
        "authority": "CatalogMX",
        "title": "Tracked historical snapshot pending authority-source audit",
        "url": "https://github.com/openbancor/catalogmx/tree/master/packages/shared-data",
    }
    # Tighten the source URL used by the 2025 verified minimum-wage row. The
    # canonical JSON only stores values; provenance belongs in this manifest.
    sources["salario_minimo_2025"] = {
        "authority": "CONASAMI / Diario Oficial de la Federación",
        "title": "Salarios mínimos generales 2025",
        "published_at": "2024-12-19",
        "url": "https://dof.gob.mx/2024/CONASAMI/CONASAMI_191224.pdf",
    }
    sources["isr_rmf_2026_anexo_8"] = {
        "authority": "SAT / Diario Oficial de la Federación",
        "title": "Anexo 8 de la Resolución Miscelánea Fiscal para 2026",
        "published_at": "2025-12-28",
        "url": "https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rmf/anexos/Anexo-8-RMF-2026_DOF-28122025.pdf",
    }
    sources["subsidio_empleo_2026"] = {
        "authority": "Diario Oficial de la Federación",
        "title": "Decreto por el que se modifica el diverso que otorga el subsidio para el empleo",
        "published_at": "2025-12-31",
        "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5777649&fecha=31/12/2025",
    }

    datasets: dict[str, FiscalDataset] = {}

    uma_entries: dict[str, FiscalManifestEntry] = {}
    for row in sorted(uma_rows, key=lambda item: item["año"]):
        year = int(row["año"])
        values = {
            "daily": row["valor_diario"],
            "monthly": row["valor_mensual"],
            "annual": row["valor_anual"],
            "currency": row["moneda"],
        }
        uma_status: FiscalDataStatus = (
            "verified" if year in VERIFIED_YEARS else "legacy_unverified"
        )
        source_id = f"uma_{year}" if f"uma_{year}" in sources else "legacy_snapshot"
        uma_entries[str(year)] = entry(
            year,
            uma_status,
            row.get("vigencia_inicio"),
            row.get("vigencia_fin"),
            [source_id],
            values,
        )
    datasets["uma"] = {
        "owner": "INEGI",
        "kind": "regulatory_parameter",
        "entries": uma_entries,
    }

    wage_entries: dict[str, FiscalManifestEntry] = {}
    sorted_wage_rows = sorted(wage_rows, key=lambda item: item["año"])
    for index, row in enumerate(sorted_wage_rows):
        year = int(row["año"])
        next_valid_from = (
            sorted_wage_rows[index + 1].get("vigencia_inicio")
            if index + 1 < len(sorted_wage_rows)
            else None
        )
        valid_to = None
        if next_valid_from:
            successor_boundary = date.fromisoformat(next_valid_from) - timedelta(days=1)
            exercise_boundary = date(year, 12, 31)
            valid_to = min(successor_boundary, exercise_boundary).isoformat()
        values = {
            key: row[key]
            for key in (
                "zona_frontera_norte",
                "resto_pais",
                "zona_general",
                "zona_a",
                "zona_b",
                "zona_c",
                "moneda",
                "periodo",
            )
            if key in row
        }
        wage_status: FiscalDataStatus = (
            "verified" if year in VERIFIED_YEARS else "legacy_unverified"
        )
        source_id = (
            f"salario_minimo_{year}"
            if f"salario_minimo_{year}" in sources
            else "legacy_snapshot"
        )
        wage_entries[str(year)] = entry(
            year,
            wage_status,
            row.get("vigencia_inicio"),
            valid_to,
            [source_id],
            values,
        )
    datasets["minimum_wage"] = {
        "owner": "CONASAMI",
        "kind": "regulatory_parameter",
        "entries": wage_entries,
    }

    ceav = imss["cuotas_imss"]["retiro_cesantia_vejez"]["cesantia_vejez"]
    ceav_entries: dict[str, FiscalManifestEntry] = {}
    for year_text, rates in sorted(ceav["patron_por_ejercicio"].items()):
        year = int(year_text)
        values = {
            "employer_rates": rates,
            "worker_rate": ceav["trabajador"],
        }
        ceav_entries[year_text] = entry(
            year,
            "verified",
            f"{year}-01-01",
            f"{year}-12-31",
            ["lss", "reforma_pensiones_2020"],
            values,
        )
    datasets["imss_ceav"] = {
        "owner": "IMSS / Congreso de la Unión",
        "kind": "rate_schedule",
        "entries": ceav_entries,
    }

    base_values = {
        "enfermedad_maternidad": imss["cuotas_imss"]["enfermedad_maternidad"],
        "invalidez_vida": imss["cuotas_imss"]["invalidez_vida"],
        "retiro": imss["cuotas_imss"]["retiro_cesantia_vejez"]["retiro"],
        "guarderias_prestaciones_sociales": imss["cuotas_imss"][
            "guarderias_prestaciones_sociales"
        ],
        "riesgo_trabajo": imss["cuotas_imss"]["riesgo_trabajo"],
    }
    datasets["imss_base_rates"] = {
        "owner": "IMSS / Congreso de la Unión",
        "kind": "rate_schedule",
        "entries": {
            str(year): entry(
                year,
                "verified",
                f"{year}-01-01",
                f"{year}-12-31",
                ["lss"],
                base_values,
                notes="Shared statutory rates; CEAV employer schedule is versioned separately.",
            )
            for year in sorted(VERIFIED_YEARS)
        },
    }

    mod40 = imss["modalidad_40"]
    mod40_entries: dict[str, FiscalManifestEntry] = {}
    for year_text, reference in sorted(mod40["referencia_por_ejercicio"].items()):
        year = int(year_text)
        values = {
            "constant_components": mod40["calculo"]["componentes_constantes"],
            "ceav_employer_rates": ceav["patron_por_ejercicio"][year_text],
            "reference_top_band_total_rate": reference[
                "tasa_total_banda_4_01_uma_en_adelante"
            ],
            "maximum_sbc_uma": mod40["limites_salario"]["maximo_uma"],
            "minimum_rule": mod40["limites_salario"]["minimo_regla"],
        }
        mod40_entries[year_text] = entry(
            year,
            "verified",
            reference["vigencia_desde"],
            reference["vigencia_hasta"],
            ["lss", "reforma_pensiones_2020"],
            values,
        )
    datasets["imss_modalidad_40"] = {
        "owner": "IMSS / Congreso de la Unión",
        "kind": "derived_rate_schedule",
        "entries": mod40_entries,
    }

    datasets["imss_modalidad_10"] = {
        "owner": "IMSS",
        "kind": "legacy_calculation_model",
        "entries": {
            str(year): entry(
                year,
                "pending_review",
                f"{year}-01-01",
                f"{year}-12-31",
                ["legacy_snapshot"],
                imss["modalidad_10"],
                notes="Retained for compatibility; source/formula audit is not complete.",
            )
            for year in sorted(VERIFIED_YEARS)
        },
    }

    isr_entries: dict[str, FiscalManifestEntry] = {}
    for year_text, brackets in sorted(isr.get("brackets", {}).items()):
        year = int(year_text)
        values = {
            "brackets": brackets,
            "subsidy": isr.get("subsidies", {}).get(year_text),
        }
        notes = "Requires source-by-source Anexo 8/subsidy audit before payroll use."
        source_ids = ["legacy_snapshot"]
        if year == 2026:
            notes = (
                "Known stale: current 2026 brackets do not match RMF 2026 Anexo 8; "
                "subsidy also has a January/February UMA-vigencia boundary."
            )
            source_ids = ["isr_rmf_2026_anexo_8", "subsidio_empleo_2026"]
        isr_entries[year_text] = entry(
            year,
            "pending_review",
            f"{year}-01-01",
            f"{year}-12-31",
            source_ids,
            values,
            notes=notes,
        )
    datasets["isr_payroll"] = {
        "owner": "SAT / SHCP",
        "kind": "rate_schedule",
        "entries": isr_entries,
    }

    manifest = cast(
        FiscalManifest,
        {
            "schema_version": 1,
            "manifest_id": "catalogmx.fiscal",
            "policy": {
                "verified": "Source-audited and safe for the declared exercise/vigencia.",
                "pending_review": "Present for compatibility but consumers should reject for audited payroll.",
                "legacy_unverified": "Historical snapshot retained; provenance audit not complete.",
            },
            "sources": sources,
            "datasets": datasets,
        },
    )
    # Hash the complete provenance-bearing payload, not only the numeric tables.
    # A source/provenance change therefore changes the manifest identity too.
    manifest["content_sha256"] = digest(manifest)
    return manifest


def ensure_sources_resolve(manifest: FiscalManifest) -> None:
    sources = manifest["sources"]
    unresolved: list[str] = []
    for dataset_id, dataset in manifest["datasets"].items():
        for exercise, item in dataset["entries"].items():
            for source_id in item["source_ids"]:
                if source_id not in sources:
                    unresolved.append(f"{dataset_id}:{exercise}:{source_id}")
    if unresolved:
        raise SystemExit("Unresolved fiscal source ids: " + ", ".join(unresolved))


def ensure_history_is_additive(manifest: FiscalManifest) -> None:
    if not MANIFEST_PATH.exists():
        return
    previous = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    missing: list[str] = []
    for dataset_id, old_dataset in previous.get("datasets", {}).items():
        new_dataset = manifest["datasets"].get(dataset_id)
        if new_dataset is None:
            missing.append(f"{dataset_id}:<dataset>")
            continue
        old_exercises = set(old_dataset.get("entries", {}))
        new_exercises = set(new_dataset.get("entries", {}))
        for exercise in sorted(old_exercises - new_exercises):
            missing.append(f"{dataset_id}:{exercise}")
    if missing:
        raise SystemExit(
            "Fiscal history removal is not allowed by normal generation: "
            + ", ".join(missing)
        )


def render_json(manifest: FiscalManifest) -> str:
    return json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def render_typescript(manifest: FiscalManifest) -> str:
    payload = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2)
    if "`" in payload or "${" in payload:
        raise SystemExit("Fiscal manifest contains template-literal control text")
    dataset_ids = sorted(manifest["datasets"])
    ids = "\n".join(f"  '{dataset_id}'," for dataset_id in dataset_ids)
    return (
        "// Generated by scripts/build_fiscal_manifest.py. DO NOT EDIT.\n"
        "export const FISCAL_DATASET_IDS = [\n" + ids + "\n] as const;\n\n"
        "export const FISCAL_MANIFEST_JSON = String.raw`" + payload + "`;\n\n"
        "export const FISCAL_MANIFEST = JSON.parse(FISCAL_MANIFEST_JSON);\n"
    )


def render_python_ids(manifest: FiscalManifest) -> str:
    dataset_ids = sorted(manifest["datasets"])
    ids = "\n".join(f'    "{dataset_id}",' for dataset_id in dataset_ids)
    return (
        "# Generated by scripts/build_fiscal_manifest.py. DO NOT EDIT.\n"
        "from __future__ import annotations\n\n"
        "from typing import Literal, TypeAlias\n\n"
        "FISCAL_DATASET_IDS = (\n" + ids + "\n)\n\n"
        "FiscalDatasetId: TypeAlias = Literal[\n" + ids + "\n]\n\n"
        '__all__ = ["FISCAL_DATASET_IDS", "FiscalDatasetId"]\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    manifest = build_manifest()
    ensure_sources_resolve(manifest)
    ensure_history_is_additive(manifest)
    expected_json = render_json(manifest)
    expected_python_ids = render_python_ids(manifest)
    expected_ts = render_typescript(manifest)

    if args.check:
        errors: list[str] = []
        if (
            not MANIFEST_PATH.exists()
            or MANIFEST_PATH.read_text(encoding="utf-8") != expected_json
        ):
            errors.append(str(MANIFEST_PATH.relative_to(ROOT)))
        if (
            not PYTHON_MANIFEST_PATH.exists()
            or PYTHON_MANIFEST_PATH.read_text(encoding="utf-8") != expected_json
        ):
            errors.append(str(PYTHON_MANIFEST_PATH.relative_to(ROOT)))
        if (
            not PYTHON_IDS_PATH.exists()
            or PYTHON_IDS_PATH.read_text(encoding="utf-8") != expected_python_ids
        ):
            errors.append(str(PYTHON_IDS_PATH.relative_to(ROOT)))
        if not TS_PATH.exists() or TS_PATH.read_text(encoding="utf-8") != expected_ts:
            errors.append(str(TS_PATH.relative_to(ROOT)))
        if errors:
            raise SystemExit("Fiscal manifest drift: " + ", ".join(errors))
        return 0

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    PYTHON_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    PYTHON_IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TS_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(expected_json, encoding="utf-8")
    PYTHON_MANIFEST_PATH.write_text(expected_json, encoding="utf-8")
    PYTHON_IDS_PATH.write_text(expected_python_ids, encoding="utf-8")
    TS_PATH.write_text(expected_ts, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
