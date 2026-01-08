/// Catalogs Library - All Mexican Data Catalogs
///
/// This library provides access to all Mexican official data catalogs
/// including SAT, Banxico, INEGI, SEPOMEX, IFT, and general Mexico catalogs.
library catalogs;

// ============================================================================
// BASE
// ============================================================================
export 'base_catalog.dart';

// ============================================================================
// BANXICO CATALOGS
// ============================================================================
export 'banxico/banks.dart';
export 'banxico/cetes_28.dart';
export 'banxico/codigos_plaza.dart';
export 'banxico/inflacion_anual.dart';
export 'banxico/instituciones_financieras.dart';
export 'banxico/monedas_divisas.dart';
export 'banxico/salarios_minimos.dart'
    hide SalariosMinimosCatalog; // Conflicts with Mexico version
export 'banxico/tiie_28.dart';
export 'banxico/tipo_cambio_usd.dart';
export 'banxico/udis.dart';

// ============================================================================
// IFT CATALOGS
// ============================================================================
export 'ift/operadores_moviles.dart';

// ============================================================================
// CNBV CATALOGS
// ============================================================================
export 'cnbv/sectores.dart';

// ============================================================================
// INEGI CATALOGS
// ============================================================================
export 'inegi/localidades.dart';
export 'inegi/municipios.dart';
export 'inegi/scian.dart';
export 'inegi/states.dart';

// ============================================================================
// MEXICO GENERAL CATALOGS
// ============================================================================
export 'mexico/giros_mercantiles.dart';
export 'mexico/hoy_no_circula.dart';
export 'mexico/placas_formatos.dart';
export 'mexico/salarios_minimos.dart'; // This is the main SalariosMinimosCatalog
export 'mexico/uma.dart';

// ============================================================================
// SAT CATALOGS - CFDI 4.0
// ============================================================================
export 'sat/cfdi/uso_cfdi.dart';
export 'sat/cfdi/forma_pago.dart';
export 'sat/cfdi/metodo_pago.dart';
export 'sat/cfdi/regimen_fiscal.dart';
export 'sat/cfdi/tipo_comprobante.dart';
export 'sat/cfdi_all.dart';

// ============================================================================
// SAT CATALOGS - CARTA PORTE
// ============================================================================
export 'sat/aeropuertos.dart';
export 'sat/carta_porte_all.dart';

// ============================================================================
// SAT CATALOGS - COMERCIO EXTERIOR
// ============================================================================
export 'sat/comercio_exterior_all.dart';

// ============================================================================
// SAT CATALOGS - NÓMINA
// ============================================================================
export 'sat/nomina_all.dart';

// ============================================================================
// SEPOMEX CATALOGS
// ============================================================================
export 'sepomex/codigos_postales.dart';
