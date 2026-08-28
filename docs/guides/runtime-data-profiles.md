# Runtime data profiles

CatalogMX keeps language-package releases separate from independently versioned regulatory and reference datasets. Runtime consumers should request a profile through `catalogmx.data.DatasetResolver` instead of depending on legacy embedded JSON snapshots.

## Resolver-ready profiles

| Profile | Datasets | Purpose |
| --- | --- | --- |
| `core` | none | Pure validators/calculators without external data. |
| `payglobal` | `banxico.reference` | Bank and routing reference data. |
| `payglobal-e2e` | `banxico.reference` | PayGlobal reference data for end-to-end usage. |
| `banxico-dynamic` | `banxico.sie_dynamic` | Independently refreshed Banxico SIE time series. |
| `sat-cfdi` | `sat.cfdi_4` | Canonical CFDI 4.0 catalogs. |
| `sat-carta-porte` | `sat.carta_porte` | Canonical Carta Porte 3.1 catalogs. |
| `sat-comercio-exterior` | `sat.cfdi_4`, `sat.comercio_exterior` | CCE 2.0-owned catalogs plus its shared CFDI 4.0 dependency. |
| `sat-nomina` | `sat.nomina_1_2` | Canonical Nómina 1.2 revision E catalogs. |
| `mexico-geo` | `inegi.ageeml`, `sepomex.codigos_postales` | National locality and postal reference data. |

## Publication contract

Each resolver-ready dataset declares a stable metadata channel in `catalog-registry.json`. The channel body points to one content-addressed immutable release. That release contains exactly one manifest and one artifact; the manifest identifies the dataset/version and records the artifact filename, `format`, `mount_path`, binary SHA-256 and semantic content SHA-256.

`DatasetResolver` resolves the channel pointer, validates the manifest against the checked-in runtime contract, verifies downloaded bytes, materializes the content under its declared mount path, and only then commits local cache state. Scheduled maintenance and push publication both use `scripts/publish_dataset_release.sh`, so moving the stable pointer is the last publication mutation.

## Compatibility boundary

The existing embedded SAT, INEGI and SEPOMEX views remain compatibility data while consumers migrate. They are not the canonical runtime source for the profiles above. In particular:

- `sat-comercio-exterior` intentionally resolves `sat.cfdi_4` alongside the CCE-owned artifact instead of duplicating the four shared CFDI catalogs.
- Carta Porte's canonical release is the complete 32-table `ccp_31_*` family; the smaller embedded JSON directory is only a convenience projection.
- AGEEML and SEPOMEX releases are fail-closed national datasets. Synthetic or partial fallback data must never replace a successfully verified canonical release.
- Nómina uses dataset contract version `1.2-revision-e`; the revision is part of runtime identity and must not be collapsed to `1.2`.

Consumers can pin `CATALOGMX_DATA_MODE=offline` to prohibit network fetches, use the default `fetch-missing` mode, or use `refresh` when freshness policy should be checked against the stable release channel.
