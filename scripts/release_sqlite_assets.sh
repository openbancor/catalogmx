#!/usr/bin/env bash
set -euo pipefail

# Release the freshly generated SQLite assets.
# Usage: scripts/release_sqlite_assets.sh [tag]
# Example: scripts/release_sqlite_assets.sh sqlite-assets

TAG="${1:-sqlite-assets}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEBAPP_DIR="${ROOT_DIR}/packages/webapp"

pushd "${WEBAPP_DIR}" >/dev/null

echo "[release] Building latest sqlite assets via npm run data:build"
npm run data:build

ASSETS=(
  "${ROOT_DIR}/packages/shared-data/mexico.sqlite3"
  "${ROOT_DIR}/packages/webapp/public/data/clave_prod_serv.db"
  "${ROOT_DIR}/packages/webapp/public/data/sepomex.db"
  "${ROOT_DIR}/packages/webapp/public/data/localidades.db"
)

echo "[release] Creating GitHub release '${TAG}' with sqlite assets"
gh release create "${TAG}" \
  "${ASSETS[@]}" \
  --clobber \
  --repo openbancor/catalogmx \
  --title "SQLite assets (${TAG})" \
  --notes "SQLite DBs for webapp/catalogmx"

popd >/dev/null
