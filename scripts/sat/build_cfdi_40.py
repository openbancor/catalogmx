#!/usr/bin/env python3
"""Build a reproducible SAT CFDI 4.0 SQLite dataset.

The SAT Anexo 20 remains authoritative. PhpCfdi's versioned
``resources-sat-catalogs`` SQLite release is used as a technical ingestion
mirror. Only the exact CFDI 4.0 table family is copied to the output artifact.

The builder fails closed when that table family changes and emits both a file
SHA-256 and a semantic content SHA-256. The generic catalog-maintenance
workflow can therefore publish a new data release only when CFDI 4.0 content
actually changes, independently from CatalogMX language-package releases.
"""

from __future__ import annotations

import argparse
import bz2
import hashlib
import json
import shutil
import sqlite3
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Sequence

LATEST_RELEASE_API = (
    "https://api.github.com/repos/phpcfdi/resources-sat-catalogs/releases/latest"
)
TECHNICAL_MIRROR = "https://github.com/phpcfdi/resources-sat-catalogs"
AUTHORITATIVE_PORTAL = (
    "https://www.sat.gob.mx/consultas/35025/formato-de-factura-electronica-(anexo-20)"
)
AUTHORITATIVE_CATALOG = (
    "http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/catCFDI.xls"
)
SOURCE_ASSET_NAME = "catalogs.db.bz2"
DATASET_ID = "sat.cfdi_4"
DATASET_VERSION = "4.0"
OUTPUT_NAME = "sat_cfdi_40.sqlite3"
MANIFEST_NAME = "sat_cfdi_40.manifest.json"

EXPECTED_TABLES = (
    "cfdi_40_aduanas",
    "cfdi_40_claves_unidades",
    "cfdi_40_codigos_postales",
    "cfdi_40_colonias",
    "cfdi_40_estados",
    "cfdi_40_exportaciones",
    "cfdi_40_formas_pago",
    "cfdi_40_impuestos",
    "cfdi_40_localidades",
    "cfdi_40_meses",
    "cfdi_40_metodos_pago",
    "cfdi_40_monedas",
    "cfdi_40_municipios",
    "cfdi_40_numeros_pedimento_aduana",
    "cfdi_40_objetos_impuestos",
    "cfdi_40_paises",
    "cfdi_40_patentes_aduanales",
    "cfdi_40_periodicidades",
    "cfdi_40_productos_servicios",
    "cfdi_40_regimenes_fiscales",
    "cfdi_40_reglas_tasa_cuota",
    "cfdi_40_tipos_comprobantes",
    "cfdi_40_tipos_factores",
    "cfdi_40_tipos_relaciones",
    "cfdi_40_usos_cfdi",
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


def fetch_latest_release() -> dict[str, Any]:
    """Fetch metadata for the latest technical-mirror release."""
    request = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "catalogmx-cfdi-40-builder",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        release = json.load(response)

    asset = next(
        (
            item
            for item in release.get("assets", [])
            if item.get("name") == SOURCE_ASSET_NAME
        ),
        None,
    )
    if asset is None:
        raise RuntimeError(f"latest technical mirror release has no {SOURCE_ASSET_NAME}")

    digest = asset.get("digest") or ""
    if digest and not digest.startswith("sha256:"):
        raise RuntimeError(f"unsupported source digest: {digest}")

    return {
        "tag": release["tag_name"],
        "published_at": release.get("published_at"),
        "asset_url": asset["browser_download_url"],
        "asset_sha256": digest.removeprefix("sha256:") or None,
        "asset_size": asset.get("size"),
    }


def download(url: str, destination: Path) -> None:
    """Download an HTTPS resource to a local file."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "catalogmx-cfdi-40-builder"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
        with destination.open("wb") as output:
            shutil.copyfileobj(response, output)


def decompress_bz2(source: Path, destination: Path) -> None:
    """Decompress a bzip2 source without loading it fully into memory."""
    with bz2.open(source, "rb") as compressed, destination.open("wb") as output:
        shutil.copyfileobj(compressed, output)


def discover_tables(connection: sqlite3.Connection) -> tuple[str, ...]:
    """Return and validate the complete CFDI 4.0 table set."""
    rows = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name LIKE 'cfdi_40_%' ORDER BY name"
    ).fetchall()
    tables = tuple(row[0] for row in rows)
    expected = tuple(sorted(EXPECTED_TABLES))
    if tables != expected:
        missing = sorted(set(expected) - set(tables))
        extra = sorted(set(tables) - set(expected))
        raise RuntimeError(
            "unexpected CFDI 4.0 schema; "
            f"missing={missing or 'none'}, extra={extra or 'none'}"
        )
    return tables


def copy_subset(source_db: Path, output_db: Path) -> dict[str, int]:
    """Copy only CFDI 4.0 tables and indexes from the mirror database."""
    output_db.parent.mkdir(parents=True, exist_ok=True)
    output_db.unlink(missing_ok=True)

    source = sqlite3.connect(f"file:{source_db}?mode=ro", uri=True)
    target = sqlite3.connect(output_db)
    try:
        tables = discover_tables(source)
        target.execute("PRAGMA journal_mode=DELETE")
        target.execute("PRAGMA foreign_keys=OFF")
        target.execute("ATTACH DATABASE ? AS upstream", (str(source_db),))

        counts: dict[str, int] = {}
        for table in tables:
            schema_row = source.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()
            if schema_row is None or not schema_row[0]:
                raise RuntimeError(f"missing CREATE TABLE statement for {table}")

            target.execute(schema_row[0])
            quoted = quote_identifier(table)
            target.execute(f"INSERT INTO {quoted} SELECT * FROM upstream.{quoted}")
            counts[table] = source.execute(
                f"SELECT COUNT(*) FROM {quoted}"
            ).fetchone()[0]

            indexes = source.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type='index' AND tbl_name=? AND sql IS NOT NULL ORDER BY name",
                (table,),
            ).fetchall()
            for (index_sql,) in indexes:
                target.execute(index_sql)

        target.commit()
        target.execute("DETACH DATABASE upstream")
        target.execute("VACUUM")
        target.commit()
        return counts
    finally:
        source.close()
        target.close()


def semantic_hash(database: Path, tables: Iterable[str]) -> str:
    """Hash table schemas and rows in stable order, independent of SQLite bytes."""
    digest = hashlib.sha256()
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        for table in sorted(tables):
            quoted = quote_identifier(table)
            schema = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()[0]
            digest.update(table.encode("utf-8"))
            digest.update(b"\0")
            digest.update(schema.encode("utf-8"))
            digest.update(b"\0")

            columns = [
                row[1] for row in connection.execute(f"PRAGMA table_info({quoted})")
            ]
            order_by = ", ".join(quote_identifier(column) for column in columns)
            for row in connection.execute(
                f"SELECT * FROM {quoted} ORDER BY {order_by}"
            ):
                digest.update(
                    json.dumps(
                        list(row), ensure_ascii=False, separators=(",", ":")
                    ).encode("utf-8")
                )
                digest.update(b"\n")
    finally:
        connection.close()
    return digest.hexdigest()


def build_manifest(
    output_db: Path,
    counts: dict[str, int],
    source_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Create deterministic provenance and integrity metadata."""
    return {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "authority": {
            "name": "SAT",
            "portal": AUTHORITATIVE_PORTAL,
            "catalog": AUTHORITATIVE_CATALOG,
        },
        "ingestion": {
            "technical_mirror": TECHNICAL_MIRROR,
            "release": source_metadata.get("tag"),
            "published_at": source_metadata.get("published_at"),
            "asset": SOURCE_ASSET_NAME,
            "asset_sha256": source_metadata.get("asset_sha256"),
            "asset_size": source_metadata.get("asset_size"),
        },
        "dataset": {
            "file": output_db.name,
            "file_sha256": sha256_file(output_db),
            "content_sha256": semantic_hash(output_db, counts),
            "table_count": len(counts),
            "row_count": sum(counts.values()),
            "tables": [
                {"name": name, "rows": counts[name]} for name in sorted(counts)
            ],
        },
    }


def build_from_source(
    source_db: Path,
    output_dir: Path,
    source_metadata: dict[str, Any] | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    """Build the filtered dataset from an already materialized mirror DB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_db = output_dir / OUTPUT_NAME
    manifest_path = output_dir / MANIFEST_NAME
    counts = copy_subset(source_db, output_db)
    manifest = build_manifest(output_db, counts, source_metadata or {})
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_db, manifest_path, manifest


def build_latest(output_dir: Path) -> tuple[Path, Path, dict[str, Any]]:
    """Download the latest mirror release and build the CFDI 4.0 dataset."""
    metadata = fetch_latest_release()
    with tempfile.TemporaryDirectory(prefix="catalogmx-cfdi-40-") as temp_dir:
        temp = Path(temp_dir)
        compressed = temp / SOURCE_ASSET_NAME
        source_db = temp / "catalogs.db"
        download(metadata["asset_url"], compressed)

        actual_source_sha = sha256_file(compressed)
        expected_source_sha = metadata.get("asset_sha256")
        if expected_source_sha and actual_source_sha != expected_source_sha:
            raise RuntimeError(
                "technical mirror asset checksum mismatch: "
                f"expected {expected_source_sha}, got {actual_source_sha}"
            )
        metadata["asset_sha256"] = actual_source_sha

        decompress_bz2(compressed, source_db)
        return build_from_source(source_db, output_dir, metadata)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument(
        "--source-db",
        type=Path,
        help="Build from a local catalogs.db instead of downloading the latest release",
    )
    parser.add_argument("--source-tag", help="Optional source tag for local builds")
    args = parser.parse_args(argv)

    if args.source_db:
        output_db, manifest_path, manifest = build_from_source(
            args.source_db,
            args.output_dir,
            {"tag": args.source_tag or "local"},
        )
    else:
        output_db, manifest_path, manifest = build_latest(args.output_dir)

    print(f"database={output_db}")
    print(f"manifest={manifest_path}")
    print(f"tables={manifest['dataset']['table_count']}")
    print(f"rows={manifest['dataset']['row_count']}")
    print(f"content_sha256={manifest['dataset']['content_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
