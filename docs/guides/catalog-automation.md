# Catalog automation

CatalogMX treats code releases and data releases as separate concerns. The canonical source for dataset freshness is `packages/shared-data/catalog-registry.json`; scheduled maintenance derives its cadence from that registry rather than maintaining a second calendar by hand.

## Scheduling model

`scripts/catalog_maintenance.py` maps an interval freshness SLA to an operational cadence:

| `max_age_days` | Cadence |
| --- | --- |
| 1-2 | daily |
| 3-14 | weekly |
| 15-45 | monthly |
| 46-120 | quarterly |
| 121-200 | semiannual |
| >200 | annual |

Datasets with `freshness.mode = pipeline` keep their dedicated pipeline and are not scheduled again. This is how `banxico.sie_dynamic` remains owned by `update-dynamic-data.yml` instead of being duplicated by the reference-catalog scheduler.

Datasets with `event` or `manual` freshness, and datasets whose registry status is `planned`, are not mutated by a time-based job.

## Staggering

A cadence can have multiple slots. The scheduler hashes the dataset ID into a stable slot so upstream systems are not all queried on the same day or hour. The assignment is deterministic: a dataset stays in the same slot unless the scheduling algorithm itself changes.

The GitHub Actions workflow currently uses:

- daily: one slot;
- weekly: two slots, Tuesday and Thursday;
- monthly: four slots, on days 3, 10, 17 and 24;
- quarterly: two slots in January, April, July and October;
- semiannual: one slot in January and July;
- annual: one January slot.

Times are intentionally different across slots. They are operational staggering, not part of the legal or authoritative meaning of a catalog.

## Adapter contract

The registry remains declarative and never contains executable shell commands. Trusted source adapters are explicitly registered in `scripts/catalog_maintenance.py`.

An adapter must:

1. retrieve data from the registered authoritative or reviewed upstream source;
2. normalize deterministically;
3. avoid deleting or rewriting enriched information unless that behavior is explicitly reviewed;
4. exit non-zero when retrieval, schema validation, or normalization is unsafe;
5. expose a semantic content identity so irrelevant upstream changes do not create false CatalogMX updates.

### Repository-data adapters

Small catalogs that are appropriate to review in Git update canonical files below `packages/shared-data`. The maintenance workflow validates the repository diff and opens or updates a pull request only when those tracked files actually changed. It does not push regulatory/reference changes directly to `master`.

`banxico.reference` is the first repository-data adapter. It uses `scripts/update_banxico_banks.py`, which checks Banxico's CEP institution endpoint and conservatively adds new institution codes without deleting or overwriting manually enriched fields.

### Release-artifact adapters

Large or independently versioned datasets should not be forced into every language package or committed as large generated blobs. A release adapter writes its files and a `*.manifest.json` below `dist/catalog-artifacts/<dataset>/`.

The manifest records authority, ingestion provenance, table/record inventory, binary SHA-256, and a semantic `content_sha256`. The workflow compares that semantic hash with the mutable dataset channel release. When the content is unchanged, nothing is published even if the technical upstream release changed for some unrelated catalog.

When content changes, the workflow publishes:

- an immutable release tagged from dataset/version plus a content-hash prefix;
- a mutable `...-latest` channel containing the same verified artifact and manifest.

Consumers can therefore choose reproducibility (immutable tag/hash) or controlled freshness (dataset-specific latest channel) without tying data updates to a Python/TypeScript/Dart/Kotlin package release.

## Carta Porte 3.1

The Carta Porte source audit found that `packages/shared-data/sat/carta_porte_3` is a legacy partial convenience view, not a complete one-to-one mirror of the official Carta Porte 3.1 dataset. The current technical representation contains 32 `ccp_31_*` catalogs, while the legacy directory contains seven convenience JSON files; some of those files do not map directly to a same-named SAT catalog.

For that reason, those seven files are not blindly overwritten by automation. `scripts/sat/build_carta_porte_31.py` instead:

1. treats the SAT Carta Porte portal and `CatalogosCartaPorte31.xls` as authoritative provenance;
2. obtains the latest versioned SQLite conversion from `phpcfdi/resources-sat-catalogs` as a technical ingestion mirror;
3. verifies the source asset checksum when GitHub publishes one;
4. requires the exact expected set of 32 `ccp_31_*` tables and fails closed if the upstream schema adds or removes a catalog;
5. copies only those 32 tables into `sat_carta_porte_31.sqlite3`;
6. computes a semantic hash over schemas and deterministically ordered rows;
7. writes `sat_carta_porte_31.manifest.json` with provenance and record counts.

Carta Porte is checked monthly because its catalogs have received changes outside major complement-version releases. The full official dataset is distributed independently; explicit convenience views can later be regenerated from it once their derivation contracts are defined.

## Current rollout

Other managed datasets already participate in planning. Until a reviewed adapter exists they are reported as `unconfigured` rather than being changed by generic scraping logic. This gives a visible automation backlog while preserving source-specific parsing and validation.

The intended adapter rollout is by authority rather than by creating dozens of unrelated workflows:

- SAT: CFDI, Carta Porte, Nómina, Comercio Exterior and tax parameters;
- Banxico: compact reference catalogs, alongside the already independent SIE dynamic-data pipeline;
- SEPOMEX: postal-code export and generated SQLite;
- INEGI: AGEEML/geographic data and later reproducible derived datasets;
- CNBV, IFT, CONAPO and IMSS: authority-specific reference/regulatory adapters.

## Local commands

```bash
# Show the complete monthly plan
python scripts/catalog_maintenance.py plan --cadence monthly

# Show only one monthly slot
python scripts/catalog_maintenance.py plan --cadence monthly --slot 2

# Machine-readable plan
python scripts/catalog_maintenance.py plan --cadence monthly --slot 2 --json

# Run one compact repository adapter
python scripts/catalog_maintenance.py run --dataset banxico.reference

# Build the current Carta Porte release artifact
python scripts/catalog_maintenance.py run --dataset sat.carta_porte
```

`--strict-unconfigured` is useful when a CI lane should fail until every dataset in a selected slot has a reviewed adapter. The default scheduled workflow is deliberately non-strict during the incremental rollout.
