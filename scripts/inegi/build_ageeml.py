#!/usr/bin/env python3
"""Build a reproducible INEGI AGEEML release artifact.

The source is INEGI's current national predefined catalog in its
"minúscula con acento, incluye bajas" ZIP distribution. The builder preserves
all active/inactive localities and interstate-zone records while normalizing a
stable subset of fields into SQLite.

Maintenance is fail-closed: network failures, an unexpected ZIP layout,
missing required columns, implausibly small data, incomplete 01-32 state
coverage, or malformed numeric geostatistical keys abort the update.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sqlite3
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Sequence

DATASET_ID = "inegi.ageeml"
DATASET_VERSION = "1"
AUTHORITATIVE_PORTAL = "https://www.inegi.org.mx/app/ageeml/default.html"
SOURCE_URL = "https://www.inegi.org.mx/contenidos/app/ageeml/min_con_acento_baja.zip"
OUTPUT_NAME = "inegi_ageeml.sqlite3"
MANIFEST_NAME = "inegi_ageeml.manifest.json"
MIN_NATIONAL_RECORDS = 250_000
EXPECTED_STATE_CODES = frozenset(f"{value:02d}" for value in range(1, 33))

# Stable normalized contract. INEGI has historically called the first field
# MAPA; recent AGEEML consumers also expose it as CVEGEO. Both represent the
# concatenated geographic key and are accepted as aliases.
OUTPUT_COLUMNS = (
    "CVEGEO",
    "Estatus",
    "CVE_ENT",
    "NOM_ENT",
    "NOM_ABR",
    "CVE_MUN",
    "NOM_MUN",
    "CVE_LOC",
    "NOM_LOC",
    "AMBITO",
    "LATITUD",
    "LONGITUD",
    "LAT_DECIMAL",
    "LON_DECIMAL",
    "ALTITUD",
    "CVE_CARTA",
    "POB_TOTAL",
    "POB_MASCULINA",
    "POB_FEMENINA",
    "TOTAL_DE_VIVIENDAS_HABITADAS",
)

REQUIRED_SOURCE_COLUMNS = frozenset(
    {
        "CVE_ENT",
        "NOM_ENT",
        "NOM_ABR",
        "CVE_MUN",
        "NOM_MUN",
        "CVE_LOC",
        "NOM_LOC",
        "AMBITO",
        "LATITUD",
        "LONGITUD",
        "LAT_DECIMAL",
        "LON_DECIMAL",
        "ALTITUD",
        "CVE_CARTA",
        "POB_TOTAL",
        "POB_MASCULINA",
        "POB_FEMENINA",
        "TOTAL DE VIVIENDAS HABITADAS",
    }
)

NULL_MARKER_FIELDS = frozenset(
    {
        "LATITUD",
        "LONGITUD",
        "LAT_DECIMAL",
        "LON_DECIMAL",
        "ALTITUD",
        "CVE_CARTA",
        "POB_TOTAL",
        "POB_MASCULINA",
        "POB_FEMENINA",
        "TOTAL DE VIVIENDAS HABITADAS",
    }
)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quote_identifier(value: str) -> str:
    """Quote an SQLite identifier."""
    return '"' + value.replace('"', '""') + '"'


def normalize_header(value: str) -> str:
    """Normalize BOM/whitespace while preserving INEGI's field spelling."""
    return value.strip().lstrip("\ufeff")


def select_csv_member(archive: zipfile.ZipFile) -> str:
    """Select the one AGEEML UTF CSV from the official ZIP."""
    candidates = [
        name
        for name in archive.namelist()
        if not name.endswith("/")
        and name.lower().endswith(".csv")
        and "ageeml_" in Path(name).name.lower()
        and "_utf" in Path(name).stem.lower()
    ]
    if len(candidates) != 1:
        raise RuntimeError(
            "unexpected AGEEML ZIP layout: expected exactly one AGEEML *_utf.csv, "
            f"found {candidates}"
        )
    return candidates[0]


def normalize_row(row: dict[str, str | None]) -> tuple[str | None, ...]:
    """Normalize one source row into the stable SQLite contract."""
    cleaned = {
        normalize_header(key): (value.strip() if value is not None else "")
        for key, value in row.items()
        if key is not None
    }

    cvegeo = cleaned.get("CVEGEO") or cleaned.get("MAPA") or ""
    source_values: dict[str, str] = {
        "CVEGEO": cvegeo,
        "Estatus": cleaned.get("Estatus") or cleaned.get("ESTATUS") or "",
        "CVE_ENT": cleaned.get("CVE_ENT", ""),
        "NOM_ENT": cleaned.get("NOM_ENT", ""),
        "NOM_ABR": cleaned.get("NOM_ABR", ""),
        "CVE_MUN": cleaned.get("CVE_MUN", ""),
        "NOM_MUN": cleaned.get("NOM_MUN", ""),
        "CVE_LOC": cleaned.get("CVE_LOC", ""),
        "NOM_LOC": cleaned.get("NOM_LOC", ""),
        "AMBITO": cleaned.get("AMBITO", ""),
        "LATITUD": cleaned.get("LATITUD", ""),
        "LONGITUD": cleaned.get("LONGITUD", ""),
        "LAT_DECIMAL": cleaned.get("LAT_DECIMAL", ""),
        "LON_DECIMAL": cleaned.get("LON_DECIMAL", ""),
        "ALTITUD": cleaned.get("ALTITUD", ""),
        "CVE_CARTA": cleaned.get("CVE_CARTA", ""),
        "POB_TOTAL": cleaned.get("POB_TOTAL", ""),
        "POB_MASCULINA": cleaned.get("POB_MASCULINA", ""),
        "POB_FEMENINA": cleaned.get("POB_FEMENINA", ""),
        "TOTAL_DE_VIVIENDAS_HABITADAS": cleaned.get(
            "TOTAL DE VIVIENDAS HABITADAS", ""
        ),
    }

    values: list[str | None] = []
    for output_column in OUTPUT_COLUMNS:
        value = source_values[output_column]
        source_column = (
            "TOTAL DE VIVIENDAS HABITADAS"
            if output_column == "TOTAL_DE_VIVIENDAS_HABITADAS"
            else output_column
        )
        if source_column in NULL_MARKER_FIELDS and value in {"", "-", "*"}:
            values.append(None)
        else:
            values.append(value)
    return tuple(values)


def validate_source_header(fieldnames: Sequence[str] | None) -> None:
    """Require the known AGEEML locality schema and a geographic-key field."""
    if not fieldnames:
        raise RuntimeError("AGEEML CSV has no header")
    normalized = {normalize_header(value) for value in fieldnames}
    missing = sorted(REQUIRED_SOURCE_COLUMNS - normalized)
    if missing:
        raise RuntimeError(f"AGEEML CSV is missing required columns: {missing}")
    if not ({"CVEGEO", "MAPA"} & normalized):
        raise RuntimeError("AGEEML CSV must contain CVEGEO or MAPA")


def iter_csv_rows(
    archive_path: Path,
) -> tuple[str, tuple[str, ...], Iterator[tuple[str | None, ...]]]:
    """Open the official ZIP and stream normalized CSV rows."""
    archive = zipfile.ZipFile(archive_path)
    member = select_csv_member(archive)
    binary = archive.open(member)
    text = io.TextIOWrapper(binary, encoding="utf-8-sig", newline="")
    reader = csv.DictReader(text)
    validate_source_header(reader.fieldnames)
    source_columns = tuple(normalize_header(value) for value in reader.fieldnames or ())

    def rows() -> Iterator[tuple[str | None, ...]]:
        try:
            for source_row in reader:
                yield normalize_row(source_row)
        finally:
            text.close()
            archive.close()

    return member, source_columns, rows()


def create_database(
    archive_path: Path,
    output_db: Path,
    *,
    min_records: int = MIN_NATIONAL_RECORDS,
) -> dict[str, Any]:
    """Validate the national catalog and build normalized SQLite."""
    output_db.parent.mkdir(parents=True, exist_ok=True)
    output_db.unlink(missing_ok=True)

    source_member, source_columns, rows = iter_csv_rows(archive_path)
    connection = sqlite3.connect(output_db)
    numeric_states: set[str] = set()
    interstate_codes: set[str] = set()
    record_count = 0
    inactive_count = 0

    try:
        columns_sql = ",\n                ".join(
            f"{quote_identifier(column)} TEXT" for column in OUTPUT_COLUMNS
        )
        connection.execute(
            f"""
            CREATE TABLE localities (
                row_id INTEGER PRIMARY KEY,
                {columns_sql}
            )
            """
        )

        placeholders = ", ".join("?" for _ in OUTPUT_COLUMNS)
        quoted_columns = ", ".join(quote_identifier(column) for column in OUTPUT_COLUMNS)
        insert_sql = f"INSERT INTO localities ({quoted_columns}) VALUES ({placeholders})"
        indexes = {column: index for index, column in enumerate(OUTPUT_COLUMNS)}

        batch: list[tuple[str | None, ...]] = []
        for row in rows:
            state_code = row[indexes["CVE_ENT"]] or ""
            municipality_code = row[indexes["CVE_MUN"]] or ""
            locality_code = row[indexes["CVE_LOC"]] or ""
            cvegeo = row[indexes["CVEGEO"]] or ""

            if state_code.isdigit():
                if len(state_code) != 2 or not 1 <= int(state_code) <= 32:
                    raise RuntimeError(f"invalid AGEEML state code: {state_code!r}")
                if len(municipality_code) != 3 or not municipality_code.isdigit():
                    raise RuntimeError(
                        f"invalid AGEEML municipality code: {municipality_code!r}"
                    )
                if len(locality_code) != 4 or not locality_code.isdigit():
                    raise RuntimeError(
                        f"invalid AGEEML locality code: {locality_code!r}"
                    )
                expected_cvegeo = state_code + municipality_code + locality_code
                if cvegeo and cvegeo != expected_cvegeo:
                    raise RuntimeError(
                        "AGEEML geographic key mismatch: "
                        f"expected {expected_cvegeo}, got {cvegeo}"
                    )
                numeric_states.add(state_code)
            else:
                if not state_code or len(state_code) > 2:
                    raise RuntimeError(f"invalid AGEEML interstate code: {state_code!r}")
                interstate_codes.add(state_code)

            if row[indexes["Estatus"]]:
                inactive_count += 1

            batch.append(row)
            record_count += 1
            if len(batch) >= 2_000:
                connection.executemany(insert_sql, batch)
                batch.clear()

        if batch:
            connection.executemany(insert_sql, batch)

        if record_count < min_records:
            raise RuntimeError(
                "AGEEML national catalog is implausibly small: "
                f"{record_count} records, expected at least {min_records}"
            )
        if numeric_states != EXPECTED_STATE_CODES:
            missing = sorted(EXPECTED_STATE_CODES - numeric_states)
            extra = sorted(numeric_states - EXPECTED_STATE_CODES)
            raise RuntimeError(
                "AGEEML catalog has unexpected state coverage; "
                f"missing={missing or 'none'}, extra={extra or 'none'}"
            )

        connection.execute("CREATE INDEX idx_ageeml_cvegeo ON localities(CVEGEO)")
        connection.execute(
            "CREATE INDEX idx_ageeml_state_municipality "
            "ON localities(CVE_ENT, CVE_MUN)"
        )
        connection.execute(
            "CREATE INDEX idx_ageeml_locality ON localities(CVE_ENT, CVE_MUN, CVE_LOC)"
        )
        connection.execute("CREATE INDEX idx_ageeml_status ON localities(Estatus)")
        connection.commit()
        connection.execute("VACUUM")
        connection.commit()
    except Exception:
        connection.close()
        output_db.unlink(missing_ok=True)
        raise
    else:
        connection.close()

    return {
        "source_member": source_member,
        "source_columns": list(source_columns),
        "record_count": record_count,
        "state_count": len(numeric_states),
        "interstate_codes": sorted(interstate_codes),
        "inactive_count": inactive_count,
    }


def semantic_hash(database: Path) -> str:
    """Hash normalized content independent of source or SQLite row order."""
    digest = hashlib.sha256()
    digest.update(DATASET_ID.encode("utf-8"))
    digest.update(b"\0")
    digest.update(DATASET_VERSION.encode("utf-8"))
    digest.update(b"\0")
    digest.update(json.dumps(OUTPUT_COLUMNS).encode("utf-8"))
    digest.update(b"\0")

    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        quoted_columns = ", ".join(quote_identifier(column) for column in OUTPUT_COLUMNS)
        query = f"SELECT {quoted_columns} FROM localities ORDER BY {quoted_columns}"
        for row in connection.execute(query):
            digest.update(
                json.dumps(
                    list(row), ensure_ascii=False, separators=(",", ":")
                ).encode("utf-8")
            )
            digest.update(b"\n")
    finally:
        connection.close()
    return digest.hexdigest()


def fetch_source(destination: Path) -> dict[str, Any]:
    """Download the official predefined ZIP and capture HTTP provenance."""
    request = urllib.request.Request(
        SOURCE_URL, headers={"User-Agent": "catalogmx-ageeml-builder"}
    )
    with urllib.request.urlopen(request, timeout=180) as response:  # noqa: S310
        with destination.open("wb") as output:
            shutil.copyfileobj(response, output)
        return {
            "url": SOURCE_URL,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "last_modified": response.headers.get("Last-Modified"),
            "etag": response.headers.get("ETag"),
            "content_type": response.headers.get("Content-Type"),
        }


def build_manifest(
    archive_path: Path,
    output_db: Path,
    statistics: dict[str, Any],
    source_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Create provenance and integrity metadata."""
    return {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "authority": {
            "name": "Instituto Nacional de Estadística y Geografía (INEGI)",
            "portal": AUTHORITATIVE_PORTAL,
            "predefined_catalog": SOURCE_URL,
        },
        "ingestion": {
            "release": source_metadata.get("last_modified")
            or source_metadata.get("retrieved_at")
            or "predefined-current",
            "retrieved_at": source_metadata.get("retrieved_at"),
            "last_modified": source_metadata.get("last_modified"),
            "etag": source_metadata.get("etag"),
            "content_type": source_metadata.get("content_type"),
            "source_sha256": sha256_file(archive_path),
            "source_member": statistics["source_member"],
            "source_columns": statistics["source_columns"],
        },
        "dataset": {
            "file": output_db.name,
            "file_sha256": sha256_file(output_db),
            "content_sha256": semantic_hash(output_db),
            "record_count": statistics["record_count"],
            "state_count": statistics["state_count"],
            "interstate_codes": statistics["interstate_codes"],
            "inactive_count": statistics["inactive_count"],
            "columns": list(OUTPUT_COLUMNS),
        },
    }


def build_from_source(
    archive_path: Path,
    output_dir: Path,
    *,
    source_metadata: dict[str, Any] | None = None,
    min_records: int = MIN_NATIONAL_RECORDS,
) -> tuple[Path, Path, dict[str, Any]]:
    """Build the release artifact from an already materialized AGEEML ZIP."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_db = output_dir / OUTPUT_NAME
    manifest_path = output_dir / MANIFEST_NAME

    statistics = create_database(archive_path, output_db, min_records=min_records)
    manifest = build_manifest(archive_path, output_db, statistics, source_metadata or {})
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_db, manifest_path, manifest


def build_latest(output_dir: Path) -> tuple[Path, Path, dict[str, Any]]:
    """Download the current official AGEEML catalog and build its artifact."""
    with tempfile.TemporaryDirectory(prefix="catalogmx-ageeml-") as temp_dir:
        archive_path = Path(temp_dir) / "min_con_acento_baja.zip"
        metadata = fetch_source(archive_path)
        return build_from_source(archive_path, output_dir, source_metadata=metadata)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument(
        "--source-zip",
        type=Path,
        help="Build from a local AGEEML ZIP instead of downloading upstream",
    )
    args = parser.parse_args(argv)

    if args.source_zip:
        output_db, manifest_path, manifest = build_from_source(
            args.source_zip, args.output_dir
        )
    else:
        output_db, manifest_path, manifest = build_latest(args.output_dir)

    print(f"database={output_db}")
    print(f"manifest={manifest_path}")
    print(f"records={manifest['dataset']['record_count']}")
    print(f"states={manifest['dataset']['state_count']}")
    print(f"interstate_codes={','.join(manifest['dataset']['interstate_codes'])}")
    print(f"content_sha256={manifest['dataset']['content_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
