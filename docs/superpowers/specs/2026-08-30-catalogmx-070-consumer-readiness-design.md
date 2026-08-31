# CatalogMX 0.7.0 Consumer Readiness Design

## Objective

Prepare PR #96 for a safe 0.7.0 release and prove that its published artifacts
work for the actual consumers: CatalogMX API Worker, Cronikos payroll, and the
PayGlobal Core, CRM, and Rails services.

CatalogMX remains the owner of Mexican fiscal tables, validators, and catalogs.
Consumers may adapt its public APIs, but they must not copy fiscal tables or SAT
catalog enumerations into their own source.

## Release boundary

The release has two stages:

1. Make PR #96 substantively clean and merge it only after exact-head CI and
   verified `reviewctl` receipts are green.
2. Prepare and publish 0.7.0 from a dedicated release change, then update local
   consumers to the published version and run registry-backed smoke tests.

No tag or registry upload is allowed while a source consumer fails to compile,
Modalidad 10 is presented as verified, or the release workflow cannot prove all
four artifacts.

## CatalogMX interfaces

### IMSS calculations

Python and TypeScript expose equivalent IMSS behavior.

- Ordinary employer/employee calculations reject non-finite salaries,
  non-positive or non-finite days, invalid risk classes, and an SBC below the
  applicable general or border-zone minimum wage.
- The public CEAV selector rejects a non-finite, non-positive, or below-minimum
  daily SBC before selecting a band. The exact minimum-wage value retains the
  special first CEAV row.
- The lower-bound rule follows article 28 of the Ley del Seguro Social:
  <https://www.diputados.gob.mx/LeyesBiblio/pdf/LSS.pdf>.
- Modalidad 40 keeps its eligibility-safe form requiring the last registered
  monthly SBC. The former ambiguous two-argument call is not silently restored;
  the migration guide gives the replacement in every supported language.
- Modalidad 10 remains callable for compatibility but is explicitly marked
  unverified in library metadata and is disabled in the public web calculator
  until issue #97 supplies audited parameters.

### Fiscal manifest

The generated manifest is a language-neutral release artifact. TypeScript and
Python expose read-only accessors with equivalent names and semantics:

- list fiscal datasets;
- retrieve one dataset;
- inspect release verification status and sources.

Public accessors return immutable or defensive values so a caller cannot alter
subsequent reads. Generator records use explicit `TypedDict` definitions rather
than unbounded `dict[str, Any]` structures.

### Package contract

The npm tarball must support CommonJS, Node ESM, and a real Cloudflare Worker
bundle for both the root export and `catalogmx/fiscal`. The Python wheel must
contain the fiscal manifest and load it outside the repository checkout. The
API Worker is an in-repository source consumer and becomes a blocking CI job.

## Consumer adapters

### Cronikos

Cronikos consumes CatalogMX through two explicit seams:

- the authenticated CatalogMX API for audited ISR/IMSS calculations;
- npm package subpath exports for SAT CFDI/Nómina catalog validation.

Its checked-in SAT enumeration fallback is removed. Startup/build failure is
preferred to using a stale copied catalog. Payroll calculation responses must
carry exercise, source, version, audit metadata, UMA, and CEAV rate so cached
receipts remain reproducible.

### PayGlobal

- Core and Rails continue using `BankCatalog` and CLABE/RFC/CURP validators.
- CRM uses the same public validators and bank catalog for onboarding.
- Each service gets a focused contract test against the 0.7.0 wheel before its
  dependency is advanced.
- The CRM's current commit-pinned CatalogMX dependency is replaced by the
  published compatible release after registry publication. Core and Rails use
  a bounded `>=0.7.0,<0.8.0` range to avoid accidental future fiscal changes.
- GitOps and sandbox-bank are smoke-tested because they import CatalogMX, but
  receive no source change unless the contract test exposes one.

## Error handling

Invalid fiscal input fails closed with `ValueError` in Python and `RangeError`
in TypeScript. HTTP adapters translate these into an existing 4xx validation
response and never return `NaN`, infinity, negative contributions, or an
apparently verified Modalidad 10 result.

Catalog loading errors remain explicit. Consumers do not fall back to copied or
invented catalog values.

## Verification

Every behavior change follows RED-GREEN-REFACTOR. Required evidence includes:

- focused Python/TypeScript regression tests for invalid IMSS inputs and the
  minimum-wage CEAV boundary;
- API Worker typecheck, tests, and Wrangler dry-run;
- npm pack plus clean CommonJS, ESM, and Worker consumers;
- Python wheel installation plus manifest access outside the repository;
- full Python, TypeScript, Dart, Kotlin, and webapp checks;
- Cronikos unit/integration/build checks against the packed npm artifact;
- PayGlobal Core/CRM/Rails contract tests against the built wheel;
- exact-head GitHub CI and verified multi-model `reviewctl` receipts;
- post-publication installs from PyPI, npm, pub.dev, and Maven Central.

## Non-goals

- Auditing or inventing Modalidad 10 rates.
- Moving payroll ownership from Cronikos into CatalogMX.
- Refactoring unrelated PayGlobal services.
- Treating model findings, a dry-run, or a successful upload as proof that a
  registry artifact is usable.
