# catalogmx

**Comprehensive Mexican Data Validators and Official Catalogs Library**

A complete multi-language library (Python 3.10+ | TypeScript 5.0+) for validating Mexican identifiers and accessing official catalogs from SAT, Banxico, INEGI, SEPOMEX, and other government agencies.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org)
[![License](https://img.shields.io/badge/license-BSD--2--Clause-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-catalogmx-blue.svg)](https://pypi.org/project/catalogmx/)
[![NPM](https://img.shields.io/badge/npm-catalogmx-red.svg)](https://www.npmjs.com/package/catalogmx)

**Languages**: [English](#) | [Español](README.es.md)

---

## Overview

**catalogmx** provides production-ready tools for Mexican data validation and official catalog access:

- **4 Validators**: RFC, CURP, CLABE, NSS with complete algorithms
- **40+ Official Catalogs**: SAT (CFDI 4.0, Comercio Exterior, Carta Porte, Nómina), INEGI, SEPOMEX, Banxico
- **170,505+ Records**: Complete databases including 157K postal codes, 2.4K municipalities, 10K+ localities with GPS
- **Multi-language Support**: Python and TypeScript with identical APIs
- **Type-Safe**: Full type hints (PEP 604) and TypeScript declarations
- **Production Ready**: Tested, documented, and actively maintained

---

## Quick Start

### Python

```bash
pip install catalogmx
```

```python
from catalogmx.validators import rfc, curp
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import LocalidadesCatalog

# Validate and generate RFC
is_valid = rfc.validate_rfc("XAXX010101000")
rfc_code = rfc.generate_rfc_persona_fisica(
    nombre="Juan",
    apellido_paterno="Pérez", 
    apellido_materno="López",
    fecha_nacimiento="1990-01-15"
)  # Returns: "PELJ900115XXX"

# Generate and validate CURP
curp_code = curp.generate_curp(
    nombre="Juan",
    apellido_paterno="Pérez",
    apellido_materno="García", 
    fecha_nacimiento="1990-05-15",
    sexo="H",
    estado="Jalisco"
)  # Returns: "PEGJ900515HJCRRN09"

# Search postal codes
postal_codes = CodigosPostales.get_by_cp("06700")
print(postal_codes[0]['asentamiento'])  # "Roma Norte"

# Geographic search with GPS coordinates
localities = LocalidadesCatalog.get_by_coordinates(
    lat=19.4326, lon=-99.1332, radio_km=10
)
```

### TypeScript

```bash
npm install catalogmx
```

```typescript
import { validateRFC, validateCURP } from 'catalogmx';
import { RegimenFiscalCatalog } from 'catalogmx/catalogs';

const isValid = validateRFC('XAXX010101000');
const regimen = RegimenFiscalCatalog.getRegimen('605');
```

---

## Features

### Validators

**RFC (Registro Federal de Contribuyentes)**
- Persona Física (13 characters) and Persona Moral (12 characters)
- Homoclave calculation using Módulo 11 algorithm
- Check digit validation
- 170+ cacophonic word replacement
- Foreign resident support

**CURP (Clave Única de Registro de Población)**
- 18-character validation with complete RENAPO algorithm
- **CURP generation** from name, birth date, gender, and state
- Check digit calculation and verification (position 18)
- State code validation (32 Mexican states)
- 70+ inconvenient words handling (Anexo 2)
- Birth date, gender, and state extraction

**CLABE (Clave Bancaria Estandarizada)**
- 18-digit bank account validation
- Modulo 10 check digit algorithm
- Bank, branch, and account number extraction
- Integration with Banxico bank catalog (110 institutions)

**NSS (Número de Seguridad Social)**
- 11-digit IMSS number validation
- Modified Luhn algorithm check digit
- Subdelegation, year, and serial extraction

### Official Catalogs

**SAT (Tax Administration Service)**
- CFDI 4.0 Core: 9 catalogs (tax regimes, CFDI uses, payment methods, etc.)
- Comercio Exterior 2.0: 8 catalogs (Incoterms, countries, currencies, customs)
- Carta Porte 3.0: 7 catalogs (airports, seaports, highways, dangerous goods)
- Nómina 1.2: 7 catalogs (payroll types, contracts, work shifts, IMSS risk levels)

**INEGI (Geographic Data)**
- Complete municipalities: 2,478 records with population data (Census 2020)
- Localities with GPS: 10,635 localities (1,000+ inhabitants)
- Geographic search by coordinates
- Urban/rural classification

**SEPOMEX (Postal Service)**
- Complete postal codes: 157,252 records
- All 32 Mexican states (100% coverage)
- Search by postal code, municipality, or state

**Banxico (Central Bank)**
- Financial institutions: 110 banks
- SPEI participation status
- Bank code validation

---

## Statistics

| Catalog | Records | Coverage | Size |
|---------|---------|----------|------|
| SEPOMEX Postal Codes | 157,252 | 100% | 43.53 MB |
| INEGI Municipalities | 2,478 | 100% | 0.98 MB |
| INEGI Localities | 10,635 | 86% population | 5.22 MB |
| SAT CFDI 4.0 | ~30 | Complete | <1 MB |
| SAT Comercio Exterior | ~500 | Complete | <1 MB |
| SAT Carta Porte | ~3,400 | Complete | <2 MB |
| SAT Nómina | ~100 | Complete | <1 MB |
| Banxico Banks | 110 | Complete | <1 MB |
| **TOTAL** | **170,505+** | **126M population** | **~50 MB** |

---

## Installation

### Python

#### From PyPI (Recommended)

```bash
pip install catalogmx
```

#### From Source

```bash
git clone https://github.com/openbancor/catalogmx.git
cd catalogmx/packages/python
pip install -e .
```

**Requirements**:
- Python 3.10 or higher
- unidecode (for RFC generation)
- click (for CLI)

### TypeScript/JavaScript

#### NPM

```bash
npm install catalogmx
```

#### Yarn

```bash
yarn add catalogmx
```

**Requirements**:
- Node.js 16 or higher
- TypeScript 5.0+ (optional, type definitions included)

---

## Documentation

### Getting Started
- [Installation Guide](docs/installation.rst)
- [Quick Start Guide](docs/quickstart.rst)
- [API Reference](docs/api/)

### Guides
- [Architecture Guide](docs/guides/architecture.md)
- [Developer's Guide](docs/guides/developers-guide.md)
- [Catalog Updates](docs/guides/catalog-updates.md)
- [CP-Locality Linking](docs/guides/cp-locality-linking.md)

### Catalogs
- [Catalog Overview](docs/catalogs/overview.md)
- [SEPOMEX Documentation](docs/catalogs/sepomex.md)
- [INEGI Documentation](docs/catalogs/inegi.md)
- [SAT Documentation](docs/catalogs/sat.md)

### Project
- [Roadmap](docs/roadmap.md)
- [Changelog](CHANGELOG.rst)
- [Catalog Changelog](docs/changelog-catalogs.md)
- [Contributing](CONTRIBUTING.rst)

---

## Usage Examples

### Address Validation

```python
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import MunicipiosCatalog

def validate_address(postal_code, municipality_name):
    """Validate Mexican address"""
    
    if not CodigosPostales.is_valid(postal_code):
        return False, "Invalid postal code"
    
    cp_info = CodigosPostales.get_by_cp(postal_code)[0]
    
    if municipality_name.lower() not in cp_info['municipio'].lower():
        return False, f"Postal code {postal_code} does not belong to {municipality_name}"
    
    return True, cp_info
```

### Geographic Analysis

```python
from catalogmx.catalogs.inegi import LocalidadesCatalog

# Find localities near a coordinate
nearby = LocalidadesCatalog.get_by_coordinates(
    lat=19.4326,      # Mexico City
    lon=-99.1332,
    radio_km=50
)

for locality in nearby[:5]:
    print(f"{locality['nom_localidad']}: {locality['distancia_km']} km")
    print(f"  Population: {locality['poblacion_total']:,}")
```

### CFDI Validation

```python
from catalogmx.validators import rfc
from catalogmx.catalogs.sat.cfdi_4 import (
    RegimenFiscalCatalog,
    UsoCFDICatalog,
    FormaPagoCatalog
)

def validate_cfdi_data(rfc_code, tax_regime, cfdi_use, payment_method):
    """Validate CFDI invoice data"""
    
    errors = []
    
    if not rfc.validate_rfc(rfc_code):
        errors.append("Invalid RFC")
    
    if not RegimenFiscalCatalog.is_valid(tax_regime):
        errors.append(f"Invalid tax regime: {tax_regime}")
    
    if not UsoCFDICatalog.is_valid(cfdi_use):
        errors.append(f"Invalid CFDI use: {cfdi_use}")
    
    if not FormaPagoCatalog.is_valid(payment_method):
        errors.append(f"Invalid payment method: {payment_method}")
    
    return len(errors) == 0, errors
```

---

## Roadmap

### Version 0.3.0 (Current - November 2025)

**Completed**:
- Complete SEPOMEX postal codes (157,252 records)
- Complete INEGI municipalities (2,478 records)
- INEGI localities with GPS coordinates (10,635 records)
- Geographic search by coordinates
- Population and housing data (Census 2020)
- Urban/rural classification
- Bilingual documentation

### Version 0.4.0 (Planned - Q1 2025)

**Planned**:
- SQLite implementation for large catalogs
- Geocoding integration (add GPS to postal codes)
- Pre-computed CP-Locality correspondence table
- TypeScript catalog synchronization
- REST API server examples
- GraphQL API examples

### Version 0.5.0 (Future - Q2-Q3 2025)

**Planned**:
- Additional validators (ISAN, license plates, MRZ)
- IFT (telecommunications) catalogs
- IMSS (social security) catalogs
- TIGIE (customs tariff) catalog
- Historical catalog versions
- ML-based address normalization
- WebAssembly compilation for validators

**Full Roadmap**: See [docs/roadmap.md](docs/roadmap.md) for detailed roadmap by catalog and implementation strategy.

---

## SQLite Strategy

For catalogs with >10,000 records, SQLite option will be provided in v0.4.0:

**Benefits**:
- 30-40% smaller file size
- 10-100x faster queries
- Spatial indexes (R-tree for GPS)
- Complex queries without loading entire dataset
- Memory efficient

**Planned Implementation** (v0.4.0):

| Catalog | JSON Size | SQLite Size | Performance Gain |
|---------|-----------|-------------|------------------|
| SEPOMEX | 43.53 MB | ~25 MB | 100x faster queries |
| Localities | 5.22 MB | ~3 MB | Spatial index support |

---

## Catalog Update Strategy

### Update Frequencies

| Catalog | Frequency | Source | Auto-update |
|---------|-----------|--------|-------------|
| SEPOMEX | Monthly | correosdemexico.gob.mx | Planned (v0.4.0) |
| INEGI | Annually | inegi.org.mx | Manual |
| SAT CFDI | Quarterly | sat.gob.mx | Planned (v0.4.0) |
| Banxico | Quarterly | banxico.org.mx | Planned (v0.4.0) |

### Current Process

```bash
# Check for updates
python scripts/check_catalog_updates.py

# Download and process
python scripts/fetch_sat_catalogs.py
python scripts/process_sepomex_file.py
python scripts/process_inegi_municipios.py
```

**Automated updates planned for v0.4.0**

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.rst](CONTRIBUTING.rst) for guidelines.

### Development Setup

```bash
git clone https://github.com/openbancor/catalogmx.git
cd catalogmx

# Python
cd packages/python
pip install -e ".[dev]"
pytest

# TypeScript
cd packages/typescript
npm install
npm test
```

### Adding New Catalogs

See [Developer's Guide](docs/guides/developers-guide.md) for detailed instructions on:
- Creating catalog JSON files
- Implementing catalog classes
- Writing tests
- Updating documentation

---

## Project Structure

```
catalogmx/
├── README.md                   # This file
├── LICENSE                     # BSD 2-Clause
├── CONTRIBUTING.rst            # Contribution guidelines
├── CHANGELOG.rst               # Project changelog
│
├── docs/                       # Documentation
│   ├── guides/                 # Technical guides
│   ├── catalogs/              # Catalog documentation
│   ├── api/                    # API reference
│   ├── roadmap.md             # Detailed roadmap
│   └── releases/              # Release notes
│
├── packages/
│   ├── python/                # Python implementation
│   │   ├── catalogmx/
│   │   ├── tests/
│   │   ├── pyproject.toml     # Modern Python config
│   │   └── requirements.txt
│   │
│   ├── typescript/            # TypeScript implementation
│   │   ├── src/
│   │   ├── tests/
│   │   └── package.json
│   │
│   └── shared-data/           # Catalog JSON data
│       ├── sepomex/          # 157K postal codes
│       ├── inegi/            # Municipalities & localities
│       ├── sat/              # Tax catalogs
│       └── banxico/          # Banking data
│
└── scripts/                   # Processing scripts
    ├── process_sepomex_file.py
    ├── process_inegi_municipios.py
    └── process_inegi_localidades.py
```

---

## License

BSD 2-Clause License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

### Official Data Sources

- **SAT** - Servicio de Administración Tributaria
- **INEGI** - Instituto Nacional de Estadística y Geografía
- **SEPOMEX** - Servicio Postal Mexicano
- **Banxico** - Banco de México
- **RENAPO** - Registro Nacional de Población

### Technology Stack

- Python 3.10+ with modern type hints (PEP 604)
- TypeScript 5.0+
- Zero external dependencies (validators)
- Lazy loading architecture
- JSON-based catalog storage

---

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/openbancor/catalogmx/issues)
- **Email**: luisfernando@informind.com

---

## Project Statistics

```
Package Size:     ~50 MB (all catalogs)
Total Catalogs:   43
Total Records:    170,505+
Population:       126,014,024 (100% coverage)
GPS Localities:   10,635
Municipalities:   2,478
Postal Codes:     157,252
Banks:            110
```

---

**catalogmx** v0.3.0 | November 2025 | Made for the Mexican developer community

