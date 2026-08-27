# SAT Nómina 1.2 data lifecycle

CatalogMX treats SAT Nómina 1.2 as a versioned regulatory dataset with its own provenance, validation and release lifecycle. Language APIs and legacy JSON views are consumers of that dataset; they are not the canonical source.

## Revision E

Nómina 1.2 remains the current payroll complement. **Revision E** is effective from **2026-01-01**.

The repository keeps the current `catNomina.xsd` synchronized between shared data and the Svelte browser asset. Revision E includes, among other changes already guarded by tests, `c_TipoPercepcion` code `057` and `c_TipoDeduccion` codes `114` and `115`.

Canonical registry entry: `sat.nomina_1_2`.

## Authority and technical ingestion

SAT remains authoritative. The registry records:

- the SAT payroll/CFDI notice as regulatory version context;
- `catNomina.xls` as the authoritative catalog workbook;
- `catNomina.xsd` as the authoritative schema resource;
- `phpcfdi/resources-sat-catalogs` as a versioned technical ingestion mirror.

The PhpCfdi mirror is used because it provides normalized SQLite tables suitable for deterministic extraction and querying. It is not the legal authority.

## Canonical 13-table boundary

`catNomina.xsd` represents thirteen catalog families. The canonical Nómina artifact therefore contains exactly these technical-mirror tables:

- `nomina_bancos`
- `nomina_origenes_recursos`
- `nomina_periodicidades_pagos`
- `nomina_riesgos_puestos`
- `nomina_tipos_contratos`
- `nomina_tipos_deducciones`
- `nomina_tipos_horas`
- `nomina_tipos_incapacidades`
- `nomina_tipos_jornadas`
- `nomina_tipos_nominas`
- `nomina_tipos_otros_pagos`
- `nomina_tipos_percepciones`
- `nomina_tipos_regimenes`

The technical mirror also contains `nomina_estados`. That table is explicitly **auxiliary** for this dataset: it comes from a separate source and is equivalent to state data published with Comercio Exterior. It is not one of the thirteen `catNomina.xsd` catalog types and is therefore not copied into the canonical Nómina artifact.

The builder validates the complete `nomina_%` namespace as **13 canonical + the known auxiliary table**. Any newly introduced or missing Nómina table stops the build for review instead of silently changing the dataset contract.

## Reproducible release artifact

`scripts/sat/build_nomina_12.py` builds:

- `sat_nomina_12.sqlite3`
- `sat_nomina_12.manifest.json`

The builder:

1. resolves the latest versioned `phpcfdi/resources-sat-catalogs` release;
2. downloads `catalogs.db.bz2` and verifies its published SHA-256 when available;
3. validates the exact known Nómina table family;
4. copies only the thirteen canonical tables and their indexes;
5. records per-table and total row counts;
6. emits a file SHA-256 and deterministic semantic content SHA-256;
7. records SAT authority and technical-mirror provenance in the manifest;
8. records `nomina_estados` as deliberately excluded auxiliary data.

Download failure, checksum mismatch, missing tables or upstream schema drift fail closed. There is no synthetic fallback.

## Existing seven JSON views

`packages/shared-data/sat/nomina_1.2` currently contains seven compatibility JSON files:

- banco
- periodicidad de pago
- riesgo de puesto
- tipo de contrato
- tipo de jornada
- tipo de nómina
- tipo de régimen

Those files support existing Python, TypeScript and Dart consumers. They are no longer modeled as the complete canonical Nómina dataset.

Six `catNomina.xsd` catalog families still lack normalized cross-language APIs:

- `c_OrigenRecurso`
- `c_TipoDeduccion`
- `c_TipoHoras`
- `c_TipoIncapacidad`
- `c_TipoOtroPago`
- `c_TipoPercepcion`

A follow-up consumer migration should derive all thirteen APIs from the canonical dataset, rather than introducing six new hard-coded regulatory copies.

## Kotlin drift

The current Kotlin implementation has a different data path from the other language packages: several Nómina catalogs have embedded Kotlin maps used when SQLite data is unavailable. Those copies can drift independently from SAT and from the shared JSON data.

The canonical release establishes the source needed to remove that divergence. The consumer follow-up should make Kotlin use the same resolver/data contract and retire embedded regulatory copies after compatibility coverage is in place.

## Publishing and scheduling

The registry freshness SLA is 31 days. `scripts/catalog_maintenance.py` therefore places `sat.nomina_1_2` in the shared monthly cadence; there is no Nómina-specific cron.

The adapter writes below:

`dist/catalog-artifacts/sat-nomina-12`

The generic maintenance publisher compares manifest `content_sha256`. A new data release is created only when canonical Nómina content changes. Package/library versions remain independent from catalog-data versions.

## Consumer migration

The intended sequence is:

1. publish and verify the canonical thirteen-table dataset;
2. expose it through the common dataset resolver/profile architecture in issue #57;
3. add normalized APIs for the six missing catalog families;
4. move the existing seven APIs to the same canonical source;
5. remove Kotlin hard-coded regulatory copies;
6. remove legacy embedded JSON views only after installed-package and compatibility tests prove they are no longer required.
