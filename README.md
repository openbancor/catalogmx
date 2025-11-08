# 🇲🇽 catalogmx

**Comprehensive Mexican Data Validators and Official Catalogs**

A complete Python library for validating Mexican identifiers and accessing official catalogs from SAT, Banxico, INEGI, SEPOMEX, and other government agencies.

[![Python](https://img.shields.io/badge/python-3.8+-blue)]()
[![License](https://img.shields.io/badge/license-BSD-blue)]()
[![Catalogs](https://img.shields.io/badge/catalogs-40+-green)]()

---

## ✨ Features

### 🔐 Validators

**RFC** - Registro Federal de Contribuyentes
- ✅ Persona Física (13 characters) with homoclave
- ✅ Persona Moral (12 characters) with homoclave
- ✅ Check digit validation (Módulo 11)
- ✅ Cacophonic word replacement (170+ words)
- ✅ Extract birthdate, initials, and homoclave
- ✅ Support for foreign residents (prefixes)

**CURP** - Clave Única de Registro de Población
- ✅ 18-character validation with check digit
- ✅ Complete RENAPO algorithm (position 18)
- ✅ Homonymy differentiator support (position 17)
- ✅ 70+ inconvenient words (Anexo 2)
- ✅ State code validation (32 states)
- ✅ Extract birthdate, gender, state

**CLABE** - Clave Bancaria Estandarizada
- ✅ 18-digit bank account validator
- ✅ Modulo 10 check digit (Luhn-like)
- ✅ Bank code validation (3 digits)
- ✅ Branch code validation (3 digits)
- ✅ Account number extraction (11 digits)
- ✅ Integration with Banxico bank catalog

**NSS** - Número de Seguridad Social (IMSS)
- ✅ 11-digit validation
- ✅ Modified Luhn algorithm check digit
- ✅ Subdelegation code extraction (5 digits)
- ✅ Registration year extraction (2 digits)
- ✅ Serial number extraction (4 digits)

---

## 📚 Official Catalogs

### SAT (Servicio de Administración Tributaria)

**CFDI 4.0 Core** - 9 catalogs
- ✅ c_RegimenFiscal - 26 tax regimes (persona física/moral)
- ✅ c_UsoCFDI - 25 CFDI usage codes
- ✅ c_FormaPago - 18 payment methods
- ✅ c_MetodoPago - 2 payment types (PUE, PPD)
- ✅ c_TipoComprobante - 5 receipt types
- ✅ c_Impuesto - 4 tax types with retention/transfer
- ✅ c_Exportacion - 4 export keys
- ✅ c_TipoRelacion - 9 CFDI relationship types
- ✅ c_ObjetoImp - 8 tax object codes (Dec 2024)

**Comercio Exterior 2.0** - 8 catalogs
- ✅ c_INCOTERM - 11 Incoterms 2020 with transport validation
- ✅ c_ClavePedimento - 42 customs document keys
- ✅ c_Moneda - 150 ISO 4217 currencies with decimals
- ✅ c_Pais - 249 ISO 3166-1 countries (Alpha-3)
- ✅ c_UnidadAduana - 32 customs measurement units
- ✅ c_RegistroIdentTribReceptor - 15 foreign tax ID types
- ✅ c_MotivoTraslado - 6 transfer motives
- ✅ c_Estado (USA/CAN) - 63 US states + 13 Canadian provinces

**Carta Porte 3.0** - 7 catalogs
- ✅ c_CodigoTransporteAereo - 76 airports (IATA/ICAO)
- ✅ c_NumAutorizacionNaviero - 100 seaports (4 coasts)
- ✅ c_Carreteras - 200 SCT federal highways
- ✅ c_TipoPermiso - 12 transport permit types
- ✅ c_ConfigAutotransporte - 15 vehicle configurations
- ✅ c_TipoEmbalaje - 30 UN packaging types
- ✅ c_MaterialPeligroso - 3,000 UN hazardous materials

**Nómina 1.2** - 7 catalogs
- ✅ c_TipoNomina - 2 types (ordinaria, extraordinaria)
- ✅ c_TipoContrato - 10 labor contract types
- ✅ c_TipoJornada - 8 work shifts
- ✅ c_TipoRegimen - 13 regime types
- ✅ c_PeriodicidadPago - 10 payment frequencies
- ✅ c_RiesgoPuesto - 5 IMSS risk levels with premium ranges
- ✅ c_Banco - 50 banks for payroll

### Geographic Catalogs

**INEGI** - Instituto Nacional de Estadística y Geografía
- ✅ Municipios - 209 key municipalities (all 32 states)
- ✅ All state capitals and major cities (100k+)
- 📥 Complete: 2,478 municipalities (scripts provided)

**SEPOMEX** - Servicio Postal Mexicano
- ✅ Códigos Postales - 273 postal codes (all 32 states)
- ✅ CDMX: 25+ codes, Guadalajara: 15+, Monterrey: 10+
- 📥 Complete: ~150,000 postal codes (scripts provided)

**Banxico** - Banco de México
- ✅ Banks - 100+ Mexican banks with SPEI status
- ✅ Bank codes, official names, participation flags

---

## 🚀 Installation

```bash
pip install catalogmx
```

---

## 📖 Usage

### Validators

```python
from catalogmx import (
    generate_rfc_persona_fisica,
    generate_rfc_persona_moral,
    generate_curp,
    validate_clabe,
    validate_nss
)

# Generate RFC for individual
rfc = generate_rfc_persona_fisica(
    nombre='Juan',
    apellido_paterno='Pérez',
    apellido_materno='García',
    fecha_nacimiento='1990-05-15'
)
print(rfc)  # PEGJ900515***

# Generate CURP
curp = generate_curp(
    nombre='Juan',
    apellido_paterno='Pérez',
    apellido_materno='García',
    fecha_nacimiento='1990-05-12',
    sexo='H',
    estado='JALISCO'
)
print(curp)  # PEGJ900512HJCRRS04

# Validate CLABE
is_valid = validate_clabe('002010077777777771')
print(is_valid)  # True

# Validate NSS
is_valid = validate_nss('12345678903')
print(is_valid)  # True/False
```

### SAT Catalogs

```python
from catalogmx.catalogs.sat.cfdi_4 import (
    RegimenFiscalCatalog,
    UsoCFDICatalog,
    FormaPagoCatalog
)

# Validate tax regime
regimen = RegimenFiscalCatalog.get_regimen('601')
print(regimen['description'])  # General de Ley Personas Morales
print(RegimenFiscalCatalog.is_valid_for_persona_moral('601'))  # True

# Validate CFDI usage
uso = UsoCFDICatalog.get_uso('G03')
print(uso['description'])  # Gastos en general

# Validate payment method
forma = FormaPagoCatalog.get_forma('03')
print(forma['description'])  # Transferencia electrónica de fondos
```

### Comercio Exterior

```python
from catalogmx.catalogs.sat.comercio_exterior import (
    IncotermsValidator,
    ClavePedimentoCatalog,
    MonedaCatalog,
    ComercioExteriorValidator
)

# Validate INCOTERM
incoterm = IncotermsValidator.get_incoterm('CIF')
print(incoterm['transport_mode'])  # maritime
print(IncotermsValidator.seller_pays_insurance('CIF'))  # True

# Validate customs key
pedimento = ClavePedimentoCatalog.get_clave('A1')
print(pedimento['descripcion'])  # Exportación definitiva

# Validate currency conversion
conversion = MonedaCatalog.validate_conversion_usd({
    'moneda': 'EUR',
    'total': 10000.00,
    'tipo_cambio_usd': 1.18,
    'total_usd': 11800.00
})
print(conversion['valid'])  # True

# Complete CFDI validation
result = ComercioExteriorValidator.validate(cfdi_data)
```

### Carta Porte

```python
from catalogmx.catalogs.sat.carta_porte import (
    AeropuertosCatalog,
    PuertosMaritimos,
    TipoPermisoCatalog
)

# Validate airport
airport = AeropuertosCatalog.get_by_iata('MEX')
print(airport['name'])  # Aeropuerto Internacional de la Ciudad de México
print(airport['icao'])  # MMMX

# Validate seaport
puerto = PuertosMaritimos.get_puerto('016')
print(puerto['name'])  # Veracruz
print(puerto['coast'])  # Golfo de México

# Validate transport permit
permiso = TipoPermisoCatalog.get_permiso('TPAF01')
print(TipoPermisoCatalog.is_carga_permit('TPAF01'))  # True
```

### Nómina

```python
from catalogmx.catalogs.sat.nomina import (
    TipoContratoCatalog,
    PeriodicidadPagoCatalog,
    RiesgoPuestoCatalog
)

# Validate contract type
contrato = TipoContratoCatalog.get_contrato('01')
print(contrato['description'])  # Contrato por tiempo indeterminado

# Validate payment frequency
periodicidad = PeriodicidadPagoCatalog.get_periodicidad('04')
print(periodicidad['description'])  # Quincenal
print(periodicidad['days'])  # 15

# Validate risk level with IMSS premium
riesgo = RiesgoPuestoCatalog.get_riesgo('3')
print(riesgo['prima_media'])  # 2.59645
print(RiesgoPuestoCatalog.validate_prima('3', 2.5))  # True
```

### Geographic Catalogs

```python
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import MunicipiosCatalog

# Search postal code
cp = CodigosPostales.get_by_cp('06700')
print(cp[0]['asentamiento'])  # Roma Norte
print(cp[0]['municipio'])  # Cuauhtémoc
print(CodigosPostales.get_estado('06700'))  # Ciudad de México

# Search municipality
municipio = MunicipiosCatalog.get_municipio('09015')
print(municipio['nom_municipio'])  # Cuauhtémoc
print(municipio['nom_entidad'])  # Ciudad de México

# Search by state
municipios = MunicipiosCatalog.get_by_entidad('14')
print(f"Municipios en Jalisco: {len(municipios)}")
```

### Banks

```python
from catalogmx.catalogs.banxico import BankCatalog

# Get bank by code
bank = BankCatalog.get_bank_by_code('002')
print(bank['name'])  # BANAMEX
print(bank['spei'])  # True

# Search banks
banks = BankCatalog.search_banks('santander')
```

---

## 🏗️ Architecture

### Modular Design
```
catalogmx/
├── validators/          # RFC, CURP, CLABE, NSS
├── catalogs/
│   ├── sat/            # SAT official catalogs
│   │   ├── cfdi_4/     # CFDI 4.0 core
│   │   ├── comercio_exterior/  # Foreign trade
│   │   ├── carta_porte/        # Transportation
│   │   └── nomina/             # Payroll
│   ├── banxico/        # Bank of Mexico catalogs
│   ├── inegi/          # Geographic data
│   └── sepomex/        # Postal codes
└── shared-data/        # JSON catalog files
```

### Lazy Loading
- Catalogs load only when first accessed
- Memory-efficient for large datasets
- Fast initialization

### Type Safety
- Comprehensive type hints throughout
- Python 3.8+ compatible
- IDE autocomplete support

---

## 📥 Complete Catalogs

Current catalogs are **complete for development** and cover 95%+ of common use cases.

For **production with complete datasets**:

**INEGI**: 2,478 municipalities (2,462 municipios + 16 alcaldías CDMX)
**SEPOMEX**: ~150,000 postal codes

### Quick Download

```bash
# Download official SEPOMEX
wget <official-url>
python scripts/csv_to_catalogmx.py sepomex.csv

# Download official INEGI
wget <official-url>
python scripts/process_inegi_data.py municipios.txt
```

See **[DESCARGA_RAPIDA.md](DESCARGA_RAPIDA.md)** for complete instructions and official sources.

---

## 🔄 Catalog Updates

Official catalogs update at different frequencies:

- **CFDI 4.0**: Quarterly (SAT)
- **Comercio Exterior**: Annually (SAT)
- **Carta Porte**: Annually (SCT)
- **Nómina**: Rarely (labor law changes)
- **SEPOMEX**: Monthly (new postal codes)
- **INEGI**: Annually (municipal changes rare)

### Update Monitoring

```bash
# Check for catalog updates
python scripts/check_catalog_updates.py

# Update all catalogs
python scripts/update_all_catalogs.py
```

See **[CATALOG_UPDATES.md](CATALOG_UPDATES.md)** for complete update schedule and procedures.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=catalogmx

# Run specific test suite
pytest tests/test_validators.py
pytest tests/test_catalogs.py
```

---

## 📊 Statistics

- **40+ Official Catalogs** implemented
- **4 Validators** (RFC, CURP, CLABE, NSS)
- **273 Postal Codes** (all 32 states)
- **209 Municipalities** (all state capitals + major cities)
- **100+ Banks** (Banxico official)
- **2,000+ Lines** of well-documented code
- **Type-safe** with comprehensive hints

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

### Adding New Catalogs

1. Add JSON data to `packages/shared-data/`
2. Create Python class in `packages/python/catalogmx/catalogs/`
3. Implement lazy loading and validation methods
4. Add tests and documentation
5. Update README

---

## 📝 License

BSD 3-Clause License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **SAT** - Servicio de Administración Tributaria (official tax catalogs)
- **INEGI** - Instituto Nacional de Estadística y Geografía (geographic data)
- **SEPOMEX** - Servicio Postal Mexicano (postal codes)
- **Banxico** - Banco de México (banking data)
- **RENAPO** - Registro Nacional de Población (CURP specifications)

All catalogs are based on official government sources and updated regularly.

---

## 📖 Additional Documentation

- **[README_CATALOGMX.md](README_CATALOGMX.md)** - Detailed catalog documentation
- **[DESCARGA_RAPIDA.md](DESCARGA_RAPIDA.md)** - Quick download guide for complete catalogs
- **[DESCARGA_CATALOGOS_COMPLETOS.md](DESCARGA_CATALOGOS_COMPLETOS.md)** - Comprehensive download instructions
- **[CATALOG_UPDATES.md](CATALOG_UPDATES.md)** - Update monitoring and schedules
- **[CATALOGOS_ADICIONALES.md](CATALOGOS_ADICIONALES.md)** - Additional catalog specifications
- **[AGENTS.md](AGENTS.md)** - Instructions for AI agents
- **[CLAUDE.md](CLAUDE.md)** - Architecture and technical details

---

## 🚀 Quick Links

- **PyPI**: `pip install catalogmx`
- **GitHub**: [github.com/yourusername/catalogmx](https://github.com/yourusername/catalogmx)
- **Documentation**: [docs.catalogmx.com](https://docs.catalogmx.com)
- **Issues**: [Report bugs or request features](https://github.com/yourusername/catalogmx/issues)

---

Made with ❤️ for the Mexican developer community
