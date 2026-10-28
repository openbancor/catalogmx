# Changelog

All notable changes to catalogmx will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- SPEI participant codes: every Banxico bank now has `spei_code` (5-digit Banxico key; 4-digit `2001` for BANXICO) next to the 3-digit CLABE `code`, with `status` (`active`/`historical`) and provenance (`spei_source`, `spei_verified_at`). New lookups by 5 digits and 3 digits and `code == spei_code[-3:]` validation in Python, Dart and TypeScript; `scripts/update_banxico_spei.py --fecha aaaa-mm-dd` regenerates the data from the open Banxico CEP service.
- Participants `40170` REVOLUT BANK, `90660` Altor and `90714` PPBALANCEMX (legal name, RFC and type unknown, left `null`).
- Banks `143` CIBanco, `608` VECTOR and `630` CB INTERCAM marked `historical` (disaffiliated from SPEI per the project owner, 2026-10-28): still resolve by 3 digits, excluded from default SPEI listings (`include_historical` option).
- N1 Cloudflare Worker API under `packages/api-worker` with authenticated RFC, CURP, CLABE, NSS, ISR, IMSS, SAT, INEGI, and SEPOMEX endpoints.
- Deterministic D1 migration/query layer for large postal-code and SAT product/service catalogs, plus production-only deployment instructions.
- Worker lint, typecheck, Jest coverage, and Wrangler dry-run gates with package coverage above 90%.

### Changed
- `get_spei_banks`/`getSPEIBanks` no longer list `630` CB INTERCAM; Banxico's current short names replace `CI BOLSA`->`TRF`, `NU MEXICO`->`NUBANK`, `Swap`->`Clip`. The `banco` object of the API worker CLABE validation now includes `spei_code` and `status`.
- Normalized missing CFDI `c_TasaOCuota` spreadsheet cells to JSON `null` so the complete small-catalog allowlist can be bundled safely.

## [0.8.0] - 2026-09-18

### Added
- Versioned effective monthly federal tax late-payment surcharge rates for 2024–2026.
- Python accessors with separate LIF base-rate and normative provenance fields, official sources, and shared-data-root resolution for wheel consumers.
- Tests and documentation that distinguish mora rates from installment/deferred-payment rates.

### Changed
- Synchronized Python, TypeScript, Dart, Kotlin, Android, and iOS package versions to `0.8.0`.

## [0.5.1] - 2026-02-04

### Fixed
- Flutter plugin packaging and native channel registration
- iOS CFDI validation/signing native handler
- Optional libxml dependency handling for TypeScript XSD validation
- WASM assets inclusion for webapp XSD validation

## [0.5.0] - 2026-02-03

### Added
- SAT Contabilidad Electrónica (Anexo 24) catalogs for código agrupador (2024/2026) + diff
- Webapp SAT catálogo de cuentas with árbol, búsqueda y filtros
- SQLite tables for contabilidad electrónica catalogs

### Changed
- Synchronized package versions to 0.5.0

## [0.4.0] - 2026-01-29

### Added
- Example apps for all platforms:
  - Python: `tipo_cambio_app.py`, `identity_app.py`
  - TypeScript: `tipo-cambio-app.ts`, `validators-app.ts`
  - Dart: `tipo_cambio_app.dart`, `validators_app.dart`
- Comprehensive test coverage configuration with Istanbul/pytest-cov/Dart coverage
- Coverage exclusion comments for infrastructure code with justifications
- Identity generator tests (97% coverage)
- Version management script (`scripts/version.sh`)
- Improved technical documentation in webapp-svelte

### Changed
- Updated documentation with comprehensive TypeScript and Dart examples
- Fixed `banxico_demo.py` to use correct API methods

### Removed
- **BREAKING**: Removed `packages/webapp` (React). Use `packages/webapp-svelte` instead.

### Security
- Fixed react-router vulnerabilities by removing unused React webapp
- Updated all npm dependencies to patch security vulnerabilities
- Zero open Dependabot alerts

## [0.3.0] - 2026-01-10

### Added
- Dart package with full feature parity
- Identity generator for test data (RFC, CURP, CLABE, NSS)
- CONAPO Zonas Metropolitanas catalog
- INEGI geographic catalogs
- Localidades catalog with pagination
- SQLite-based data loading for all catalogs

### Changed
- Migrated webapp to SvelteKit (webapp-svelte)
- Improved Banxico catalog APIs
- Synchronized versions across all packages

## [0.2.0] - 2025-12-15

### Added
- TypeScript package
- Banxico catalogs (tipo de cambio, TIIE, CETES, UDI, inflacion)
- Tax calculators (ISR, IVA, IEPS, RESICO)
- IMSS/INFONAVIT calculators

## [0.1.0] - 2025-11-08

### Added
- Initial Python package
- RFC, CURP, CLABE, NSS validators
- Basic catalog infrastructure

[Unreleased]: https://github.com/openbancor/catalogmx/compare/v0.5.1...HEAD
[0.5.1]: https://github.com/openbancor/catalogmx/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/openbancor/catalogmx/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/openbancor/catalogmx/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/openbancor/catalogmx/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/openbancor/catalogmx/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/openbancor/catalogmx/releases/tag/v0.1.0
