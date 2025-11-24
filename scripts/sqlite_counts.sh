#!/usr/bin/env bash
set -euo pipefail

# Print row counts for every table in a SQLite file (excluding sqlite_internal/FTS internals).
# Usage: scripts/sqlite_counts.sh path/to/db.sqlite3

DB_PATH="${1:-packages/webapp/public/data/mexico.sqlite3}"

if [[ ! -f "$DB_PATH" ]]; then
  echo "[counts] File not found: $DB_PATH" >&2
  exit 1
fi

tables=$(sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts%' ORDER BY name;")
printf "%-50s %12s\n" "table" "rows"
printf "%-50s %12s\n" "-----" "----"
while IFS= read -r table; do
  count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM \"$table\";")
  printf "%-50s %12s\n" "$table" "$count"
done <<< "$tables"
