#!/usr/bin/env python3
"""One-shot finalization for the SAT Nómina 1.2 parity branch.

The temporary workflow that invokes this script deletes both itself and this
script before committing. Keeping the transformations explicit makes the large
canonical data refresh deterministic without hand-editing generated JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one replacement, found {count}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_registry() -> None:
    path = ROOT / "packages/shared-data/catalog-registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    dataset = next(item for item in registry["datasets"] if item["id"] == "sat.nomina_1_2")
    implementation = dataset["implementation"]
    implementation["status"] = "complete"
    implementation["embedded_convenience_json_files"] = 13
    implementation["normalized_catalogs"] = 13
    implementation["missing_normalized_catalogs"] = []
    implementation["consumer_migration_required_before_removal"] = True
    dataset["notes"] = (
        "Revision E is effective from 2026-01-01. The canonical release contains the "
        "13 catalog families represented by catNomina.xsd; nomina_estados remains an "
        "explicitly excluded auxiliary table. All 13 embedded JSON compatibility views "
        "are generated from the canonical artifact, and Python, TypeScript, Dart and "
        "Kotlin expose 13/13 catalog families. Kotlin no longer carries embedded "
        "regulatory copies. Embedded views remain until issue #57 completes the common "
        "dataset resolver/profile migration."
    )
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_scheduler() -> None:
    path = ROOT / "scripts/catalog_maintenance.py"
    old = '''    "sat.nomina_1_2": (\n        sys.executable,\n        "scripts/sat/build_nomina_12.py",\n        "--output-dir",\n        "dist/catalog-artifacts/sat-nomina-12",\n    ),'''
    new = '''    "sat.nomina_1_2": (\n        sys.executable,\n        "scripts/sat/build_nomina_12.py",\n        "--output-dir",\n        "dist/catalog-artifacts/sat-nomina-12",\n        "--compat-output-dir",\n        "packages/shared-data/sat/nomina_1.2",\n    ),'''
    replace_once(path, old, new)

    test_path = ROOT / "packages/python/tests/test_catalog_maintenance_script.py"
    marker = '''\ndef test_unconfigured_adapter_is_reported_without_execution():\n'''
    insertion = '''\ndef test_nomina_adapter_regenerates_compatibility_views():\n    module = load_module()\n    command = module.ADAPTERS["sat.nomina_1_2"]\n\n    assert "--compat-output-dir" in command\n    assert "packages/shared-data/sat/nomina_1.2" in command\n\n\ndef test_unconfigured_adapter_is_reported_without_execution():\n'''
    replace_once(test_path, marker, insertion)


def update_docs() -> None:
    path = ROOT / "docs/guides/sat-nomina-12.md"
    path.write_text(
        '''# SAT Nómina 1.2 data lifecycle

CatalogMX treats SAT Nómina 1.2 as a versioned regulatory dataset with its own provenance, validation and release lifecycle. Language APIs and embedded JSON compatibility views consume that dataset; they are not the canonical source.

## Revision E

Nómina 1.2 remains the current payroll complement. **Revision E** is effective from **2026-01-01**.

The repository keeps the current `catNomina.xsd` synchronized between shared data and the Svelte browser asset. Revision E includes, among other changes guarded by tests, `c_TipoPercepcion` codes through `057` and `c_TipoDeduccion` codes through `115`.

Canonical registry entry: `sat.nomina_1_2`.

## Authority and technical ingestion

SAT remains authoritative. The registry records the SAT payroll/CFDI notice, `catNomina.xls`, and `catNomina.xsd` as authoritative resources. `phpcfdi/resources-sat-catalogs` is a versioned technical ingestion mirror used for deterministic normalized extraction; it is not the legal authority.

## Canonical 13-table boundary

`catNomina.xsd` represents thirteen catalog families. The canonical Nómina artifact contains exactly:

- `nomina_bancos`
- `nomina_origenes_recursos`
- `nomina_periodicidades_pagos`
- `nomina_riesgos_puestos`
- `nomina_tipos_contratos`
- `nomina_tipos_deducciones`
- `nomina_tipos_horas`
- `nomina_tipos_incapacidades`
- `nomina_tipos_jornadas`
- `nomina_tipos_nominas`
- `nomina_tipos_otros_pagos`
- `nomina_tipos_percepciones`
- `nomina_tipos_regimenes`

The technical mirror also contains `nomina_estados`. That table is explicitly **auxiliary** for this dataset and is not copied into the canonical Nómina artifact. The builder validates the complete `nomina_%` namespace as **13 canonical + the known auxiliary table**. Any missing or newly introduced table stops the build for review.

## Reproducible release artifact

`scripts/sat/build_nomina_12.py` builds `sat_nomina_12.sqlite3` and `sat_nomina_12.manifest.json`. It resolves a versioned technical-mirror release, verifies the source digest when available, validates the exact table family, copies only the thirteen canonical tables and indexes, records row counts and provenance, and emits both byte-level and semantic SHA-256 hashes.

Download failure, checksum mismatch, missing tables or upstream schema drift fail closed. There is no synthetic fallback.

## Thirteen compatibility views

`packages/shared-data/sat/nomina_1.2` contains one generated compatibility JSON view for every canonical family. `scripts/catalog_maintenance.py` invokes the builder with `--compat-output-dir`, so the same canonical ingestion refreshes the release artifact and the embedded compatibility views.

SAT-owned code, description and vigencia fields are regenerated from canonical SQLite data. CatalogMX-specific enrichments are narrowly whitelisted and preserved by code:

- `periodicidad_pago.json`: `days`
- `riesgo_puesto.json`: `prima_minima`, `prima_media`, `prima_maxima`

Compatibility consumers may expose aliases such as `code`/`clave`, `description`/`descripcion`, and `full_name`/`razon_social`; those aliases do not create an independent regulatory source.

## Cross-language API parity

Python, TypeScript, Dart and Kotlin expose all **13/13** Nómina catalog families. Existing seven public catalog APIs remain available and the six previously missing families are now first-class APIs:

- `c_OrigenRecurso`
- `c_TipoDeduccion`
- `c_TipoHoras`
- `c_TipoIncapacidad`
- `c_TipoOtroPago`
- `c_TipoPercepcion`

Python uses the shared-data resolver for embedded compatibility views. TypeScript and Dart normalize historical aliases at their catalog boundary. Kotlin first reads canonical `nomina_*` SQLite tables when a dataset database is configured and otherwise reads the generated shared JSON views; hard-coded Nómina regulatory maps have been removed.

## Publishing and scheduling

The registry freshness SLA is 31 days. The generic scheduler therefore places `sat.nomina_1_2` in the monthly cadence. The release adapter writes below `dist/catalog-artifacts/sat-nomina-12` and regenerates the thirteen compatibility views in the repository.

The generic publisher compares manifest `content_sha256`; a new data release is created only when canonical Nómina content changes. Package/library versions remain independent from catalog-data versions.

## Remaining resolver migration

Issue #57 remains the transport/distribution migration. The API completeness work is no longer blocked on it: all four SDKs already expose 13/13 through the compatibility contract. The remaining sequence is to make installed consumers resolve the independently versioned canonical dataset/profile, prove that path with installed-package integration tests, and only then remove embedded JSON compatibility views.
''',
        encoding="utf-8",
    )


def update_revision_test() -> None:
    path = ROOT / "packages/python/tests/test_sat_nomina_revision_e.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "def test_registry_records_revision_e_canonical_distribution_and_api_gap():\n    \"\"\"Canonical data completeness and language API completeness are distinct.\"\"\"",
        "def test_registry_records_revision_e_canonical_distribution_and_api_parity():\n    \"\"\"Canonical distribution and compatibility APIs cover all 13 families.\"\"\"",
    )
    replacements = {
        'assert implementation["status"] == "partial"': 'assert implementation["status"] == "complete"',
        'assert implementation["embedded_convenience_json_files"] == 7': 'assert implementation["embedded_convenience_json_files"] == 13',
        'assert implementation["normalized_catalogs"] == 7': 'assert implementation["normalized_catalogs"] == 13',
        '''    assert set(implementation["missing_normalized_catalogs"]) == {\n        "c_OrigenRecurso",\n        "c_TipoDeduccion",\n        "c_TipoHoras",\n        "c_TipoIncapacidad",\n        "c_TipoOtroPago",\n        "c_TipoPercepcion",\n    }''': '    assert implementation["missing_normalized_catalogs"] == []',
    }
    for old, new in replacements.items():
        if old not in text:
            raise RuntimeError(f"revision test replacement not found: {old[:80]!r}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


def update_typescript_regressions() -> None:
    path = ROOT / "packages/typescript/tests/sat-catalogs-complete.test.ts"
    text = path.read_text(encoding="utf-8")
    replacements = [
        ("expect(banco!.name).toBe('Banamex');", "expect(banco!.name.toUpperCase()).toContain('BANAMEX');"),
        ("expect(BancoNominaCatalog.getName('002')).toBe('Banamex');", "expect(BancoNominaCatalog.getName('002')?.toUpperCase()).toContain('BANAMEX');"),
        ('''  test('getRazonSocial() returns undefined when data field is missing', () => {\n    // The underlying data uses "full_name" instead of "razon_social",\n    // so this returns undefined for all entries.\n    expect(BancoNominaCatalog.getRazonSocial('002')).toBeUndefined();\n  });''', '''  test('getRazonSocial() exposes the compatibility legal-name alias', () => {\n    expect(BancoNominaCatalog.getRazonSocial('002')).toContain('Banco Nacional');\n  });'''),
        ('''\n  // Note: searchByName crashes due to data/type mismatch (razon_social is undefined).\n  // This documents the known issue rather than asserting broken behavior.\n''', '''\n  test('searchByName() searches display and legal names', () => {\n    expect(BancoNominaCatalog.searchByName('Banamex').length).toBeGreaterThan(0);\n  });\n'''),
        ('''  test('getDescription() returns undefined (data field mismatch)', () => {\n    // Data uses "description" but code reads "descripcion"\n    expect(TipoRegimenCatalog.getDescription('02')).toBeUndefined();\n  });''', '''  test('getDescription() exposes the normalized description alias', () => {\n    expect(TipoRegimenCatalog.getDescription('02')).toContain('Sueldos');\n  });'''),
        ("test('getAll() returns a non-empty array of 5 risk classes'", "test('getAll() returns five risk classes plus No aplica'"),
        ("expect(all.length).toBe(5);", "expect(all.length).toBe(6);"),
        ("expect(RiesgoPuestoCatalog.getRiesgo('99')).toBeUndefined();", "expect(RiesgoPuestoCatalog.getRiesgo('ZZ')).toBeUndefined();"),
        ("expect(RiesgoPuestoCatalog.isValid('99')).toBe(false);", "expect(RiesgoPuestoCatalog.isValid('99')).toBe(true);"),
        ("expect(RiesgoPuestoCatalog.getDescription('99')).toBeUndefined();", "expect(RiesgoPuestoCatalog.getDescription('99')).toBe('No aplica');"),
        ('''    // Note: isOrdinaria('E') also returns true because "extraordinaria"\n    // contains the substring "ORDINARIA". This is a known quirk of the\n    // substring-based implementation.\n    expect(TipoNominaCatalog.isOrdinaria('E')).toBe(true);''', '''    expect(TipoNominaCatalog.isOrdinaria('E')).toBe(false);'''),
    ]
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise RuntimeError(f"TypeScript replacement expected once, found {count}: {old[:90]!r}")
        text = text.replace(old, new, 1)

    # Obsolete comments describing the old description-field mismatch.
    text = text.replace(
        '''\n  // Note: searchByDescription, isDiurna, isNocturna, isMixta reference\n  // "descripcion" but the actual data field is "description". These methods\n  // throw at runtime due to the property mismatch. We test that the catalog\n  // loads correctly and basic lookups work.\n''',
        "\n",
    )
    text = text.replace(
        '''\n  // Note: isIndefinido, isDeterminado, searchByDescription reference "descripcion"\n  // but the actual JSON data field is "description". These throw at runtime.\n''',
        "\n",
    )
    path.write_text(text, encoding="utf-8")


def fix_kotlin_vigencia_normalization() -> None:
    path = ROOT / "packages/kotlin/src/main/kotlin/com/openbancor/catalogmx/catalogs/sat/nomina/NominaCatalogs.kt"
    replace_once(
        path,
        '''        if (item.containsKey("vigencia_desde")) {\n            item.putIfAbsent("valid_from", item["vigencia_desde"]?.toString()?.ifBlank { null })\n        }\n        if (item.containsKey("vigencia_hasta")) {\n            item.putIfAbsent("valid_to", item["vigencia_hasta"]?.toString()?.ifBlank { null })\n        }''',
        '''        if (item.containsKey("vigencia_desde")) {\n            val validFrom = item["vigencia_desde"]?.toString()?.takeIf { it.isNotBlank() }\n            item.putIfAbsent("valid_from", validFrom)\n        }\n        if (item.containsKey("vigencia_hasta")) {\n            val validTo = item["vigencia_hasta"]?.toString()?.takeIf { it.isNotBlank() }\n            item.putIfAbsent("valid_to", validTo)\n        }''',
    )


def main() -> None:
    update_registry()
    update_scheduler()
    update_docs()
    update_revision_test()
    update_typescript_regressions()
    fix_kotlin_vigencia_normalization()


if __name__ == "__main__":
    main()
