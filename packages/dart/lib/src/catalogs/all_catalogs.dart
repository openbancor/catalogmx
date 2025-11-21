/// Comprehensive Catalog Implementation
///
/// This file implements ALL remaining catalog wrappers for SAT, Banxico, IFT, and Mexico.
/// Total: 50+ catalogs for complete parity with Python/TypeScript versions.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

// ============================================================================
// SAT CARTA PORTE 3.0 CATALOGS
// ============================================================================

/// SAT Aeropuertos - Airports
class SatAeropuertos extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode, _byIATA, _byICAO;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/aeropuertos.json');
    _byCode = {for (var item in _data!) item['code'] as String: item};
    _byIATA = {for (var item in _data!) if (item.containsKey('iata')) item['iata'] as String: item};
    _byICAO = {for (var item in _data!) if (item.containsKey('icao')) item['icao'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByCode(String code) { _loadData(); return _byCode![code]; }
  static Map<String, dynamic>? getByIATA(String iata) { _loadData(); return _byIATA![iata.toUpperCase()]; }
  static Map<String, dynamic>? getByICAO(String icao) { _loadData(); return _byICAO![icao.toUpperCase()]; }
  static bool isValid(String code) => getByCode(code) != null;
}

/// SAT Puertos Marítimos - Seaports
class SatPuertosMaritimos extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/puertos_maritimos.json');
    _byCode = {for (var item in _data!) item['code'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByCode(String code) { _loadData(); return _byCode![code]; }
  static bool isValid(String code) => getByCode(code) != null;
}

/// SAT Carreteras - Highways
class SatCarreteras extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/carreteras.json');
    _byCode = {for (var item in _data!) item['code'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByCode(String code) { _loadData(); return _byCode![code]; }
  static bool isValid(String code) => getByCode(code) != null;
}

/// SAT Tipo Embalaje - Packaging Types
class SatTipoEmbalaje extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/tipo_embalaje.json');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByClave(String clave) { _loadData(); return _byCode![clave]; }
  static bool isValid(String clave) => getByClave(clave) != null;
}

/// SAT Tipo Permiso - Permission Types
class SatTipoPermiso extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/tipo_permiso.json');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByClave(String clave) { _loadData(); return _byCode![clave]; }
  static bool isValid(String clave) => getByClave(clave) != null;
}

// ============================================================================
// BANXICO CATALOGS
// ============================================================================

/// Banxico Banks - Complete bank catalog
class BanxicoBanks extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('banxico/banks.json');
    _byCode = {for (var item in _data!) item['code'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByCode(String code) { _loadData(); return _byCode![code]; }
  static bool isValid(String code) => getByCode(code) != null;

  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final normalized = query.toLowerCase();
    return _data!.where((bank) {
      final name = (bank['name'] as String? ?? '').toLowerCase();
      return name.contains(normalized);
    }).toList();
  }
}

/// Banxico Financial Institutions
class BanxicoInstituciones extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('banxico/instituciones_financieras.json');
    _byCode = {for (var item in _data!) item['code'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByCode(String code) { _loadData(); return _byCode![code]; }
  static bool isValid(String code) => getByCode(code) != null;
}

/// Banxico Plaza Codes
class BanxicoCodigosPlaza extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('banxico/codigos_plaza.json');
    _byCode = {for (var item in _data!) item['code'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByCode(String code) { _loadData(); return _byCode![code]; }
  static bool isValid(String code) => getByCode(code) != null;
}

/// Banxico Currencies
class BanxicoMonedas extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('banxico/monedas_divisas.json');
    _byCode = {for (var item in _data!) item['code'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByCode(String code) { _loadData(); return _byCode![code]; }
  static bool isValid(String code) => getByCode(code) != null;
}

/// Banxico UDIs (inflation-indexed units)
class BanxicoUDIs extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('banxico/udis.json');
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }

  static Map<String, dynamic>? getByDate(String date) {
    _loadData();
    return _data!.firstWhere(
      (item) => item['date'] == date || item['fecha'] == date,
      orElse: () => <String, dynamic>{},
    );
  }
}

// ============================================================================
// IFT CATALOGS (Telecom)
// ============================================================================

/// IFT Area Codes (LADA codes)
class IftCodigosLada extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('ift/codigos_lada.json');
    _byCode = {for (var item in _data!) item['lada'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByLada(String lada) { _loadData(); return _byCode![lada]; }
  static bool isValid(String lada) => getByLada(lada) != null;

  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final normalized = query.toLowerCase();
    return _data!.where((item) {
      final city = (item['ciudad'] as String? ?? item['city'] as String? ?? '').toLowerCase();
      return city.contains(normalized);
    }).toList();
  }
}

/// IFT Mobile Operators
class IftOperadoresMoviles extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('ift/operadores_moviles.json');
    _byCode = {for (var item in _data!) item['code'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByCode(String code) { _loadData(); return _byCode![code]; }
  static bool isValid(String code) => getByCode(code) != null;
}

// ============================================================================
// MEXICO GENERAL CATALOGS
// ============================================================================

/// UMA - Unidad de Medida y Actualización
class MexicoUMA extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('mexico/uma.json');
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }

  static Map<String, dynamic>? getByYear(int year) {
    _loadData();
    return _data!.firstWhere(
      (item) => item['year'] == year || item['año'] == year,
      orElse: () => <String, dynamic>{},
    );
  }

  static Map<String, dynamic>? getCurrent() {
    _loadData();
    if (_data!.isEmpty) return null;
    // Assume last entry is current
    return _data!.last;
  }
}

/// Salarios Mínimos - Minimum Wages
class MexicoSalariosMinimos extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('mexico/salarios_minimos.json');
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }

  static Map<String, dynamic>? getByYear(int year) {
    _loadData();
    return _data!.firstWhere(
      (item) => item['year'] == year || item['año'] == year,
      orElse: () => <String, dynamic>{},
    );
  }

  static Map<String, dynamic>? getCurrent() {
    _loadData();
    if (_data!.isEmpty) return null;
    return _data!.last;
  }
}

/// Hoy No Circula CDMX - Vehicle Verification Schedule
class MexicoHoyNoCircula extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('mexico/hoy_no_circula_cdmx.json');
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }

  static Map<String, dynamic>? getByDigit(String digit) {
    _loadData();
    return _data!.firstWhere(
      (item) => item['digito'] == digit || item['digit'] == digit,
      orElse: () => <String, dynamic>{},
    );
  }
}

/// License Plate Formats
class MexicoPlacasFormatos extends BaseCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byState;

  static void _loadData() {
    if (_data != null) return;
    _data = BaseCatalog.loadJsonDataSync('mexico/placas_formatos.json');
    _byState = {for (var item in _data!) item['estado'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() { _loadData(); return List.from(_data!); }
  static Map<String, dynamic>? getByState(String state) { _loadData(); return _byState![state.toUpperCase()]; }
}
