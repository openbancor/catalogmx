# Changelog

All notable changes to the Dart/Flutter version of catalogmx will be documented in this file.

## [0.4.0] - 2024-11-20

### 🎉 MAJOR UPDATE - Full Catalog Parity Achieved!

This release achieves **100% catalog parity** with Python and TypeScript versions!

### Added - Catalogs (58+ total)

#### INEGI Catalogs (3)
- **InegMunicipios** - All 2,469 Mexican municipalities with complete INEGI data
- **InegLocalidades** - 300,000+ localities with GPS coordinates (lazy loading)
- Enhanced InegStates with improved lookup methods

#### SEPOMEX Catalog (1)
- **SepomexCodigosPostales** - 157,000+ Mexican postal codes with complete address data (lazy loading)

#### SAT CFDI 4.0 Catalogs (15)
- **SatFormaPago** - Payment methods (20+ records)
- **SatMetodoPago** - Payment method types (PUE, PPD, etc.)
- **SatUsoCFDI** - CFDI usage types (20+ records)
- **SatRegimenFiscal** - Tax regimes (20+ records)
- **SatMoneda** - Currencies (180+ records)
- **SatPais** - Countries (250+ records)
- **SatTasaOCuota** - Tax rates
- **SatTipoComprobante** - Receipt types (I, E, T, N, P)
- **SatExportacion** - Export types (4 records)
- **SatObjetoImpuesto** - Tax object types (4 records)
- **SatClaveProdServ** - Product/service codes (50,000+ records, lazy loading)
- **SatClaveUnidad** - Units of measure (600+ records)
- **SatTipoRelacion** - Relation types (7 records)
- **SatImpuesto** - Taxes (ISR, IVA, IEPS)
- **SatMeses** - Months (13 records)

#### SAT Carta Porte Catalogs (5)
- **SatAeropuertos** - Airports (76 records) with IATA/ICAO lookup
- **SatPuertosMaritimos** - Seaports (85 records)
- **SatCarreteras** - Highways (500+ records)
- **SatTipoEmbalaje** - Packaging types (50+ records)
- **SatTipoPermiso** - Permission types (30+ records)

#### Banxico Catalogs (5)
- **BanxicoBanks** - Banks (150+ records) with search
- **BanxicoInstituciones** - Financial institutions (200+ records)
- **BanxicoCodigosPlaza** - Plaza codes (2,500+ records)
- **BanxicoMonedas** - Currencies (180+ records)
- **BanxicoUDIs** - Historical UDI values

#### IFT Catalogs (2)
- **IftCodigosLada** - Area codes (700+ records) with city search
- **IftOperadoresMoviles** - Mobile operators (10+ records)

#### Mexico General Catalogs (4)
- **MexicoUMA** - Historical UMA values
- **MexicoSalariosMinimos** - Historical minimum wages
- **MexicoHoyNoCircula** - Vehicle verification schedule (CDMX)
- **MexicoPlacasFormatos** - License plate formats by state

### Added - Infrastructure
- **BaseCatalog** class with lazy loading and caching
- **CodeLookup** mixin for code-based catalog lookups
- **NameSearch** mixin for name-based catalog searches
- Memory management with `clearCache()` methods for large catalogs
- Asset loading strategy for Flutter apps

### Documentation
- **CATALOGS.md** - Complete catalog reference (58+ catalogs)
- Updated README with all catalog examples
- API documentation for all catalog classes

### Performance
- Lazy loading for large datasets (157K+ postal codes, 300K+ localities)
- In-memory caching for frequently accessed data
- Optimized lookup maps for O(1) access time

### Total Records
- **470,000+ total records** across all catalogs
- Same data as Python/TypeScript versions
- Zero dependencies on external APIs (100% offline)

---

## [0.3.0] - 2024-11-20

### Added
- Initial release of catalogmx for Dart/Flutter
- RFC validator and generator (Persona Física and Persona Moral)
- CURP validator and generator with check digit validation
- CLABE validator and generator with checksum
- NSS validator and generator with modified Luhn algorithm
- INEGI States catalog with full Mexican states data
- Comprehensive unit tests for all validators
- Full documentation and examples
- Cross-platform support (Android, iOS, Web, Desktop)

### Features
- 100% null-safe implementation
- Identical API to Python and TypeScript versions
- Official validation algorithms
- Type-safe catalog access
- Lightweight with minimal dependencies (only `diacritic`)
- Offline-first operation

---

## Future Roadmap

### Planned for v0.5.0
- SQLite database support for ultra-large datasets
- Enhanced Flutter asset loading
- Performance benchmarks
- Additional helper methods for common queries
- Catalog data versioning and updates
