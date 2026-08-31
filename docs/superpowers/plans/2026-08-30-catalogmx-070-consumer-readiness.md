# CatalogMX 0.7.0 Consumer Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release CatalogMX 0.7.0 with validated fiscal inputs and proven compatibility with the API Worker, Cronikos payroll, and PayGlobal catalog consumers.

**Architecture:** CatalogMX owns fiscal and catalog data and exposes defensive language-parity APIs. Consumers depend only on package/API contracts and prove them with isolated contract tests; no consumer carries copied fiscal tables.

**Tech Stack:** Python 3.10+, TypeScript 5/Jest, ClojureScript/shadow-cljs, Dart/Flutter, Kotlin/Gradle, Cloudflare Workers/Wrangler, GitHub Actions, reviewctl.

---

### Task 1: Pin isolated workspaces and baselines

**Files:** No source changes.

- [ ] Record physical root, branch, SHA, remote, and dirty status for CatalogMX, Cronikos, PayGlobal Core, CRM, and Rails.
- [ ] Create or reuse isolated worktrees without altering existing feature branches.
- [ ] Run each repository's focused existing CatalogMX tests and record any baseline failures before implementation.

### Task 2: Reject invalid ordinary IMSS inputs

**Files:**
- Modify: `packages/typescript/tests/imss-vectors.test.ts`
- Modify: `packages/typescript/src/calculators/imss-calculator.ts`
- Modify: `packages/python/tests/test_imss_calculator.py`
- Modify: `packages/python/catalogmx/calculators/imss.py`

- [ ] Add parameterized tests asserting that `NaN`, infinity, zero, negative salary, non-positive days, and SBC below the selected zone's minimum fail with `RangeError`/`ValueError`:

```typescript
expect(() => IMSSCalculator.calcularCuotasObreroPatronales(Number.NaN, 30, 2026)).toThrow(RangeError);
expect(() => IMSSCalculator.calcularCuotasObreroPatronales(315.03, 30, 2026)).toThrow(RangeError);
expect(() => IMSSCalculator.calcularCuotasObreroPatronales(315.04, -1, 2026)).toThrow(RangeError);
```

```python
@pytest.mark.parametrize("salary,days", [(math.nan, 30), (315.03, 30), (315.04, -1)])
def test_rejects_invalid_ordinary_imss_input(salary: float, days: int) -> None:
    with pytest.raises(ValueError):
        calcular_cuotas_obrero_patronales(salary, days, 2026)
```
- [ ] Run the focused tests and verify they fail because current calculations return a value.
- [ ] Add one small input guard per language and call it before any arithmetic or CEAV selection.
- [ ] Re-run focused tests and both complete IMSS suites.

### Task 3: Protect public fiscal/catalog values

**Files:**
- Modify: `packages/typescript/tests/fiscal-manifest.test.ts`
- Modify: `packages/typescript/src/fiscal/index.ts`
- Create: `packages/python/catalogmx/fiscal.py`
- Create: `packages/python/tests/test_fiscal_manifest.py`
- Modify: `packages/python/pyproject.toml`
- Modify: `scripts/build_fiscal_manifest.py`

- [ ] Add TypeScript mutation tests proving a returned dataset/source cannot alter the next read.
- [ ] Add Python tests for list/get/status/source parity and wheel-contained manifest loading; verify imports fail before implementation:

```python
def test_fiscal_dataset_reads_are_defensive() -> None:
    first = get_fiscal_dataset("imss_ceav")
    first["verification"] = "mutated"
    assert get_fiscal_dataset("imss_ceav")["verification"] != "mutated"
```
- [ ] Make TypeScript return deeply frozen defensive values and add the equivalent Python read-only API.
- [ ] Define generator `TypedDict` records for dataset, source, and verification structures.
- [ ] Build a wheel, install it into a clean temporary environment, and run the manifest tests outside the checkout.

### Task 4: Repair the API Worker and CI gap

**Files:**
- Modify: `packages/api-worker/src/calculations.ts`
- Modify: `packages/api-worker/tests/calculations.test.ts`
- Modify: `.github/workflows/ci.yml`

- [ ] Add a test asserting rounded IMSS output retains `uma_diaria` and `ceav_patron_rate`; verify the API Worker typecheck/test fails first:

```typescript
expect(roundImssResult(input)).toMatchObject({ uma_diaria: 117.31, ceav_patron_rate: 0.07513 });
```
- [ ] Preserve and round both fields in `roundImssResult`.
- [ ] Add a blocking `api-worker` CI job running `npm ci && npm run validate`.
- [ ] Run API Worker validation, including Wrangler dry-run.

### Task 5: Make the unverified Modalidad 10 boundary visible

**Files:**
- Modify: `packages/webapp-svelte/src/routes/calculadoras/imss/+page.svelte`
- Create: `packages/webapp-svelte/scripts/check-imss-public-contract.mjs`
- Modify: `packages/webapp-svelte/package.json`

- [ ] Add a failing source-contract assertion that the public calculator does not offer or advertise Modalidad 10 as updated:

```js
assert.doesNotMatch(source, /value: 'modalidad10'/);
assert.doesNotMatch(source, /Cuotas actualizadas 2024-2026/);
assert.match(source, /pendiente de auditoría/i);
```

- [ ] Remove the selectable/calculated result and show a concise pending-audit notice linked to issue #97.
- [ ] Add `node scripts/check-imss-public-contract.mjs` to the webapp `check` script, then run `npm run check` and `npm run build`.

### Task 6: Document the 0.7 migration and package contracts

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.rst`
- Create: `docs/guides/v0.7-fiscal-migration.md`
- Modify: `packages/typescript/package.json`
- Modify: `.github/workflows/ci.yml`

- [ ] Document the explicit last-SBC Modalidad 40 call in Python and TypeScript, zone selection, date semantics, and the pending Modalidad 10 status.
- [ ] Add clean tarball tests for `require`, ESM import, and Cloudflare Worker bundling of root and `catalogmx/fiscal` exports.
- [ ] Run `npm pack --dry-run`, install the tarball in clean consumers, and verify all three package modes.

### Task 7: Replace Cronikos copied catalogs with package exports

**Files (Cronikos worktree):**
- Modify: `src/cronikos/catalogmx_nomina.cljs`
- Modify: `test/cronikos/catalogmx_nomina_test.cljs`
- Modify: `scripts/test-catalogmx-integration.sh`
- Modify: `package.json`
- Modify: `package-lock.json`

- [ ] Add a failing contract test requiring real `catalogmx/catalogs` and `catalogmx/cfdi` providers for representative Nómina and CFDI keys:

```clojure
(is (true? ((:valid? provider) :tipo-regimen "02")))
(is (false? ((:valid? provider) :tipo-regimen "XX")))
(is (= :catalogmx (:source provider)))
```
- [ ] Remove checked-in enumeration fallbacks and fail closed when the required package export is missing.
- [ ] Exercise audited IMSS response parsing for `uma_diaria` and `ceav_patron_rate`.
- [ ] Install the local packed 0.7 candidate and run Cronikos tests, integration test, release build, and Worker dry-run.

### Task 8: Prove PayGlobal catalog consumers

**Files (isolated PayGlobal worktrees):**
- Modify: `payglobal-core/tests/test_catalogs.py`
- Modify: `payglobal-core/pyproject.toml`
- Modify: `payglobal-core/uv.lock`
- Modify: `payglobal-crm/backend/onboarding/tests/test_account_validation.py`
- Modify: `payglobal-crm/backend/pyproject.toml`
- Modify: `payglobal-crm/backend/uv.lock`
- Modify: `payglobal-rails/tests/test_catalogs_coverage.py`
- Modify: `payglobal-rails/pyproject.toml`
- Modify: `payglobal-rails/uv.lock`

- [ ] Add or extend tests for RFC/CURP/CLABE validation, Banxico bank lookup, SPEI filtering, and immutable repeated reads using the candidate wheel. Representative immutability assertion:

```python
first = get_bank_by_code("012")
first["name"] = "mutated"
assert get_bank_by_code("012")["name"] != "mutated"
```

- [ ] Run tests first against the existing pinned/released dependency and record contract mismatches.
- [ ] Install the candidate wheel without copying source and make only the minimal consumer adaptations required.
- [ ] Run each focused suite and repository quality command; smoke-test GitOps and sandbox-bank imports without editing them unless a failure requires it.

### Task 9: Full verification and exact-head review

**Files:** All changed files only.

- [ ] Run `git diff --check` and every platform's formatter, linter, typecheck, test, build, and package dry-run.
- [ ] Rebuild npm/Python artifacts and repeat clean consumer tests.
- [ ] Run Standards and Spec reviews against the fixed base SHA.
- [ ] Run bounded multi-model reviews through `reviewctl`, verify every receipt, reproduce findings, and fix all verified critical/important findings.
- [ ] Push the reviewed head to PR #96 and require CI green on that exact SHA before merge.

### Task 10: Publish and verify 0.7.0

**Files:**
- Modify package version files and `CHANGELOG.rst` in a dedicated release change.

- [ ] Set Python, TypeScript, Dart, and Kotlin versions to `0.7.0` and verify consistency in preflight.
- [ ] Confirm PyPI trusted publishing and npm/pub.dev/Maven environment credentials without exposing secret values.
- [ ] Merge only after exact-head review and CI, create tag `v0.7.0`, and observe all publisher jobs.
- [ ] Install each artifact by version from its public registry and run its native smoke test.
- [ ] Advance Cronikos and PayGlobal dependencies to the published version, regenerate lockfiles, rerun consumer suites, and leave their local changes on isolated branches for review.
