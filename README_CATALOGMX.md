# 🇲🇽 catalogmx

**Comprehensive Mexican Data Validators and Official Catalogs**

`catalogmx` is a complete library for validating Mexican identifiers (RFC, CURP, CLABE, NSS) and accessing official catalogs from SAT, Banxico, INEGI, SEPOMEX, and IFT. Available for both Python and TypeScript/JavaScript.

---

## ✨ Features

### 🔐 Validators (Implemented)

- **RFC** - Registro Federal de Contribuyentes
  - Persona Física (13 characters)
  - Persona Moral (12 characters)
  - Check digit validation
  - Cacophonic word replacement

- **CURP** - Clave Única de Registro de Población
  - 18-character validation
  - Check digit algorithm (position 18)
  - Homonymy support (differentiator in position 17)
  - 70+ inconvenient words (Anexo 2)

- **CLABE** - Clave Bancaria Estandarizada
  - 18-digit bank account validator
  - Modulo 10 check digit
  - Bank code extraction (3 digits)
  - Branch code (3 digits)
  - Account number (11 digits)

- **NSS** - Número de Seguridad Social (IMSS)
  - 11-digit validation
  - Modified Luhn algorithm
  - Subdelegation, year, serial extraction

### 📚 Catalogs

#### ✅ Implemented (Phase 1)

- **Banxico - Banks**: 100+ Mexican banks with SPEI participation status
- **INEGI - States**: 32 states + Federal District with CURP codes, INEGI codes, abbreviations

#### 🚧 Coming Soon (Phases 2-5)

- **SAT Essentials** (Phase 2)
  - c_RegimenFiscal - Tax regimes
  - c_UsoCFDI - CFDI usage codes
  - c_FormaPago - Payment methods
  - c_MetodoPago - Payment types
  - c_TipoComprobante - Receipt types
  - c_Impuesto - Taxes
  - c_TasaOCuota - Tax rates
  - c_Moneda - Currencies (ISO 4217) - ~180 currencies
  - c_Pais - Countries (ISO 3166-1) - ~250 countries
  - **Comercio Exterior 2.0** (Foreign Trade Complement - vigente desde enero 2024) ⭐⭐
    - c_INCOTERM - 11 Incoterms 2020 (EXW, FCA, FOB, CIF, DDP, etc.)
    - c_ClavePedimento - ~40 customs document keys (A1, V1, C1, etc.)
    - c_FraccionArancelaria - ~20,000 TIGIE tariff classifications (NICO 10-digit)
    - c_UnidadAduana - ~30 customs measurement units
    - c_RegistroIdentTribReceptor - Foreign tax ID types
    - c_MotivoTraslado - Transfer motives (for CFDI type T)
    - c_Estado (for USA/Canada) - US States & Canadian Provinces (ISO 3166-2)

- **INEGI Complete** (Phase 3)
  - 2,469 Municipalities
  - Localities
  - AGEBs (Basic Geostatistical Areas)

- **SAT Extended** (Phase 4)
  - c_ClaveProdServ - ~52,000 product/service codes
  - c_ClaveUnidad - ~3,000 unit codes
  - Nomina catalogs (payroll)
  - Código Agrupador (accounting)
  - **Carta Porte 3.0** (Transportation)
    - c_Estaciones - Transport stations (bus, train, maritime, air)
    - c_CodigoTransporteAereo - Airports (IATA/ICAO codes)
    - c_NumAutorizacionNaviero - Seaports and maritime authorization
    - c_Carreteras - SCT highway catalog (Guardia Nacional)
    - c_TipoPermiso - SCT transport permit types
    - c_ConfigAutotransporte - Vehicle configurations
    - c_TipoEmbalaje - Packaging types
    - c_MaterialPeligroso - Hazardous materials

- **SEPOMEX** (Phase 4)
  - ~150,000 postal codes
  - Colonia → Municipality → State mapping
  - Settlement types

- **IFT** (Phase 5)
  - LADA codes
  - Phone number validation
  - Geographic numbering zones

- **Banxico Financial Data** (Phase 5)
  - **Historical Interest Rates** (via SIE API)
    - TIIE (Tasa de Interés Interbancaria de Equilibrio)
      - 28 days, 91 days, 182 days
    - CETES (Certificados de la Tesorería)
      - 28, 91, 182, 364 days
    - Tasa Objetivo (Target Rate) - Banco de México
    - Historical data via Banxico SIE REST API
    - Series codes: SF60648 (TIIE 28d), SF60633 (CETES 28d), SF61745 (Target rate)
  - Exchange rates (FIX) historical
  - **Mexican Holidays Calendar** (3 types) ⭐⭐⭐
    - **Banking holidays** (CNBV) - 10 days/year
    - **Labor holidays** (LFT) - 7 mandatory days/year
    - **Judicial holidays** (SCJN) - Courts calendar
    - Historical: 2000-2024 (25 years)
    - Future: 2025-2034 (10 years)
    - **Key distinction**: Days that are business days but NOT banking days (e.g., Viernes Santo)
    - Business days calculator API

---

## 🚀 Installation

### Python

```bash
pip install catalogmx
```

### TypeScript/JavaScript

```bash
npm install catalogmx
# or
yarn add catalogmx
```

---

## 📖 Usage

### Python

```python
from catalogmx import (
    generate_rfc_persona_fisica,
    generate_curp,
    validate_clabe,
    validate_nss,
)
from catalogmx.catalogs.banxico import BankCatalog
from catalogmx.catalogs.inegi import StateCatalog

# Generate RFC
rfc = generate_rfc_persona_fisica(
    nombre='Juan',
    apellido_paterno='Pérez',
    apellido_materno='García',
    fecha_nacimiento='1990-05-15'
)
print(rfc)  # PEGJ900515

# Generate CURP with custom differentiator for homonyms
curp = generate_curp(
    nombre='Juan',
    apellido_paterno='Pérez',
    apellido_materno='García',
    fecha_nacimiento='1990-05-12',
    sexo='H',
    estado='JALISCO',
    differentiator='0'  # For resolving homonyms
)
print(curp)  # PEGJ900512HJCRRS04

# Validate CLABE
is_valid = validate_clabe('002010077777777771')
print(is_valid)  # True

# Get bank info
bank = BankCatalog.get_bank_by_code('002')
print(bank['name'])  # BANAMEX
print(bank['spei'])  # True

# Get state info
state = StateCatalog.get_state_by_name('JALISCO')
print(state['code'])  # JC
print(state['clave_inegi'])  # 14

# Validate NSS (IMSS)
is_valid_nss = validate_nss('12345678903')
```

### TypeScript

```typescript
import {
  generateRfcPersonaFisica,
  generateCurp,
  validateClabe,
  validateNss,
  BankCatalog,
  StateCatalog
} from 'catalogmx';

// Generate RFC
const rfc = generateRfcPersonaFisica({
  nombre: 'Juan',
  apellidoPaterno: 'Pérez',
  apellidoMaterno: 'García',
  fechaNacimiento: '1990-05-15'
});
console.log(rfc);  // PEGJ900515

// Generate CURP
const curp = generateCurp({
  nombre: 'Juan',
  apellidoPaterno: 'Pérez',
  apellidoMaterno: 'García',
  fechaNacimiento: '1990-05-12',
  sexo: 'H',
  estado: 'JALISCO',
  differentiator: '0'
});

// Validate CLABE
const isValid = validateClabe('002010077777777771');

// Get bank info
const bank = BankCatalog.getBankByCode('002');
console.log(bank.name);  // BANAMEX

// Get state info
const state = StateCatalog.getStateByName('JALISCO');
console.log(state.code);  // JC
```

---

## 🏗️ Project Structure

```
catalogmx/
├── README.md
├── packages/
│   ├── python/
│   │   ├── catalogmx/
│   │   │   ├── validators/
│   │   │   │   ├── rfc.py
│   │   │   │   ├── curp.py
│   │   │   │   ├── clabe.py
│   │   │   │   └── nss.py
│   │   │   ├── catalogs/
│   │   │   │   ├── sat/
│   │   │   │   ├── banxico/
│   │   │   │   │   └── banks.py
│   │   │   │   ├── inegi/
│   │   │   │   │   └── states.py
│   │   │   │   ├── sepomex/
│   │   │   │   └── ift/
│   │   │   └── helpers.py
│   │   └── tests/
│   │
│   ├── typescript/
│   │   ├── src/
│   │   │   ├── validators/
│   │   │   ├── catalogs/
│   │   │   └── index.ts
│   │   └── tests/
│   │
│   └── shared-data/               # Single source of truth
│       ├── sat/
│       ├── banxico/
│       │   └── banks.json         # 100+ banks
│       ├── inegi/
│       │   └── states.json        # 32 states
│       ├── sepomex/
│       ├── ift/
│       └── misc/
│           └── cacophonic_words.json
│
└── scripts/
    ├── fetch_sat_catalogs.py
    ├── fetch_inegi_data.py
    ├── fetch_sepomex_data.py
    └── build_sqlite_dbs.py
```

---

## 🎯 Implementation Status

### ✅ Phase 1: MVP - Core Validators (COMPLETE)
- [x] RFC (Persona Física/Moral)
- [x] CURP (with check digit validation)
- [x] CLABE (with modulo 10 algorithm)
- [x] NSS (IMSS social security number)
- [x] Bank catalog (100+ banks)
- [x] States catalog (32 states)
- [x] Monorepo structure
- [x] Shared data (JSON)

### 🚧 Phase 2: SAT Essentials (IN PROGRESS)
- [ ] c_RegimenFiscal
- [ ] c_UsoCFDI
- [ ] c_FormaPago
- [ ] c_MetodoPago
- [ ] c_TipoComprobante
- [ ] c_Impuesto
- [ ] c_TasaOCuota
- [ ] c_Moneda
- [ ] c_Pais
- [ ] c_TipoRelacion
- [ ] c_Exportacion
- [ ] c_ObjetoImp
- [ ] **Comercio Exterior 2.0** (Complement for foreign trade) ⭐⭐
  - [ ] c_INCOTERM (11 Incoterms 2020)
  - [ ] c_ClavePedimento (~40 customs keys)
  - [ ] c_FraccionArancelaria (~20,000 TIGIE tariff codes - SQLite)
  - [ ] c_UnidadAduana (~30 customs units)
  - [ ] c_RegistroIdentTribReceptor (foreign tax ID types)
  - [ ] c_MotivoTraslado (transfer motives)
  - [ ] c_Estado (US States & Canadian Provinces - ISO 3166-2)

### 📋 Phase 3: INEGI Complete
- [ ] 2,469 Municipalities
- [ ] Localities
- [ ] AGEBs

### 📋 Phase 4: SAT Extended
- [ ] c_ClaveProdServ (52k records - SQLite)
- [ ] c_ClaveUnidad (3k records)
- [ ] Nomina catalogs
  - [ ] c_TipoContrato
  - [ ] c_TipoJornada
  - [ ] c_TipoPercepcion (50+ income types)
  - [ ] c_TipoDeduccion (20+ deduction types)
  - [ ] c_TipoRegimen
  - [ ] c_PeriodicidadPago
- [ ] Código Agrupador (accounting grouping code)
- [ ] **Carta Porte 3.0**
  - [ ] c_Estaciones (transport stations)
  - [ ] c_CodigoTransporteAereo (airports - IATA/ICAO)
  - [ ] c_NumAutorizacionNaviero (seaports)
  - [ ] c_Carreteras (SCT federal highways)
  - [ ] c_TipoPermiso (SCT permits)
  - [ ] c_ConfigAutotransporte (vehicle config)
  - [ ] c_TipoEmbalaje (packaging)
  - [ ] c_MaterialPeligroso (hazmat)

### 📋 Phase 5: Complementos
- [ ] SEPOMEX postal codes (150k - SQLite)
- [ ] IFT telephony catalogs
  - [ ] LADA codes
  - [ ] Phone number validator
  - [ ] Geographic zones
- [ ] CONDUSEF financial products
- [ ] **Banxico SIE API - Historical Financial Data**
  - [ ] TIIE (28d, 91d, 182d)
  - [ ] CETES (28d, 91d, 182d, 364d)
  - [ ] Tasa Objetivo (Banxico target rate)
  - [ ] Exchange rates (FIX) historical
- [ ] **Mexican Holidays Calendar System**
  - [ ] Banking holidays (CNBV) - 2000-2034
  - [ ] Labor holidays (LFT) - 2000-2034
  - [ ] Judicial holidays (SCJN) - 2000-2034
  - [ ] Business days calculator
  - [ ] Banking days calculator
  - [ ] Holiday type differentiation API
- [ ] UMA historical values
- [ ] Minimum wage historical

### 📋 Phase 6: TypeScript Implementation
- [ ] Port all validators to TypeScript
- [ ] Shared catalog access
- [ ] Parity tests
- [ ] npm package

---

## 🔧 Development

### Fetching Official Data

Scripts are provided to download official catalogs from government sources:

```bash
# Download SAT catalogs (CFDI 4.0)
python scripts/fetch_sat_catalogs.py

# Download INEGI data (municipalities, localities)
python scripts/fetch_inegi_data.py

# Download SEPOMEX postal codes
python scripts/fetch_sepomex_data.py

# Build SQLite databases for large catalogs
python scripts/build_sqlite_dbs.py
```

### Running Tests

```bash
# Python
cd packages/python
pytest

# TypeScript (when implemented)
cd packages/typescript
npm test
```

---

## 📚 Official Sources

All catalog data comes from official Mexican government sources:

- **SAT**:
  - [Anexo 20 - CFDI 4.0](http://omawww.sat.gob.mx/tramitesyservicios/Paginas/anexo_20_version3-3.htm)
  - [Carta Porte 3.0 Catalogs](http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/CatalogosCartaPorte30.xls)
  - [Comercio Exterior Catalogs](http://omawww.sat.gob.mx/tramitesyservicios/Paginas/catalogos_emision_cfdi_complemento_ce.htm)
- **Banxico**:
  - [SPEI Participants](https://www.banxico.org.mx/cep-scl/listaInstituciones.do)
  - [SIE API - Economic Information System](https://www.banxico.org.mx/SieAPIRest/)
  - [Historical Interest Rates](https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=18&accion=consultarCuadroAnalitico&idCuadro=CA51)
- **INEGI**:
  - [Marco Geoestadístico](https://www.inegi.org.mx/servicios/catalogounico.html)
  - [Web Service API](https://www.inegi.org.mx/servicios/catalogounico.html)
- **SEPOMEX**:
  - [Código Postal](https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx)
- **IFT**:
  - [Plan de Numeración](https://sns.ift.org.mx:8081/sns-frontend/planes-numeracion/descarga-publica.xhtml)
- **SCT**:
  - [Federal Highways Information](https://www.sct.gob.mx/carreteras/)
  - [Highway Catalog - Guardia Nacional](https://www.gob.mx/guardianacional/documentos/catalogo-de-carreteras-y-tramos-competencia-de-las-coordinaciones-estatales-de-la-guardia-nacional)

---

## 🤝 Contributing

Contributions are welcome! This is a massive project covering all Mexican official catalogs. Priority areas:

1. **Phase 2-5 Catalog Implementation**: Help implement remaining SAT, INEGI, SEPOMEX catalogs
2. **TypeScript Port**: Port validators and catalogs to TypeScript
3. **Data Scripts**: Improve download scripts to fetch latest official data
4. **Tests**: Add comprehensive tests for all validators and catalogs
5. **Documentation**: Improve examples and API documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- **SAT** - Servicio de Administración Tributaria
- **Banxico** - Banco de México
- **INEGI** - Instituto Nacional de Estadística y Geografía
- **SEPOMEX** - Servicio Postal Mexicano
- **IFT** - Instituto Federal de Telecomunicaciones
- **RENAPO** - Registro Nacional de Población

All catalog data is sourced from official government publications and is public domain.

---

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/luisfernandobarrera/catalogmx/issues)
- **Discussions**: [GitHub Discussions](https://github.com/luisfernandobarrera/catalogmx/discussions)

---

**Made with ❤️ for the Mexican developer community**
