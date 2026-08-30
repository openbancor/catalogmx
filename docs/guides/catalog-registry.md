# Catalog Registry and Data Provenance

`catalogmx` contains reference data with very different lifecycles: fiscal catalogs, geographic classifications, banking reference data, regulatory parameters, and daily financial time series. Treating all of them as a single static bundle makes it difficult to know what exists, where it came from, and whether it is still current.

`packages/shared-data/catalog-registry.json` is the canonical metadata registry for catalog maintenance. The existing `.catalog-versions.json` remains temporarily as a legacy compatibility manifest for `scripts/check_catalog_updates.py`; it must not be used as evidence that the repository inventory is current.

## Registry responsibilities

The registry describes four separate facts that were previously conflated:

1. **Inventory** — which dataset families catalogmx manages and which local artifacts implement them.
2. **Provenance** — the authority and authoritative upstream artifacts or portals.
3. **Distribution** — whether data is embedded in packages, published independently as a data release, or optional.
4. **Freshness** — how often upstream should be checked and when it was actually verified.

A file existing in the repository only proves inventory. It does **not** prove that the data is current.

## Dataset kinds

- `reference`: identifiers, code lists, geographic catalogs, and similar master data whose identity is primarily the current authoritative set.
- `classification`: explicitly versioned taxonomies/classification systems, such as SCIAN 2023, where edition identity and migration between editions are part of the data contract.
- `regulatory_parameters`: tables or values whose meaning depends on fiscal, labor, or regulatory rules.
- `time_series`: observations that change continuously or on a regular schedule.
- `derived`: reproducible datasets produced from another authoritative dataset.

A classification can still be reference data in the broad domain sense, but the separate registry kind prevents a versioned taxonomy from accidentally inheriting the refresh policy of a continuously maintained master-data catalog from the same authority.

## Status and distribution

`managed` means catalogmx currently materializes the dataset. `planned` means the dataset is intentionally registered but is not yet materialized. `legacy` is reserved for data being retired or migrated.

Distribution is independent from status:

- `embedded`: ships with one or more catalogmx packages/assets.
- `release`: published independently from the library release cycle.
- `optional`: downloaded or materialized only when requested.
- `mixed`: more than one of the above mechanisms is intentional.

This distinction is important for large datasets. A dataset can be part of the catalogmx data model without being bundled into every Python, TypeScript, Dart, or Kotlin package.

## Freshness modes

- `interval`: upstream should be explicitly checked within `max_age_days`.
- `pipeline`: an automated workflow owns freshness; the registry records that workflow.
- `event`: the source changes through irregular official editions or releases.
- `manual`: an explicit human/source review is required.

`upstream_checked_at` means that the authoritative source was actually reviewed. Do not update it merely because code was touched or a local database was rebuilt.

## Derived datasets and DENUE

DENUE is intentionally modeled as `inegi.denue.filtered`, a **derived filtered view**, not as a complete mirror of the national directory.

A derived dataset must preserve enough information to reproduce it from the authoritative upstream source. Before DENUE can move from `planned` to `managed`, its `derivation.filter_spec` must define the filter unambiguously. The registry also records that the full upstream DENUE dataset is not retained in catalogmx core.

A future materialization should record at least:

- upstream DENUE edition/cut and source checksum when available;
- exact filter specification and its version;
- transformation code version;
- output checksum and record count;
- effective/source date separately from generation date.

This same pattern applies to other useful subsets of very large government datasets.

## CLI

Validate registry structure and local paths:

```bash
python scripts/catalog_registry.py validate
```

Audit freshness without failing merely because source reviews are due:

```bash
python scripts/catalog_registry.py audit
```

Machine-readable audit:

```bash
python scripts/catalog_registry.py audit --json
```

Once a maintenance lane has reliable source adapters, it can enforce its freshness SLA with:

```bash
python scripts/catalog_registry.py audit --fail-on-due
```

The bootstrap registry intentionally starts with unknown `upstream_checked_at` values for source families that have not yet been re-audited. This makes stale knowledge visible instead of silently converting repository age into regulatory provenance.

## Migration plan

The migration from `.catalog-versions.json` should be incremental:

1. Register the real local inventory and validate it in CI.
2. Re-resolve each authoritative upstream source and record a real source check.
3. Add source-specific fetch/parse/diff adapters.
4. Archive raw upstream artifacts or checksums where licensing and size allow.
5. Generate normalized artifacts and human-readable diffs.
6. Publish dynamic/large datasets independently from semantic library releases.
7. Retire `.catalog-versions.json` and the hard-coded legacy checker when all source families have migrated.

The registry is metadata, not a second copy of the data. Dataset-specific schemas remain with their normalized artifacts and language adapters.