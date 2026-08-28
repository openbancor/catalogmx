# Code lifecycle / data lifecycle migration

CatalogMX treats the language packages and runtime datasets as separate release domains.

## Package boundary

The Python wheel contains code, validators, catalog adapters and the generated `dataset_contract.json`. Canonical runtime datasets are independently versioned and never derive their identity or freshness from the wheel version.

The wheel retains one explicitly declared Banxico dynamic SQLite bootstrap snapshot because zero-network startup is useful. That snapshot is non-canonical: it does not participate in release identity or freshness and it never suppresses a normal verified remote fetch.

## Runtime boundary

`DatasetResolver` owns:

- dataset discovery through stable release pointers;
- immutable artifact/manifest verification;
- content-addressed local caching;
- freshness evaluation;
- explicit fetch, refresh and offline policies;
- shared-root materialization for deployment.

The effective runtime precedence is:

1. `CATALOGMX_SHARED_DATA` as the strict operator-controlled override;
2. a verified content-addressed cache;
3. development-only repository compatibility sources where the contract declares them;
4. the verified immutable release when network resolution is allowed;
5. an explicitly declared package bootstrap only for offline or first-fetch-failure fallback.

`CATALOGMX_SHARED_DATA` is fail-closed. If an operator configures it but the requested dataset is absent, CatalogMX reports the deployment error instead of silently selecting another source.

## Compatibility APIs

Historical APIs may remain while consumers migrate, but compatibility must be implemented as a facade over the common resolver contract rather than as a second downloader/cache lifecycle.

The Python `DataUpdater` API is the first completed example: it retains the historical entry points for Banxico time-series callers while delegating runtime data resolution to `banxico.sie_dynamic`. Historical `max_age_hours` values are translated into the common resolver TTL.

## Explicit controls

- `catalogmx fetch --profile <profile>` explicitly synchronizes a profile;
- `catalogmx data fetch ...` remains the structured equivalent;
- `CATALOGMX_CACHE_TTL=86400` sets a 24-hour operational TTL override;
- `CATALOGMX_DATA_MODE=fetch-missing` only fetches absent data;
- `CATALOGMX_DATA_MODE=refresh` evaluates TTL/freshness;
- `CATALOGMX_DATA_MODE=offline` prohibits network access.

`catalogmx fetch` is a synchronization operation. A bootstrap fallback does not make a failed explicit synchronization appear successful.

## Concrete examples

### First use with network access

```bash
export CATALOGMX_DATA_MODE=fetch-missing
export CATALOGMX_CACHE_TTL=86400

python - <<'PY'
from catalogmx.catalogs.banxico.udis_sqlite import UDICatalog

print(UDICatalog.get_actual())
PY
```

With no shared volume and an empty cache, `DatasetResolver` reads the stable `banxico.sie_dynamic` pointer, downloads the immutable manifest and `mexico_dynamic.sqlite3`, verifies their hashes, installs the object in the content-addressed cache, and the catalog queries that verified SQLite file. The packaged bootstrap is present but is not selected.

A second process sharing the same cache resolves the verified object locally without repeating the first-use download.

### Offline first use

```bash
export CATALOGMX_DATA_MODE=offline
export CATALOGMX_CACHE_DIR=/tmp/catalogmx-empty-cache
unset CATALOGMX_SHARED_DATA

python - <<'PY'
from catalogmx.data.updater import get_database_path

print(get_database_path(auto_update=False))
PY
```

If no verified cache exists, the resolver returns the explicitly declared package bootstrap. It remains compatibility data: it is not written into `current.json` and is not reported as a verified cached release.

If a verified cache already exists, that cache outranks the bootstrap even in offline mode.

### Network outage on first use

In `fetch-missing` mode CatalogMX first attempts the verified release. If the request fails and there is no verified cache, `banxico.sie_dynamic` may use its declared bootstrap. Once connectivity returns, an explicit synchronization performs a real fetch and verification:

```bash
catalogmx fetch --profile banxico-dynamic
```

After that, normal resolution uses the verified cached release rather than the bootstrap.

### Kubernetes / shared volume

A deployment job or init container synchronizes the data once:

```bash
catalogmx fetch --profile banxico-dynamic --dest /var/lib/catalogmx
```

Application pods mount the directory read-only and run with:

```bash
export CATALOGMX_SHARED_DATA=/var/lib/catalogmx
export CATALOGMX_DATA_MODE=offline
```

The pod resolves `/var/lib/catalogmx/dynamic/mexico_dynamic.sqlite3`. It does not contact GitHub, inspect a user cache, or use the package bootstrap. Release acquisition is therefore kept outside the request-serving path.

## Remaining consumer cutover

Resolver-ready SAT, INEGI, SEPOMEX, CONAPO, IFT and Banxico artifacts already have independent publication lifecycles. Some historical Python convenience loaders still read repository compatibility views. Their migration is a consumer-adapter concern: they should translate canonical resolver artifacts into the existing public return shapes without reintroducing package-data trees or independent cache mechanisms.
