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

## SPEI participant codes (5 digits) and CLABE bank codes (3 digits)

Banxico identifies each SPEI participant with a 5-digit key (for example
`40012` = BBVA MEXICO); the last three digits are the bank code embedded in a
CLABE (`012`). `banks.json` carries both on every row:

| Field | Meaning |
| --- | --- |
| `code` | 3-digit CLABE bank code (unchanged, still the lookup key of the existing APIs) |
| `spei_code` | 5-digit SPEI participant code, or `null` when the bank is not in the current list. BANXICO itself is the official 4-digit `2001`. Always satisfies `code == spei_code[-3:]` |
| `status` | `active`, or `historical` for banks disaffiliated from SPEI |
| `spei_source`, `spei_verified_at` | Provenance: Banxico service and consultation date (`aaaa-mm-dd`) |

Participants added from the 2026-10-27 list (`40170` REVOLUT BANK, `90660`
Altor, `90714` PPBALANCEMX) carry only the official short name; `full_name`,
`rfc` and `tipo_institucion` are `null` because no official data was available
(nothing is invented).

`143` CIBanco, `608` VECTOR and `630` CB INTERCAM are **historical**: the
project owner stated on 2026-10-28 that they were disaffiliated from SPEI, and
the current Banxico list confirms their absence. They keep their 3-digit code
and history (old CLABEs still resolve), have `spei_code: null`, `spei: false`,
`spei_disaffiliated: true` and an unknown `spei_disaffiliation_date`
(`null`; never guessed). They are excluded from the default SPEI listings;
Python `BankCatalog.get_spei_banks(include_historical=True)`, Dart
`BanxicoBanks.getSPEIBanks(includeHistorical: true)` and TypeScript
`BankCatalog.getSPEIBanks(true)` include them.

The default SPEI listings exclude every row with `status == "historical"`, whatever its `spei` flag (so a participant dropped by a future source update is excluded even though `sync_banks()` does not infer `spei: false` from absence; only the three owner-declared banks get `spei: false`).

APIs (Python / Dart / TypeScript): lookup by 5 digits
(`get_bank_by_spei_code` / `getBySpeiCode` / `getBankBySpeiCode`), by 3 digits
(`get_bank_by_clabe_code` / `getByClabeCode` / `getBankByClabeCode`) and
validation of a 5-digit code against the 3-digit one (`validate_spei_code` /
`validateSpeiCode`). The Kotlin catalog reads the same JSON without logic of
its own and was not extended.

Regenerate from the open Banxico service (no credentials) with an explicit date:

```bash
python scripts/update_banxico_spei.py --fecha 2026-10-27
```

Note: applying the 2026-10-27 list also adopted Banxico's current short names
for three existing rows (`CI BOLSA` -> `TRF`, `NU MEXICO` -> `NUBANK`,
`Swap` -> `Clip`), so name lookups with the old names no longer match.
