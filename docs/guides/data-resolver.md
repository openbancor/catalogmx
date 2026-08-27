# Dataset resolver and profiles

CatalogMX versions code and data independently. Reference/regulatory datasets can therefore change without forcing a Python, TypeScript, Dart, or Kotlin package release.

This guide documents the first runtime implementation of that model: Python consumers using the `core`, `payglobal`, and `payglobal-e2e` profiles with the independently published `banxico.reference` dataset.

## Resolution model

Importing CatalogMX does not fetch data. Resolution occurs when a consumer actually accesses a catalog that needs an external dataset or when the data CLI is invoked.

For a dataset-aware lookup, the effective precedence is:

1. `CATALOGMX_SHARED_DATA` — strict application/production override;
2. local content-addressed CatalogMX cache;
3. deliberately embedded package data, when a dataset is actually packaged;
4. repository `packages/shared-data` layout during development;
5. verified GitHub Release fetch when the selected data mode permits it.

A configured `CATALOGMX_SHARED_DATA` is fail-closed. If the directory or requested dataset is missing, CatalogMX reports that configuration error instead of silently reaching the network.

Legacy calls such as `get_shared_data_path("banxico", "banks.json")` retain local/repository behavior and bridge to `banxico.reference` only when no local shared-data path exists. This keeps current SDK APIs compatible while removing installed-wheel assumptions about repository paths or symlinks.

## Data modes

Set `CATALOGMX_DATA_MODE` to one of:

- `offline` — never fetch; require the configured root or a populated cache;
- `fetch-missing` — default; use available local/cache data and fetch a missing dataset;
- `refresh` — refresh a stale cached dataset according to the registry freshness SLA.

A refresh that cannot reach the release channel may continue using an already verified cached object. A missing dataset has no synthetic or unverified fallback.

## Integrity model

`banxico.reference` is published as `banxico_reference.tar.gz` with `banxico_reference.manifest.json`.

The resolver downloads the manifest first, then:

1. validates dataset id, version, expected artifact name, and manifest schema;
2. verifies the complete artifact SHA-256;
3. allows only manifest-declared regular archive members;
4. rejects absolute paths, `..` traversal, duplicate or unexpected members;
5. verifies every extracted file SHA-256;
6. stores the result under a semantic `content_sha256` object directory;
7. atomically updates the current-cache pointer only after verification succeeds.

The release builder normalizes tar/gzip metadata, so identical reviewed source bytes create identical artifacts. `content_sha256` is computed from canonical JSON semantics, so whitespace-only source changes do not create a new semantic data version.

The mutable `data-banxico-reference-1-latest` tag is a discovery channel. The publishing workflow also creates an immutable tag containing the first 16 characters of the semantic content hash. Runtime integrity never depends on mutable `master` content.

## Profiles

The canonical registry currently exposes:

| Profile | Datasets | Purpose |
| --- | --- | --- |
| `core` | none | Pure validators/calculators with no external data requirement |
| `payglobal` | `banxico.reference` | Bank/routing data used by runtime services |
| `payglobal-e2e` | `banxico.reference` | Runtime data plus identity/CLABE generation references such as `codigos_plaza.json` |

The wheel contains a generated `dataset_contract.json` projection of these registry fields. CI requires that projection to match the canonical registry exactly.

## CLI

Inspect the local state:

```bash
catalogmx data status --profile payglobal
catalogmx data cache info --profile payglobal
```

Fetch into the normal user cache:

```bash
catalogmx data fetch --profile payglobal
```

Force synchronization of a dataset:

```bash
catalogmx data update --dataset banxico.reference
```

Verify the populated cache without network access:

```bash
CATALOGMX_DATA_MODE=offline catalogmx data verify --profile payglobal
```

Clear one cached dataset:

```bash
catalogmx data cache clear --dataset banxico.reference
```

## Kubernetes / production

Production services should normally synchronize data before application startup rather than letting every pod fetch independently.

An init container or deployment job can materialize a conventional shared-data root:

```bash
catalogmx data fetch --profile payglobal --dest /var/lib/catalogmx
```

Application containers then mount that directory read-only and use:

```text
CATALOGMX_SHARED_DATA=/var/lib/catalogmx
CATALOGMX_DATA_MODE=offline
```

This makes startup deterministic and removes GitHub availability from the request-serving path. The materialized directory also contains `.catalogmx/manifests/` so the exact release metadata can be retained alongside the runtime data.

## Environment variables

- `CATALOGMX_SHARED_DATA` — strict shared-data root override;
- `CATALOGMX_CACHE_DIR` — cache root (default `~/.cache/catalogmx`);
- `CATALOGMX_DATA_MODE` — `offline`, `fetch-missing`, or `refresh`;
- `CATALOGMX_RELEASE_BASE_URL` — release base override, primarily for mirrors/tests.

## Publishing boundary

The monthly catalog-maintenance workflow may discover a Banxico reference change and open a normal data PR. It does **not** publish that unreviewed workspace state as a runtime artifact.

After reviewed Banxico data lands on `master`, `publish-reference-data.yml` rebuilds the bundle from the committed source. It publishes only when semantic content changed. This separates upstream observation, human/repository review, and runtime distribution.

## Next migration phases

The same manifest/resolver contract will be extended to SAT and geo profiles, then the existing Banxico dynamic time-series updater will be expressed through the common dataset metadata model. Existing compatibility blobs remain until their SDK consumers have migrated and installed-package tests prove they are no longer required.
