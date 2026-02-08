#!/usr/bin/env python3
"""Audit catalog SQL usage in webapp routes against the SQLite schema."""

from __future__ import annotations

import argparse
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

QUERY_PATTERN = re.compile(r"query(?:<[^>]+>)?\s*\(\s*`([\s\S]*?)`\s*\)", re.M)
TABLE_PATTERN = re.compile(r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b", re.I)


@dataclass(frozen=True)
class SqlUsage:
    file: Path
    table: str


def print_section(title: str, lines: Iterable[str]) -> None:
    rows = list(lines)
    if not rows:
        return
    print(f"\n{title}")
    for row in rows:
        print(f"  - {row}")


def extract_sql_usage(path: Path) -> list[SqlUsage]:
    source = path.read_text(encoding="utf-8")
    usages: list[SqlUsage] = []
    for sql in QUERY_PATTERN.findall(source):
        for table in TABLE_PATTERN.findall(sql):
            usages.append(SqlUsage(file=path, table=table))
    return usages


def collect_usages(routes_dir: Path) -> list[SqlUsage]:
    usages: list[SqlUsage] = []
    for file_path in sorted(routes_dir.rglob("*")):
        if file_path.suffix not in {".svelte", ".ts"}:
            continue
        usages.extend(extract_sql_usage(file_path))
    return usages


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit catalog queries vs SQLite schema.")
    parser.add_argument(
        "--db",
        default="packages/shared-data/mexico.sqlite3",
        help="SQLite database path (default: packages/shared-data/mexico.sqlite3)",
    )
    parser.add_argument(
        "--catalog-routes",
        default="packages/webapp-svelte/src/routes/catalogos",
        help="Catalog routes path to scan (default: packages/webapp-svelte/src/routes/catalogos)",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    routes_path = Path(args.catalog_routes)

    if not db_path.exists():
        raise SystemExit(f"[audit] sqlite db not found: {db_path}")
    if not routes_path.exists():
        raise SystemExit(f"[audit] routes path not found: {routes_path}")

    usages = collect_usages(routes_path)
    if not usages:
        raise SystemExit("[audit] no SQL queries found in catalog routes")

    conn = sqlite3.connect(db_path)
    existing_tables = {
        row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }

    missing = []
    for usage in usages:
        if usage.table not in existing_tables:
            missing.append(f"{usage.file}: {usage.table}")

    unique_tables = sorted({usage.table for usage in usages})
    print(f"[audit] query occurrences: {len(usages)}")
    print(f"[audit] distinct tables referenced: {len(unique_tables)}")

    print_section("Tables referenced", unique_tables)
    print_section("Missing tables", missing)

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
