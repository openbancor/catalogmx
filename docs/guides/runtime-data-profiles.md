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
- Carta Porte's canonical release is the complete 32-table `ccp_31_*` family. The smaller tracked JSON directory contains legacy compatibility/enrichment views and is not a complete or schema-equivalent mirror of the SAT 3.1 artifact.
- AGEEML and SEPOMEX releases are fail-closed national datasets; synthetic/partial data cannot replace a verified canonical release.
- Nómina runtime identity is `1.2-revision-e`, not merely `1.2`.
- CONAPO and IFT reviewed bundles explicitly preserve CatalogMX compatibility/enrichment semantics instead of claiming to be raw authority exports.
- Banxico dynamic data keeps an explicitly declared non-canonical wheel bootstrap for offline/first-fetch failure compatibility. The historical `DataUpdater` API still delegates to `DatasetResolver`; normal online resolution and freshness use the independent release/cache contract.

### Python Nómina consumer cutover

The Python Nómina 1.2 public catalog classes now terminate at `DatasetResolver` and read the canonical `sat_nomina_12.sqlite3` artifact. `BancoCatalog`, `PeriodicidadPagoCatalog`, `RiesgoPuestoCatalog` and the other ten public Nómina catalog classes keep their historical method names, return aliases and lazy-loading behavior; only the runtime source changed.

Two convenience fields are intentionally code-owned CatalogMX enrichments rather than SAT artifact columns: payment-period `days`, and the risk-class `prima_minima` / `prima_media` / `prima_maxima` values. Keeping those mappings explicit separates CatalogMX behavior from authority-owned rows without requiring a second runtime data lifecycle.

The tracked `packages/shared-data/sat/nomina_1.2/*.json` views remain for source review and SDK compatibility while other consumers migrate. Python does **not** use them as a runtime fallback: missing tables, invalid identifiers or resolver/integrity failures remain fail-closed. Installed-wheel CI builds a local verified Nómina release and exercises all 13 public Python catalog classes without packaging the shared-data JSON tree.

### Python CFDI 4.0 consumer cutover

The fourteen Python CFDI 4.0 compatibility surfaces that historically depended on tracked JSON now read the canonical `sat_cfdi_40.sqlite3` artifact through `DatasetResolver`: exportación, forma y método de pago, objeto de impuesto, tipo de relación, tipo de comprobante, impuestos, régimen fiscal, uso CFDI, meses, periodicidad, tipo factor, clave de unidad and tasa o cuota. Their existing public classes and historical dictionary conventions remain stable where those conventions were functional, while authority-owned values come from the current independent release.

Compatibility projection is explicit rather than implicit JSON fallback. For example, `UsoCFDICatalog` derives `applies_to` from the canonical physical/moral applicability flags, `ImpuestoCatalog` retains CatalogMX's long tax-name convenience labels, and `ClaveUnidadCatalog` preserves its historical `DD-MM-YYYY` presentation while using the canonical release's current vigencia values. The tracked `packages/shared-data/sat/cfdi_4.0/*.json` files remain cross-SDK/source-review views and are not a Python runtime source for these consumers.

`TasaOCuota` now fixes the pre-existing mismatch between its raw spreadsheet-shaped JSON loader and the normalized fields expected by `get_by_range_and_tax()`. It projects canonical `cfdi_40_reglas_tasa_cuota` rows to `tipo`, `valor_mínimo`, `valor_máximo`, `impuesto`, `factor`, `trasladado`, `retenido` and vigencia fields. Fixed rules expose `valor_mínimo=None` and keep the exact SAT decimal text in `valor_máximo`; range rules expose both limits. Query criteria use `None` as a wildcard, compare numeric inputs through `Decimal`, accept `001`/`002`/`003` as aliases for `ISR`/`IVA`/`IEPS`, compare factor names case-insensitively, and honor both transfer and retention flags.

The shared SAT SQLite reader keeps `id` as its default ordering key but also accepts a validated tuple of ordering columns for canonical tables with composite identity such as `cfdi_40_reglas_tasa_cuota`. Empty, missing or unsafe ordering identifiers fail closed before SQL execution.

Deterministic tests exercise the CFDI APIs against a local `CATALOGMX_SHARED_DATA` SQLite mount, and installed-wheel CI exercises the same public surfaces through a verified release-pointer/cache path without packaging the shared-data JSON tree.

### Python Carta Porte 3.1 consumer cutover

Four Python Carta Porte surfaces with direct canonical SAT counterparts now terminate at `DatasetResolver` and read `sat_carta_porte_31.sqlite3`: `ConfigAutotransporteCatalog`, `MaterialPeligrosoCatalog`, `TipoEmbalajeCatalog` and `TipoPermisoCatalog`. They keep their public lookup/search methods while expanding from the small tracked snapshots to the current canonical tables.

Authority-owned and CatalogMX-owned fields are kept distinct. Vehicle axes, wheel counts, trailer capability, dangerous-goods class/division, permit transport key and vigencias come directly from the SAT artifact. High-level vehicle/permit classifications and packaging material labels are convenience derivations used to preserve historical searches. Legacy `packing_group`, `grupo_embalaje` and `categoria_onu` values are not present in the SAT Carta Porte 3.1 tables, so Python exposes them as unknown instead of fabricating them from obsolete partial snapshots.

The remaining Carta Porte legacy surfaces require separate source/identity work rather than a mechanical SQLite cutover. Current SAT airports are rows in `ccp_31_estaciones` with SAT station IDs such as `EA0426` plus an IATA designator; the historical Python airport snapshot instead used IATA as `code` and added ICAO/city/state fields not published by the Carta Porte table. Maritime stations similarly use current `PMxxx` SAT IDs rather than the tracked snapshot's numeric port codes. `CarreterasCatalog` has no direct table in the canonical 32-table Carta Porte 3.1 release and therefore needs an independently identified SICT source instead of being represented as SAT data.

Installed-wheel CI builds a verified local `sat.carta_porte` release and exercises these four migrated public classes through the release-pointer/cache path without packaging the tracked Carta Porte JSON directory.

### Python Comercio Exterior 2.0 consumer cutover

Four Python Comercio Exterior surfaces with direct CCE 2.0 authority tables now terminate at `DatasetResolver` and read `sat_comercio_exterior_20.sqlite3`: `EstadoCatalog`, `IncotermsValidator`, `MotivoTrasladoCatalog` and `UnidadAduanaCatalog`.

The cutover intentionally updates runtime values when the tracked snapshots disagree with the current canonical release. `cce_20_estados` contains 50 USA states, 13 Canadian provinces/territories and 32 Mexican states; the historical Python `EstadoCatalog` contract still exposes only USA/Canada, but now uses the authority's current membership and codes, including `UN` for Nunavut. `cce_20_motivos_traslado` keeps six rows but its current code `01` text differs materially from the legacy snapshot. `cce_20_unidades_medida` contains 23 current units rather than the tracked snapshot's 20.

INCOTERM identity, official Spanish text and vigencias come from `cce_20_incoterms`. Transport applicability plus seller-freight/insurance helpers remain explicit CatalogMX/ICC convenience rules in code so those useful historical Python methods do not masquerade as SAT columns. The existing `MotivoTrasladoCatalog.requires_propietario()` application rule is also explicit in code; code `05` now activates the `ComercioExteriorValidator` requirement for at least one `Propietario`, instead of silently remaining false because the legacy JSON omitted that metadata. Customs-unit `type` is likewise a search-only CatalogMX classification layered over the authority rows.

`MonedaCatalog` is a Comercio Exterior API but its data owner is the reused CFDI 4.0 dependency. Python now resolves it from `sat.cfdi_4` / `cfdi_40_monedas`, so code, SAT text, decimal precision, permitted variation and vigencias share the same lifecycle as every other CFDI-owned consumer. The legacy `pais` field is retained as a compatibility key with value `None`: it is not a column of `cfdi_40_monedas`, and assigning one country to every ISO 4217 currency is not a universally valid one-to-one relationship. Currency search therefore uses authority code/name rather than the obsolete country enrichment. The existing USD-conversion validation behavior remains code-owned application logic.

Several historical APIs deliberately remain outside this slice because their source boundary is different. `ClavePedimentoCatalog` exposes roughly 42 general Anexo 22 customs keys, while the CCE 2.0-owned `cce_20_claves_pedimentos` table contains only `A1`; it needs its own customs-source lifecycle rather than destructive narrowing. `RegistroIdentTribCatalog` has no CCE-owned table; current tax-identity patterns are associated with countries in the reused CFDI `cfdi_40_paises` table and require an API/model redesign. `PaisCatalog` also depends on CFDI authority data, but its historical Alpha-2 lookup is an ISO 3166 enrichment that `cfdi_40_paises` does not publish. CatalogMX does not add a new runtime dependency or hidden Alpha-2 mapping merely to preserve that convenience; country cutover remains deferred until an explicit ISO enrichment/source policy is defined.

Installed-wheel CI builds a verified local `sat.comercio_exterior` release and exercises the four CCE-owned migrated public classes through the release-pointer/cache path without packaging the tracked Comercio Exterior JSON directory. The existing `Python CFDI Consumer Data` gate separately exercises `MonedaCatalog` through the verified `sat.cfdi_4` release/cache path, matching the true data owner instead of creating a duplicate CCE lifecycle.

The remaining consumer migration rule is simple: public catalog APIs may translate canonical datasets into historical return shapes, but they must ultimately obtain runtime data from `DatasetResolver` rather than create another downloader, cache or package-data lifecycle.
