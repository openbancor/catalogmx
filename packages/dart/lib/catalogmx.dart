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
// CALCULATORS
// ============================================================================

export 'src/calculators/isr.dart';

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
// CATALOGS - BANXICO (Banco de México)
// ============================================================================

export 'src/catalogs/banxico/banks.dart';
export 'src/catalogs/banxico/codigos_plaza.dart';
export 'src/catalogs/banxico/instituciones_financieras.dart';
export 'src/catalogs/banxico/monedas_divisas.dart';
export 'src/catalogs/banxico/cetes_28.dart';
export 'src/catalogs/banxico/inflacion_anual.dart';
export 'src/catalogs/banxico/salarios_minimos.dart'
    hide SalariosMinimosCatalog; // Conflicts with Mexico version
export 'src/catalogs/banxico/tiie_28.dart';
export 'src/catalogs/banxico/tipo_cambio_usd.dart';
export 'src/catalogs/banxico/udis.dart';

// ============================================================================
// CATALOGS - IFT (Instituto Federal de Telecomunicaciones)
// ============================================================================

export 'src/catalogs/ift/operadores_moviles.dart';

// ============================================================================
// CATALOGS - MEXICO (General Mexican Catalogs)
// ============================================================================

export 'src/catalogs/mexico/hoy_no_circula.dart';
export 'src/catalogs/mexico/placas_formatos.dart';
export 'src/catalogs/mexico/salarios_minimos.dart'; // This is the main SalariosMinimosCatalog
export 'src/catalogs/mexico/uma.dart';

// ============================================================================
// CATALOGS - SAT (Servicio de Administración Tributaria)
// ============================================================================

// SAT CFDI 4.0 Catalogs (15+ catalogs)
export 'src/catalogs/sat/cfdi/uso_cfdi.dart';
export 'src/catalogs/sat/cfdi/forma_pago.dart';
export 'src/catalogs/sat/cfdi/metodo_pago.dart';
export 'src/catalogs/sat/cfdi/regimen_fiscal.dart';
export 'src/catalogs/sat/cfdi/tipo_comprobante.dart';
export 'src/catalogs/sat/cfdi_all.dart';

// SAT Carta Porte Catalogs (7+ catalogs)
export 'src/catalogs/sat/aeropuertos.dart';
export 'src/catalogs/sat/carta_porte_all.dart';

// SAT Comercio Exterior Catalogs (8+ catalogs)
export 'src/catalogs/sat/comercio_exterior_all.dart';

// SAT Nómina Catalogs (7+ catalogs)
export 'src/catalogs/sat/nomina_all.dart';

// Legacy catalog exports (backwards compatibility)
export 'src/catalogs/sat/cfdi_catalogs.dart';
// Note: all_catalogs.dart is not exported to avoid ambiguous exports
// All catalogs are already exported individually from their respective modules

// ============================================================================
// UTILITIES
// ============================================================================

export 'src/utils/text_utils.dart';
export 'src/utils/date_utils.dart';
export 'src/utils/catalog_helper.dart';
export 'src/catalogs/base_catalog.dart';
