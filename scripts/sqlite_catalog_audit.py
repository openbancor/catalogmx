#!/usr/bin/env python3
"""Audit webapp dataset configs against SQLite schema."""

from __future__ import annotations

import argparse
import re
import sqlite3
from pathlib import Path
from typing import Iterable


def parse_dataset_configs(source: str) -> list[dict[str, object]]:
    match = re.search(
        r"export const datasetConfigs = \[(.*)\]\s+as DatasetConfig\[];",
        source,
        re.S,
    )
    if not match:
        raise ValueError("datasetConfigs array not found in datasets.ts")

    block = match.group(1)
    items: list[dict[str, object]] = []
    idx = 0

    while True:
        start_match = re.search(r"\n\s*\{\n\s*id: '([^']+)'", block[idx:])
        if not start_match:
            break

        start = idx + start_match.start()
        brace_depth = 0
        end = None

        for i in range(start, len(block)):
            if block[i] == "{":
                brace_depth += 1
            elif block[i] == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    end = i
                    break

        if end is None:
            break

        obj = block[start : end + 1]
        idx = end + 1

        id_match = re.search(r"id: '([^']+)'", obj)
        table_match = re.search(r"table: '([^']+)'", obj)
        if not id_match or not table_match:
            continue

        columns_block = re.search(r"columns:\s*\[(.*?)\],", obj, re.S)
        search_block = re.search(r"searchColumns:\s*\[(.*?)\],", obj, re.S)

        columns = re.findall(r"key: '([^']+)'", columns_block.group(1)) if columns_block else []
        search_columns = re.findall(r"'([^']+)'", search_block.group(1)) if search_block else []

        items.append(
            {
                "id": id_match.group(1),
                "table": table_match.group(1),
                "columns": columns,
                "search_columns": search_columns,
            }
        )

    return items


def fetch_table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    cur = conn.execute(f'PRAGMA table_info("{table}")')
    return {row[1] for row in cur.fetchall()}


def print_section(title: str, lines: Iterable[str]) -> None:
    lines = list(lines)
    if not lines:
        return
    print(f"\n{title}")
    for line in lines:
        print(f"  - {line}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit dataset configs vs SQLite schema.")
    parser.add_argument(
        "--db",
        default="packages/shared-data/mexico.sqlite3",
        help="SQLite database path (default: packages/shared-data/mexico.sqlite3)",
    )
    parser.add_argument(
        "--datasets",
        default="packages/webapp/src/data/datasets.ts",
        help="Datasets config path (default: packages/webapp/src/data/datasets.ts)",
    )
    args = parser.parse_args()

    dataset_path = Path(args.datasets)
    db_path = Path(args.db)

    if not dataset_path.exists():
        raise SystemExit(f"[audit] datasets file not found: {dataset_path}")
    if not db_path.exists():
        raise SystemExit(f"[audit] sqlite db not found: {db_path}")

    items = parse_dataset_configs(dataset_path.read_text(encoding="utf-8"))
    if not items:
        raise SystemExit("[audit] no datasets parsed from datasets.ts")

    conn = sqlite3.connect(db_path)
    existing_tables = {
        row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }

    missing_tables = []
    missing_columns = []
    missing_search = []

    for item in items:
        table = str(item["table"])
        if table not in existing_tables:
            missing_tables.append(f"{item['id']} -> {table}")
            continue

        table_columns = fetch_table_columns(conn, table)
        columns = [col for col in item["columns"] if col not in table_columns]
        search_columns = [col for col in item["search_columns"] if col not in table_columns]

        if columns:
            missing_columns.append(f"{item['id']} ({table}): {', '.join(columns)}")
        if search_columns:
            missing_search.append(f"{item['id']} ({table}): {', '.join(search_columns)}")

    print(f"[audit] datasets: {len(items)}")
    print_section("Missing tables", missing_tables)
    print_section("Missing column keys", missing_columns)
    print_section("Missing search columns", missing_search)

    if missing_tables or missing_columns or missing_search:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
