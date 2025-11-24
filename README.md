# catalogmx

## Enterprise-Grade Mexican Data Validation and Official Catalog Library

**catalogmx** is a comprehensive, production-ready library providing validated access to Mexican government data sources and robust validation tools for Mexican identification systems. Built for financial institutions, fintech applications, e-commerce platforms, and enterprise systems requiring compliance with Mexican regulations.

[![Python Version](https://img.shields.io/pypi/pyversions/catalogmx)](https://pypi.org/project/catalogmx/)
[![PyPI Version](https://img.shields.io/pypi/v/catalogmx)](https://pypi.org/project/catalogmx/)
[![NPM Version](https://img.shields.io/npm/v/catalogmx)](https://www.npmjs.com/package/catalogmx)
[![pub.dev Version](https://img.shields.io/pub/v/catalogmx)](https://pub.dev/packages/catalogmx)
[![Test Coverage](https://img.shields.io/badge/coverage-93.78%25-brightgreen)](https://github.com/openbancor/catalogmx)
[![Tests Passing](https://img.shields.io/badge/tests-1206%20passing-brightgreen)](https://github.com/openbancor/catalogmx)
[![License](https://img.shields.io/badge/license-BSD--2--Clause-blue.svg)](LICENSE)

**Languages**: [English](#) | [Español](README.es.md)

---

## Executive Summary

**catalogmx** delivers enterprise-grade validation and data access for Mexican regulatory compliance and business operations:

- **4 Production-Ready Validators**: RFC, CURP, CLABE, NSS with complete official algorithms
- **58 Official Government Catalogs**: SAT, INEGI, SEPOMEX, Banxico, IFT, National Regulations
- **470,000+ Verified Records**: Complete databases with 157K postal codes, 300K localities, 2.4K municipalities
- **Multi-Platform Support**: Python 3.10+, TypeScript 5.0+, and Dart/Flutter 3.0+ with identical APIs
- **Type-Safe Implementation**: Full type hints (PEP 604), TypeScript declarations, and Dart null-safety
- **Enterprise Quality**: 93.78% test coverage (1,206 tests across all platforms), comprehensive documentation, production-ready

---

## Business Value

### Financial Services
- **KYC/AML Compliance**: Validate RFC, CURP, and NSS for customer onboarding
- **SPEI Transfers**: CLABE validation with bank directory integration
- **Tax Compliance**: Complete SAT catalog access for CFDI generation
- **Payroll Processing**: Validated IMSS data and nómina catalogs

### E-Commerce & Logistics
- **Address Validation**: 157K postal codes with municipality and state data
- **Shipping Integration**: Geographic search with GPS coordinates
- **Customs Documentation**: Comercio Exterior catalogs for international shipments
- **Route Planning**: Carta Porte catalogs with airports, seaports, and highways

### Government & Public Sector
- **Citizen Services**: CURP and RFC validation for government applications
- **Geographic Analysis**: Complete INEGI municipal and locality data
- **Regulatory Compliance**: Up-to-date SAT catalogs for tax systems
- **Data Quality**: Validated against official government sources

### Technology Platforms
- **Fintech Applications**: Banking, payments, and financial services
- **SaaS Platforms**: Multi-tenant systems requiring Mexican data
- **API Services**: RESTful and GraphQL backends
- **Mobile Applications**: Lightweight validators with offline capability

---

## Installation

### Python

**Recommended (using uv - 10-100x faster):**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install catalogmx
uv pip install catalogmx
```

**Using pip:**
```bash
pip install catalogmx
```

**Development install:**
```bash
cd packages/python
uv pip install -e ".[dev]"
```

### TypeScript/JavaScript

```bash
npm install catalogmx
```

**Yarn:**
```bash
yarn add catalogmx
```

**Development:**
```bash
cd packages/typescript
npm install
npm run build
```

### Dart/Flutter

**Flutter:**
```bash
flutter pub add catalogmx
```

**Dart only:**
```bash
dart pub add catalogmx
```

**Manual (pubspec.yaml):**
```yaml
dependencies:
  catalogmx: ^0.4.0
```

**Development:**
```bash
cd packages/dart
dart pub get
dart test
```

---

## Core Validators

### RFC (Registro Federal de Contribuyentes)

Validate Mexican tax identification numbers for individuals and corporations.

```python
from catalogmx.validators import rfc

# Validate existing RFC
is_valid = rfc.validate_rfc("GODE561231GR8")  # Returns: True

# Generate RFC for individual (Persona Física)
rfc_code = rfc.generate_rfc_persona_fisica(
    nombre="Juan",
    apellido_paterno="García",
    apellido_materno="López",
    fecha_nacimiento="1990-05-15"
)  # Returns: "GALJ900515XXX"

# Generate RFC for corporation (Persona Moral)
rfc_code = rfc.generate_rfc_persona_moral(
    razon_social="Tecnología Sistemas Integrales S.A.",
    fecha_constitucion="2009-09-09"
)  # Returns: "TSI090909XXX"

# Detect RFC type
rfc_type = rfc.detect_rfc_type("GODE561231GR8")  # Returns: "fisica"
```

**Features:**
- Complete Módulo 11 homoclave algorithm
- Check digit validation
- 170+ cacophonic word replacement
- Support for foreign residents
- Type detection (física/moral)

### CURP (Clave Única de Registro de Población)

Validate and generate Mexican national identification numbers.

```python
from catalogmx.validators import curp

# Validate existing CURP
is_valid = curp.validate_curp("GORS561231HVZNNL00")  # Returns: True

# Generate CURP
curp_code = curp.generate_curp(
    nombre="Juan",
    apellido_paterno="García",
    apellido_materno="López",
    fecha_nacimiento="1990-05-15",
    sexo="H",
    estado="Jalisco"
)  # Returns: "GALJ900515HJCRPN01"

# Extract information from CURP
info = curp.get_curp_info("GORS561231HVZNNL00")
# Returns: {
#     'birth_date': datetime.date(1956, 12, 31),
#     'gender': 'H',
#     'state': 'Veracruz',
#     'is_valid': True
# }
```

**Features:**
- Complete RENAPO algorithm implementation
- 18-position validation
- Check digit verification (position 18)
- 32 Mexican state code validation
- 70+ inconvenient word handling
- Birth date, gender, and state extraction

### CLABE (Clave Bancaria Estandarizada)

Validate Mexican bank account numbers for electronic transfers.

```python
from catalogmx.validators import clabe

# Validate CLABE
is_valid = clabe.validate_clabe("002010077777777771")  # Returns: True

# Generate CLABE with check digit
clabe_number = clabe.generate_clabe(
    bank_code="002",      # Banamex
    branch_code="010",
    account_number="07777777777"
)  # Returns: "002010077777777771"

# Extract CLABE components
info = clabe.get_clabe_info("002010077777777771")
# Returns: {
#     'bank_code': '002',
#     'branch_code': '010',
#     'account_number': '07777777777',
#     'check_digit': '1',
#     'clabe': '002010077777777771'
# }
```

**Features:**
- Modulo 10 check digit validation
- Bank code verification
- Integration with Banxico SPEI directory
- Component extraction (bank, branch, account)
- Check digit generation

### NSS (Número de Seguridad Social)

Validate Mexican social security numbers.

```python
from catalogmx.validators import nss

# Validate NSS
is_valid = nss.validate_nss("12345678903")  # Returns: True

# Generate NSS with check digit
nss_number = nss.generate_nss(
    subdelegation="12",
    year="34",
    serial="56",
    sequential="7890"
)  # Returns: "12345678903"

# Extract NSS components
info = nss.get_nss_info("12345678903")
# Returns: {
#     'subdelegation': '12',
#     'year': '34',
#     'serial': '56',
#     'sequential': '7890',
#     'check_digit': '3',
#     'nss': '12345678903'
# }
```

**Features:**
- Modified Luhn algorithm implementation
- IMSS subdelegation validation
- Component extraction
- Check digit generation and verification

---

## Official Catalogs

### SAT (Servicio de Administración Tributaria) - 31 Catalogs

#### CFDI 4.0 (Digital Tax Receipts) - 16 Catalogs
- **Tax Regimes** (c_RegimenFiscal): 33 fiscal regimes
- **CFDI Uses** (c_UsoCFDI): 30+ valid uses
- **Payment Methods** (c_FormaPago / c_MetodoPago): 99 payment forms, 3 payment methods
- **Tax Types** (c_Impuesto): Federal and local taxes
- **Product/Service Codes** (c_ClaveProdServ): 52,896 codes with SQLite FTS5 search
- **Unit Codes** (c_ClaveUnidad): 2,400+ measurement units
- **Document Types** (c_TipoComprobante): Invoice types
- **Tax Objects** (c_ObjetoImp): Tax object codes
- **Export Types** (c_Exportacion): Export classifications
- **Relationship Types** (c_TipoRelacion): Document relationships
- **Tax Factors** (c_TipoFactor): Rate/quota/exemption
- **Rates and Quotas** (c_TasaOCuota): Applicable tax rates
- **Months** (c_Meses): Month codes
- **Periodicity** (c_Periodicidad): Payment periods

#### Comercio Exterior 2.0 (Foreign Trade) - 8 Catalogs
- **Incoterms**: 11 international commercial terms (ICC 2020)
- **Countries** (c_Pais): 250+ countries with ISO 3166-1 codes
- **Currencies** (c_Moneda): 180+ currencies with ISO 4217 codes
- **Customs Declarations** (c_ClavePedimento): 40+ customs procedure codes
- **Customs Units** (c_UnidadAduana): 30+ measurement units for customs
- **Transfer Motives** (c_MotivoTraslado): Transfer reasons for type T documents
- **Tax ID Types** (c_RegistroIdentTrib): Foreign tax identification types
- **USA/Canada States**: US states and Canadian provinces

#### Carta Porte 3.0 (Transportation Waybill) - 7 Catalogs
- **Airports** (c_CodigoTransporteAereo): Mexican and international airports
- **Seaports** (c_NumAutorizacionNaviero): Maritime ports
- **Federal Highways** (c_Carreteras): Federal highway network
- **Dangerous Materials** (c_MaterialPeligroso): UN hazardous materials codes
- **Packaging Types** (c_TipoEmbalaje): Packaging classifications
- **Transport Permits** (c_TipoPermiso): Transport authorization types
- **Vehicle Configurations** (c_ConfigAutotransporte): Truck configurations

#### Nómina 1.2 (Payroll) - 7 Catalogs
- **Banks** (c_Banco): Banking institutions for payroll
- **Payment Periodicity** (c_PeriodicidadPago): Payment frequencies
- **Job Risk Levels** (c_RiesgoPuesto): IMSS risk classifications
- **Contract Types** (c_TipoContrato): Employment contract types
- **Work Shifts** (c_TipoJornada): Shift types (day, night, mixed)
- **Payroll Types** (c_TipoNomina): Ordinary and extraordinary
- **Regime Types** (c_TipoRegimen): Social security regimes

### INEGI (National Statistics Institute) - 4 Catalogs

- **Municipalities** (Municipios): 2,478 municipalities with population data (Census 2020)
- **Localities** (Localidades): 10,635 localities (1,000+ inhabitants) with GPS coordinates
- **States** (Estados): 32 Mexican states with INEGI codes
- **Geographic Search**: Coordinate-based locality search with radius filtering

### SEPOMEX (Mexican Postal Service) - 2 Catalogs

- **Postal Codes** (Códigos Postales): 157,252 postal codes with complete address data
- **Postal Code Database**: SQLite version for high-performance queries

### Banxico (Bank of Mexico) - 5 Catalogs

- **Banks** (Instituciones Bancarias): 110 financial institutions
- **SPEI Participants**: Electronic payment system directory
- **Plaza Codes** (Códigos de Plaza): 463 geographic banking codes
- **Financial Institutions** (Instituciones Financieras): 20+ institution types with regulators
- **Currencies** (Monedas y Divisas): International currencies with exchange rate indicators
- **UDI Values** (Unidades de Inversión): Historical UDI values (1995-2025)

### IFT (Telecommunications Institute) - 2 Catalogs

- **Mobile Operators** (Operadores Móviles): Licensed telecommunications operators

### Mexico National - 4 Catalogs

- **Minimum Wages** (Salarios Mínimos): Historical minimum wage data (2010-2025)
- **UMA** (Unidad de Medida y Actualización): Reference values (2017-2025)
- **Hoy No Circula**: Mexico City traffic restrictions with exemptions
- **License Plate Formats**: Official vehicle plate formats by state

---

## Technical Specifications

### Architecture

- **Hybrid Storage**: JSON for small catalogs, SQLite with FTS5 for large datasets (>10K records)
- **Lazy Loading**: Catalogs loaded on-demand to minimize memory footprint
- **Type Safety**: Complete type hints (Python) and TypeScript declarations
- **Zero External Dependencies**: Validators are standalone (only unidecode for RFC/CURP generation)
- **Cross-Platform**: Works on Linux, macOS, Windows, and web browsers

### Performance

- **Package Size**: 108KB (Python wheel), minimal footprint
- **Memory Efficient**: Lazy loading prevents unnecessary data loading
- **Fast Queries**: SQLite with FTS5 for full-text search in large catalogs
- **Search Performance**: <10ms for indexed queries on SQLite catalogs

### Quality Assurance

- **Test Coverage**: 93.78% (926 Python tests + 221 TypeScript tests)
- **50+ Modules**: 100% test coverage
- **CI/CD**: Automated testing on Python 3.10-3.13 and Node 18+
- **Production Validated**: Used in production environments

---

## Use Cases

### Financial Technology (Fintech)

**Customer Onboarding (KYC)**
```python
from catalogmx.validators import rfc, curp, nss

# Validate customer identification
rfc_valid = rfc.validate_rfc(customer_rfc)
curp_valid = curp.validate_curp(customer_curp)
nss_valid = nss.validate_nss(customer_nss)

if all([rfc_valid, curp_valid, nss_valid]):
    # Proceed with onboarding
    pass
```

**SPEI Transfers**
```python
from catalogmx.validators import clabe
from catalogmx.catalogs.banxico import BankCatalog

# Validate beneficiary account
if clabe.validate_clabe(beneficiary_clabe):
    clabe_info = clabe.get_clabe_info(beneficiary_clabe)
    bank = BankCatalog.get_bank_by_code(clabe_info['bank_code'])
    
    if bank['spei']:
        # Process SPEI transfer
        pass
```

### E-Commerce & Marketplaces

**Address Validation**
```python
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import MunicipiosCatalog

# Validate shipping address
postal_data = CodigosPostales.get_by_cp(shipping_postal_code)

if postal_data:
    verified_state = postal_data[0]['estado']
    verified_municipality = postal_data[0]['municipio']
    
    # Calculate shipping costs by zone
    pass
```

### Tax Compliance & Accounting

**CFDI Generation**
```python
from catalogmx.catalogs.sat.cfdi_4 import (
    RegimenFiscalCatalog,
    UsoCFDICatalog,
    FormaPagoCatalog
)

# Validate tax regime
regimen = RegimenFiscalCatalog.get_regimen_fiscal(customer_regimen)
if regimen and RegimenFiscalCatalog.is_valid_for_persona_fisica(customer_regimen):
    # Generate CFDI
    pass

# Validate CFDI use
uso_valid = UsoCFDICatalog.is_valid(cfdi_use_code)
```

### Logistics & International Trade

**Customs Documentation**
```python
from catalogmx.catalogs.sat.comercio_exterior import (
    IncotermsValidator,
    PaisCatalog,
    MonedaCatalog
)

# Validate international shipment
incoterm_valid = IncotermsValidator.is_valid("CIF")
country_valid = PaisCatalog.is_valid("USA")
currency_valid = MonedaCatalog.is_valid("USD")

# Validate currency conversion
conversion_result = MonedaCatalog.validate_conversion_usd({
    "moneda": "MXN",
    "total": 20000,
    "tipo_cambio_usd": 20.0,
    "total_usd": 1000
})
```

---

## API Documentation

### Validators Module

#### RFC Validator

**Methods:**
- `validate_rfc(rfc: str, check_checksum: bool = True) -> bool`
- `generate_rfc_persona_fisica(nombre, apellido_paterno, apellido_materno, fecha_nacimiento) -> str`
- `generate_rfc_persona_moral(razon_social, fecha_constitucion) -> str`
- `detect_rfc_type(rfc: str) -> str | None`
- `is_valid_rfc(rfc: str) -> bool` (alias)

#### CURP Validator

**Methods:**
- `validate_curp(curp: str, check_digit: bool = True) -> bool`
- `generate_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado) -> str`
- `get_curp_info(curp: str) -> dict | None`
- `is_valid_curp(curp: str) -> bool` (alias)

#### CLABE Validator

**Methods:**
- `validate_clabe(clabe: str) -> bool`
- `generate_clabe(bank_code, branch_code, account_number) -> str`
- `get_clabe_info(clabe: str) -> dict | None`

#### NSS Validator

**Methods:**
- `validate_nss(nss: str) -> bool`
- `generate_nss(subdelegation, year, serial, sequential) -> str`
- `get_nss_info(nss: str) -> dict | None`

### Catalogs Module

All catalogs follow a consistent API pattern:

```python
# Standard catalog methods
catalog.get_all() -> list[dict]                    # Get all records
catalog.get_by_code(code: str) -> dict | None      # Get by code/ID
catalog.is_valid(code: str) -> bool                # Validate code exists
catalog.search(query: str) -> list[dict]           # Search (if applicable)
```

**Example:**
```python
from catalogmx.catalogs.sat.cfdi_4 import RegimenFiscalCatalog

# Get all regimes
regimenes = RegimenFiscalCatalog.get_all()

# Get specific regime
regimen = RegimenFiscalCatalog.get_regimen_fiscal("605")

# Validate regime exists
is_valid = RegimenFiscalCatalog.is_valid("605")

# Check if valid for person type
valid_for_fisica = RegimenFiscalCatalog.is_valid_for_persona_fisica("605")
```

---

## Production Deployment

### System Requirements

**Python:**
- Python 3.10 or higher
- 200MB disk space (with all catalogs)
- Minimal memory footprint (lazy loading)

**TypeScript/Node.js:**
- Node.js 18 or higher
- npm 7 or higher

**Dart/Flutter:**
- Dart SDK 3.0 or higher
- Flutter 3.10 or higher (for Flutter apps)
- Works on iOS, Android, Web, macOS, Windows, Linux

### Dependencies

**Python Runtime:**
- `unidecode>=1.4.0` (RFC/CURP accent handling)
- `click>=8.0.0` (CLI interface)

**Python Development:**
- `pytest>=7.4.0` (testing)
- `pytest-cov>=4.1.0` (coverage)
- `black>=23.0.0` (formatting)
- `ruff>=0.1.0` (linting)

**TypeScript:**
- `better-sqlite3` (SQLite access)
- `sql.js` (WebAssembly SQLite)

### Performance Characteristics

| Operation | Performance | Notes |
|-----------|-------------|-------|
| RFC validation | <1ms | No external dependencies |
| CURP validation | <1ms | Complete algorithm |
| CLABE validation | <1ms | Modulo 10 check |
| Postal code lookup | <5ms | JSON (O(1) with index) |
| Geographic search | <10ms | SQLite with spatial index |
| Full-text search | <20ms | SQLite FTS5 |

### Scalability

- **Concurrent Requests**: Thread-safe, suitable for multi-threaded applications
- **Caching**: Catalogs loaded once per process
- **Memory Usage**: ~50-100MB with all catalogs loaded
- **Database Connections**: SQLite connection pooling supported

---

## Integration Examples

### FastAPI REST API

```python
from fastapi import FastAPI, HTTPException
from catalogmx.validators import rfc
from catalogmx.catalogs.sepomex import CodigosPostales

app = FastAPI(title="catalogmx API")

@app.get("/validate/rfc/{rfc_code}")
async def validate_rfc_endpoint(rfc_code: str):
    is_valid = rfc.validate_rfc(rfc_code)
    return {
        "rfc": rfc_code,
        "valid": is_valid,
        "type": rfc.detect_rfc_type(rfc_code) if is_valid else None
    }

@app.get("/postal-codes/{cp}")
async def get_postal_code(cp: str):
    data = CodigosPostales.get_by_cp(cp)
    if not data:
        raise HTTPException(status_code=404, detail="Postal code not found")
    return data
```

### Express.js (Node.js)

```typescript
import express from 'express';
import { validateRFC, validateCURP } from 'catalogmx';

const app = express();

app.get('/validate/rfc/:rfc', (req, res) => {
    const isValid = validateRFC(req.params.rfc);
    res.json({ rfc: req.params.rfc, valid: isValid });
});

app.listen(3000);
```

### Flutter/Dart

```dart
import 'package:catalogmx/catalogmx.dart';

// Validate RFC
final isValidRfc = validateRFC('GODE561231GR8');

// Generate RFC for individual
final rfc = generateRFC(
  nombre: 'Juan',
  apellidoPaterno: 'Garcia',
  apellidoMaterno: 'Lopez',
  fechaNacimiento: DateTime(1990, 5, 15),
);

// Validate CURP
final isValidCurp = validateCURP('GORS561231HVZNNL00');

// Generate CURP
final curp = generateCURP(
  nombre: 'Juan',
  apellidoPaterno: 'Garcia',
  apellidoMaterno: 'Lopez',
  fechaNacimiento: DateTime(1990, 5, 15),
  sexo: 'H',
  estado: 'Jalisco',
);

// Validate bank account (CLABE)
final isValidClabe = validateCLABE('002010077777777771');

// Access catalogs
final states = InegStates.getAll();
final cdmx = InegStates.getByCode('DF');
final municipalities = InegMunicipios.getByState('09');
final postalData = SepomexCodigosPostales.getByCP('06600');
```

### Django

```python
from django.http import JsonResponse
from catalogmx.validators import rfc

def validate_rfc_view(request, rfc_code):
    is_valid = rfc.validate_rfc(rfc_code)
    return JsonResponse({
        'rfc': rfc_code,
        'valid': is_valid
    })
```

---

## Testing & Quality Assurance

### Test Coverage

- **Overall Coverage**: 93.78% (Python), ~90% (TypeScript), ~85% (Dart)
- **Total Tests**: 926 (Python) + 221 (TypeScript) + 59 (Dart) = 1,206
- **Modules at 100%**: 50+ modules including all core validators
- **CI/CD**: Automated testing on Python 3.10-3.13, Node.js 18+, and Dart stable/beta

### Running Tests

```bash
# Python tests
cd packages/python
pytest tests/ --cov=catalogmx --cov-report=html

# TypeScript tests
cd packages/typescript
npm test

# Dart tests
cd packages/dart
dart test

# View coverage report
open packages/python/htmlcov/index.html
```

### Quality Metrics

- **Test Success Rate**: 100% (1,206 tests across all platforms)
- **Code Quality**: Python (Black + Ruff), TypeScript (ESLint + Prettier), Dart (dart analyze + format)
- **Type Safety**: Full mypy compliance (Python), TypeScript strict mode, Dart null-safety
- **Documentation**: Comprehensive inline and external docs

---

## Documentation

### Quick Reference
- **[Installation Guide](docs/installation.rst)** - Detailed setup instructions
- **[Quick Start Guide](docs/quickstart.rst)** - Get started in 5 minutes
- **[API Reference](docs/api/)** - Complete API documentation
- **[Testing Guide](docs/testing-coverage.md)** - Test suite and coverage
- **[Modern Packaging](docs/modern-packaging.md)** - Using uv and pyproject.toml
- **[Documentation Index](docs/DOCUMENTATION_INDEX.md)** - Complete documentation hub

### For Developers
- **[Developer Guide](docs/guides/developers-guide.md)** - Contributing guidelines
- **[Architecture](docs/guides/architecture.md)** - System design
- **[AI Agent Rules](CLAUDE.md)** - Guidelines for AI assistants

### External Resources
- **PyPI**: https://pypi.org/project/catalogmx/
- **npm**: https://www.npmjs.com/package/catalogmx
- **pub.dev**: https://pub.dev/packages/catalogmx
- **GitHub**: https://github.com/openbancor/catalogmx
- **Issues**: https://github.com/openbancor/catalogmx/issues

---

## Roadmap

### Current Version: 0.4.0 (Production Ready)

**Delivered:**
- 58 official catalogs with 470K+ records
- 4 production validators (RFC, CURP, CLABE, NSS)
- Multi-platform: Python 3.10+, TypeScript 5.0+, Dart/Flutter 3.0+
- 93.78% test coverage (1,206 tests)
- SQLite hybrid architecture with lazy loading
- Comprehensive publishing infrastructure (PyPI, NPM, pub.dev)
- CI/CD automation with GitHub Actions

### Version 0.5.0 (Q1 2025) - Enhancement

**Planned:**
- Complete SEPOMEX SQLite migration
- Postal code geocoding (lat/lon for all 157K codes)
- CP ↔ Locality linkage table
- Additional SAT catalogs
- Enhanced Flutter widgets for validation
- WebAssembly support for browser performance

### Version 0.6.0 (Q2-Q3 2025) - Expansion

**Planned:**
- New validators (vehicle plates, passport MRZ)
- IMSS catalogs (clinics, sub delegations)
- TIGIE complete tariff schedule (~10K codes)
- ML-powered address normalization
- Historical catalog versions
- Offline-first mobile support

### See [Product Roadmap](docs/roadmap.md) for detailed planning

---

## Support & Maintenance

### Release Schedule

- **Minor Versions** (0.x.0): Quarterly (every 3-4 months)
- **Patch Versions** (0.3.x): As needed (bug fixes, catalog updates)
- **Major Versions** (1.0.0): When API is declared stable

### Catalog Updates

Government catalogs are updated according to official publication schedules:

| Catalog | Update Frequency | Source |
|---------|-----------------|--------|
| SEPOMEX | Monthly | Correos de México |
| INEGI | Annually | INEGI Census |
| SAT CFDI | Quarterly | SAT Official |
| Banxico | Quarterly | Banco de México |

### Community Support

- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive guides and API references
- **Email Support**: luisfernando@informind.com

---

## License

BSD 2-Clause License. See [LICENSE](LICENSE) for details.

---

## Credits

### Official Data Sources

- **SAT** (Servicio de Administración Tributaria)
- **INEGI** (Instituto Nacional de Estadística y Geografía)
- **SEPOMEX** (Servicio Postal Mexicano)
- **Banxico** (Banco de México)
- **RENAPO** (Registro Nacional de Población)
- **IFT** (Instituto Federal de Telecomunicaciones)

### Maintainer

**Luis Fernando Barrera**
- Email: luisfernando@informind.com
- GitHub: [@openbancor](https://github.com/openbancor)

---

**catalogmx v0.4.0** | **Python + TypeScript + Dart** | **1,206 Tests** | **93.78% Coverage** | **Production Ready** | **BSD-2-Clause**
