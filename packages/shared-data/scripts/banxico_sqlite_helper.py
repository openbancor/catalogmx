"""
Helper functions for Banxico fetch scripts to write directly to SQLite database.

Fetcher process exit contract:
- 0: success, including an already-current local dataset
- 1: source/configuration/parse/write failure
- 3: the requested official-source window was valid but contained no observations

Exit code 3 is deliberately nonzero so callers can distinguish a publication
calendar gap from an ordinary successful update without parsing human logs.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_OBSERVATION = 3

# Default database path
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = SCRIPT_DIR.parent
DB_FILE = DATA_ROOT / "mexico_dynamic.sqlite3"


def ensure_database_exists(db_path: Path = DB_FILE):
    """
    Ensure the database and tables exist

    Creates the database with full schema if it doesn't exist
    """
    if not db_path.exists():
        print(f"[db] Creating new database at {db_path}")
        # Create database with schema
        schema_path = DATA_ROOT / "schema_dynamic.sql"
        if schema_path.exists():
            db = sqlite3.connect(db_path)
            with open(schema_path, "r", encoding="utf-8") as f:
                db.executescript(f.read())
            db.close()
            print("[db] ✓ Database created with schema")
        else:
            raise FileNotFoundError(f"Schema file not found: {schema_path}")


def get_last_date(
    db_path: Path,
    table: str,
    date_column: str = "fecha",
    where_clause: str = "",
) -> str | None:
    """
    Get the last date from a table

    Args:
        db_path: Path to SQLite database
        table: Table name
        date_column: Name of date column (default: 'fecha')
        where_clause: Optional WHERE clause (e.g., "plazo = 28")

    Returns:
        Last date as YYYY-MM-DD string, or None if no data
    """
    if not db_path.exists():
        return None

    try:
        db = sqlite3.connect(db_path)
        query = f"SELECT MAX({date_column}) FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"

        cursor = db.execute(query)
        row = cursor.fetchone()
        db.close()

        return row[0] if row and row[0] else None
    except Exception as e:
        print(f"[db] Warning: Could not read from database: {e}")
        return None


def save_to_db(
    db_path: Path,
    table: str,
    records: list[dict[str, Any]],
    conflict_columns: list[str] | None = None,
) -> int:
    """
    Save records to SQLite database using INSERT OR REPLACE

    Args:
        db_path: Path to SQLite database
        table: Table name
        records: List of dictionaries with column names as keys
        conflict_columns: Columns that define uniqueness (for conflict resolution)
                         If None, uses all columns from first record

    Returns:
        Number of records inserted/updated
    """
    if not records:
        return 0

    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    # Get column names from first record
    columns = list(records[0].keys())

    # Build INSERT OR REPLACE query
    placeholders = ", ".join(["?" for _ in columns])
    query = f"""
        INSERT OR REPLACE INTO {table} ({', '.join(columns)})
        VALUES ({placeholders})
    """

    inserted = 0
    for record in records:
        values = [record.get(col) for col in columns]
        cursor.execute(query, values)
        inserted += 1

    db.commit()
    db.close()

    return inserted


def get_table_stats(db_path: Path, table: str) -> dict[str, Any]:
    """
    Get statistics about a table

    Returns:
        Dictionary with count, min_date, max_date
    """
    if not db_path.exists():
        return {"count": 0, "min_date": None, "max_date": None}

    try:
        db = sqlite3.connect(db_path)
        cursor = db.execute(f"SELECT COUNT(*), MIN(fecha), MAX(fecha) FROM {table}")
        count, min_date, max_date = cursor.fetchone()
        db.close()

        return {"count": count or 0, "min_date": min_date, "max_date": max_date}
    except Exception as e:
        print(f"[db] Warning: Could not get table stats: {e}")
        return {"count": 0, "min_date": None, "max_date": None}


def update_metadata_version(db_path: Path):
    """Update the legacy compatibility version metadata to today's date."""
    if not db_path.exists():
        return

    try:
        db = sqlite3.connect(db_path)
        today = datetime.now().strftime("%Y-%m-%d")
        db.execute(
            """
            INSERT OR REPLACE INTO _metadata (key, value)
            VALUES ('version', ?)
            """,
            (today,),
        )
        db.commit()
        db.close()
        print(f"[db] Updated metadata version to {today}")
    except Exception as e:
        print(f"[db] Warning: Could not update metadata: {e}")