"""Read canonical SAT catalog tables from DatasetResolver SQLite artifacts.

The helper deliberately contains no catalog-specific projection logic.  It only
resolves the independently versioned dataset artifact, opens SQLite read-only,
validates the requested table, and returns rows as dictionaries.  Public
catalog modules remain responsible for their historical API shape.
"""

from __future__ import annotations

import re
import sqlite3
from typing import Any

from catalogmx.data.resolver import get_dataset_path

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _quote_identifier(value: str) -> str:
    if _IDENTIFIER_RE.fullmatch(value) is None:
        raise ValueError(f"unsafe SQLite identifier: {value!r}")
    return f'"{value}"'


def read_dataset_table(
    dataset_id: str,
    database_name: str,
    table: str,
    *,
    order_by: str = "id",
) -> list[dict[str, Any]]:
    """Return one canonical dataset table as dictionaries.

    Resolution may use ``CATALOGMX_SHARED_DATA``, verified cache, or a verified
    release according to the common DatasetResolver policy. Importing this
    module performs no network I/O; resolution happens only when rows are read.
    """
    quoted_table = _quote_identifier(table)
    quoted_order = _quote_identifier(order_by)
    database = get_dataset_path(dataset_id, database_name)

    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if exists is None:
            raise RuntimeError(f"{dataset_id}: canonical SQLite table is missing: {table}")

        columns = {
            row[1] for row in connection.execute(f"PRAGMA table_info({quoted_table})")
        }
        if order_by not in columns:
            raise RuntimeError(
                f"{dataset_id}: canonical SQLite table {table} has no {order_by} column"
            )

        rows = connection.execute(
            f"SELECT * FROM {quoted_table} ORDER BY {quoted_order}"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


__all__ = ["read_dataset_table"]
