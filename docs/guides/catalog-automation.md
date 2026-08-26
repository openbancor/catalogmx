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
2. normalize deterministically into canonical repository files;
3. avoid deleting or rewriting enriched information unless that behavior is explicitly reviewed;
4. exit non-zero when retrieval or normalization is unsafe;
5. leave unchanged files byte-identical whenever upstream content produces no semantic change.

The maintenance workflow then validates the registry, checks changed JSON/data, runs `git diff --check`, and opens or updates a pull request only when canonical data actually changed. It does not push reference or regulatory changes directly to `master`.

## Current rollout

The first scheduled reference adapter is `banxico.reference`, using `scripts/update_banxico_banks.py`. That updater uses Banxico's CEP institution endpoint and conservatively adds new institution codes without deleting or overwriting manually enriched fields.

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

# Run one reviewed adapter
python scripts/catalog_maintenance.py run --dataset banxico.reference
```

`--strict-unconfigured` is useful when a CI lane should fail until every dataset in a selected slot has a reviewed adapter. The default scheduled workflow is deliberately non-strict during the incremental rollout.
