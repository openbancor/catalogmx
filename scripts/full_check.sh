#!/usr/bin/env bash
set -euo pipefail

# Run main quality gates across shared-data, webapp-svelte, TypeScript, Python and Dart.

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
  for script in \
    fetch_udis_banxico.py \
    fetch_tipo_cambio_banxico.py \
    fetch_tipo_cambio_hist_banxico.py \
    fetch_tiie_banxico.py \
    fetch_cetes_banxico.py \
    fetch_inflacion_banxico.py \
    fetch_salarios_minimos_banxico.py; do
    echo "📊 Running ${script}..."
    python "scripts/${script}" || echo "⚠️  Warning: ${script} failed, continuing..."
  done
  popd >/dev/null
else
  info "BANXICO_TOKEN not set, skipping Banxico API updates"
fi

step "Build unified SQLite database"
pushd "${ROOT_DIR}/packages/shared-data" >/dev/null
python build_unified_sqlite.py --output mexico.sqlite3
if command -v sqlite3 >/dev/null 2>&1; then
  sqlite3 mexico.sqlite3 "PRAGMA wal_checkpoint(TRUNCATE); PRAGMA journal_mode=DELETE; VACUUM;"
  rm -f mexico.sqlite3-shm mexico.sqlite3-wal
fi
popd >/dev/null

step "Sync SQLite to webapp-svelte static assets"
cp "${ROOT_DIR}/packages/shared-data/mexico.sqlite3" "${ROOT_DIR}/packages/webapp-svelte/static/data/mexico.sqlite3"

step "Webapp Svelte: typecheck + build"
pushd "${ROOT_DIR}/packages/webapp-svelte" >/dev/null
npm run check
npm run build
popd >/dev/null

step "TypeScript package: lint + typecheck + tests"
pushd "${ROOT_DIR}/packages/typescript" >/dev/null
npm run lint
npm run format:check
npm run typecheck
npm test
npm test -- tests/integration-workflows.test.ts
popd >/dev/null

step "Python package: format + lint + typecheck + tests"
pushd "${ROOT_DIR}/packages/python" >/dev/null
black catalogmx
ruff check catalogmx
mypy catalogmx
pytest tests/ --cov=catalogmx --cov-branch
pytest tests/test_integration_workflows.py -q
popd >/dev/null

step "Dart package: analyze + format check + tests"
pushd "${ROOT_DIR}/packages/dart" >/dev/null
dart format --set-exit-if-changed .
dart analyze
dart test
dart test test/integration_workflows_test.dart
popd >/dev/null

echo
echo "All checks completed."
