#!/usr/bin/env bash
set -euo pipefail

# Run all main quality gates: data build, webapp build, TS lint/typecheck, Python lint/tests, Dart checks.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

step() {
  echo
  echo "==> $*"
}

step "Build SQLite data (mexico.sqlite3 and public/data copies)"
pushd "${ROOT_DIR}/packages/webapp" >/dev/null
npm run data:build
npm run sync:data
popd >/dev/null

step "Build webapp (TypeScript + Vite)"
pushd "${ROOT_DIR}/packages/webapp" >/dev/null
npm run build
popd >/dev/null

step "TypeScript package: lint + typecheck"
pushd "${ROOT_DIR}/packages/typescript" >/dev/null
npm run lint
npm run typecheck
popd >/dev/null

step "Python package: format check + lint + typecheck + tests"
pushd "${ROOT_DIR}/packages/python" >/dev/null
black --check catalogmx
ruff check catalogmx
mypy catalogmx
pytest tests/ --cov=catalogmx --cov-branch
popd >/dev/null

step "Dart package: analyze + format check + tests"
pushd "${ROOT_DIR}/packages/dart" >/dev/null
dart analyze
dart format --set-exit-if-changed .
dart test
popd >/dev/null

echo
echo "All checks completed."
