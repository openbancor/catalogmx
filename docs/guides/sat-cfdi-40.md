# SAT CFDI 4.0 data maintenance

CatalogMX separates the CFDI 4.0 library/API surface from the lifecycle of the SAT catalog data. CFDI 4.0 has been the mandatory Anexo 20 version since 2023-04-01, but its catalog rows can change without a new CFDI schema version and therefore must not require a new Python, TypeScript, Dart, or Kotlin release.

## Sources

The SAT Anexo 20 page and SAT catalog workbook remain authoritative. CatalogMX uses `phpcfdi/resources-sat-catalogs` as a reviewed technical ingestion mirror because it publishes a versioned SQLite representation with the complete catalog families and checksummed release assets.

The technical mirror currently represents CFDI 4.0 as 25 `cfdi_40_*` tables. The existing `packages/shared-data/sat/cfdi_4.0` directory contains 16 convenience JSON files and is therefore a partial compatibility view, not the complete canonical dataset. The small `c_Estado` view is generated deterministically from the reviewed SAT `catCFDI.xsd` because Nómina 1.2 references that CFDI-owned type. A separate Nómina-only projection exposes `84111505`, the value mandated by SAT's filling guide, without pretending to preload the complete `c_ClaveProdServ` catalog in edge runtimes.

## Canonical artifact

`scripts/sat/build_cfdi_40.py` builds:

- `sat_cfdi_40.sqlite3`
- `sat_cfdi_40.manifest.json`

The builder:

1. resolves the latest versioned technical-mirror release;
2. downloads `catalogs.db.bz2` and verifies its published SHA-256 when available;
3. requires the exact reviewed set of 25 `cfdi_40_*` tables;
4. fails closed if a table is added or removed so a new SAT catalog cannot become silently invisible;
5. copies only the CFDI 4.0 tables and their indexes;
6. records per-table and total row counts;
7. computes a file SHA-256 and a semantic hash over table schemas and deterministically ordered rows.

The semantic hash is independent of unrelated changes to Carta Porte, Nómina, Retenciones, or another SAT family present in the same technical-mirror release.

## Scheduling and publication

`sat.cfdi_4` remains on the 31-day freshness SLA and therefore participates in the monthly staggered `Catalog Maintenance` schedule. The adapter writes to `dist/catalog-artifacts/sat-cfdi-40`.

The generic release publisher compares `dataset.content_sha256` with the current dataset-specific channel. If normalized CFDI 4.0 content is unchanged, no release is created. If it changed, CatalogMX publishes an immutable content-addressed tag and refreshes the dataset-specific latest channel.

This gives consumers two modes:

- reproducible: pin the immutable release/content hash;
- fresh: follow the CFDI 4.0 latest data channel.

Neither mode changes the CatalogMX library version.

## Legacy compatibility

The following remain in the repository until language consumers migrate to the common dataset resolver from issue #57:

- `packages/shared-data/sat/cfdi_4.0`
- `packages/shared-data/sqlite/clave_prod_serv.db`
- the current language-specific convenience APIs built on those files.

The legacy `scripts/fetch_sat_catalogs.py` must not be used for unattended maintenance. It has historically used dated workbook URLs, covers only a subset of catalogs, and writes execution timestamps into generated data. After consumer migration it can be removed or rewritten as a compatibility-view generator from the canonical released dataset.
