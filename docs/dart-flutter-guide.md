# catalogmx for Flutter/Dart - Complete Guide

## Overview

The **catalogmx** Dart/Flutter package provides enterprise-grade Mexican data validation and catalog access for Flutter and Dart applications. It maintains 100% API compatibility with the Python and TypeScript versions while following Dart best practices.

## Installation

Add to your `pubspec.yaml`:

```yaml
dependencies:
  catalogmx: ^0.3.0
```

Then run:

```bash
flutter pub get
```

## Package Structure

```
packages/dart/
├── lib/
│   ├── catalogmx.dart              # Main export file
│   └── src/
│       ├── validators/             # All validators
│       │   ├── rfc_validator.dart
│       │   ├── curp_validator.dart
│       │   ├── clabe_validator.dart
│       │   └── nss_validator.dart
│       ├── catalogs/               # Official catalogs
│       │   ├── inegi/
│       │   │   ├── states.dart
│       │   │   └── municipios.dart
│       │   ├── sat/
│       │   │   └── aeropuertos.dart
│       │   └── banxico/
│       │       └── banks.dart
│       └── utils/                  # Utilities
│           ├── text_utils.dart
│           ├── date_utils.dart
│           └── catalog_helper.dart
├── test/                          # Unit tests
│   ├── rfc_validator_test.dart
│   ├── curp_validator_test.dart
│   ├── clabe_validator_test.dart
│   ├── nss_validator_test.dart
│   └── catalogs_test.dart
├── example/
│   └── main.dart                  # Example usage
├── pubspec.yaml                   # Package manifest
├── README.md                      # Package documentation
└── CHANGELOG.md                   # Version history
```

## Features Implemented

### ✅ Complete Validators

1. **RFC (Registro Federal de Contribuyentes)**
   - Validation for Persona Física (13 chars)
   - Validation for Persona Moral (12 chars)
   - RFC generation with official algorithm
   - Checksum validation
   - Type detection
   - Homoclave calculation

2. **CURP (Clave Única de Registro de Población)**
   - Full 18-character validation
   - CURP generation from personal data
   - Check digit validation
   - State code mapping (all 32 states + NE)
   - Birth date extraction
   - Gender extraction

3. **CLABE (Clave Bancaria Estandarizada)**
   - 18-digit CLABE validation
   - CLABE generation
   - Check digit calculation (3,7,1 pattern)
   - Component extraction (bank, branch, account)

4. **NSS (Número de Seguridad Social)**
   - 11-digit NSS validation
   - NSS generation
   - Modified Luhn algorithm check digit
   - Component extraction

### ✅ Catalogs

1. **INEGI States** - Complete implementation with embedded data
   - 32 Mexican states + born abroad
   - Multiple lookup methods (code, name, INEGI clave)
   - Search functionality

2. **INEGI Municipios** - Placeholder structure
3. **SAT Aeropuertos** - Placeholder structure
4. **Banxico Banks** - Placeholder structure

### ✅ Utilities

- Text normalization and accent removal
- Date validation and conversion
- Name cleaning with excluded words
- Catalog lazy loading helpers

### ✅ Testing

- 5 comprehensive test files
- Tests for all validators
- Tests for catalogs
- Edge case coverage
- Error handling tests

## Usage Examples

### RFC Validation

```dart
import 'package:catalogmx/catalogmx.dart';

// Simple validation
bool isValid = validateRFC('XAXX010101000');  // Generic RFC

// Generate RFC
String rfc = generateRFC(
  nombre: 'Juan',
  apellidoPaterno: 'García',
  apellidoMaterno: 'López',
  fechaNacimiento: DateTime(1990, 5, 15),
);

// Detailed validation
RFCValidator validator = RFCValidator('OEAF771012HM8');
print(validator.detectType());      // "Persona Física"
print(validator.isFisica());        // true
print(validator.validateChecksum()); // true
```

### CURP Generation

```dart
String curp = generateCURP(
  nombre: 'María José',
  apellidoPaterno: 'Hernández',
  apellidoMaterno: 'López',
  fechaNacimiento: DateTime(1985, 3, 15),
  sexo: 'M',  // H=Male, M=Female
  estado: 'Ciudad de México',
);

// Extract information
CURPValidator validator = CURPValidator(curp);
DateTime? birthDate = validator.getBirthDate();
String? gender = validator.getGender();
String? stateCode = validator.getStateCode();
```

### CLABE Operations

```dart
// Validate
bool isValid = validateCLABE('002010077777777771');

// Generate
String clabe = generateCLABE(
  bankCode: '002',    // Banamex
  branchCode: '010',
  accountNumber: '07777777777',
);

// Extract info
Map<String, String?>? info = getCLABEInfo(clabe);
print(info!['bank_code']);
print(info['account_number']);
```

### Catalog Access

```dart
// Get all states
List<Map<String, dynamic>> states = InegStates.getAll();

// Lookup by code
Map<String, dynamic>? cdmx = InegStates.getByCode('DF');
print(cdmx!['name']);  // "CIUDAD DE MEXICO"

// Lookup by name
Map<String, dynamic>? jalisco = InegStates.getByName('Jalisco');
print(jalisco!['clave_inegi']);  // "14"

// Search
List<Map<String, dynamic>> results = InegStates.search('Baja');
// Returns Baja California and Baja California Sur
```

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Android  | ✅ Full support | Tested on Android 7.0+ |
| iOS      | ✅ Full support | Tested on iOS 12.0+ |
| Web      | ✅ Full support | All modern browsers |
| Windows  | ✅ Full support | Windows 10+ |
| macOS    | ✅ Full support | macOS 10.14+ |
| Linux    | ✅ Full support | All distributions |

## Dependencies

The package has minimal dependencies:

- `diacritic: ^0.1.5` - For accent removal (similar to Python's unidecode)

Dev dependencies:
- `test: ^1.24.0` - Testing framework
- `lints: ^3.0.0` - Dart linting

## Running Tests

```bash
# Run all tests
dart test

# Run with coverage
dart test --coverage=coverage

# Run specific test file
dart test test/rfc_validator_test.dart

# Run in Flutter environment
flutter test
```

## Future Enhancements

### Planned for v0.4.0
- [ ] Full INEGI municipios catalog (2,469 municipalities)
- [ ] Full INEGI localidades catalog (GPS coordinates)
- [ ] Full SEPOMEX postal codes (157K+ codes)
- [ ] Asset loading strategy for Flutter apps
- [ ] SQLite support for large datasets

### Planned for v0.5.0
- [ ] SAT complete catalogs (taxes, customs, etc.)
- [ ] Banxico complete bank catalog
- [ ] IFT operator catalog
- [ ] Performance optimizations
- [ ] Caching strategies

## Integration with Flutter Apps

### Basic Setup

```dart
// main.dart
import 'package:flutter/material.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'catalogmx Demo',
      home: ValidatorScreen(),
    );
  }
}

class ValidatorScreen extends StatefulWidget {
  @override
  _ValidatorScreenState createState() => _ValidatorScreenState();
}

class _ValidatorScreenState extends State<ValidatorScreen> {
  final _rfcController = TextEditingController();
  String _validationResult = '';

  void _validateRFC() {
    setState(() {
      final isValid = validateRFC(_rfcController.text);
      _validationResult = isValid ? '✅ Valid RFC' : '❌ Invalid RFC';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('RFC Validator')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _rfcController,
              decoration: InputDecoration(labelText: 'Enter RFC'),
            ),
            ElevatedButton(
              onPressed: _validateRFC,
              child: Text('Validate'),
            ),
            Text(_validationResult),
          ],
        ),
      ),
    );
  }
}
```

## API Compatibility

The Dart/Flutter version maintains 100% API compatibility with Python and TypeScript:

| Feature | Python | TypeScript | Dart/Flutter |
|---------|--------|------------|--------------|
| RFC validation | `validate_rfc()` | `validateRFC()` | `validateRFC()` |
| RFC generation | `generate_rfc()` | `generateRFC()` | `generateRFC()` |
| CURP validation | `validate_curp()` | `validateCURP()` | `validateCURP()` |
| CURP generation | `generate_curp()` | `generateCURP()` | `generateCURP()` |
| CLABE validation | `validate_clabe()` | `validateCLABE()` | `validateCLABE()` |
| NSS validation | `validate_nss()` | `validateNSS()` | `validateNSS()` |
| States catalog | `InegStates.get_all()` | `InegStates.getAll()` | `InegStates.getAll()` |

## Contributing

See the main [CONTRIBUTING.rst](../CONTRIBUTING.rst) for guidelines.

For Dart-specific contributions:
1. Follow Dart style guide
2. Run `dart analyze` before committing
3. Ensure all tests pass with `dart test`
4. Add tests for new features
5. Update documentation

## License

BSD-2-Clause License. See [LICENSE](../LICENSE) for details.

## Support

- **GitHub Issues**: https://github.com/openbancor/catalogmx/issues
- **Main Documentation**: https://github.com/openbancor/catalogmx
- **Dart Package**: https://pub.dev/packages/catalogmx
