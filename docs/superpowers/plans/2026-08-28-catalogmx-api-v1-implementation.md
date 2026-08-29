# CatalogMX API v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved N1 Cloudflare Worker API in `packages/api-worker` with authenticated validation, auditable ISR/IMSS calculations, versioned small catalogs, bounded D1 catalog queries, tests, gates, and production-only deployment instructions.

**Architecture:** Keep the API as an independent Web-API-only Worker package. A small-data preload module registers bundled JSON through CatalogMX's existing `setCatalogJsonData` seam; pure validators and calculators are imported directly from `packages/typescript`; large SEPOMEX and SAT product/service requests use fixed, parameter-bound D1 statements. Authentication and rate limiting run before request-body handling, while route/method checks remain deterministic and all failures use one JSON error shape.

**Tech Stack:** TypeScript 5, Cloudflare Workers/Wrangler, Web Crypto API, Jest/ts-jest, Prettier, ESLint, Cloudflare D1, existing CatalogMX TypeScript source and shared JSON catalogs.

---

## File map

Create the following focused files:

- `packages/api-worker/package.json`, `package-lock.json`, `tsconfig.json`, `jest.config.cjs`, `eslint.config.cjs`, `.prettierrc.json`: package scripts, compiler/test/lint configuration, and pinned dependencies.
- `packages/api-worker/wrangler.toml`: non-production Worker/D1/rate-limit template with an explicit placeholder database id.
- `packages/api-worker/src/types.ts`: Worker environment, limiter, D1, route, and response types.
- `packages/api-worker/src/errors.ts`: typed public API errors and stable JSON responses.
- `packages/api-worker/src/auth.ts`: secret parsing, SHA-256 key authentication, and key-id-only results.
- `packages/api-worker/src/rate-limit.ts`: Cloudflare limiter adapter and in-memory test limiter.
- `packages/api-worker/src/data.ts`: small JSON imports, one-time preload registration, catalog allowlists, and catalog version.
- `packages/api-worker/src/validation.ts`: body parsing and bounded field validation.
- `packages/api-worker/src/validators.ts`: RFC/CURP/CLABE/NSS response adapters.
- `packages/api-worker/src/calculations.ts`: ISR/IMSS adapters, audit fields, and boundary rounding.
- `packages/api-worker/src/d1.ts`: typed prepared D1 queries for SEPOMEX and `clave-prod-serv`.
- `packages/api-worker/src/catalogs.ts`: allowlisted small catalog dispatch and large D1 dispatch.
- `packages/api-worker/src/router.ts`: route/method dispatch, auth/limit pipeline, and generic failure isolation.
- `packages/api-worker/src/index.ts`: Wrangler default export and named fetch entrypoint.
- `packages/api-worker/tests/helpers.ts`: deterministic test environment, API-key secret fixture, and D1 test double.
- `packages/api-worker/tests/auth.test.ts`, `validation.test.ts`, `validators.test.ts`, `calculations.test.ts`, `catalogs.test.ts`, `router.test.ts`: focused RED/GREEN tests for the approved contract.
- `packages/api-worker/migrations/0001_initial.sql`: D1 tables, indexes, and FTS5 virtual tables matching the shared SQLite schema.
- `packages/api-worker/DEPLOYMENT.md`: production-only resource, import, secret, route, smoke-test, and p95 instructions.
- `CHANGELOG.md`: an unreleased N1 API entry.

No production Cloudflare resource, secret, D1 import, route, or deployment command will be executed by this plan.

### Task 1: Package boundary and test harness

**Files:**
- Create: `packages/api-worker/package.json`
- Create: `packages/api-worker/tsconfig.json`
- Create: `packages/api-worker/jest.config.cjs`
- Create: `packages/api-worker/eslint.config.cjs`
- Create: `packages/api-worker/.prettierrc.json`
- Create: `packages/api-worker/wrangler.toml`
- Create: `packages/api-worker/tests/helpers.ts`
- Test: `packages/api-worker/tests/router.test.ts`

- [ ] **Step 1: Write the first failing route test**

Create a test that imports `fetch` from `src/index`, sends an unauthenticated request to `/api/v1/validate/rfc`, and expects status `401`, the shared error shape, JSON content type, and `Cache-Control: no-store`.

- [ ] **Step 2: Run the focused test and verify the expected missing-module failure**

Run: `cd packages/api-worker && npm test -- --runInBand tests/router.test.ts`

Expected: Jest fails because `src/index` does not exist yet; no implementation file is created to make this pass.

- [ ] **Step 3: Add only package configuration and the test environment**

Configure scripts `lint`, `format:check`, `typecheck`, `test`, `test:coverage`, `build`, and `validate`. Use `wrangler deploy --dry-run --outdir dist` for the Worker bundle, `jest --coverage` with a 90% global threshold, and TypeScript `strict`, `noUnusedLocals`, `noUnusedParameters`, `resolveJsonModule`, and `moduleResolution: node` so the Worker can consume the existing TypeScript source seam directly. The test helper exports `TEST_API_KEY`, a SHA-256 record, `authorizedEnv()`, and a typed D1 fake without implementing production behavior.

- [ ] **Step 4: Run the test again and keep it red for the missing Worker entrypoint**

Run: `cd packages/api-worker && npm test -- --runInBand tests/router.test.ts`

Expected: the harness loads, then fails with a missing `src/index` module. This confirms the first behavioral test is real and not passing accidentally.

- [ ] **Step 5: Commit the package boundary**

Run:

```bash
git add packages/api-worker/package.json packages/api-worker/tsconfig.json packages/api-worker/jest.config.cjs packages/api-worker/eslint.config.cjs packages/api-worker/.prettierrc.json packages/api-worker/wrangler.toml packages/api-worker/tests/helpers.ts packages/api-worker/tests/router.test.ts
git commit -m "chore(api): scaffold worker package and test harness"
```

### Task 2: Authentication, rotation, rate limiting, and error contract

**Files:**
- Create: `packages/api-worker/src/types.ts`
- Create: `packages/api-worker/src/errors.ts`
- Create: `packages/api-worker/src/auth.ts`
- Create: `packages/api-worker/src/rate-limit.ts`
- Test: `packages/api-worker/tests/auth.test.ts`
- Modify: `packages/api-worker/tests/router.test.ts`

- [ ] **Step 1: Write failing authentication and limiter tests**

Cover missing/invalid keys as `401`, malformed or absent production key secret as `503`, two active digests accepted during rotation, inactive digests rejected, only the authenticated key id passed to the limiter, limiter rejection as `429` with `Retry-After`, and missing production limiter as `503`. Assert that the response body never contains the raw key.

- [ ] **Step 2: Run authentication tests and verify RED**

Run: `cd packages/api-worker && npm test -- --runInBand tests/auth.test.ts tests/router.test.ts`

Expected: failures identify missing auth/limiter modules or behavior rather than assertion typos.

- [ ] **Step 3: Implement the minimal auth and error interfaces**

Use `crypto.subtle.digest('SHA-256', TextEncoder().encode(rawKey))`, normalize digests to lowercase hex, validate secret records `{ id: string, active: boolean, digest: string }[]`, compare bytes without early equality returns, and return only `{ keyId }`. Define `ApiError(status, code, message, headers?)`, `jsonResponse` with `Content-Type: application/json`, `Cache-Control: no-store`, deterministic `JSON.stringify`, and the exact `{ error: { code, message } }` shape. Define `RateLimiterBinding.limit({ key })` and a test-only `MemoryRateLimiter`.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run: `cd packages/api-worker && npm test -- --runInBand tests/auth.test.ts tests/router.test.ts`

Expected: all authentication, rotation, limiter, and error assertions pass.

- [ ] **Step 5: Commit the security boundary**

```bash
git add packages/api-worker/src/types.ts packages/api-worker/src/errors.ts packages/api-worker/src/auth.ts packages/api-worker/src/rate-limit.ts packages/api-worker/tests/auth.test.ts packages/api-worker/tests/router.test.ts
git commit -m "feat(api): add API key authentication and rate limiting"
```

### Task 3: Request validation and identifier endpoints

**Files:**
- Create: `packages/api-worker/src/validation.ts`
- Create: `packages/api-worker/src/data.ts`
- Create: `packages/api-worker/src/validators.ts`
- Test: `packages/api-worker/tests/validation.test.ts`
- Test: `packages/api-worker/tests/validators.test.ts`

- [ ] **Step 1: Write failing body and identifier endpoint tests**

Cover malformed JSON, non-object JSON, missing `value`, non-string `value`, empty-but-present values returning a normal `valid: false` result, uppercase/trimmed output, RFC `tipo`, CLABE details plus non-personal bank `{ code, name, full_name, spei }`, and all four validator routes. Test that the preload registers calculator JSON, INEGI, SEPOMEX, Banxico, Nómina, and small CFDI data through `setCatalogJsonData` before catalog reads.

- [ ] **Step 2: Run the tests and verify RED**

Run: `cd packages/api-worker && npm test -- --runInBand tests/validation.test.ts tests/validators.test.ts`

Expected: failures identify missing request/validator/data adapters.

- [ ] **Step 3: Implement bounded parsing and preloading**

`parseJsonObject` catches malformed JSON and rejects arrays/null; `requireString` enforces fields. `data.ts` imports only the small JSON files and registers their exact loader paths once, exports `CATALOG_VERSION = '2026-01-05'`, the Nómina `2026` snapshot, and explicit catalog maps. `validators.ts` calls the existing pure library functions and never logs or stores the raw request body.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `cd packages/api-worker && npm test -- --runInBand tests/validation.test.ts tests/validators.test.ts`

Expected: all malformed-body, normalized-output, RFC type, CLABE bank, and validator-route tests pass.

- [ ] **Step 5: Commit validation endpoints**

```bash
git add packages/api-worker/src/validation.ts packages/api-worker/src/data.ts packages/api-worker/src/validators.ts packages/api-worker/tests/validation.test.ts packages/api-worker/tests/validators.test.ts
git commit -m "feat(api): expose authenticated identifier validation"
```

### Task 4: Auditable ISR and IMSS calculations

**Files:**
- Create: `packages/api-worker/src/calculations.ts`
- Test: `packages/api-worker/tests/calculations.test.ts`

- [ ] **Step 1: Write failing calculation tests**

Cover valid ISR and IMSS requests, every supported ISR period, unsupported period/exercise as `422`, wrong types and finite/non-negative/range violations as `400`, rejection of `name`, `rfc`, `curp`, `nss`, and `clabe` fields, risk class `1` in the IMSS audit, complete worker/patron component maps, boundary rounding to two decimals, raw calculator values in `auditoria`, selected fiscal table limits/rate/fixed fee/subsidy, formula identifiers, and byte-for-byte deterministic responses for identical requests.

- [ ] **Step 2: Run calculation tests and verify RED**

Run: `cd packages/api-worker && npm test -- --runInBand tests/calculations.test.ts`

Expected: failures identify missing calculation adapter behavior.

- [ ] **Step 3: Implement calculator delegation and audit projections**

Preload `isr-tables.json`, `imss-tables.json`, and `imss-catalogs.json`, call `ISRCalculator.calcular(base, ejercicio, periodo, false)` only after `getTabla` confirms the requested table, and call `IMSSCalculator.calcularCuotasObreroPatronales(sdi, dias, ejercicio, 1)`. Round only response projections with a two-decimal helper; retain the exact result under `auditoria.interno`; construct `tabla_aplicada` and `regla_aplicada` from the selected table/UMA and fixed formula strings. Reject extra fields before delegation.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `cd packages/api-worker && npm test -- --runInBand tests/calculations.test.ts`

Expected: all calculation, audit, PII, bounds, and determinism tests pass.

- [ ] **Step 5: Commit calculation endpoints**

```bash
git add packages/api-worker/src/calculations.ts packages/api-worker/tests/calculations.test.ts
git commit -m "feat(api): add auditable ISR and IMSS endpoints"
```

### Task 5: Small catalogs and fixed D1 queries

**Files:**
- Create: `packages/api-worker/src/d1.ts`
- Create: `packages/api-worker/src/catalogs.ts`
- Create: `packages/api-worker/migrations/0001_initial.sql`
- Test: `packages/api-worker/tests/catalogs.test.ts`

- [ ] **Step 1: Write failing catalog and SQL tests**

Cover all seven Nómina allowlist entries requiring `vigencia=2026`, all supported small CFDI `c_*` entries, INEGI states/municipios, SEPOMEX `cp` lookup, catalog version header and metadata, unsupported names as `404`, missing/old vigencia as `400`/`422`, page-size cap `100`, missing D1 as `503`, product/service exact `clave` and FTS `q` queries, postal `cp`/bounded `q` queries, deterministic ordering, and assertions that all SQL uses `?` placeholders with bound parameters and no user-provided identifiers.

- [ ] **Step 2: Run catalog tests and verify RED**

Run: `cd packages/api-worker && npm test -- --runInBand tests/catalogs.test.ts`

Expected: failures identify missing D1/catalog dispatch or SQL behavior.

- [ ] **Step 3: Implement the D1 boundary and allowlists**

Define a minimal typed D1 interface (`prepare(sql).bind(...).all()`), use fixed `SELECT` projections and `ORDER BY` clauses for `codigos_postales` and `clave_prod_serv`, and return mapped rows without fallback data. Implement exact product key lookup and FTS5 search; reject requests that omit both `clave` and `q`. Route small catalogs through the preload store, set `X-Catalog-Version`, and include `{ metadata: { vigencia: 2026 } }` only for Nómina responses. The migration creates both base tables, indexes, and their FTS5 virtual tables with content linkage.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `cd packages/api-worker && npm test -- --runInBand tests/catalogs.test.ts`

Expected: all allowlist, header, version, D1, SQL-binding, pagination, and availability tests pass.

- [ ] **Step 5: Commit catalogs and D1 boundary**

```bash
git add packages/api-worker/src/d1.ts packages/api-worker/src/catalogs.ts packages/api-worker/migrations/0001_initial.sql packages/api-worker/tests/catalogs.test.ts
git commit -m "feat(api): add versioned catalogs and D1 queries"
```

### Task 6: Worker router and full endpoint integration

**Files:**
- Create: `packages/api-worker/src/router.ts`
- Create: `packages/api-worker/src/index.ts`
- Modify: `packages/api-worker/tests/router.test.ts`

- [ ] **Step 1: Extend failing integration tests**

Cover the complete pipeline for every endpoint, `405` plus `Allow: POST`/`GET`, unknown routes as `404`, unexpected exceptions as generic `500`, no request-body/API-key logging hooks, fixed headers, stable key ordering for repeated requests, and auth-before-body behavior for protected routes.

- [ ] **Step 2: Run the integration suite and verify RED**

Run: `cd packages/api-worker && npm test -- --runInBand tests/router.test.ts`

Expected: route integration assertions fail until the router and Worker entrypoint exist.

- [ ] **Step 3: Implement the Worker request pipeline**

Use route descriptors with exact paths and methods, perform route/method resolution, authenticate, rate-limit by key id, preload small data, parse/validate the body or query, dispatch to the endpoint adapter, and catch only `ApiError` publicly while converting unknown errors to a generic `500`. Export `{ fetch: handleRequest }` as the default Worker module and a named `fetch` for tests.

- [ ] **Step 4: Run the entire API test suite and verify GREEN**

Run: `cd packages/api-worker && npm run test:coverage`

Expected: all API tests pass and global lines, statements, functions, and branches are each at least 90%.

- [ ] **Step 5: Commit the Worker entrypoint**

```bash
git add packages/api-worker/src/router.ts packages/api-worker/src/index.ts packages/api-worker/tests/router.test.ts
git commit -m "feat(api): route catalogmx API v1 worker endpoints"
```

### Task 7: Deployment instructions and repository documentation

**Files:**
- Create: `packages/api-worker/DEPLOYMENT.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write documentation acceptance tests/checks**

Verify by text search that the instructions name D1 creation, migration/import of both large tables and FTS indexes, rate-limit namespace allocation, `CATALOGMX_API_KEYS` JSON shape, zero-downtime digest rotation, route configuration, deploy command, authenticated smoke tests, and p95 measurement, and explicitly state that none of these external mutations was run.

- [ ] **Step 2: Add concrete production-only instructions**

Document commands with operator-supplied database/namespace identifiers, import validation queries, secret creation and rotation order, route example for `/api/v1/*`, `wrangler deploy`, smoke requests for each endpoint family, and a p95 measurement procedure. Keep all raw keys out of the repository and make the template fail closed until bindings/secrets are configured.

- [ ] **Step 3: Add the conventional changelog entry**

Add an `Unreleased` entry describing the new API Worker, tests, D1 migration, and deployment guide without claiming production deployment or production data availability.

- [ ] **Step 4: Commit documentation**

```bash
git add packages/api-worker/DEPLOYMENT.md CHANGELOG.md
git commit -m "docs(api): add N1 deployment instructions and changelog"
```

### Task 8: Verification gates and final review

**Files:**
- Modify only if formatting or gate configuration requires it.

- [ ] **Step 1: Run the API gates**

Run:

```bash
cd packages/api-worker
npm run lint
npm run format:check
npm run typecheck
npm run test:coverage
npm run build
```

Expected: every command exits `0`; coverage is at least 90% in all configured metrics; Wrangler produces a dry-run bundle without performing a deployment.

- [ ] **Step 2: Run the existing TypeScript and Webapp gates**

Run:

```bash
cd packages/typescript && npm run lint && npm run format:check && npm run typecheck && npm test
cd ../webapp-svelte && npm run build
```

Expected: the existing TypeScript suite remains at 1,431 passing tests and the static webapp build passes.

- [ ] **Step 3: Run the Python baseline and record only unrelated existing failures**

Run: `packages/python/.venv/bin/python -m pytest packages/python/tests/ --cov=catalogmx --cov-branch`

Expected: the known two identity-generation failures under the current date/Faker runtime may remain; no N1 file changes those areas. If any new failure appears outside that known baseline, investigate before completion.

- [ ] **Step 4: Inspect the final diff and repository state**

Run: `git status --short && git diff --check && git log --oneline --decorate -12`

Confirm that only the API package, its plan/spec documentation, and `CHANGELOG.md` changed; no secrets, generated coverage, `dist`, database dumps, or production receipts are tracked.

- [ ] **Step 5: Use verification-before-completion before the handoff**

Re-read the approved design line by line against the implementation and report concrete command output, coverage, existing-suite status, known Python baseline status, commit list, and the exact production gates intentionally left for the operator.
