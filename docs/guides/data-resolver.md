# Dataset resolver and independent data lifecycle

CatalogMX versions code and runtime data independently. Language packages contain code, validators and the generated dataset contract; mutable regulatory/reference datasets are independently versioned artifacts.

The Python runtime uses `DatasetResolver` as the common boundary for Banxico reference and dynamic data, SAT, INEGI, SEPOMEX, CONAPO and IFT datasets. Importing `catalogmx` performs no network I/O.

## Resolution model

Resolution occurs on explicit fetch or first access to a dataset-aware API. The precedence is:

1. `CATALOGMX_SHARED_DATA` — strict application/production override;
2. verified local content-addressed cache;
3. deliberately packaged data, only when a dataset contract explicitly retains such a compatibility source;
4. repository `packages/shared-data` layout for development compatibility;
5. verified immutable release fetch when the configured data mode permits it.

`CATALOGMX_SHARED_DATA` is fail-closed. If it is configured but the requested mount is missing, CatalogMX reports the deployment error instead of silently contacting GitHub.

## Data modes

`CATALOGMX_DATA_MODE` is explicit:

- `offline` — never use the network;
- `fetch-missing` — default; fetch only when no usable local dataset exists;
- `refresh` — use the dataset freshness policy and refresh stale verified cache entries.

`fetch-missing` deliberately does **not** become `refresh` when a cache entry ages. The modes are separate operational policies.

A refresh failure may fall back to a previously verified cached object. Missing, corrupt or unverified data has no synthetic fallback.

## Cache freshness and TTL

Each dataset declares its normal freshness SLA in `catalog-registry.json`. The generated runtime contract carries that policy to the resolver.

`CATALOGMX_CACHE_TTL` is an optional operational override expressed in positive integer **seconds**. For example:

```text
CATALOGMX_CACHE_TTL=86400
```

sets a 24-hour cache TTL for the resolver instance. When absent, the dataset-specific registry SLA remains authoritative. The TTL controls staleness and therefore `refresh`; it does not change `fetch-missing` into an implicit refresh policy.

The Python API may also pass `cache_ttl_seconds=` directly to `DatasetResolver`.

## Artifact integrity and discovery

Resolver-ready datasets use a stable release channel only for discovery. Its body is a small JSON pointer to a content-addressed immutable release.

The immutable release owns the artifact and manifest. Before cache state changes, the resolver validates:

1. pointer schema, dataset identity/version, filenames and semantic hash;
2. immutable manifest identity and artifact metadata;
3. pointer/manifest semantic-hash agreement;
4. complete artifact SHA-256;
5. declared archive members or file shape;
6. extracted/member checksums and safe paths where applicable.

Valid content is installed below a semantic `content_sha256` object directory and `current.json` is updated atomically only after verification. Concurrent cold-cache installation is race-tolerant and never intentionally overwrites a valid concurrent winner.

Publication uses the inverse protocol: build from reviewed input, publish immutable content, verify it, then move the stable pointer last. A failed publication therefore cannot replace the previous known-good channel target.

## Profiles

Profiles are synchronization conveniences, not Python dependency extras. Current examples include:

- `core` — no external datasets;
- `payglobal` / `payglobal-e2e` — `banxico.reference`;
- `banxico-dynamic` — `banxico.sie_dynamic`;
- `sat-cfdi`, `sat-carta-porte`, `sat-comercio-exterior`, `sat-nomina`;
- `mexico-geo` — AGEEML, SEPOMEX and CONAPO territorial data;
- `mexico-telecom` — IFT numbering reference data.

The wheel contains `catalogmx/data/dataset_contract.json`, generated from `catalog-registry.json`. CI requires that projection to remain synchronized with the canonical registry.

## CLI

The original explicit-fetch surface is available directly:

```bash
catalogmx fetch --profile payglobal
```

The structured data CLI remains available and is equivalent for fetching:

```bash
catalogmx data fetch --profile payglobal
catalogmx data status --profile payglobal
catalogmx data update --dataset banxico.sie_dynamic
catalogmx data verify --profile payglobal
catalogmx data cache info --profile payglobal
catalogmx data cache clear --dataset banxico.reference
```

Use `--dest` to materialize a conventional shared root:

```bash
catalogmx fetch --profile payglobal --dest /var/lib/catalogmx
```

## Legacy `DataUpdater`

`DataUpdater`, `get_database_path()` and `update_now()` remain public compatibility APIs for Banxico time-series consumers. They no longer implement a second downloader/cache/version protocol: they delegate to `DatasetResolver` for `banxico.sie_dynamic`.

The dynamic SQLite database is therefore not a code-wheel fallback. Offline use requires a verified resolver cache or `CATALOGMX_SHARED_DATA`.

Historical `max_age_hours=24` arguments are translated to resolver TTL seconds, preserving the old API while keeping one runtime data mechanism.

## Kubernetes / production

Production should normally synchronize data before request-serving containers start:

```text
init container / deployment job
    -> catalogmx fetch --profile payglobal --dest /var/lib/catalogmx
application containers
    -> CATALOGMX_SHARED_DATA=/var/lib/catalogmx
    -> CATALOGMX_DATA_MODE=offline
    -> /var/lib/catalogmx mounted read-only
```

This keeps GitHub out of the request-serving path and makes startup deterministic. `.catalogmx/manifests/` in a materialized root retains exact release metadata alongside the mounted data.

## Environment variables

- `CATALOGMX_SHARED_DATA` — strict shared-data root override and highest-priority runtime source;
- `CATALOGMX_CACHE_DIR` — local content-addressed cache root;
- `CATALOGMX_CACHE_TTL` — optional positive TTL override in seconds;
- `CATALOGMX_DATA_MODE` — `offline`, `fetch-missing`, or `refresh`;
- `CATALOGMX_RELEASE_BASE_URL` — immutable release asset base override for mirrors/tests;
- `CATALOGMX_RELEASE_METADATA_BASE_URL` — stable pointer metadata base override.

## Architectural invariant

The intended boundary is:

> **CatalogMX packages code, schemas/contracts and behavior. Runtime datasets have independent identity, provenance, freshness policy and immutable artifacts. Every data-consuming API should ultimately resolve through the same dataset contract, regardless of whether the bytes come from a local cache, a Kubernetes shared volume or a remote release.**

Compatibility loaders may temporarily translate historical API shapes, but they must not introduce a second distribution or cache lifecycle.
