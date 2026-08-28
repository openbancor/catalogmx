# Code lifecycle / data lifecycle migration

CatalogMX treats the language packages and runtime datasets as separate release domains.

## Package boundary

The Python wheel contains code, validators, catalog adapters and the generated `dataset_contract.json`. Mutable runtime datasets are independently versioned and canonical releases never depend on the wheel version. The Python wheel retains one explicitly declared Banxico dynamic SQLite bootstrap snapshot only as a non-canonical offline/first-run failure fallback.

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


## Bootstrap semantics

The Banxico dynamic bootstrap exists for compatibility and zero-network startup, but it does not participate in freshness or release identity. Resolution prefers `CATALOGMX_SHARED_DATA`, then a verified content-addressed cache. In normal `fetch-missing`/`refresh` operation the resolver still attempts the verified immutable release before considering bootstrap. Bootstrap is used when `offline` has no better source, or when a first remote fetch fails and no verified cache exists. Explicit `catalogmx fetch` remains a synchronization operation and therefore fails if it cannot fetch and verify the requested release.
