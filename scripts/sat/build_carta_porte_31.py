#!/usr/bin/env python3
"""Build a reproducible Carta Porte 3.1 SQLite dataset.

The SAT remains the authoritative source. PhpCfdi's resources-sat-catalogs
release is used as a versioned technical ingestion mirror because it converts
the SAT Excel catalogs into an open SQLite representation with change history.

Only the 32 ``ccp_31_*`` tables are copied into the output database. The
manifest contains both a file hash and a semantic content hash, allowing a
scheduled workflow to avoid publishing a new CatalogMX data release when a
PhpCfdi release changes only unrelated SAT catalogs.
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
AUTHORITATIVE_PORTAL = "https://www.sat.gob.mx/portal/public/tramites/complemento-carta-porte"
AUTHORITATIVE_CATALOG = (
    "http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/"
    "CatalogosCartaPorte31.xls"
)
SOURCE_ASSET_NAME = "catalogs.db.bz2"
DATASET_ID = "sat.carta_porte"
DATASET_VERSION = "3.1"
OUTPUT_NAME = "sat_carta_porte_31.sqlite3"
MANIFEST_NAME = "sat_carta_porte_31.manifest.json"
ARTIFACT_FORMAT = "file"
MOUNT_PATH = "sat/carta_porte_3.1"

EXPECTED_TABLES = (
    "ccp_31_autorizaciones_naviero",
    "ccp_31_claves_unidades",
    "ccp_31_codigos_transporte_aereo",
    "ccp_31_colonias",
    "ccp_31_condiciones_especiales",
    "ccp_31_configuraciones_autotransporte",
    "ccp_31_configuraciones_maritimas",
    "ccp_31_contenedores",
    "ccp_31_contenedores_maritimos",
    "ccp_31_derechos_de_paso",
    "ccp_31_documentos_aduaneros",
    "ccp_31_estaciones",
    "ccp_31_figuras_transporte",
    "ccp_31_formas_farmaceuticas",
    "ccp_31_localidades",
    "ccp_31_materiales_peligrosos",
    "ccp_31_municipios",
    "ccp_31_partes_transporte",
    "ccp_31_productos_servicios",
    "ccp_31_regimenes_aduaneros",
    "ccp_31_registros_istmo",
    "ccp_31_sectores_cofepris",
    "ccp_31_tipos_carga",
    "ccp_31_tipos_carro",
    "ccp_31_tipos_embalaje",
    "ccp_31_tipos_estacion",
    "ccp_31_tipos_materia",
    "ccp_31_tipos_permiso",
    "ccp_31_tipos_remolque",
    "ccp_31_tipos_servicio",
    "ccp_31_tipos_trafico",
    "ccp_31_transportes",
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
    """Fetch metadata for the latest PhpCfdi catalogs release."""
    request = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "catalogmx-carta-porte-builder",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        release = json.load(response)

    asset = next(
        (item for item in release.get("assets", []) if item.get("name") == SOURCE_ASSET_NAME),
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
        url, headers={"User-Agent": "catalogmx-carta-porte-builder"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
        with destination.open("wb") as output:
            shutil.copyfileobj(response, output)


def decompress_bz2(source: Path, destination: Path) -> None:
    """Decompress a bzip2 file without loading it fully into memory."""
    with bz2.open(source, "rb") as compressed, destination.open("wb") as output:
        shutil.copyfileobj(compressed, output)


def discover_tables(connection: sqlite3.Connection) -> tuple[str, ...]:
    """Return and validate the complete Carta Porte 3.1 table set."""
    rows = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name LIKE 'ccp_31_%' ORDER BY name"
    ).fetchall()
    tables = tuple(row[0] for row in rows)
    expected = tuple(sorted(EXPECTED_TABLES))
    if tables != expected:
        missing = sorted(set(expected) - set(tables))
        extra = sorted(set(tables) - set(expected))
        raise RuntimeError(
            "unexpected Carta Porte 3.1 schema; "
            f"missing={missing or 'none'}, extra={extra or 'none'}"
        )
    return tables


def copy_subset(source_db: Path, output_db: Path) -> dict[str, int]:
    """Copy only CCP 3.1 tables and indexes from a SAT catalogs database."""
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
    """Hash schemas and rows in a stable order, independent of SQLite bytes."""
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
            query = f"SELECT * FROM {quoted} ORDER BY {order_by}"
            for row in connection.execute(query):
                encoded = json.dumps(
                    list(row),
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
                digest.update(encoded)
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
            "format": ARTIFACT_FORMAT,
            "mount_path": MOUNT_PATH,
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
    """Build the filtered dataset from an already materialized source DB."""
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
    """Download the latest mirror release and build the filtered dataset."""
    metadata = fetch_latest_release()
    with tempfile.TemporaryDirectory(prefix="catalogmx-carta-porte-") as temp_dir:
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
