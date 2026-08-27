# Banxico institution reference lifecycle

CatalogMX separates current Banco de México payment-system reference data from compatibility enrichments maintained by the project.

## Current source snapshot

Banco de México's CEP-SCL service publishes a live list of financial institutions with two source-owned fields:

- the full Banxico institution key used by the payment-system service;
- the current short institution name.

`scripts/update_banxico_banks.py` stores that source-faithful view in:

`packages/shared-data/banxico/spei_institutions.json`

The snapshot also contains the three-digit compatibility code derived from the final three digits of the Banxico key. The updater validates that this projection is one-to-one; if two current keys ever collapse to the same three-digit code, maintenance stops for review.

The source parser is fail-closed. A response with fewer than 50 institutions, duplicate keys, duplicate projected codes, invalid keys, malformed HTML, or a network failure does not mutate repository data.

## Enriched compatibility view

`packages/shared-data/banxico/banks.json` remains the existing cross-language compatibility catalog. It contains project-maintained enrichments that are not owned by the live CEP list, including fields such as legal name, RFC, institution type and historical records.

Maintenance therefore does not rebuild `banks.json` from scratch. It:

1. refreshes the current short name and full Banxico key for codes present in the live source;
2. marks those rows with `cep_current: true`;
3. preserves manual enrichment fields;
4. preserves rows absent from the current CEP list and marks them `cep_current: false` instead of deleting history;
5. adds newly observed current institutions with conservative compatibility defaults for fields that have not yet been enriched.

The legacy `spei` field is deliberately not inferred from absence in the CEP consultation list. Direct SPEI participation and CEP availability are related but are not treated as identical lifecycle signals by the updater.

## Frequency

`banxico.reference` uses the registry-driven monthly cadence (`max_age_days = 31`). This is intentionally more frequent than the expected rate of structural change: the update is cheap, and the maintenance workflow opens a repository change only when the source snapshot or compatibility view actually changes.

There is no package release for every check. Reference-data changes remain independent from Python, TypeScript, Dart and Kotlin package versions.

## Authority boundary

Banco de México is authoritative. The live CEP-SCL institution list is the operational source for current institution keys and short names. Banco de México's published direct-SPEI-participant document is useful for legal names and participation context, but it has its own publication cut and is not silently merged into fields maintained from another source.

Future enrichment automation should add provenance per field/source rather than treating one Banxico page as authoritative for every attribute in `banks.json`.
