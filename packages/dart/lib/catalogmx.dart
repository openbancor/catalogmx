/// Enterprise-grade Mexican data validation and official catalog library for Flutter/Dart
///
/// This library provides:
/// - **Validators**: RFC, CURP, CLABE, NSS with complete official algorithms
/// - **Generators**: Create valid RFC and CURP codes from personal data
/// - **58+ Official Catalogs**: SAT, INEGI, SEPOMEX, Banxico with 170K+ records
/// - **Type-safe**: Full null-safety support for Dart 3.0+
/// - **Offline**: All validators and catalogs work without internet connection
///
/// ## Quick Start
///
/// ```dart
/// import 'package:catalogmx/catalogmx.dart';
///
/// // Validate identifiers
/// bool isValid = validateRFC('XAXX010101000');
/// bool isValidCurp = validateCURP('OEAF771012HMCRGR09');
/// bool isValidClabe = validateCLABE('002010077777777771');
///
/// // Generate RFC
/// String rfc = generateRFC(
///   nombre: 'Juan',
///   apellidoPaterno: 'García',
///   apellidoMaterno: 'López',
///   fechaNacimiento: DateTime(1990, 5, 15),
/// );
///
/// // Access catalogs
/// List<Map<String, dynamic>> states = InegStates.getAll();
/// Map<String, dynamic>? cdmx = InegStates.getByCode('09');
/// ```
library catalogmx;

// Validators
export 'src/validators/rfc_validator.dart';
export 'src/validators/curp_validator.dart';
export 'src/validators/clabe_validator.dart';
export 'src/validators/nss_validator.dart';

// Catalogs - INEGI
export 'src/catalogs/inegi/states.dart';
export 'src/catalogs/inegi/municipios.dart';

// Catalogs - SAT
export 'src/catalogs/sat/aeropuertos.dart';

// Catalogs - Banxico
export 'src/catalogs/banxico/banks.dart';

// Utilities
export 'src/utils/text_utils.dart';
export 'src/utils/date_utils.dart';
