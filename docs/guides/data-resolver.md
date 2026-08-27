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

A refresh that cannot reach the release channel may continue using an already verified cached object. A missing or corrupt dataset has no synthetic or unverified fallback. An explicit fetch/update repairs a corrupt cached object from the verified release.

## Integrity and publication model

`banxico.reference` is built as `banxico_reference.tar.gz` with `banxico_reference.manifest.json`.

Publication separates discovery from immutable data:

1. reviewed `master` data is rebuilt deterministically;
2. the complete artifact/manifest pair is published under a content-addressed immutable release tag;
3. the workflow downloads and byte-verifies both immutable assets;
4. only after that verification succeeds does it update the stable `data-banxico-reference-1-latest` release body;
5. that body is a small JSON pointer containing the immutable release tag and semantic content SHA-256.

The stable channel therefore owns no mutable artifact/manifest pair. If immutable publication or verification fails, the existing channel still points to the previous complete release. Runtime clients first read the channel metadata, then download both data assets from the immutable tag.

The resolver then:

1. validates the channel pointer schema, dataset id/version, release tag, filenames, and semantic hash;
2. validates the immutable manifest identity/version/artifact metadata;
3. requires the pointer and manifest semantic hashes to match;
4. verifies the complete artifact SHA-256;
5. allows only manifest-declared regular archive members;
6. rejects absolute paths, `..` traversal, duplicate/unexpected members, and symlinks;
7. verifies every extracted file size and SHA-256;
8. stores the result under a semantic `content_sha256` object directory;
9. atomically updates the current-cache state only after a valid object exists.

Cache object installation is race-tolerant. Concurrent processes sharing one cold cache may both prepare the same immutable object; once one process installs a valid object, the other treats that verified object as the successful outcome. Repair uses a unique quarantine rename for an invalid object and never intentionally overwrites a valid concurrent winner.

The bundle builder normalizes tar/gzip metadata, so identical reviewed source bytes create identical artifacts. `content_sha256` is computed from canonical JSON semantics, so whitespace-only source changes do not create a new semantic data version.

## Profiles

The canonical registry currently exposes:

| Profile | Datasets | Purpose |
| --- | --- | --- |
| `core` | none | Pure validators/calculators with no external data requirement |
| `payglobal` | `banxico.reference` | Bank/routing data used by runtime services |
| `payglobal-e2e` | `banxico.reference` | Runtime data plus identity/CLABE generation references such as `codigos_plaza.json` |

The wheel contains a generated `dataset_contract.json` projection of registry metadata. Datasets published only from reviewed `master` are projected with `discovery: release-pointer`, keeping transport behavior derived from the canonical lifecycle contract rather than duplicated manually. CI requires the checked-in projection to match the registry exactly.

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

Force synchronization or repair of a dataset:

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

This makes startup deterministic and removes GitHub availability from the request-serving path. The materialized directory also contains `.catalogmx/manifests/` so exact immutable release metadata can be retained alongside runtime data.

## Environment variables

- `CATALOGMX_SHARED_DATA` — strict shared-data root override;
- `CATALOGMX_CACHE_DIR` — cache root (default `~/.cache/catalogmx`);
- `CATALOGMX_DATA_MODE` — `offline`, `fetch-missing`, or `refresh`;
- `CATALOGMX_RELEASE_BASE_URL` — immutable release asset base override, primarily for mirrors/tests;
- `CATALOGMX_RELEASE_METADATA_BASE_URL` — release-metadata API base override for the stable pointer channel.

## Publishing boundary

The monthly catalog-maintenance workflow may discover a Banxico reference change and open a normal data PR. It does **not** publish that unreviewed workspace state as a runtime artifact.

After reviewed Banxico data lands on `master`, `publish-reference-data.yml` rebuilds the bundle from committed source. It publishes only when semantic content changed. This separates upstream observation, repository review, immutable runtime distribution, and the final stable-channel pointer update.

## Next migration phases

The same manifest/resolver contract will be extended to SAT and geo profiles, then the existing Banxico dynamic time-series updater will be expressed through the common dataset metadata model. Existing compatibility blobs remain until their SDK consumers have migrated and installed-package tests prove they are no longer required.
