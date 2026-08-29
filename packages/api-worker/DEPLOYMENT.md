# catalogmx API Worker: production runbook

This document prepares the production operations for N1. The implementation
worktree contains no production database, secret, route, or deployment receipt.
The commands below are operator steps and must be run only after the values
marked `<...>` have been reviewed for the target Cloudflare account.

The Worker expects the bindings `CATALOG_DB` and `API_RATE_LIMITER` declared in
`wrangler.toml`. Cloudflare D1 uses a Worker binding and prepared statements;
the rate limiter is keyed by the authenticated API-key id. See the official
[D1 Worker API documentation](https://developers.cloudflare.com/d1/worker-api/d1-database/)
and [Workers Rate Limiting bindings](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/).

## 1. Preflight

From the repository root:

```bash
cd packages/api-worker
npm ci
npm run validate
```

`validate` runs formatting, lint, typecheck, the coverage gate, and the
Wrangler dry-run. It must not be replaced by a deploy command. Authenticate
the operator separately with the intended Cloudflare account before the
resource-creation steps.

Before production import, resolve the source-data exception documented in the
implementation: `packages/shared-data/sat/cfdi_4.0/c_TasaOCuota.json` contains
non-JSON `NaN` values and is intentionally not exposed by this N1 build. Keep
that catalog disabled until its upstream data is corrected and a new fixture,
test, and catalog allowlist entry are reviewed.

## 2. Create D1 and apply the schema

Replace the placeholder `database_id` in `wrangler.toml` with the id returned
by the account that owns the production Worker. Do not reuse the placeholder
UUID or a database from another environment.

```bash
npx wrangler d1 create catalogmx-api-v1
# Copy the returned database_id into packages/api-worker/wrangler.toml.
npx wrangler d1 migrations apply catalogmx-api-v1 --remote
```

The migration creates `codigos_postales`, `clave_prod_serv`, their indexes,
and the two FTS5 tables. Verify the remote migration status before importing
rows.

## 3. Import the large catalogs

The checked-in source database is read-only input. Generate bounded SQL files
with explicit destination-column order, then apply each file remotely. This
keeps the request path free of Node filesystem and SQLite access.

```bash
source_db=../shared-data/mexico.sqlite3
import_dir="$(mktemp -d)"

sqlite3 "$source_db" <<'SQL' > "$import_dir/codigos_postales.sql"
.mode insert codigos_postales
SELECT cp, asentamiento, tipo_asentamiento, municipio, estado, ciudad,
       NULL AS cp_oficina, codigo_estado, codigo_municipio, zona
FROM codigos_postales
ORDER BY cp, asentamiento;
SQL

sqlite3 "$source_db" <<'SQL' > "$import_dir/clave_prod_serv.sql"
.mode insert clave_prod_serv
SELECT clave, descripcion, incluye_iva, incluye_ieps, complemento,
       fecha_inicio_vigencia, fecha_fin_vigencia, palabras_similares,
       estimulo_franja_fronteriza
FROM clave_prod_serv
ORDER BY clave;
SQL

split -l 1000 "$import_dir/codigos_postales.sql" "$import_dir/cp-"
split -l 1000 "$import_dir/clave_prod_serv.sql" "$import_dir/cps-"

for file in "$import_dir"/cp-* "$import_dir"/cps-*; do
  npx wrangler d1 execute catalogmx-api-v1 --remote --file="$file"
done

npx wrangler d1 execute catalogmx-api-v1 --remote --command \
  "INSERT INTO codigos_postales_fts(codigos_postales_fts) VALUES ('rebuild'); INSERT INTO clave_prod_serv_fts(clave_prod_serv_fts) VALUES ('rebuild');"
```

If an import chunk fails, stop, record the chunk name and remote error, and
repair or resume from a verified database state. Do not silently continue.
After import, verify counts and representative deterministic queries in D1:

```bash
npx wrangler d1 execute catalogmx-api-v1 --remote --command \
  "SELECT 'codigos_postales' AS tabla, COUNT(*) AS total FROM codigos_postales UNION ALL SELECT 'clave_prod_serv', COUNT(*) FROM clave_prod_serv;"
npx wrangler d1 execute catalogmx-api-v1 --remote --command \
  "SELECT clave, descripcion FROM clave_prod_serv WHERE clave = '01010101' ORDER BY clave LIMIT 1;"
```

Expected source row counts for the checked-in snapshot are 157252 postal
records and 52514 product/service records. A different approved snapshot must
record its source version and expected counts before deployment.

## 4. Configure API keys and rotation

`CATALOGMX_API_KEYS` is a JSON array of records with only `id`, `active`, and a
lowercase SHA-256 `digest` of the raw key. The raw key is never stored in the
repository, secret value output, response body, or logs. Generate and deliver
the raw key through the organization’s approved secure channel.

Example operator flow (the raw key is entered without echo):

```bash
read -r -s API_KEY
printf '\n'
digest="$(printf '%s' "$API_KEY" | shasum -a 256 | cut -d ' ' -f 1)"
payload="$(jq -cn --arg digest "$digest" '[{id:"client-2026-01",active:true,digest:$digest}]')"
printf '%s' "$payload" | npx wrangler secret put CATALOGMX_API_KEYS
unset API_KEY digest payload
```

For rotation, publish a secret containing both the active old record and the
new active record, verify the new key with a non-sensitive request, then
publish a replacement with the old record set to `active:false`. A malformed,
empty, or missing secret intentionally makes the Worker fail closed with 503.

## 5. Configure the rate limiter and route

Choose a positive, account-appropriate `namespace_id` that is not reused by an
unrelated limiter, and retain the N1 policy of 100 requests per 60 seconds.
Update the placeholder in `wrangler.toml` only after review. The binding key is
the authenticated client id, not an IP address.

Configure the production hostname in a reviewed Wrangler environment or in
the deployment configuration, for example:

```toml
[[routes]]
pattern = "api.example.com/api/v1/*"
zone_name = "example.com"
```

See Cloudflare’s [Wrangler configuration reference](https://developers.cloudflare.com/workers/wrangler/configuration/)
for D1 binding and route configuration.

## 6. Deploy and smoke-test (operator gate)

Run the deploy only after the local gates, remote migration/count checks,
secret review, and route review pass:

```bash
npx wrangler deploy
```

With the raw key supplied interactively, exercise one request from each
surface and inspect status, `X-Catalog-Version`, `vigencia` where applicable,
and the absence of raw secrets in bodies or logs:

```bash
read -r -s API_KEY
printf '\n'
api_url='https://api.example.com'

curl -fsS -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"value":"BACL891217NJ5"}' \
  "$api_url/api/v1/validate/rfc"

curl -fsS -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"base_gravable":15000,"periodo":"mensual","ejercicio":2026}' \
  "$api_url/api/v1/calc/isr"

curl -fsS -D - -o /tmp/catalogmx-api-catalog.json \
  -H "X-API-Key: $API_KEY" \
  "$api_url/api/v1/catalogs/sat/nomina/tipo-nomina?vigencia=2026"

curl -fsS -H "X-API-Key: $API_KEY" \
  "$api_url/api/v1/catalogs/sepomex/codigos-postales?cp=06700&limit=10&page=1"

curl -fsS -H "X-API-Key: $API_KEY" \
  "$api_url/api/v1/catalogs/sat/cfdi/clave-prod-serv?clave=01010101"

unset API_KEY
```

Also verify the negative gates: missing/invalid key is 401, malformed JSON is
400, unsupported fiscal data is 422, an exhausted client limiter is 429 with
`Retry-After`, and D1/binding misconfiguration is 503. Keep response and log
samples free of real personal data.

## 7. Measure p95 before sign-off

The design requires a production-equivalent p95 measurement but does not set a
numeric SLO. Establish the target with the service owner, then record a
bounded run for validation, calculation, a small catalog, and each D1 query
mode. For example, with `oha` installed:

```bash
oha -n 100 -c 5 \
  -H "X-API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  -m POST \
  -d '{"value":"BACL891217NJ5"}' \
  "$api_url/api/v1/validate/rfc"
```

Record the endpoint, concurrency, sample size, p95, status distribution,
catalog version, Worker deployment id, and D1 snapshot. Do not treat a local
build or Wrangler dry-run as production latency evidence.

## Readiness checklist

- [ ] Production D1 id and rate-limit namespace reviewed and substituted.
- [ ] Migration applied remotely; row counts and FTS exact/query lookups verified.
- [ ] Corrected/approved handling for `c_TasaOCuota` recorded before exposing it.
- [ ] API secret installed and a rotation/revocation owner identified.
- [ ] Route and hostname reviewed.
- [ ] Deploy receipt, smoke results, and p95 evidence recorded.
- [ ] No raw API keys, production data, database dumps, or receipts committed.
