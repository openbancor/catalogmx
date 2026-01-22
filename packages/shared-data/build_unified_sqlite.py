#!/usr/bin/env python3
"""Generate mexico.sqlite3 by merging every shared catalog into a single database."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path
from typing import Iterable, Iterator, List, Sequence

DATA_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = DATA_ROOT / "mexico.sqlite3"

SQLITE_SOURCES = [
    {
        "path": DATA_ROOT / "mexico_dynamic.sqlite3",
        "tables": [
            {"source": "udis", "target": "banxico_udis"},
            {"source": "tipo_cambio", "target": "banxico_tipo_cambio", "where": "fuente = 'FIX'"},
            {"source": "tipo_cambio", "target": "banxico_tipo_cambio_hist", "where": "fuente = 'historico'"},
            {"source": "tiie", "target": "banxico_tiie"},
            {"source": "cetes", "target": "banxico_cetes"},
            {"source": "inflacion", "target": "banxico_inflacion"},
            {"source": "salarios_minimos", "target": "banxico_salarios_minimos"},
        ],
    },
    {
        "path": DATA_ROOT / "sqlite" / "geo_mexico.db",
        "tables": [
            {"source": "geo_estados", "target": "geo_estados"},
            {"source": "geo_municipios", "target": "geo_municipios"},
            {"source": "geo_zonas_metropolitanas", "target": "geo_zonas_metropolitanas"},
            {"source": "geo_municipio_zm", "target": "geo_municipio_zm"},
        ],
    },
]

INDEX_DEFINITIONS: dict[str, list[Sequence[str]]] = {
    "codigos_postales": [
        ("idx_codigos_postales_cp", ("cp",)),
        ("idx_codigos_postales_estado", ("estado",)),
        ("idx_codigos_postales_asentamiento", ("asentamiento",)),
    ],
    "localidades": [
        ("idx_localidades_nom_loc", ("nom_loc",)),
        ("idx_localidades_nom_ent", ("nom_ent",)),
        ("idx_localidades_nom_mun", ("nom_mun",)),
    ],
    "clave_prod_serv": [
        ("idx_clave_prod_serv_clave", ("clave",)),
        ("idx_clave_prod_serv_desc", ("descripcion",)),
    ],
    "geo_estados": [
        ("idx_geo_estados_slug", ("nombre_slug",)),
    ],
    "geo_municipios": [
        ("idx_geo_municipios_estado", ("cve_entidad",)),
        ("idx_geo_municipios_slug", ("nombre_slug",)),
        ("idx_geo_municipios_estado_slug", ("estado_slug", "nombre_slug")),
    ],
    "geo_zonas_metropolitanas": [
        ("idx_geo_zm_slug", ("nombre_slug",)),
    ],
    "geo_municipio_zm": [
        ("idx_geo_mzm_zm", ("zm_id",)),
    ],
}

FTS_CONFIG = [
    {
        "name": "codigos_postales_fts",
        "content_table": "codigos_postales",
        "columns": ["cp", "asentamiento", "municipio", "estado"],
    },
    {
        "name": "clave_prod_serv_fts",
        "content_table": "clave_prod_serv",
        "columns": ["clave", "descripcion", "palabras_similares"],
    },
]

EXCLUDED_JSON_DIRS = {"sqlite"}

JSON_TABLE_OVERRIDES = {
    # Use the full catalog as the canonical table; skip the truncated file elsewhere.
    "sepomex/codigos_postales_completo.json": "codigos_postales",
    "inegi/localidades.json": "localidades",
    "sat/cfdi_4.0/clave_prod_serv.json": "clave_prod_serv",
}

# Files that should not be imported (e.g., truncated/demo datasets or migrated to SQLite).
SKIP_JSON_FILES = {
    "sepomex/codigos_postales.json",
    # Banxico data now comes from mexico_dynamic.sqlite3
    "banxico/udis.json",
    "banxico/tipo_cambio_usd.json",
    "banxico/tipo_cambio_hist.json",
    "banxico/tiie_28.json",
    "banxico/cetes_28.json",
    "banxico/inflacion_anual.json",
    "banxico/salarios_minimos.json",
}

# JSON files that should be stored as raw payloads in SQLite for browser usage.
RAW_JSON_FILES = {
    "isr-tables.json",
    "resico-tables.json",
    "imss-tables.json",
    "imss-catalogs.json",
    "sat/impuestos/isr_tablas.json",
    "sat/impuestos/iva_tasas.json",
    "sat/impuestos/ieps_tasas.json",
    "sat/impuestos/retenciones.json",
    "sat/impuestos/impuestos_locales.json",
}


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def rewrite_create_sql(sql: str, old: str, new: str) -> str:
    """Rewrite CREATE TABLE statement to use a new table name."""
    # Match: CREATE TABLE [IF NOT EXISTS] old_name
    # Handles optional quotes/backticks around table name
    pattern = re.compile(
        rf"(CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?)\s+[`\"]?{re.escape(old)}[`\"]?\b",
        re.IGNORECASE,
    )
    return pattern.sub(rf"\1 {quote_ident(new)}", sql, count=1)


def create_database(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path))
    # Use DELETE mode to avoid WAL propagation issues with ATTACH
    pragmas = [
        "PRAGMA journal_mode=DELETE;",
        "PRAGMA synchronous=NORMAL;",
        "PRAGMA foreign_keys=OFF;",
        "PRAGMA temp_store=MEMORY;",
    ]
    for pragma in pragmas:
        conn.execute(pragma)
    return conn


def copy_tables_with_separate_connection(
    dest_conn: sqlite3.Connection, db_path: Path, table_specs: list
) -> None:
    """Copy tables using a separate read-only connection to avoid corruption."""
    # Open source database read-only
    src_conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    src_conn.row_factory = sqlite3.Row

    try:
        for table_spec in table_specs:
            src_table = table_spec["source"]
            dest_table = table_spec.get("target", src_table)
            where_clause = table_spec.get("where", "")

            # Check if table exists
            table_check = src_conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (src_table,),
            ).fetchone()
            if not table_check:
                print(f"[build] WARNING: {db_path.name} does not contain table '{src_table}'. Skipped.")
                continue

            # Get schema
            schema_row = src_conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                (src_table,),
            ).fetchone()
            if not schema_row or not schema_row[0]:
                print(f"[build] WARNING: could not read schema for {src_table} in {db_path}")
                continue

            # Create table in destination
            dest_conn.execute(f"DROP TABLE IF EXISTS {quote_ident(dest_table)}")
            create_sql = rewrite_create_sql(schema_row[0], src_table, dest_table)
            dest_conn.execute(create_sql)

            # Read data from source
            select_query = f"SELECT * FROM {quote_ident(src_table)}"
            if where_clause:
                select_query += f" WHERE {where_clause}"

            rows = src_conn.execute(select_query).fetchall()
            if not rows:
                print(f"[build] WARNING: {src_table} in {db_path.name} has no data.")
                continue

            # Get column names
            col_names = [desc[0] for desc in src_conn.execute(select_query).description]
            placeholders = ",".join(["?"] * len(col_names))
            col_list = ",".join(quote_ident(c) for c in col_names)

            insert_sql = f"INSERT INTO {quote_ident(dest_table)} ({col_list}) VALUES ({placeholders})"
            dest_conn.executemany(insert_sql, [tuple(row) for row in rows])

            filter_msg = f" (filtered: {where_clause})" if where_clause else ""
            print(f"[build] Imported {dest_table} ({len(rows):,} rows) from {db_path.name}{filter_msg}")

        dest_conn.commit()
    finally:
        src_conn.close()


def attach_and_copy_tables(conn: sqlite3.Connection) -> None:
    for idx, source in enumerate(SQLITE_SOURCES):
        db_path: Path = source["path"]
        if not db_path.exists():
            print(f"[build] WARNING: skipped missing {db_path}")
            continue

        # Use separate connection method to avoid corrupting source databases
        copy_tables_with_separate_connection(conn, db_path, source["tables"])


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def iter_json_files() -> Iterator[Path]:
    for path in sorted(DATA_ROOT.rglob("*.json")):
        if path.is_dir():
            continue
        rel_parts = path.relative_to(DATA_ROOT).parts
        if rel_parts and rel_parts[0] in EXCLUDED_JSON_DIRS:
            continue
        rel_str = "/".join(rel_parts)
        if rel_str in SKIP_JSON_FILES:
            continue
        yield path


def table_name_for_json(path: Path) -> str:
    rel = path.relative_to(DATA_ROOT)
    rel_str = "/".join(rel.parts)
    if rel_str in JSON_TABLE_OVERRIDES:
        return JSON_TABLE_OVERRIDES[rel_str]
    parts = []
    for part in rel.parts:
        name = part.lower().replace(" ", "_").replace("-", "_")
        if name.endswith(".json"):
            name = name[: -len(".json")]
        name = name.replace(".", "_")
        parts.append(name.rstrip("_"))
    return "_".join(parts).rstrip("_")


def ensure_list_of_records(data: object) -> List[dict]:
    if isinstance(data, list):
        return [wrap_record(item) for item in data]
    if isinstance(data, dict):
        if "items" in data and isinstance(data["items"], list):
            return [wrap_record(item) for item in data["items"]]
        if "data" in data and isinstance(data["data"], list):
            return [wrap_record(item) for item in data["data"]]
        list_fields = [
            (key, value) for key, value in data.items() if isinstance(value, list) and len(value) > 0
        ]
        if list_fields:
            # Prefer the largest list of records when multiple list fields exist.
            key, records = max(list_fields, key=lambda kv: len(kv[1]))
            print(f"[build] Using list field '{key}' with {len(records)} records")
            return [wrap_record(item) for item in records]
        if all(isinstance(v, dict) for v in data.values()):
            rows = []
            for key, value in data.items():
                base = {"key": key}
                if isinstance(value, dict):
                    base.update(value)
                else:
                    base["value"] = value
                rows.append(base)
            return rows
        return [wrap_record(data)]
    return [wrap_record({"value": data})]


def wrap_record(item: object) -> dict:
    if isinstance(item, dict):
        return dict(item)
    return {"value": item}


def transform_special_case(path: Path, payload: object) -> list[dict] | None:
    # Handle nested structures that hold multiple lists under semantic keys.
    rel = "/".join(path.relative_to(DATA_ROOT).parts)
    if rel == "misc/cacophonic_words.json" and isinstance(payload, dict):
        rows: list[dict] = []
        for scope, scope_data in payload.items():
            if not isinstance(scope_data, dict):
                continue
            for field, value in scope_data.items():
                # field can be list or dict of lists
                if isinstance(value, list):
                    for word in value:
                        rows.append({"scope": scope, "field": field, "value": word})
                elif isinstance(value, dict):
                    for inner_key, inner_list in value.items():
                        if isinstance(inner_list, list):
                            for word in inner_list:
                                rows.append({"scope": scope, "field": f"{field}:{inner_key}", "value": word})
        if rows:
            print(f"[build] Flattened cacophonic words into {len(rows)} rows")
            return rows
    return None


def normalize_clave_prod_serv_schema(conn: sqlite3.Connection) -> None:
    """Align clave_prod_serv schema with legacy snake_case expected by SDKs and tests."""
    table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='clave_prod_serv'"
    ).fetchone()
    if not table_exists:
        return

    cols = {row[1] for row in conn.execute("PRAGMA table_info(clave_prod_serv)").fetchall()}

    # Already normalized
    if {"clave", "descripcion", "incluye_iva", "incluye_ieps"}.issubset(cols):
        return

    expected_source = {
        "id",
        "descripcion",
        "incluirIVATrasladado",
        "incluirIEPSTrasladado",
        "complementoQueDebeIncluir",
        "fechaInicioVigencia",
        "fechaFinVigencia",
        "estimuloFranjaFronteriza",
        "palabrasSimilares",
    }
    if not expected_source.issubset(cols):
        print("[build] WARNING: clave_prod_serv schema unexpected; leaving as-is")
        return

    conn.execute("DROP TABLE IF EXISTS clave_prod_serv_tmp")
    conn.execute(
        """
        CREATE TABLE clave_prod_serv_tmp AS
        SELECT
            id AS clave,
            descripcion,
            CASE
                WHEN lower(incluirIVATrasladado) IN ('si','sí','1','true','yes') THEN 1
                ELSE 0
            END AS incluye_iva,
            CASE
                WHEN lower(incluirIEPSTrasladado) IN ('si','sí','1','true','yes') THEN 1
                ELSE 0
            END AS incluye_ieps,
            complementoQueDebeIncluir AS complemento,
            fechaInicioVigencia AS fecha_inicio_vigencia,
            fechaFinVigencia AS fecha_fin_vigencia,
            estimuloFranjaFronteriza AS estimulo_franja_fronteriza,
            palabrasSimilares AS palabras_similares
        FROM clave_prod_serv
        """
    )
    conn.execute("DROP TABLE clave_prod_serv")
    conn.execute("ALTER TABLE clave_prod_serv_tmp RENAME TO clave_prod_serv")
    conn.commit()
    print("[build] Normalized clave_prod_serv schema to snake_case")


def create_legacy_views(conn: sqlite3.Connection) -> None:
    """Create compatibility views for legacy table/column names."""
    table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='clave_prod_serv'"
    ).fetchone()
    if not table_exists:
        return

    conn.execute("DROP VIEW IF EXISTS c_ClaveProdServ")
    conn.execute(
        """
        CREATE VIEW c_ClaveProdServ AS
        SELECT
            clave AS c_ClaveProdServ,
            descripcion AS Descripcion,
            incluye_iva AS IncluirIVAtrasladado,
            incluye_ieps AS IncluirIEPStrasladado,
            complemento AS ComplementoQueDebeIncluir,
            fecha_inicio_vigencia AS FechaInicioVigencia,
            fecha_fin_vigencia AS FechaFinVigencia,
            estimulo_franja_fronteriza AS EstimuloFranjaFronteriza,
            palabras_similares AS PalabrasSimilares
        FROM clave_prod_serv
        """
    )


def infer_column_types(records: List[dict], columns: Sequence[str]) -> dict[str, str]:
    def infer(values: Iterable[object]) -> str:
        column_type = "TEXT"
        for value in values:
            if value is None:
                continue
            if isinstance(value, bool):
                return "INTEGER"
            if isinstance(value, int):
                if column_type != "REAL":
                    column_type = "INTEGER"
                continue
            if isinstance(value, float):
                column_type = "REAL"
                continue
            return "TEXT"
        return column_type

    result: dict[str, str] = {}
    for column in columns:
        values = (record.get(column) for record in records)
        result[column] = infer(values)
    return result


def normalize_value(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float, str)):
        return value
    return json.dumps(value, ensure_ascii=False)


def import_json_catalogs(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS catalog_json (
            path TEXT PRIMARY KEY,
            payload TEXT NOT NULL
        )
        """
    )
    for json_path in iter_json_files():
        table_name = table_name_for_json(json_path)
        rel_str = "/".join(json_path.relative_to(DATA_ROOT).parts)
        with json_path.open("r", encoding="utf-8") as fh:
            try:
                payload = json.load(fh)
            except json.JSONDecodeError as exc:
                print(f"[build] WARNING: failed to parse {json_path}: {exc}")
                continue

        if rel_str in RAW_JSON_FILES:
            conn.execute(
                "INSERT OR REPLACE INTO catalog_json (path, payload) VALUES (?, ?)",
                (rel_str, json.dumps(payload, ensure_ascii=False)),
            )

        special = transform_special_case(json_path, payload)
        records = special if special is not None else ensure_list_of_records(payload)
        if not records:
            print(f"[build] WARNING: {json_path} has no records, skipped.")
            continue

        columns = sorted({key for record in records for key in record.keys()})
        type_map = infer_column_types(records, columns)

        column_defs = ", ".join(f"{quote_ident(col)} {type_map[col]}" for col in columns)
        conn.execute(f"DROP TABLE IF EXISTS {quote_ident(table_name)}")
        conn.execute(f"CREATE TABLE {quote_ident(table_name)} ({column_defs})")

        placeholders = ",".join("?" for _ in columns)
        rows = [
            [normalize_value(record.get(col)) for col in columns]
            for record in records
        ]
        conn.executemany(
            f"INSERT INTO {quote_ident(table_name)} VALUES ({placeholders})", rows
        )
        conn.commit()
        print(f"[build] Imported {table_name} ({len(rows):,} rows) from {json_path.relative_to(DATA_ROOT)}")

    # Post-process schemas that need legacy compatibility
    normalize_clave_prod_serv_schema(conn)


def create_indexes(conn: sqlite3.Connection) -> None:
    for table, definitions in INDEX_DEFINITIONS.items():
        existing = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        ).fetchone()
        if not existing:
            continue
        for index_name, columns in definitions:
            columns_expr = ", ".join(quote_ident(col) for col in columns)
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS {quote_ident(index_name)} "
                f"ON {quote_ident(table)} ({columns_expr})"
            )


def create_fts_indexes(conn: sqlite3.Connection) -> None:
    for config in FTS_CONFIG:
        base_table = config["content_table"]
        table_exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (base_table,),
        ).fetchone()
        if not table_exists:
            continue

        conn.execute(f"DROP TABLE IF EXISTS {quote_ident(config['name'])}")
        columns_expr = ",\n        ".join(config["columns"])
        conn.execute(
            f"""
            CREATE VIRTUAL TABLE {quote_ident(config['name'])}
            USING fts5(
                {columns_expr},
                content={quote_ident(base_table)}
            );
            """
        )
        insert_columns = ", ".join(config["columns"])
        conn.execute(
            f"""
            INSERT INTO {quote_ident(config['name'])}(rowid, {insert_columns})
            SELECT rowid, {insert_columns} FROM {quote_ident(base_table)};
            """
        )


def finalize_database(conn: sqlite3.Connection) -> None:
    create_indexes(conn)
    create_fts_indexes(conn)
    create_legacy_views(conn)
    conn.commit()
    conn.execute("ANALYZE;")
    
    # Close WAL mode for browser compatibility
    # IMPORTANT: SQLite WASM and sql.js need clean database files
    print("[build] Closing WAL mode for browser compatibility...")
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    conn.execute("PRAGMA journal_mode=DELETE;")
    
    conn.execute("VACUUM;")


def export_individual_sqlite_dbs(conn: sqlite3.Connection) -> None:
    """Export key tables into standalone SQLite files for webapp assets."""
    exports = [
        (
            DATA_ROOT / "sqlite" / "sepomex.db",
            [
                ("codigos_postales", "codigos_postales"),
            ],
        ),
        (
            DATA_ROOT / "sqlite" / "localidades.db",
            [
                ("localidades", "localidades"),
            ],
        ),
        (
            DATA_ROOT / "sqlite" / "clave_prod_serv.db",
            [
                ("clave_prod_serv", "clave_prod_serv"),
            ],
        ),
    ]

    for idx, (dest_path, table_mappings) in enumerate(exports):
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if dest_path.exists():
            dest_path.unlink()

        alias = f"dest_{idx}"
        conn.execute(f"ATTACH DATABASE {quote_literal(str(dest_path))} AS {alias}")
        try:
            for source_table, target_table in table_mappings:
                exists = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                    (source_table,),
                ).fetchone()
                if not exists:
                    print(f"[export] WARNING: source table '{source_table}' missing; skipped for {dest_path.name}")
                    continue

                conn.execute(f"DROP TABLE IF EXISTS {alias}.{quote_ident(target_table)}")
                conn.execute(
                    f"CREATE TABLE {alias}.{quote_ident(target_table)} AS "
                    f"SELECT * FROM main.{quote_ident(source_table)}"
                )
        finally:
            conn.execute(f"DETACH DATABASE {alias}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Destination sqlite file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--skip-json",
        action="store_true",
        help="Skip importing JSON catalogs (only copy existing SQLite sources).",
    )
    parser.add_argument(
        "--skip-sqlite",
        action="store_true",
        help="Skip copying existing SQLite sources (only import JSON catalogs).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path: Path = args.output
    if not output_path.is_absolute():
        output_path = output_path.resolve()

    print(f"[build] Generating {output_path}")
    conn = create_database(output_path)
    try:
        if not args.skip_sqlite:
            attach_and_copy_tables(conn)
        if not args.skip_json:
            import_json_catalogs(conn)
        finalize_database(conn)
        export_individual_sqlite_dbs(conn)
        print(f"[build] mexico.sqlite3 ready at {output_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
