"""Read canonical SAT catalog tables from DatasetResolver SQLite artifacts.

The helper deliberately contains no catalog-specific projection logic. It only
resolves the independently versioned dataset artifact, opens SQLite read-only,
validates the requested table and ordering columns, and returns rows as
dictionaries. Public catalog modules remain responsible for their historical
API shape.
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
    order_by: str | tuple[str, ...] = "id",
) -> list[dict[str, Any]]:
    """Return one canonical dataset table as dictionaries.

    Resolution may use ``CATALOGMX_SHARED_DATA``, verified cache, or a verified
    release according to the common DatasetResolver policy. Importing this
    module performs no network I/O; resolution happens only when rows are read.

    ``order_by`` defaults to the conventional ``id`` column but may be a tuple
    for canonical tables whose identity is composite. Every identifier is
    validated before SQL construction and every requested ordering column must
    exist in the table.
    """
    quoted_table = _quote_identifier(table)
    order_columns = (order_by,) if isinstance(order_by, str) else order_by
    if not order_columns:
        raise ValueError("order_by must contain at least one SQLite identifier")
    quoted_order = tuple(_quote_identifier(column) for column in order_columns)
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
            row[1]
            for row in connection.execute(f"PRAGMA table_info({quoted_table})")
        }
        missing_order_columns = [
            column for column in order_columns if column not in columns
        ]
        if missing_order_columns:
            missing = ", ".join(missing_order_columns)
            raise RuntimeError(
                f"{dataset_id}: canonical SQLite table {table} has no ordering "
                f"column(s): {missing}"
            )

        order_clause = ", ".join(quoted_order)
        rows = connection.execute(
            f"SELECT * FROM {quoted_table} ORDER BY {order_clause}"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


__all__ = ["read_dataset_table"]
