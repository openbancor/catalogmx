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

step "Update Banxico data (optional)"
if [ -n "${BANXICO_TOKEN:-}" ]; then
  pushd "${ROOT_DIR}/packages/shared-data" >/dev/null

  echo "📊 Updating UDI data..."
  python3 scripts/fetch_udis_banxico.py --token "${BANXICO_TOKEN}" || {
    echo "⚠️  Warning: Failed to fetch UDI data from Banxico, continuing..."
  }

  echo "💱 Updating Tipo de Cambio FIX..."
  python3 scripts/fetch_tipo_cambio_banxico.py --token "${BANXICO_TOKEN}" || {
    echo "⚠️  Warning: Failed to fetch Tipo de Cambio FIX from Banxico, continuing..."
  }

  echo "📈 Updating Tipo de Cambio Histórico..."
  python3 scripts/fetch_tipo_cambio_hist_banxico.py --token "${BANXICO_TOKEN}" || {
    echo "⚠️  Warning: Failed to fetch Tipo de Cambio Histórico from Banxico, continuing..."
  }

  echo "💰 Updating TIIE 28 días..."
  python3 scripts/fetch_tiie_banxico.py --token "${BANXICO_TOKEN}" || {
    echo "⚠️  Warning: Failed to fetch TIIE 28d from Banxico, continuing..."
  }

  echo "📊 Updating CETES 28 días..."
  python3 scripts/fetch_cetes_banxico.py --token "${BANXICO_TOKEN}" || {
    echo "⚠️  Warning: Failed to fetch CETES 28d from Banxico, continuing..."
  }

  echo "📈 Updating Inflación Anual..."
  python3 scripts/fetch_inflacion_banxico.py --token "${BANXICO_TOKEN}" || {
    echo "⚠️  Warning: Failed to fetch Inflación from Banxico, continuing..."
  }

  echo "💼 Updating Salarios Mínimos..."
  python3 scripts/fetch_salarios_minimos_banxico.py --token "${BANXICO_TOKEN}" || {
    echo "⚠️  Warning: Failed to fetch Salarios Mínimos from Banxico, continuing..."
  }

  popd >/dev/null
else
  info "BANXICO_TOKEN not set, skipping Banxico data updates"
  info "To enable: export BANXICO_TOKEN='your_token' or get one at https://www.banxico.org.mx/SieAPIRest/service/v1/token"
fi

step "Build SQLite data (mexico.sqlite3 and public/data copies)"
pushd "${ROOT_DIR}/packages/webapp" >/dev/null
npm run data:build
npm run sync:data
popd >/dev/null

step "Copy Banxico JSON data to webapp"
cp "${ROOT_DIR}/packages/shared-data/banxico"/*.json "${ROOT_DIR}/packages/webapp/public/data/banxico/" || {
  echo "⚠️  Warning: Failed to copy some Banxico JSON files, continuing..."
}

step "Sync mexico.sqlite3 to webapp-svelte static assets"
WEBAPP_SVELTE_DATA="${ROOT_DIR}/packages/webapp-svelte/static/data"
if [ -d "$WEBAPP_SVELTE_DATA" ]; then
  cp "${ROOT_DIR}/packages/shared-data/mexico.sqlite3" "${WEBAPP_SVELTE_DATA}/mexico.sqlite3"
else
  echo "⚠️  Warning: webapp-svelte static/data not found, skipping..."
fi

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

step "Python package: format + lint + typecheck + tests"
pushd "${ROOT_DIR}/packages/python" >/dev/null
echo "📝 Formatting with black..."
black catalogmx
echo "🔍 Linting with ruff..."
ruff check --fix catalogmx
echo "📊 Type checking with mypy..."
mypy catalogmx
echo "🧪 Running tests with pytest..."
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
