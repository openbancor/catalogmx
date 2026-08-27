# SAT Comercio Exterior 2.0 data lifecycle

CatalogMX treats the SAT Comercio Exterior 2.0 complement as a versioned data contract, not as a directory of JSON files that can be overwritten blindly.

## Authority and current version

The SAT remains the authoritative source. Comercio Exterior **2.0** is the current complement version and is integrated with CFDI 4.0 from **2024-01-18**.

Canonical registry entry: `sat.comercio_exterior`.

Sources recorded by the registry:

- SAT Factura de comercio exterior portal: authoritative version/effective-date context;
- SAT Comercio Exterior technical page: authoritative technical documents and catalog links;
- `phpcfdi/resources-sat-catalogs`: versioned technical ingestion mirror used to build reproducible SQLite artifacts.

The technical mirror is an ingestion convenience, not the legal authority.

## 10 owned catalogs + 4 shared CFDI catalogs

The current technical mirror exposes exactly ten CCE 2.0-owned tables:

- `cce_20_claves_pedimentos`
- `cce_20_colonias`
- `cce_20_estados`
- `cce_20_fracciones_arancelarias`
- `cce_20_incoterms`
- `cce_20_localidades`
- `cce_20_motivos_traslado`
- `cce_20_municipios`
- `cce_20_tipos_operacion`
- `cce_20_unidades_medida`

The complement also reuses four CFDI 4.0 catalog families instead of defining duplicate CCE tables:

- `cfdi_40_codigos_postales`
- `cfdi_40_monedas`
- `cfdi_40_paises`
- `cfdi_40_regimenes_fiscales`

Therefore the canonical CCE artifact is intentionally **not self-contained**. Its manifest declares a dependency on dataset `sat.cfdi_4`, version 4.0. Dataset profiles/resolvers must fetch the CCE and CFDI artifacts together when an application needs the complete Comercio Exterior catalog contract.

This avoids duplicating large shared catalogs and keeps ownership explicit.

## Legacy embedded views

`packages/shared-data/sat/comercio_exterior` currently contains eight JSON files. They are compatibility views, not a complete one-to-one representation of the current SAT catalog family.

The directory mixes several semantics:

- CCE-owned convenience data, such as pedimento/incoterm/motivo catalogs;
- shared data, such as countries and currencies;
- derived convenience data, such as tax-registration metadata.

The maintenance adapter must **not** overwrite those files by assuming filename equivalence with SAT/PhpCfdi tables. They remain available until consumers migrate to the common dataset resolver/profile architecture tracked in issue #57.

## Reproducible release artifact

`scripts/sat/build_comercio_exterior_20.py` builds:

- `sat_comercio_exterior_20.sqlite3`
- `sat_comercio_exterior_20.manifest.json`

The builder:

1. resolves the latest versioned `phpcfdi/resources-sat-catalogs` release;
2. downloads `catalogs.db.bz2` and verifies its published SHA-256 when GitHub exposes one;
3. requires the exact ten `cce_20_*` tables;
4. requires all four shared CFDI dependency tables to exist in the source mirror;
5. copies only the ten CCE-owned tables and their indexes;
6. records per-table and total row counts;
7. emits file SHA-256 and a deterministic semantic content SHA-256;
8. records the `sat.cfdi_4` dependency in the manifest.

Any missing/extra CCE table, missing dependency, checksum mismatch or download failure aborts the build. There is no synthetic fallback.

## Publishing and scheduling

The registry freshness SLA is 31 days. `scripts/catalog_maintenance.py` therefore places `sat.comercio_exterior` in the shared monthly maintenance cadence; there is no CCE-specific cron.

The adapter writes below:

`dist/catalog-artifacts/sat-comercio-exterior-20`

The generic maintenance publisher compares the manifest `content_sha256`. A new dataset release is published only when the CCE-owned semantic content changes. Changes that affect only unrelated SAT families in the upstream mirror do not produce a new CCE release.

Code/package releases remain independent from catalog-data releases.

## Consumer migration

The intended resolver/profile sequence is:

1. fetch/verify `sat.cfdi_4`;
2. fetch/verify `sat.comercio_exterior`;
3. expose them as one logical Comercio Exterior data profile while preserving dataset provenance;
4. migrate language-specific consumers away from direct repository-relative JSON paths;
5. remove legacy embedded convenience views only after compatibility guarantees are met.
