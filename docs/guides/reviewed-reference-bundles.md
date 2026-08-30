# Reviewed reference bundles: CONAPO and IFT

CatalogMX distinguishes **authority refresh** from **runtime distribution**. Some small reference datasets in the repository are reviewed compatibility views: they preserve useful CatalogMX normalization or enrichment, but they are not claimed to be byte-for-byte exports from the public authority.

For these datasets, the runtime release is built only from reviewed files already present on `master`. The builder does not scrape the authority and does not mutate the source snapshot.

## `conapo.territorial`

The runtime bundle contains:

- `conapo/sun_2020.csv`
- `conapo/municipios_tipologia.csv`

They represent the reviewed CatalogMX views for Sistema Urbano Nacional 2020 and Metrópolis de México 2020. CONAPO/SEDATU/INEGI publications remain the authority boundary; a future source refresh must be reviewed before it changes the tracked views.

Runtime contract:

- version: `2020`
- channel: `data-conapo-territorial-2020-latest`
- artifact: `conapo_territorial.tar.gz`
- manifest: `conapo_territorial.manifest.json`
- mount path: `conapo`

The stable channel is pointer-only. The immutable content-addressed release contains the bundle and manifest.

## `ift.numbering`

The runtime bundle contains:

- `ift/codigos_lada.json`
- `ift/operadores_moviles.json`
- `ift/operadores_pnn.json`

The IFT Sistema Nacional de Numeración is authoritative for numbering assignments. The tracked CatalogMX JSON files also contain compatibility enrichments such as INEGI mappings, metropolitan overlays, and convenience operator fields. The release therefore describes itself as a reviewed compatibility snapshot rather than as a one-to-one IFT export.

Runtime contract:

- version: `1`
- channel: `data-ift-numbering-1-latest`
- artifact: `ift_numbering.tar.gz`
- manifest: `ift_numbering.manifest.json`
- mount path: `ift`

`packages/shared-data/sqlite/prefijos_telefonicos.db` remains a legacy repository snapshot. No current Python runtime loader consumes it, and it is intentionally **not** part of the reviewed runtime bundle. It should be audited or retired separately rather than silently promoted into the canonical runtime artifact.

## Deterministic build contract

`scripts/build_reviewed_reference.py` fails closed if the reviewed namespace changes. It canonicalizes JSON semantically, normalizes text line endings, writes deterministic tar/gzip metadata, and records:

- dataset id and version;
- artifact SHA-256;
- semantic content SHA-256;
- exact mount path;
- per-file paths, sizes, and SHA-256 values.

The common `DatasetResolver` validates the pointer, immutable release tag, manifest contract, artifact checksum, safe extraction paths, exact extracted namespace, and per-file checksums before promoting a dataset into the local cache.

## Python runtime resolution

The CONAPO and IFT catalog loaders use `get_shared_data_path()` instead of calculating repository-relative paths. Resolution therefore follows the common policy:

1. explicit `CATALOGMX_SHARED_DATA` override;
2. resolver cache;
3. deliberate package-local fallback when one exists;
4. repository layout for development;
5. optional verified release fetch when the configured mode allows it.

Importing `catalogmx` performs no network I/O. Fetching occurs only when a data-backed API is accessed or the CLI/resolver is asked to fetch a dataset/profile.

Profiles introduced/extended by this migration:

- `mexico-geo` includes `conapo.territorial` in addition to the existing geographic datasets;
- `mexico-telecom` resolves `ift.numbering`.

## Production model

Production services should normally prefetch profiles into a mounted data root and run applications with `CATALOGMX_SHARED_DATA` pointing at that read-only root. Runtime fetch remains useful for development and CI, but it is not required for Kubernetes application pods.
