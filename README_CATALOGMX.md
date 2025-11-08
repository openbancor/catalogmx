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

#### ✅ Implemented

**Phase 1 - Foundation**
- **Banxico - Banks**: 100+ Mexican banks with SPEI participation status
- **INEGI - States**: 32 states + Federal District with CURP codes, INEGI codes, abbreviations

**Phase 2 - SAT CFDI 4.0 Core** ✅
- ✅ c_RegimenFiscal - 26 tax regimes (persona física/moral)
- ✅ c_UsoCFDI - 25 CFDI usage codes (G01-G03, I01-I08, D01-D10, CP01, CN01)
- ✅ c_FormaPago - 18 payment methods (efectivo, transferencia, tarjeta, etc.)
- ✅ c_MetodoPago - 2 payment types (PUE, PPD)
- ✅ c_TipoComprobante - 5 receipt types (I, E, T, N, P)
- ✅ c_Impuesto - 4 tax types (ISR, IVA, IEPS) with retention/transfer flags
- ✅ c_Exportacion - 4 export keys
- ✅ c_TipoRelacion - 9 CFDI relationship types
- ✅ c_ObjetoImp - 8 tax object codes (updated Dec 2024)

**Phase 2 - SAT Comercio Exterior 2.0** ✅
- ✅ c_INCOTERM - 11 Incoterms 2020 (EXW, FCA, FOB, CIF, DDP, etc.)
- ✅ c_ClavePedimento - 42 customs document keys (A1, V1, C1, etc.)
- ✅ c_Moneda - 150 ISO 4217 currencies with decimal precision
- ✅ c_Pais - 249 ISO 3166-1 countries (Alpha-3)
- ✅ c_UnidadAduana - 32 customs measurement units
- ✅ c_RegistroIdentTribReceptor - 15 foreign tax ID types with regex validation
- ✅ c_MotivoTraslado - 6 transfer motives (for CFDI type T)
- ✅ c_Estado (for USA/Canada) - 63 US States/territories + 13 Canadian provinces (ISO 3166-2)

**Phase 3 - SAT Carta Porte 3.0** ✅
- ✅ c_CodigoTransporteAereo - 76 Mexican airports (IATA/ICAO codes) - sample 20
- ✅ c_NumAutorizacionNaviero - 100 seaports and maritime authorization - sample 25
- ✅ c_Carreteras - 200 SCT federal highways - sample 20
- ✅ c_TipoPermiso - 12 SCT transport permit types
- ✅ c_ConfigAutotransporte - 15 vehicle configurations (C2, C3, T2S1, T3S2, etc.)
- ✅ c_TipoEmbalaje - 30 UN packaging types (1A, 4G, 5H, etc.)
- ✅ c_MaterialPeligroso - 3,000 UN hazardous materials - sample 50

**Phase 4 - SAT Nómina 1.2** ✅
- ✅ c_TipoNomina - 2 types (ordinaria, extraordinaria)
- ✅ c_TipoContrato - 10 contract types
- ✅ c_TipoJornada - 8 work shifts (diurna, nocturna, mixta, etc.)
- ✅ c_TipoRegimen - 13 regime types (sueldos, asimilados, etc.)
- ✅ c_PeriodicidadPago - 10 payment frequencies (diario, semanal, quincenal, etc.)
- ✅ c_RiesgoPuesto - 5 risk levels (Class I-V) with IMSS premium ranges
- ✅ c_Banco - 50 banks for payroll deposits

**Phase 5 - Geographic Catalogs** 🔄
- ✅ SEPOMEX - Postal codes sample (50/~150,000 codes) with settlement types
- ✅ INEGI Municipios - Municipalities sample (50/2,469) with INEGI codes

#### 🚧 Coming Soon (Future Phases)

- **SAT Extended Catalogs**
  - c_ClaveProdServ - ~52,000 product/service codes
  - c_ClaveUnidad - ~3,000 unit codes
  - c_FraccionArancelaria - ~20,000 TIGIE tariff classifications (SQLite)
  - Código Agrupador (accounting)

- **INEGI Complete**
  - Localities (~90,000 - SQLite)
  - AGEBs (Basic Geostatistical Areas ~200,000 - SQLite)

- **SEPOMEX Complete**
  - Full ~150,000 postal codes (SQLite)
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

# COMERCIO EXTERIOR - Validate CFDI with Foreign Trade Complement
from catalogmx.catalogs.sat.comercio_exterior import (
    IncotermsValidator,
    ClavePedimentoCatalog,
    MonedaCatalog,
    PaisCatalog,
    EstadoCatalog,
    ComercioExteriorValidator,
)

# Validate INCOTERM
incoterm = IncotermsValidator.get_incoterm('CIF')
print(incoterm['name'])  # Cost, Insurance and Freight
print(incoterm['transport_mode'])  # maritime
print(IncotermsValidator.seller_pays_insurance('CIF'))  # True

# Validate customs key
pedimento = ClavePedimentoCatalog.get_clave('A1')
print(pedimento['descripcion'])  # Exportación definitiva
print(ClavePedimentoCatalog.is_export('A1'))  # True

# Validate currency conversion
conversion = MonedaCatalog.validate_conversion_usd({
    'moneda': 'EUR',
    'total': 10000.00,
    'tipo_cambio_usd': 1.18,
    'total_usd': 11800.00
})
print(conversion['valid'])  # True

# Validate US state for foreign trade
estado = EstadoCatalog.get_estado_usa('CA')
print(estado['name'])  # California

# Validate complete CFDI with Comercio Exterior
cfdi_ce = {
    'tipo_comprobante': 'I',
    'incoterm': 'CIF',
    'clave_pedimento': 'A1',
    'moneda': 'USD',
    'tipo_cambio_usd': 1.0,
    'total': 50000.00,
    'total_usd': 50000.00,
    'mercancias': [{
        'fraccion_arancelaria': '84713001',
        'unidad_aduana': '14',
        'cantidad_aduana': 100,
        'valor_unitario_aduana': 500.00,
        'pais_origen': 'USA'
    }],
    'receptor': {
        'pais': 'USA',
        'estado': 'TX',
        'tipo_registro_trib': '04',
        'num_reg_id_trib': '123456789'
    }
}

result = ComercioExteriorValidator.validate(cfdi_ce)
if result['valid']:
    print("CFDI Comercio Exterior válido")
else:
    for error in result['errors']:
        print(f"Error: {error}")

# CFDI 4.0 Core Catalogs
from catalogmx.catalogs.sat.cfdi_4 import (
    RegimenFiscalCatalog,
    UsoCFDICatalog,
    FormaPagoCatalog,
    TipoComprobanteCatalog,
)

# Validate tax regime
regimen = RegimenFiscalCatalog.get_regimen('601')
print(regimen['description'])  # General de Ley Personas Morales
print(RegimenFiscalCatalog.is_valid_for_persona_moral('601'))  # True

# Validate CFDI usage
uso = UsoCFDICatalog.get_uso('G03')
print(uso['description'])  # Gastos en general
print(UsoCFDICatalog.is_deduction_category('G03'))  # True

# Validate payment method
forma_pago = FormaPagoCatalog.get_forma('03')
print(forma_pago['description'])  # Transferencia electrónica de fondos

# CARTA PORTE 3.0 - Transportation Documentation
from catalogmx.catalogs.sat.carta_porte import (
    AeropuertosCatalog,
    PuertosMaritimos,
    TipoPermisoCatalog,
    ConfigAutotransporteCatalog,
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
print(permiso['name'])  # Autotransporte Federal de Carga General
print(TipoPermisoCatalog.is_carga_permit('TPAF01'))  # True

# Validate vehicle configuration
config = ConfigAutotransporteCatalog.get_config('T3S2')
print(config['name'])  # Tractocamión Semirremolque (5 ejes)
print(config['axes'])  # 5

# NÓMINA 1.2 - Payroll
from catalogmx.catalogs.sat.nomina import (
    TipoContratoCatalog,
    TipoJornadaCatalog,
    PeriodicidadPagoCatalog,
    RiesgoPuestoCatalog,
    BancoCatalog,
)

# Validate contract type
contrato = TipoContratoCatalog.get_contrato('01')
print(contrato['description'])  # Contrato de trabajo por tiempo indeterminado

# Validate work shift
jornada = TipoJornadaCatalog.get_jornada('01')
print(jornada['description'])  # Diurna
print(jornada['hours'])  # 6:00 a 20:00

# Validate payment frequency
periodicidad = PeriodicidadPagoCatalog.get_periodicidad('04')
print(periodicidad['description'])  # Quincenal
print(periodicidad['days'])  # 15

# Validate risk level and IMSS premium
riesgo = RiesgoPuestoCatalog.get_riesgo('3')
print(riesgo['description'])  # Clase III
print(riesgo['prima_media'])  # 2.59645
print(RiesgoPuestoCatalog.validate_prima('3', 2.5))  # True (within range)

# Validate bank for payroll
banco = BancoCatalog.get_banco('002')
print(banco['name'])  # Banamex
print(banco['full_name'])  # Banco Nacional de México, S.A.

# GEOGRAPHIC CATALOGS
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import MunicipiosCatalog

# Validate postal code
cp_info = CodigosPostales.get_by_cp('06700')
print(cp_info[0]['asentamiento'])  # Roma Norte
print(cp_info[0]['municipio'])  # Cuauhtémoc
print(CodigosPostales.get_estado('06700'))  # Ciudad de México

# Validate municipality
municipio = MunicipiosCatalog.get_municipio('09015')
print(municipio['nom_municipio'])  # Cuauhtémoc
print(municipio['nom_entidad'])  # Ciudad de México
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
- [ ] c_Moneda (basic - done in CE)
- [ ] c_Pais (basic - done in CE)
- [ ] c_TipoRelacion
- [ ] c_Exportacion
- [ ] c_ObjetoImp
- [x] **Comercio Exterior 2.0** (Complement for foreign trade) ⭐⭐ **COMPLETE**
  - [x] c_INCOTERM (11 Incoterms 2020)
  - [x] c_ClavePedimento (~40 customs keys)
  - [ ] c_FraccionArancelaria (~20,000 TIGIE tariff codes - SQLite) **[Pending: TIGIE data download]**
  - [x] c_UnidadAduana (~30 customs units)
  - [x] c_RegistroIdentTribReceptor (foreign tax ID types)
  - [x] c_MotivoTraslado (transfer motives)
  - [x] c_Moneda (~180 ISO 4217 currencies)
  - [x] c_Pais (~250 ISO 3166-1 countries)
  - [x] c_Estado (US States & Canadian Provinces - ISO 3166-2)
  - [x] ComercioExteriorValidator (complete validation logic)

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
