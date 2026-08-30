# CatalogMX API v1 Design

**Status:** Approved for implementation

**Date:** 2026-08-28

## Goal

Expose the N1 internal API required by Cronikos: authenticated RFC, CURP,
CLABE and NSS validation; auditable ISR and IMSS calculations; and versioned
SAT, INEGI and SEPOMEX catalog access. The implementation must preserve the
existing TypeScript library behavior, keep personal data out of calculations,
and remain deployable at the Cloudflare edge without bundling the large
catalog JSON files.

## Context and constraints

- The current web application is SvelteKit with `adapter-static` and is
  deployed as a Cloudflare Pages static site.
- The TypeScript package already owns the validators, calculators, catalog
  loaders and shared data. Its normal loader is synchronous and supports
  preloaded JSON in non-Node runtimes.
- `packages/shared-data/mexico.sqlite3` already contains the `codigos_postales`
  and `clave_prod_serv` tables plus FTS5 indexes. The database is approximately
  47 MB; the corresponding JSON files are approximately 40 MB and 17 MB.
- Current repository baseline in the isolated worktree is 1,431 passing
  TypeScript tests. Python executes 1,618 tests with two unrelated baseline
  failures in identity generation under the current date/Faker runtime; N1
  must not modify those areas.
- N1 includes source, tests, local Worker configuration and deployment
  instructions. Creating Cloudflare resources, importing production D1 data,
  setting production secrets, and deploying are explicit follow-up gates.

## Runtime decision

Implement a separate module Worker in `packages/api-worker` and route
`/api/v1/*` to it at the API host or at the existing Pages hostname through a
Cloudflare route. Keep the SvelteKit Pages project static and independently
deployable.

Pages Functions was considered because it can run Worker code and bind D1, but
it is file-based, lives inside the Pages project, and participates in the
Pages deployment and invocation routing. A dedicated Worker gives the API its
own `wrangler` configuration, D1 binding, rate-limit binding, secret lifecycle
and rollback boundary. It also avoids adding an authenticated Function to
every static Pages deployment.

The Worker uses only Web APIs at runtime. Small catalog data and calculator
tables are bundled as JSON and registered through the existing TypeScript
loader's preload seam. Large catalog requests use asynchronous prepared D1
queries; no Node filesystem, `better-sqlite3`, or synchronous SQLite path is
used in the Worker request path.

## API contract

All requests below require `X-API-Key`. Responses use
`Content-Type: application/json` and the error shape:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Human-readable, non-sensitive explanation"
  }
}
```

The Worker does not log API keys or request bodies. Calculation requests are
accepted only as numeric amounts and control parameters; no employee name,
RFC, CURP, NSS, CLABE or other personal field is accepted by either
calculation endpoint.

### Validation endpoints

```text
POST /api/v1/validate/rfc   {"value": string}
POST /api/v1/validate/curp  {"value": string}
POST /api/v1/validate/clabe {"value": string}
POST /api/v1/validate/nss   {"value": string}
```

Responses preserve the normalized identifier in uppercase and expose the
existing library result. RFC includes `tipo` from `detectRfcType`; CLABE
includes `banco` only as a non-personal catalog object when its bank code is
known. A missing or invalid identifier is a normal validation result with
`valid: false`, not a server error. Malformed JSON or a missing `value` is a
400 error.

### Calculation endpoints

```text
POST /api/v1/calc/isr
{"base_gravable": number, "periodo": "diario|semanal|quincenal|mensual|anual", "ejercicio": number}

POST /api/v1/calc/imss
{"sdi": number, "dias_cotizados": number, "ejercicio": number}
```

ISR delegates to `ISRCalculator.calcular`. The response contains
`retencion_mensual` for compatibility with the Cronikos contract, the
requested `periodo`, the existing detailed numeric result, and
`tabla_aplicada`/`regla_aplicada` with the fiscal year, selected limits,
fixed fee, marginal rate, subsidy and calculation formula. The request is
rejected when the exercise or period has no loaded table.

IMSS delegates to
`IMSSCalculator.calcularCuotasObreroPatronales`, using risk class 1 because
the N1 contract does not carry a risk-class parameter. The response exposes
`cuotas_obrera`, `cuotas_patronal`, a complete `desglose` of the existing
component maps, and `regla_aplicada` with the exercise, UMA source, risk-class
assumption and formula identifiers.

Numbers are finite, non-negative, bounded to a safe request range, and are
rounded to two decimal places only at the API boundary. Internal calculator
values remain available in the audit section so consumers can reconcile
rounding. No timestamp, random value, or request-specific personal data is
included in a successful response, keeping results deterministic.

### Catalog endpoints

```text
GET /api/v1/catalogs/sat/nomina/{catalogo}?vigencia=2026
GET /api/v1/catalogs/sat/cfdi/{catalogo}
GET /api/v1/catalogs/inegi/estados
GET /api/v1/catalogs/inegi/municipios
GET /api/v1/catalogs/sepomex/codigos-postales?cp=06700
```

The API uses an explicit allowlist rather than arbitrary filesystem or SQL
names. SAT Nómina exposes the catalog files currently present under
`sat/nomina_1.2`; SAT CFDI exposes the current small `c_*` catalogs and the
large `clave-prod-serv` D1 query; INEGI exposes `estados` and `municipios`;
SEPOMEX exposes postal-code lookup. Unsupported catalog names return 404.

`vigencia` is mandatory for SAT Nómina and must be the currently loaded fiscal
snapshot (`2026` in this release). Historical years are rejected until their
separate data snapshots exist; the API never labels one current snapshot as a
historical catalog. The catalog response is `{ "items": [...] }` and every
successful catalog response includes `X-Catalog-Version` plus the requested
fiscal validity in response metadata where applicable.

Large queries have a maximum page size of 100. SEPOMEX requires `cp`; the
service also supports bounded `q`/pagination for local diagnostics. The
`clave-prod-serv` service supports exact `clave` lookup or FTS5 `q` lookup.
All SQL uses fixed query templates and bound parameters, with deterministic
`ORDER BY` clauses.

## Authentication and rate limiting

Production secrets use:

- `CATALOGMX_API_KEYS`: JSON records containing an opaque key id, an active
  flag and the SHA-256 digest of the raw key. The raw key is never committed,
  returned, or logged.
- `API_RATE_LIMITER`: Cloudflare Rate Limiting binding. The key passed to the
  binding is the authenticated key id, not an IP address or raw secret.

Adding a new digest before removing the old digest allows rotation without a
downtime window. In production, a missing key secret or rate-limit binding is
fail-closed with a 503 configuration error; local tests may inject an
in-memory limiter. Missing/invalid keys return 401, and an exceeded limiter
returns 429 with `Retry-After`.

## Data flow

1. The Worker validates method and route, then authenticates `X-API-Key`.
2. The authenticated key id is checked against the Cloudflare limiter.
3. JSON bodies are parsed and validated without retaining or logging PII.
4. Validation calls the existing pure validators and the small bank catalog.
5. Calculation calls the existing TypeScript calculators after their table
   JSON is preloaded once per isolate.
6. Small catalog routes use existing catalog data preloaded into the library
   loader. Large routes issue prepared D1 queries against the existing table
   and FTS5 schema.
7. The response is serialized with stable field ordering from the source
   object, fixed headers, and no cacheable authenticated content.

## Error and availability behavior

- 400: malformed JSON, wrong field types, missing required query parameters or
  out-of-range numeric input.
- 401: missing or invalid API key.
- 404: unknown route or catalog allowlist entry.
- 405: unsupported HTTP method, with an `Allow` header.
- 429: key-specific rate limit exceeded.
- 422: syntactically valid but unsupported fiscal exercise/period.
- 503: required production binding/data source unavailable.
- 500: unexpected internal failure; the message is generic and the cause is
  available only to server-side observability.

The Worker has no fallback that silently substitutes a missing fiscal table
or returns an empty large catalog. This keeps Cronikos from treating an
availability or data-version failure as a valid zero result.

## Testing and verification

The Worker package has focused tests covering authentication, rotation,
limiting, validation, calculations, audit fields, PII rejection, catalog
version headers, fiscal-vigencia errors, D1 exact and FTS lookups, route
errors, and deterministic serialization. D1 is represented by a small typed
test double because production D1 is an external binding; its SQL templates
and bound parameters are asserted in the tests.

Verification gates are:

```text
packages/python/.venv/bin/python -m pytest tests/ --cov=catalogmx --cov-branch
packages/typescript: npm run lint && npm run format:check && npm run typecheck && npm test
packages/api-worker: npm run lint && npm run format:check && npm run typecheck && npm run test:coverage && npm run build
packages/webapp-svelte: npm run build
```

The existing Python baseline failures are tracked separately and are not
changed by N1. The API package has its own 90% minimum coverage threshold;
the existing TypeScript package thresholds remain unchanged.

## Deployment boundary

The repository will include a Wrangler template, D1 migration/import notes,
secret format, key-rotation steps and a route example. Production readiness
still requires creating the D1 database, importing the two large tables and
their FTS indexes, allocating the rate-limit namespace, setting
`CATALOGMX_API_KEYS`, configuring the route, deploying the Worker and running
authenticated smoke tests plus a p95 measurement. None of those external
state changes is performed by the local implementation.

## Source references

- Cronikos Nómina extension contract: `/Users/luisfernando/Code/workspaces/cronikos/docs/NOMINA-EXTENSION.md`
- [CatalogMX Cloudflare Pages design](../../SPEC-cloudflare-pages.md)
- [Cloudflare Pages Functions routing](https://developers.cloudflare.com/pages/functions/routing/)
- [Cloudflare D1 Worker API](https://developers.cloudflare.com/d1/worker-api/d1-database/)
- [Cloudflare Rate Limiting API](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/)
