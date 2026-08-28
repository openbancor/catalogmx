# Code lifecycle / data lifecycle migration

CatalogMX treats the language packages and runtime datasets as separate release domains.

## Package boundary

The Python wheel contains code, validators, catalog adapters and the generated `dataset_contract.json`. Mutable runtime datasets are not versioned by the wheel. In particular, the Banxico dynamic SQLite database is no longer an embedded package fallback.

## Runtime boundary

`DatasetResolver` owns:

- dataset discovery through stable release pointers;
- immutable artifact/manifest verification;
- content-addressed local caching;
- freshness evaluation;
- explicit fetch, refresh and offline policies;
- shared-root materialization for deployment.

`CATALOGMX_SHARED_DATA` remains the highest-priority strict override. This is the preferred application boundary for Kubernetes deployments using an init container or synchronization job.

## Compatibility APIs

Historical APIs may remain while consumers migrate, but compatibility must be implemented as a facade over the common resolver contract rather than as a second downloader/cache lifecycle.

The Python `DataUpdater` API is the first completed example: it retains the historical entry points for Banxico time-series callers while delegating runtime data resolution to `banxico.sie_dynamic`.

## Explicit controls

- `catalogmx fetch --profile <profile>` explicitly synchronizes a profile;
- `catalogmx data fetch ...` remains the structured equivalent;
- `CATALOGMX_CACHE_TTL=86400` sets a 24-hour operational TTL override;
- `CATALOGMX_DATA_MODE=fetch-missing` only fetches absent data;
- `CATALOGMX_DATA_MODE=refresh` evaluates TTL/freshness;
- `CATALOGMX_DATA_MODE=offline` prohibits network access.

## Remaining consumer cutover

Resolver-ready SAT/INEGI/SEPOMEX artifacts already have independent publication lifecycles. Some historical Python convenience loaders still read repository compatibility views. Their migration is a consumer-adapter concern: they should translate canonical resolver artifacts into the existing public return shapes without reintroducing package-data or independent cache mechanisms.
