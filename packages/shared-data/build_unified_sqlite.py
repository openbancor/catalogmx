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
        "columns": ["id", "descripcion", "palabrasSimilares"],
    },
]

EXCLUDED_JSON_DIRS = {"sqlite"}

JSON_TABLE_OVERRIDES = {
    "sepomex/codigos_postales.json": "codigos_postales",
    "sepomex/codigos_postales_completo.json": "codigos_postales_completo",
    "inegi/localidades.json": "localidades",
    "sat/cfdi_4.0/clave_prod_serv.json": "clave_prod_serv",
}


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def rewrite_create_sql(sql: str, old: str, new: str) -> str:
    pattern = re.compile(
        rf"(CREATE TABLE(?: IF NOT EXISTS)?)\s+([`\"[]?){re.escape(old)}([`\"\\]]?)",
        re.IGNORECASE,
    )
    return pattern.sub(rf"\1 {quote_ident(new)}", sql, count=1)


def create_database(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path))
    pragmas = [
        "PRAGMA journal_mode=WAL;",
        "PRAGMA synchronous=OFF;",
        "PRAGMA foreign_keys=OFF;",
        "PRAGMA temp_store=MEMORY;",
    ]
    for pragma in pragmas:
        conn.execute(pragma)
    return conn


def attach_and_copy_tables(conn: sqlite3.Connection) -> None:
    for idx, source in enumerate(SQLITE_SOURCES):
        db_path: Path = source["path"]
        if not db_path.exists():
            print(f"[build] WARNING: skipped missing {db_path}")
            continue

        attach_name = f"src_{idx}"
        conn.execute(f"ATTACH DATABASE {quote_literal(str(db_path))} AS {attach_name}")
        for table_spec in source["tables"]:
            src_table = table_spec["source"]
            dest_table = table_spec.get("target", src_table)

            table_present = conn.execute(
                f"SELECT 1 FROM {attach_name}.sqlite_master WHERE type='table' AND name=?",
                (src_table,),
            ).fetchone()
            if not table_present:
                print(f"[build] WARNING: {db_path.name} does not contain table '{src_table}'. Skipped.")
                continue

            schema_row = conn.execute(
                f"SELECT sql FROM {attach_name}.sqlite_master "
                "WHERE type='table' AND name=?",
                (src_table,),
            ).fetchone()
            if not schema_row or not schema_row[0]:
                print(f"[build] WARNING: could not read schema for {src_table} in {db_path}")
                continue

            conn.execute(f"DROP TABLE IF EXISTS {quote_ident(dest_table)}")
            create_sql = rewrite_create_sql(schema_row[0], src_table, dest_table)
            conn.execute(create_sql)
            try:
                conn.execute(
                    f"INSERT INTO {quote_ident(dest_table)} "
                    f"SELECT * FROM {attach_name}.{quote_ident(src_table)}"
                )
            except sqlite3.Error as exc:
                print(f"[build] WARNING: failed to copy {src_table} from {db_path.name}: {exc}")
                conn.execute(f"DROP TABLE IF EXISTS {quote_ident(dest_table)}")
                continue

            count = conn.execute(
                f"SELECT COUNT(*) FROM {quote_ident(dest_table)}"
            ).fetchone()[0]
            print(f"[build] Imported {dest_table} ({count:,} rows) from {db_path.name}")

        conn.execute(f"DETACH DATABASE {attach_name}")


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def iter_json_files() -> Iterator[Path]:
    for path in sorted(DATA_ROOT.rglob("*.json")):
        if path.is_dir():
            continue
        rel_parts = path.relative_to(DATA_ROOT).parts
        if rel_parts and rel_parts[0] in EXCLUDED_JSON_DIRS:
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
    for json_path in iter_json_files():
        table_name = table_name_for_json(json_path)
        with json_path.open("r", encoding="utf-8") as fh:
            try:
                payload = json.load(fh)
            except json.JSONDecodeError as exc:
                print(f"[build] WARNING: failed to parse {json_path}: {exc}")
                continue

        records = ensure_list_of_records(payload)
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
    conn.commit()
    conn.execute("ANALYZE;")
    conn.execute("VACUUM;")


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
        print(f"[build] mexico.sqlite3 ready at {output_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
