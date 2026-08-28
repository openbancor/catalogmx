#!/usr/bin/env python3
"""Validate and describe the Banxico dynamic SQLite release artifact.

The daily updater mutates ``mexico_dynamic.sqlite3`` from Banco de México and
other explicitly documented official sources. This script is the publication
gate: it validates the SQLite shape and plausible record coverage, computes a
binary SHA-256 and a semantic SHA-256 that ignores volatile ``updated_at``
columns, and emits the dataset manifest consumed by ``DatasetResolver``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping, Sequence

DATASET_ID = "banxico.sie_dynamic"
DATASET_VERSION = "1"
OUTPUT_NAME = "mexico_dynamic.sqlite3"
MANIFEST_NAME = "mexico_dynamic.manifest.json"
MOUNT_PATH = "dynamic"

TABLE_COLUMNS: dict[str, tuple[str, ...]] = {
    "udis": ("fecha", "valor", "anio", "mes", "tipo", "moneda", "notas"),
    "tipo_cambio": (
        "fecha",
        "fuente",
        "tipo_cambio",
        "anio",
        "mes",
        "moneda_origen",
        "moneda_destino",
    ),
    "tiie": ("fecha", "plazo", "tasa", "anio", "mes"),
    "cetes": ("fecha", "plazo", "tasa", "anio", "mes"),
    "inflacion": (
        "fecha",
        "anio",
        "mes",
        "inpc",
        "inflacion_mensual",
        "inflacion_anual",
    ),
    "salarios_minimos": ("fecha", "zona", "salario_diario", "anio", "mes"),
}

# These are intentionally conservative publication guards, not expected exact
# counts. A truncated/empty database must never replace the live release.
MINIMUM_COUNTS: dict[str, int] = {
    "udis": 10_000,
    "tipo_cambio": 20_000,
    "tiie": 5_000,
    "cetes": 3_000,
    "inflacion": 100,
    "salarios_minimos": 100,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def semantic_hash(connection: sqlite3.Connection) -> str:
    """Hash source values in stable order while ignoring volatile timestamps."""
    digest = hashlib.sha256()
    for table in sorted(TABLE_COLUMNS):
        columns = TABLE_COLUMNS[table]
        quoted_table = quote_identifier(table)
        quoted_columns = ", ".join(quote_identifier(column) for column in columns)
        order_by = ", ".join(quote_identifier(column) for column in columns)
        digest.update(table.encode("utf-8"))
        digest.update(b"\0")
        for row in connection.execute(
            f"SELECT {quoted_columns} FROM {quoted_table} ORDER BY {order_by}"
        ):
            digest.update(
                json.dumps(list(row), ensure_ascii=False, separators=(",", ":")).encode(
                    "utf-8"
                )
            )
            digest.update(b"\n")
    return digest.hexdigest()


def validate_database(
    path: Path,
    minimum_counts: Mapping[str, int] = MINIMUM_COUNTS,
) -> dict[str, Any]:
    """Fail closed on corrupt, incomplete, or structurally incompatible data."""
    if not path.is_file():
        raise RuntimeError(f"dynamic SQLite artifact does not exist: {path}")

    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        quick_check = connection.execute("PRAGMA quick_check").fetchone()
        if quick_check != ("ok",):
            raise RuntimeError(f"dynamic SQLite integrity check failed: {quick_check!r}")

        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        expected = set(TABLE_COLUMNS) | {"_metadata"}
        missing = sorted(expected - tables)
        if missing:
            raise RuntimeError("dynamic SQLite is missing tables: " + ", ".join(missing))

        metadata = dict(connection.execute("SELECT key, value FROM _metadata").fetchall())
        data_version = metadata.get("version")
        if not isinstance(data_version, str) or not data_version:
            raise RuntimeError("dynamic SQLite metadata is missing version")
        if metadata.get("source") != "banxico":
            raise RuntimeError("dynamic SQLite metadata source is not banxico")

        counts: dict[str, int] = {}
        latest_dates: dict[str, str | None] = {}
        for table in sorted(TABLE_COLUMNS):
            quoted = quote_identifier(table)
            count = int(connection.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0])
            minimum = minimum_counts.get(table, 0)
            if count < minimum:
                raise RuntimeError(
                    f"dynamic SQLite table {table} looks incomplete: "
                    f"expected at least {minimum}, got {count}"
                )
            counts[table] = count
            latest_dates[table] = connection.execute(
                f"SELECT MAX(fecha) FROM {quoted}"
            ).fetchone()[0]

        return {
            "data_version": data_version,
            "schema_version": metadata.get("schema_version"),
            "counts": counts,
            "latest_dates": latest_dates,
            "content_sha256": semantic_hash(connection),
        }
    finally:
        connection.close()


def build_manifest(
    path: Path,
    minimum_counts: Mapping[str, int] = MINIMUM_COUNTS,
) -> dict[str, Any]:
    """Build a resolver manifest after applying the selected coverage guards."""
    validation = validate_database(path, minimum_counts=minimum_counts)
    return {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "data_version": validation["data_version"],
        "authority": {
            "name": "BANXICO",
            "api": "https://www.banxico.org.mx/SieAPIRest/service/v1/",
        },
        "dataset": {
            "file": path.name,
            "format": "file",
            "mount_path": MOUNT_PATH,
            "file_sha256": sha256_file(path),
            "content_sha256": validation["content_sha256"],
            "bytes": path.stat().st_size,
            "table_count": len(TABLE_COLUMNS),
            "row_count": sum(validation["counts"].values()),
            "tables": [
                {
                    "name": table,
                    "rows": validation["counts"][table],
                    "latest_date": validation["latest_dates"][table],
                }
                for table in sorted(TABLE_COLUMNS)
            ],
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, nargs="?", default=Path(OUTPUT_NAME))
    parser.add_argument("--output", type=Path, default=Path(MANIFEST_NAME))
    args = parser.parse_args(argv)

    manifest = build_manifest(args.database)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Validated {args.database}: data={manifest['data_version']} "
        f"content={manifest['dataset']['content_sha256']}"
    )
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
