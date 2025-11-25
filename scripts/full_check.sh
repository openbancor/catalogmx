#!/usr/bin/env bash
set -euo pipefail

# Run all main quality gates: data build, webapp build, TS lint/typecheck, Python lint/tests, Dart checks.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

step() {
  echo
  echo "==> $*"
}

info() {
  echo "ℹ️  $*"
}

step "Update UDI data from Banxico (optional)"
if [ -n "${BANXICO_TOKEN:-}" ]; then
  pushd "${ROOT_DIR}/packages/shared-data" >/dev/null
  python3 scripts/fetch_udis_banxico.py --token "${BANXICO_TOKEN}" || {
    echo "⚠️  Warning: Failed to fetch UDI data from Banxico, continuing with existing data..."
  }
  popd >/dev/null
else
  info "BANXICO_TOKEN not set, skipping UDI update"
  info "To enable: export BANXICO_TOKEN='your_token' or get one at https://www.banxico.org.mx/SieAPIRest/service/v1/token"
fi

step "Build SQLite data (mexico.sqlite3 and public/data copies)"
pushd "${ROOT_DIR}/packages/webapp" >/dev/null
npm run data:build
npm run sync:data
popd >/dev/null

step "Close WAL mode for browser compatibility (SQLite WASM / sql.js)"
MEXICO_DB="${ROOT_DIR}/packages/shared-data/mexico.sqlite3"
if [ -f "$MEXICO_DB" ]; then
  if command -v sqlite3 &> /dev/null; then
    echo "Closing WAL and removing journal files..."
    sqlite3 "$MEXICO_DB" "PRAGMA wal_checkpoint(TRUNCATE); PRAGMA journal_mode=DELETE; VACUUM;"
    rm -f "${MEXICO_DB}-shm" "${MEXICO_DB}-wal"
    echo "✓ Database cleaned for browser use"
  else
    echo "⚠️  WARNING: sqlite3 CLI not found. Install: brew install sqlite"
  fi
fi

# Also clean webapp public/data
WEBAPP_DB="${ROOT_DIR}/packages/webapp/public/data/mexico.sqlite3"
if [ -f "$WEBAPP_DB" ]; then
  if command -v sqlite3 &> /dev/null; then
    sqlite3 "$WEBAPP_DB" "PRAGMA wal_checkpoint(TRUNCATE); PRAGMA journal_mode=DELETE; VACUUM;"
    rm -f "${WEBAPP_DB}-shm" "${WEBAPP_DB}-wal"
  fi
fi

step "Build webapp (TypeScript + Vite)"
pushd "${ROOT_DIR}/packages/webapp" >/dev/null
npm run build
popd >/dev/null

step "TypeScript package: lint + typecheck + tests"
pushd "${ROOT_DIR}/packages/typescript" >/dev/null
npm run lint:fix
npm run format
npm run typecheck
npm test
popd >/dev/null

step "Python package: format check + lint + typecheck + tests"
pushd "${ROOT_DIR}/packages/python" >/dev/null
black catalogmx
ruff check --fix catalogmx
mypy catalogmx
pytest tests/ --cov=catalogmx --cov-branch
popd >/dev/null

step "Dart package: analyze + format check + tests"
pushd "${ROOT_DIR}/packages/dart" >/dev/null
dart format .
dart analyze
dart test
popd >/dev/null

echo
echo "All checks completed."
