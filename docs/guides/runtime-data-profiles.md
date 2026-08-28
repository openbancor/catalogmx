# Runtime data profiles

CatalogMX keeps language-package releases separate from independently versioned regulatory and reference datasets. Runtime consumers request datasets or profiles through `DatasetResolver` instead of treating tracked compatibility snapshots as the distribution mechanism.

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
| `mexico-geo` | `inegi.ageeml`, `sepomex.codigos_postales`, `conapo.territorial` | National locality, postal and territorial reference data. |
| `mexico-telecom` | `ift.numbering` | Reviewed IFT numbering compatibility reference data. |

## Publication contract

Each resolver-ready dataset declares a stable metadata channel in `catalog-registry.json`. The channel is pointer-only and identifies one content-addressed immutable release. That immutable release contains the manifest and artifact. The manifest identifies the dataset/version and records the artifact filename, `format`, `mount_path`, binary SHA-256 and semantic content SHA-256.

`DatasetResolver` resolves the pointer, validates it against the generated runtime contract, verifies immutable bytes, materializes the declared mount path and only then commits local cache state. Scheduled maintenance and push publication use the common transactional publisher so moving the stable pointer remains the last publication mutation.

## Runtime policy

- `CATALOGMX_SHARED_DATA` is the strict highest-priority source for deployment/Kubernetes mounts.
- `fetch-missing` is the default and only reaches the network when a requested dataset is absent.
- `refresh` evaluates cache freshness and can update a stale verified object.
- `offline` prohibits network resolution.
- `CATALOGMX_CACHE_TTL` optionally overrides the registry freshness SLA in positive integer seconds; `86400` means 24 hours.

The explicit synchronization command can be written either as:

```bash
catalogmx fetch --profile mexico-geo
```

or through the structured namespace:

```bash
catalogmx data fetch --profile mexico-geo
```

## Compatibility boundary

A resolver-ready canonical artifact does not automatically mean every historical convenience API has completed its runtime cutover. During migration, tracked JSON or other compatibility views may remain in the repository for source review and cross-SDK compatibility, but they are not the canonical independent distribution channel.

Important boundaries:

- `sat-comercio-exterior` resolves `sat.cfdi_4` alongside the CCE-owned artifact rather than duplicating four shared CFDI catalogs.
- Carta Porte's canonical release is the complete 32-table `ccp_31_*` family; its smaller JSON directory is a compatibility projection.
- AGEEML and SEPOMEX releases are fail-closed national datasets; synthetic/partial data cannot replace a verified canonical release.
- Nómina runtime identity is `1.2-revision-e`, not merely `1.2`.
- CONAPO and IFT reviewed bundles explicitly preserve CatalogMX compatibility/enrichment semantics instead of claiming to be raw authority exports.
- Banxico dynamic data keeps an explicitly declared non-canonical wheel bootstrap for offline/first-fetch failure compatibility. The historical `DataUpdater` API still delegates to `DatasetResolver`; normal online resolution and freshness use the independent release/cache contract.

### Python Nómina consumer cutover

The Python Nómina 1.2 public catalog classes now terminate at `DatasetResolver` and read the canonical `sat_nomina_12.sqlite3` artifact. `BancoCatalog`, `PeriodicidadPagoCatalog`, `RiesgoPuestoCatalog` and the other ten public Nómina catalog classes keep their historical method names, return aliases and lazy-loading behavior; only the runtime source changed.

Two convenience fields are intentionally code-owned CatalogMX enrichments rather than SAT artifact columns: payment-period `days`, and the risk-class `prima_minima` / `prima_media` / `prima_maxima` values. Keeping those mappings explicit separates CatalogMX behavior from authority-owned rows without requiring a second runtime data lifecycle.

The tracked `packages/shared-data/sat/nomina_1.2/*.json` views remain for source review and SDK compatibility while other consumers migrate. Python does **not** use them as a runtime fallback: missing tables, invalid identifiers or resolver/integrity failures remain fail-closed. Installed-wheel CI builds a local verified Nómina release and exercises all 13 public Python catalog classes without packaging the shared-data JSON tree.

### Python CFDI 4.0 consumer cutover

Thirteen coherent Python CFDI 4.0 catalog surfaces now read the canonical `sat_cfdi_40.sqlite3` artifact through `DatasetResolver`: exportación, forma y método de pago, objeto de impuesto, tipo de relación, tipo de comprobante, impuestos, régimen fiscal, uso CFDI, meses, periodicidad, tipo factor and clave de unidad. Their existing public classes and historical dictionary shapes remain stable while authority-owned values come from the current independent release.

Compatibility projection is explicit rather than implicit JSON fallback. For example, `UsoCFDICatalog` derives `applies_to` from the canonical physical/moral applicability flags, `ImpuestoCatalog` retains CatalogMX's long tax-name convenience labels, and `ClaveUnidadCatalog` preserves its historical `DD-MM-YYYY` presentation while using the canonical release's current vigencia values. The tracked `packages/shared-data/sat/cfdi_4.0/*.json` files remain cross-SDK/source-review views and are not a Python runtime source for these migrated consumers.

`TasaOCuota` is deliberately excluded from this cutover. Its historical loader reads a raw spreadsheet-shaped JSON export while `get_by_range_and_tax()` expects normalized keys that those rows do not contain. That pre-existing API inconsistency is handled as a separate bug-fix slice against canonical `cfdi_40_reglas_tasa_cuota` rather than being silently redefined inside the lifecycle migration.

Deterministic tests exercise the migrated APIs against a local `CATALOGMX_SHARED_DATA` SQLite mount, and installed-wheel CI exercises the same public surfaces through a verified release-pointer/cache path without packaging the shared-data JSON tree.

The remaining consumer migration rule is simple: public catalog APIs may translate canonical datasets into historical return shapes, but they must ultimately obtain runtime data from `DatasetResolver` rather than create another downloader, cache or package-data lifecycle.
