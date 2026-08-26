#!/usr/bin/env python3
"""Build a reproducible SEPOMEX national postal-code SQLite artifact.

The source is the official Correos de México / SEPOMEX national TXT export.
The builder is intentionally fail-closed: an unavailable source, unexpected
schema, malformed row, implausibly small national dataset, or incomplete state
coverage aborts the update instead of falling back to synthetic data.

The output manifest contains a semantic content hash so the generic catalog
maintenance workflow publishes a new data release only when normalized postal
code content actually changes.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

DATASET_ID = "sepomex.codigos_postales"
DATASET_VERSION = "1"
AUTHORITATIVE_PORTAL = (
    "https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/"
    "CodigoPostal_Exportar.aspx"
)
SOURCE_URL = "https://www.correosdemexico.gob.mx/datosabiertos/cp/cpdescarga.txt"
OUTPUT_NAME = "sepomex_codigos_postales.sqlite3"
MANIFEST_NAME = "sepomex_codigos_postales.manifest.json"
MIN_NATIONAL_RECORDS = 100_000
EXPECTED_STATE_CODES = frozenset(f"{value:02d}" for value in range(1, 33))
EXPECTED_COLUMNS = (
    "d_codigo",
    "d_asenta",
    "d_tipo_asenta",
    "D_mnpio",
    "d_estado",
    "d_ciudad",
    "d_CP",
    "c_estado",
    "c_oficina",
    "c_CP",
    "c_tipo_asenta",
    "c_mnpio",
    "id_asenta_cpcons",
    "d_zona",
    "c_cve_ciudad",
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


def decode_source(raw: bytes) -> tuple[str, str]:
    """Decode SEPOMEX text, preferring explicit Unicode before legacy encodings."""
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise RuntimeError("unable to decode SEPOMEX source")  # pragma: no cover


def iter_source_rows(source_path: Path) -> tuple[str, Iterator[tuple[str, ...]]]:
    """Locate the official header and return normalized source rows."""
    text, encoding = decode_source(source_path.read_bytes())
    reader = csv.reader(io.StringIO(text), delimiter="|")

    header_found = False

    def rows() -> Iterator[tuple[str, ...]]:
        nonlocal header_found
        for row_number, raw_row in enumerate(reader, start=1):
            row = tuple(value.strip().lstrip("\ufeff") for value in raw_row)

            if not header_found:
                if row == EXPECTED_COLUMNS:
                    header_found = True
                continue

            if not row or not any(row):
                continue
            if len(row) != len(EXPECTED_COLUMNS):
                raise RuntimeError(
                    f"unexpected SEPOMEX row width at source line {row_number}: "
                    f"expected {len(EXPECTED_COLUMNS)}, got {len(row)}"
                )

            postal_code = row[0]
            if len(postal_code) != 5 or not postal_code.isdigit():
                raise RuntimeError(
                    f"invalid SEPOMEX postal code at source line {row_number}: "
                    f"{postal_code!r}"
                )

            state_code = row[7]
            if not state_code.isdigit() or not 1 <= int(state_code) <= 32:
                raise RuntimeError(
                    f"invalid SEPOMEX state code at source line {row_number}: "
                    f"{state_code!r}"
                )

            yield row

        if not header_found:
            raise RuntimeError(
                "SEPOMEX source does not contain the expected 15-column TXT header"
            )

    return encoding, rows()


def create_database(
    source_path: Path,
    output_db: Path,
    *,
    min_records: int = MIN_NATIONAL_RECORDS,
) -> dict[str, Any]:
    """Parse the national export, validate coverage, and build SQLite."""
    output_db.parent.mkdir(parents=True, exist_ok=True)
    output_db.unlink(missing_ok=True)

    encoding, rows = iter_source_rows(source_path)
    connection = sqlite3.connect(output_db)
    state_codes: set[str] = set()
    postal_codes: set[str] = set()
    record_count = 0

    try:
        columns_sql = ",\n                ".join(
            f"{quote_identifier(column)} TEXT NOT NULL" for column in EXPECTED_COLUMNS
        )
        connection.execute(
            f"""
            CREATE TABLE postal_codes (
                row_id INTEGER PRIMARY KEY,
                {columns_sql}
            )
            """
        )

        placeholders = ", ".join("?" for _ in EXPECTED_COLUMNS)
        quoted_columns = ", ".join(quote_identifier(column) for column in EXPECTED_COLUMNS)
        insert_sql = (
            f"INSERT INTO postal_codes ({quoted_columns}) VALUES ({placeholders})"
        )

        batch: list[tuple[str, ...]] = []
        for row in rows:
            batch.append(row)
            record_count += 1
            postal_codes.add(row[0])
            state_codes.add(row[7].zfill(2))

            if len(batch) >= 2_000:
                connection.executemany(insert_sql, batch)
                batch.clear()

        if batch:
            connection.executemany(insert_sql, batch)

        if record_count < min_records:
            raise RuntimeError(
                "SEPOMEX national export is implausibly small: "
                f"{record_count} records, expected at least {min_records}"
            )
        if state_codes != EXPECTED_STATE_CODES:
            missing = sorted(EXPECTED_STATE_CODES - state_codes)
            extra = sorted(state_codes - EXPECTED_STATE_CODES)
            raise RuntimeError(
                "SEPOMEX national export has unexpected state coverage; "
                f"missing={missing or 'none'}, extra={extra or 'none'}"
            )

        connection.execute(
            "CREATE INDEX idx_postal_codes_cp ON postal_codes(d_codigo)"
        )
        connection.execute(
            "CREATE INDEX idx_postal_codes_state_municipality "
            "ON postal_codes(c_estado, c_mnpio)"
        )
        connection.execute(
            "CREATE INDEX idx_postal_codes_settlement ON postal_codes(d_asenta)"
        )
        connection.execute(
            "CREATE INDEX idx_postal_codes_cons ON postal_codes(id_asenta_cpcons)"
        )
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
        "encoding": encoding,
        "record_count": record_count,
        "unique_postal_codes": len(postal_codes),
        "state_count": len(state_codes),
    }


def semantic_hash(database: Path) -> str:
    """Hash normalized rows independent of source ordering or SQLite bytes."""
    digest = hashlib.sha256()
    digest.update(DATASET_ID.encode("utf-8"))
    digest.update(b"\0")
    digest.update(DATASET_VERSION.encode("utf-8"))
    digest.update(b"\0")
    digest.update(json.dumps(EXPECTED_COLUMNS).encode("utf-8"))
    digest.update(b"\0")

    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        quoted_columns = ", ".join(quote_identifier(column) for column in EXPECTED_COLUMNS)
        order_by = quoted_columns
        query = f"SELECT {quoted_columns} FROM postal_codes ORDER BY {order_by}"
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
    """Download the official national TXT export and capture HTTP provenance."""
    request = urllib.request.Request(
        SOURCE_URL, headers={"User-Agent": "catalogmx-sepomex-builder"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
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
    source_path: Path,
    output_db: Path,
    statistics: dict[str, Any],
    source_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Create provenance, integrity, rights, and inventory metadata."""
    return {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "authority": {
            "name": "Servicio Postal Mexicano / Correos de México",
            "portal": AUTHORITATIVE_PORTAL,
            "data_url": SOURCE_URL,
        },
        "rights": {
            "source_terms_checked_at": "2026-08-26",
            "project_relicenses_source_data": False,
            "notice": (
                "The official SEPOMEX portal provides the national catalog free "
                "of charge and states that commercialization of the catalog, in "
                "whole or in part, is not permitted. Consumers must comply with "
                "the source terms independently of CatalogMX code licensing."
            ),
        },
        "ingestion": {
            "release": source_metadata.get("last_modified")
            or source_metadata.get("retrieved_at")
            or "source-file",
            "retrieved_at": source_metadata.get("retrieved_at"),
            "last_modified": source_metadata.get("last_modified"),
            "etag": source_metadata.get("etag"),
            "content_type": source_metadata.get("content_type"),
            "source_sha256": sha256_file(source_path),
            "source_encoding": statistics["encoding"],
        },
        "dataset": {
            "file": output_db.name,
            "file_sha256": sha256_file(output_db),
            "content_sha256": semantic_hash(output_db),
            "record_count": statistics["record_count"],
            "unique_postal_codes": statistics["unique_postal_codes"],
            "state_count": statistics["state_count"],
            "columns": list(EXPECTED_COLUMNS),
        },
    }


def build_from_source(
    source_path: Path,
    output_dir: Path,
    *,
    source_metadata: dict[str, Any] | None = None,
    min_records: int = MIN_NATIONAL_RECORDS,
) -> tuple[Path, Path, dict[str, Any]]:
    """Build the release artifact from an already materialized SEPOMEX TXT file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_db = output_dir / OUTPUT_NAME
    manifest_path = output_dir / MANIFEST_NAME

    statistics = create_database(source_path, output_db, min_records=min_records)
    manifest = build_manifest(
        source_path, output_db, statistics, source_metadata or {}
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_db, manifest_path, manifest


def build_latest(output_dir: Path) -> tuple[Path, Path, dict[str, Any]]:
    """Download the current official source and build its release artifact."""
    with tempfile.TemporaryDirectory(prefix="catalogmx-sepomex-") as temp_dir:
        source_path = Path(temp_dir) / "CPdescarga.txt"
        metadata = fetch_source(source_path)
        return build_from_source(source_path, output_dir, source_metadata=metadata)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument(
        "--source-file",
        type=Path,
        help="Build from a local CPdescarga.txt instead of downloading upstream",
    )
    args = parser.parse_args(argv)

    if args.source_file:
        output_db, manifest_path, manifest = build_from_source(
            args.source_file, args.output_dir
        )
    else:
        output_db, manifest_path, manifest = build_latest(args.output_dir)

    print(f"database={output_db}")
    print(f"manifest={manifest_path}")
    print(f"records={manifest['dataset']['record_count']}")
    print(f"postal_codes={manifest['dataset']['unique_postal_codes']}")
    print(f"states={manifest['dataset']['state_count']}")
    print(f"content_sha256={manifest['dataset']['content_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
