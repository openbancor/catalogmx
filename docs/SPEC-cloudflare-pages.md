# SPEC: catalogmx on Cloudflare Pages (catalogmx.openbancor.com)

Owner: Luis Fernando Barrera
Status: Draft

## Goal
Host the webapp at `catalogmx.openbancor.com` with stable SQLite VFS access to the full catalogs.

## Problem Inventory (gitignore-style)
```
# Hosting/data issues observed on GitHub Pages
VFS_RANGE_UNRELIABLE
HEAD_GZIP_LENGTH_UNKNOWN
CHUNK_404_INTERMITTENT
CDN_CACHE_STALE_ASSETS

# Data plumbing
MEXICO_SQLITE_MISSING_VIEW
SQLITE_RELEASE_DEP_CHAIN

# UX impact
SQLITE_LOAD_FAILURES
CATALOG_QUERY_ERRORS
PARTIAL_TABLE_LOADS
```

## Why It Breaks Today
- GitHub Pages sometimes serves `HEAD` with `Content-Encoding: gzip`, so `Content-Length` is invalid for VFS.
- Chunked VFS calls occasionally return 404 due to CDN cache propagation.
- `sql.js-httpvfs` requires stable `Range` responses; any mismatch yields `doXHR failed`.
- Release pipelines were coupled to a missing `mexico_dynamic.sqlite3` asset, blocking updates.
- Missing legacy view (`c_ClaveProdServ`) caused SQL errors.

## Decision
Move the webapp to Cloudflare Pages and serve SQLite assets from a reliable object store
that supports `Range`, stable `Content-Length`, and predictable cache headers.

## Architecture (Proposed)
### App
- Cloudflare Pages: `catalogmx.openbancor.com`
- Build output: `packages/webapp-svelte/build`

### Data (VFS)
Option A (recommended):
- Cloudflare R2 bucket for:
  - `mexico.sqlite3`
  - `mexico.sqlite3.meta.json`
  - `mexico.sqlite3.0000..NNNN` chunks
- R2 served via a public domain, e.g. `data.catalogmx.openbancor.com`

Option B (acceptable):
- Cloudflare Pages static assets for chunks
- Still use a dedicated subdomain to isolate cache rules

## Required Headers (Data Domain)
- `Accept-Ranges: bytes`
- `Content-Length` must match raw file size (no gzip for sqlite/chunks)
- `Content-Type: application/octet-stream`
- Cache: long TTL + cache-bust via filename or querystring

## Webapp Changes
- Base URL for DB set to data domain, not app domain.
- VFS config uses:
  - `urlPrefix` = `https://data.catalogmx.openbancor.com/mexico.sqlite3.`
  - `databaseLengthBytes` from `mexico.sqlite3.meta.json`
  - `cacheBust` from `meta.json`
- Keep SQL view compatibility:
  - Ensure `c_ClaveProdServ` view exists in `mexico.sqlite3`.

## Build & Deploy Flow
1) Build unified DB:
   - `packages/shared-data/build_unified_sqlite.py`
2) Split into chunks:
   - `mexico.sqlite3.0000` etc.
3) Generate metadata:
   - `mexico.sqlite3.meta.json` with `length` + `cacheBust`
4) Upload to R2 (or Pages static if Option B).
5) Deploy webapp to Cloudflare Pages.

## Cloudflare Pages Configuration
- Project root: repository root
- Build command: `cd packages/webapp-svelte && npm ci && npm run build`
- Output directory: `packages/webapp-svelte/build`
- Environment:
  - `VITE_DATA_BASE_URL=https://data.catalogmx.openbancor.com`
  - `VITE_SQLITE_LENGTH`, `VITE_SQLITE_HASH` optional (meta JSON preferred)

## Data Domain Configuration (R2)
- Public bucket with `Range` support.
- Disable gzip for `.sqlite3` and chunk files.
- Cache rules:
  - Immutable for chunks (`max-age=31536000, immutable`)
  - Short cache for `mexico.sqlite3.meta.json` (e.g. 5 minutes).

## Rollout Plan
1) Deploy data domain and verify:
   - `HEAD` returns `Content-Length` and `Accept-Ranges`.
2) Deploy app pointing to data domain.
3) Smoke test:
   - `/catalogos/sat/cfdi` loads 52,514 rows (paged).
4) Switch DNS:
   - `catalogmx.openbancor.com` -> Pages.

## Risks
- If gzip is enabled on data domain, VFS will break.
- If chunk count changes, stale caches could request missing chunks.
- Large file download fallback (`sql.js`) is slower on mobile.

## Success Criteria
- No `doXHR failed` errors in console for catalogs.
- VFS loads catalogs on first try.
- `Productos y Servicios` renders 52,514 rows with paging.
- `catalogmx.openbancor.com` serves the app without CDN cache mismatch.
