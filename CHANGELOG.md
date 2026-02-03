# Changelog

All notable changes to catalogmx will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/openbancor/catalogmx/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/openbancor/catalogmx/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/openbancor/catalogmx/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/openbancor/catalogmx/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/openbancor/catalogmx/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/openbancor/catalogmx/releases/tag/v0.1.0
