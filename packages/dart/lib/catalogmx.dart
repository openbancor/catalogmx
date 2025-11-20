/// Enterprise-grade Mexican data validation and official catalog library for Flutter/Dart
///
/// This library provides:
/// - **Validators**: RFC, CURP, CLABE, NSS with complete official algorithms
/// - **Generators**: Create valid RFC and CURP codes from personal data
/// - **58+ Official Catalogs**: SAT, INEGI, SEPOMEX, Banxico, IFT with 470K+ records
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
/// List<Map<String, dynamic>> banks = BanxicoBanks.getAll();
/// ```
library catalogmx;

// ============================================================================
// VALIDATORS
// ============================================================================

export 'src/validators/rfc_validator.dart';
export 'src/validators/curp_validator.dart';
export 'src/validators/clabe_validator.dart';
export 'src/validators/nss_validator.dart';

// ============================================================================
// CATALOGS - INEGI (Instituto Nacional de Estadística y Geografía)
// ============================================================================

export 'src/catalogs/inegi/states.dart';
export 'src/catalogs/inegi/municipios.dart';
export 'src/catalogs/inegi/localidades.dart';

// ============================================================================
// CATALOGS - SEPOMEX (Servicio Postal Mexicano)
// ============================================================================

export 'src/catalogs/sepomex/codigos_postales.dart';

// ============================================================================
// CATALOGS - SAT (Servicio de Administración Tributaria)
// ============================================================================

// SAT CFDI 4.0 Catalogs (15 catalogs)
export 'src/catalogs/sat/cfdi_catalogs.dart';

// SAT Carta Porte, Banxico, IFT, Mexico (30+ catalogs)
export 'src/catalogs/all_catalogs.dart';

// ============================================================================
// UTILITIES
// ============================================================================

export 'src/utils/text_utils.dart';
export 'src/utils/date_utils.dart';
export 'src/catalogs/base_catalog.dart';
