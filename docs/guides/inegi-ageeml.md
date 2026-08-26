# INEGI AGEEML data maintenance

CatalogMX treats the INEGI geographic registry (AGEEML) and the SCIAN industrial classification as independent datasets. They share an authority and a repository directory, but they do not share a lifecycle.

## AGEEML

AGEEML is the **Catálogo Único de Claves de Áreas Geoestadísticas Estatales, Municipales y Localidades**. INEGI describes it as a registry under permanent updating and exposes current national predefined catalogs for download.

CatalogMX uses the official national **Minúscula con acento, incluye bajas** ZIP:

`https://www.inegi.org.mx/contenidos/app/ageeml/min_con_acento_baja.zip`

The 31-day registry SLA maps AGEEML to the monthly maintenance lane. The latest cut visible in INEGI's indexed AGEEML page during the 2026-08-26 audit was `2026/JUN`; the released artifact is content-addressed, so publication does not depend on that human-readable cut label being available in the download response.

### Canonical artifact

`scripts/inegi/build_ageeml.py` builds:

- `inegi_ageeml.sqlite3`
- `inegi_ageeml.manifest.json`

The builder downloads the official ZIP, requires exactly one `AGEEML_*_utf.csv`, validates the known locality schema, and normalizes a stable set of geographic, coordinate, population and status fields.

The SQLite artifact includes both current and baja records. It also preserves non-numeric interstate-zone entity codes such as `CD`, `CO`, `CQ`, `CT`, `CY`, and `QY` when present. These are not malformed state codes; INEGI uses such codes for interstate areas pending definitive entity assignment.

For ordinary state records, maintenance requires:

- all 32 state codes `01` through `32`;
- three-digit municipality keys;
- four-digit locality keys;
- consistency between `CVEGEO`/`MAPA` and the concatenated state + municipality + locality key;
- at least 250,000 national records.

The adapter is fail-closed. It does not use the old `scripts/download_inegi_complete.py` fallback, because that fallback contains only a partial hand-written municipality list and stale metadata.

### Release identity

The manifest records the source ZIP SHA-256, the source CSV member and columns, HTTP provenance, normalized row counts, state coverage, interstate codes, inactive-record count, output-file SHA-256 and semantic `content_sha256`.

The semantic hash orders normalized rows independently of source order. The generic `Catalog Maintenance` workflow therefore publishes a new immutable/latest AGEEML release only when normalized geographic content actually changes.

### Compatibility migration

The current embedded files remain temporarily available:

- `packages/shared-data/inegi/states.json`
- `packages/shared-data/inegi/municipios.json`
- `packages/shared-data/inegi/municipios_completo.json`
- `packages/shared-data/inegi/localidades.json`

They are legacy convenience views, not the future canonical complete distribution. They should be regenerated explicitly from the release dataset only after their derivation contracts and all language consumers are migrated to the common data resolver.

## SCIAN 2023

`packages/shared-data/inegi/scian` is tracked separately as `inegi.scian_2023`.

SCIAN 2023 is a versioned industrial classification, not a monthly geographic registry. Its registry freshness mode is `event`, so the monthly AGEEML GitHub Action will never rewrite it. A future SCIAN revision should be handled as a classification-version transition with its own source audit and equivalence/migration policy.
