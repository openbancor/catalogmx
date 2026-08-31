# catalogmx (Dart/Flutter)

**Enterprise-grade Mexican data validation and official catalog library for Flutter and Dart applications.**

[![pub package](https://img.shields.io/pub/v/catalogmx.svg)](https://pub.dev/packages/catalogmx)
[![License: BSD-2-Clause](https://img.shields.io/badge/license-BSD--2--Clause-blue.svg)](../../LICENSE)

This is the official Dart/Flutter port of [catalogmx](https://github.com/openbancor/catalogmx), maintaining 100% API compatibility with the Python and TypeScript versions.

Published packages:
- pub.dev: https://pub.dev/packages/catalogmx
- PyPI: https://pypi.org/project/catalogmx/
- npm: https://www.npmjs.com/package/catalogmx

---

## 🚀 Features

### Validators (100% Algorithm Compliant)
- ✅ **RFC** - Registro Federal de Contribuyentes (Tax ID)
- ✅ **CURP** - Clave Única de Registro de Población (National ID)
- ✅ **CLABE** - Clave Bancaria Estandarizada (Bank Account)
- ✅ **NSS** - Número de Seguridad Social (Social Security)

### Generators and Identity Helpers
- ✅ Generate RFC (persona física and moral)
- ✅ Generate CURP from personal data
- ✅ Generate CLABE with check digit
- ✅ Generate NSS with check digit
- ✅ Identity helper workflows (`identity.dart`)

### Tax and Payroll Calculators
- ✅ ISR calculator
- ✅ RESICO calculator
- ✅ IMSS calculators
- ✅ IVA / IEPS / retenciones / impuestos locales
- ✅ Costo total del trabajador

### CFDI Tooling
- ✅ CFDI 4.0 XML builder
- ✅ CFDI validation helpers
- ✅ CFDI signing helpers
- ✅ CFDI PAC helper interfaces

### Official Catalogs
- 📦 **SAT** - CFDI, Nómina, Carta Porte, Comercio Exterior y Contabilidad Electrónica
- 📦 **Banxico** - Banks, plazas, institutions, divisas, UDI, tipo de cambio, TIIE, CETES, inflación y salarios
- 📦 **INEGI** - States, municipalities, localities and SCIAN
- 📦 **SEPOMEX** - Postal codes (standard + complete)
- 📦 **IFT** - Mobile operators and LADA codes
- 📦 **CNBV** - Financial sectors
- 📦 **Mexico** - UMA, salarios mínimos, hoy no circula, placas y giros mercantiles

### Enterprise Features
- 🎯 **Type-safe** - Full null-safety support for Dart 3.0+
- 📱 **Cross-platform** - Works on iOS, Android, Web, Desktop
- 🔒 **Offline-first** - All validators work without internet
- 🚀 **Lightweight** - Minimal dependencies
- 📚 **Well-tested** - Comprehensive unit tests
- 📖 **Documented** - Full API documentation

---

## 📦 Installation

Add this to your `pubspec.yaml`:

```yaml
dependencies:
  catalogmx: ^0.7.0
```

Then run:

```bash
flutter pub get
```

---

## 🎯 Quick Start

### Validators

```dart
import 'package:catalogmx/catalogmx.dart';

void main() {
  // Validate identifiers
  bool isValid = validateRFC('XAXX010101000');  // true
  bool isValidCurp = validateCURP('OEAF771012HMCRGR09');  // true
  bool isValidClabe = validateCLABE('002010077777777771');  // true
  bool isValidNss = validateNSS('12345678903');  // true

  // Generate RFC
  String rfc = generateRFC(
    nombre: 'Juan',
    apellidoPaterno: 'García',
    apellidoMaterno: 'López',
    fechaNacimiento: DateTime(1990, 5, 15),
  );

  // Generate CURP
  String curp = generateCURP(
    nombre: 'Juan',
    apellidoPaterno: 'García',
    apellidoMaterno: 'López',
    fechaNacimiento: DateTime(1990, 5, 15),
    sexo: 'H',
    estado: 'Jalisco',
  );

  // Generate CLABE
  String clabe = generateCLABE(
    bankCode: '002',
    branchCode: '010',
    accountNumber: '07777777777',
  );

  // Generate NSS
  String nss = generateNSS(
    subdelegation: '12',
    year: '34',
    serial: '56',
    sequential: '7890',
  );
}
```

### Catalogs

```dart
import 'package:catalogmx/catalogmx.dart';

void main() {
  // Get all Mexican states
  List<Map<String, dynamic>> states = InegStates.getAll();

  // Get state by code
  Map<String, dynamic>? cdmx = InegStates.getByCode('DF');
  print(cdmx!['name']);  // "CIUDAD DE MEXICO"

  // Get state by name
  Map<String, dynamic>? jalisco = InegStates.getByName('Jalisco');

  // Search states
  List<Map<String, dynamic>> results = InegStates.search('mexico');
}
```

### Catalog Inventory (Dart package)

- **SAT CFDI**: régimen fiscal, uso CFDI, forma de pago, método de pago, tipo de comprobante.
- **SAT Nómina**: bancos, periodicidad de pago, tipo de contrato, tipo de jornada, tipo de nómina, tipo de régimen, riesgo de puesto.
- **SAT Carta Porte**: aeropuertos, carreteras, configuración de autotransporte, material peligroso, puertos marítimos, tipo de embalaje, tipo de permiso.
- **SAT Comercio Exterior**: países, monedas, incoterms, claves de pedimento, unidad aduana, motivos de traslado, registro de identificación tributaria, estados USA/Canadá.
- **SAT Contabilidad Electrónica**: código agrupador.
- **Banxico**: bancos, códigos de plaza, instituciones financieras, monedas/divisas, UDI, tipo de cambio USD, TIIE 28, CETES 28, inflación anual, salarios mínimos.
- **INEGI**: estados, municipios, municipios completo, localidades, SCIAN.
- **SEPOMEX**: códigos postales y códigos postales completo.
- **IFT**: operadores móviles y códigos LADA.
- **CNBV**: sectores.
- **México**: UMA, salarios mínimos, hoy no circula, formatos de placas, giros mercantiles.

---

## 📚 Full Documentation

### RFC (Registro Federal de Contribuyentes)

RFC is Mexico's tax identification number. There are two types:
- **Persona Física** (Individual): 13 characters
- **Persona Moral** (Company): 12 characters

```dart
// Validate RFC
bool isValid = validateRFC('OEAF771012HM8');

// Generate RFC for individual
String rfc = generateRFC(
  nombre: 'Juan',
  apellidoPaterno: 'García',
  apellidoMaterno: 'López',
  fechaNacimiento: DateTime(1990, 5, 15),
);

// Generate RFC for company
String rfcMoral = generateRFCMoral(
  razonSocial: 'Grupo Bimbo S.A.B. de C.V.',
  fechaConstitucion: DateTime(1993, 5, 5),
);

// Detect RFC type
RFCValidator validator = RFCValidator('OEAF771012HM8');
String type = validator.detectType();  // "Persona Física"
bool isFisica = validator.isFisica();  // true
bool isMoral = validator.isMoral();    // false
```

### CURP (Clave Única de Registro de Población)

CURP is Mexico's unique population registry code (18 characters).

```dart
// Validate CURP
bool isValid = validateCURP('OEAF771012HMCRGR09');

// Generate CURP
String curp = generateCURP(
  nombre: 'Juan',
  apellidoPaterno: 'García',
  apellidoMaterno: 'López',
  fechaNacimiento: DateTime(1990, 5, 15),
  sexo: 'H',  // H=Male, M=Female
  estado: 'Jalisco',
);

// Extract information
CURPValidator validator = CURPValidator('OEAF771012HMCRGR09');
DateTime? birthDate = validator.getBirthDate();
String? gender = validator.getGender();  // "Hombre" or "Mujer"
String? stateCode = validator.getStateCode();
```

### CLABE (Clave Bancaria Estandarizada)

CLABE is the standardized 18-digit bank account number for SPEI transfers.

```dart
// Validate CLABE
bool isValid = validateCLABE('002010077777777771');

// Generate CLABE
String clabe = generateCLABE(
  bankCode: '002',
  branchCode: '010',
  accountNumber: '07777777777',
);

// Extract information
Map<String, String?>? info = getCLABEInfo('002010077777777771');
print(info!['bank_code']);      // "002"
print(info['branch_code']);     // "010"
print(info['account_number']);  // "07777777777"
```

### NSS (Número de Seguridad Social)

NSS is the 11-digit social security number issued by IMSS.

```dart
// Validate NSS
bool isValid = validateNSS('12345678903');

// Generate NSS
String nss = generateNSS(
  subdelegation: '12',
  year: '34',
  serial: '56',
  sequential: '7890',
);

// Extract information
Map<String, String?>? info = getNSSInfo('12345678903');
print(info!['subdelegation']);  // "12"
print(info['year']);           // "34"
```

---

## 🏗️ Platform Support

| Platform | Status |
|----------|--------|
| Android  | ✅ Supported |
| iOS      | ✅ Supported |
| Web      | ✅ Supported |
| Windows  | ✅ Supported |
| macOS    | ✅ Supported |
| Linux    | ✅ Supported |

---

## 🧪 Testing

Run tests:

```bash
dart test
```

With coverage:

```bash
dart test --coverage=coverage
```

---

## 📄 License

BSD-2-Clause License. See [LICENSE](../../LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.rst](../../CONTRIBUTING.rst) for guidelines.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/openbancor/catalogmx/issues)
- **Documentation**: [Main README](../../README.md)
- **Python version**: [PyPI](https://pypi.org/project/catalogmx/)
- **TypeScript version**: [NPM](https://www.npmjs.com/package/catalogmx)

---

## 🌟 Related Packages

- **Python**: `pip install catalogmx`
- **TypeScript/Node.js**: `npm install catalogmx`
- **Dart/Flutter**: `flutter pub add catalogmx` (this package)

All three versions maintain 100% API compatibility and identical validation algorithms.
