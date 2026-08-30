# SAT Nómina 1.2 data lifecycle

CatalogMX treats SAT Nómina 1.2 as a versioned regulatory dataset with its own provenance, validation and release lifecycle. Language APIs and embedded JSON compatibility views consume that dataset; they are not the canonical source.

## Revision E

Nómina 1.2 remains the current payroll complement. **Revision E** is effective from **2026-01-01**.

The repository keeps the current `catNomina.xsd` synchronized between shared data and the Svelte browser asset. Revision E includes, among other changes guarded by tests, `c_TipoPercepcion` codes through `057` and `c_TipoDeduccion` codes through `115`.

Canonical registry entry: `sat.nomina_1_2`.

## Authority and technical ingestion

SAT remains authoritative. The registry records the SAT payroll/CFDI notice, `catNomina.xls`, and `catNomina.xsd` as authoritative resources. `phpcfdi/resources-sat-catalogs` is a versioned technical ingestion mirror used for deterministic normalized extraction; it is not the legal authority.

## Canonical 13-table boundary

`catNomina.xsd` represents thirteen catalog families. The canonical Nómina artifact contains exactly:

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

The technical mirror also contains `nomina_estados`. That table is explicitly **auxiliary** for this dataset and is not copied into the canonical Nómina artifact. The builder validates the complete `nomina_%` namespace as **13 canonical + the known auxiliary table**. Any missing or newly introduced table stops the build for review.

## Reproducible release artifact

`scripts/sat/build_nomina_12.py` builds `sat_nomina_12.sqlite3` and `sat_nomina_12.manifest.json`. It resolves a versioned technical-mirror release, verifies the source digest when available, validates the exact table family, copies only the thirteen canonical tables and indexes, records row counts and provenance, and emits both byte-level and semantic SHA-256 hashes.

Download failure, checksum mismatch, missing tables or upstream schema drift fail closed. There is no synthetic fallback.

## Thirteen compatibility views

`packages/shared-data/sat/nomina_1.2` contains one generated compatibility JSON view for every canonical family. `scripts/catalog_maintenance.py` invokes the builder with `--compat-output-dir`, so the same canonical ingestion refreshes the release artifact and the embedded compatibility views.

SAT-owned code, description and vigencia fields are regenerated from canonical SQLite data. CatalogMX-specific enrichments are narrowly whitelisted and preserved by code:

- `periodicidad_pago.json`: `days`
- `riesgo_puesto.json`: `prima_minima`, `prima_media`, `prima_maxima`

Compatibility consumers may expose aliases such as `code`/`clave`, `description`/`descripcion`, and `full_name`/`razon_social`; those aliases do not create an independent regulatory source.

## Cross-language API parity

Python, TypeScript, Dart and Kotlin expose all **13/13** Nómina catalog families. Existing seven public catalog APIs remain available and the six previously missing families are now first-class APIs:

- `c_OrigenRecurso`
- `c_TipoDeduccion`
- `c_TipoHoras`
- `c_TipoIncapacidad`
- `c_TipoOtroPago`
- `c_TipoPercepcion`

Python uses the shared-data resolver for embedded compatibility views. TypeScript and Dart normalize historical aliases at their catalog boundary. Kotlin first reads canonical `nomina_*` SQLite tables when a dataset database is configured and otherwise reads the generated shared JSON views; hard-coded Nómina regulatory maps have been removed.

## Publishing and scheduling

The registry freshness SLA is 31 days. The generic scheduler therefore places `sat.nomina_1_2` in the monthly cadence. The release adapter writes below `dist/catalog-artifacts/sat-nomina-12` and regenerates the thirteen compatibility views in the repository.

The generic publisher compares manifest `content_sha256`; a new data release is created only when canonical Nómina content changes. Package/library versions remain independent from catalog-data versions.

## Remaining resolver migration

Issue #57 remains the transport/distribution migration. The API completeness work is no longer blocked on it: all four SDKs already expose 13/13 through the compatibility contract. The remaining sequence is to make installed consumers resolve the independently versioned canonical dataset/profile, prove that path with installed-package integration tests, and only then remove embedded JSON compatibility views.
