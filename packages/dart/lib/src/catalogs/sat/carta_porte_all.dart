/// Catálogos SAT Carta Porte 3.0 - Implementación Completa
///
/// Este archivo contiene todos los catálogos del SAT para Carta Porte 3.0
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

// ============================================================================
// CARTA PORTE 3.0 - TRANSPORTE
// ============================================================================

/// Catálogo de Aeropuertos
class AeropuertosCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;
  static Map<String, Map<String, dynamic>>? _byIATA;
  static Map<String, Map<String, dynamic>>? _byICAO;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/aeropuertos.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('aeropuertos')
        ? (jsonData.first['aeropuertos'] as List).cast<Map<String, dynamic>>()
        : jsonData;

    _byCode = {for (var item in _data!) item['code'] as String: item};
    _byIATA = {
      for (var item in _data!)
        if (item.containsKey('iata')) item['iata'] as String: item
    };
    _byICAO = {
      for (var item in _data!)
        if (item.containsKey('icao')) item['icao'] as String: item
    };
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByCode(String code) {
    _loadData();
    return _byCode![code];
  }

  static Map<String, dynamic>? getByIATA(String iata) {
    _loadData();
    return _byIATA![iata.toUpperCase()];
  }

  static Map<String, dynamic>? getByICAO(String icao) {
    _loadData();
    return _byICAO![icao.toUpperCase()];
  }

  static bool isValid(String code) => getByCode(code) != null;

  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final q = query.toUpperCase();
    return _data!.where((item) =>
        (item['nombre'] as String? ?? '').toUpperCase().contains(q) ||
        (item['ciudad'] as String? ?? '').toUpperCase().contains(q)
    ).toList();
  }
}

/// Catálogo de Puertos Marítimos
class PuertosMaritimosCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/puertos_maritimos.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('puertos')
        ? (jsonData.first['puertos'] as List).cast<Map<String, dynamic>>()
        : jsonData;
    _byCode = {for (var item in _data!) item['code'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByCode(String code) {
    _loadData();
    return _byCode![code];
  }

  static bool isValid(String code) => getByCode(code) != null;

  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final q = query.toUpperCase();
    return _data!.where((item) =>
        (item['nombre'] as String? ?? '').toUpperCase().contains(q)
    ).toList();
  }
}

/// Catálogo de Carreteras
class CarreterasCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/carreteras.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('carreteras')
        ? (jsonData.first['carreteras'] as List).cast<Map<String, dynamic>>()
        : jsonData;
    _byCode = {for (var item in _data!) item['code'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByCode(String code) {
    _loadData();
    return _byCode![code];
  }

  static bool isValid(String code) => getByCode(code) != null;
}

/// Catálogo de Configuraciones de Autotransporte
class ConfigAutotransporteCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/config_autotransporte.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('configuraciones')
        ? (jsonData.first['configuraciones'] as List).cast<Map<String, dynamic>>()
        : jsonData;
    _byClave = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byClave![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

// ============================================================================
// CARTA PORTE 3.0 - MATERIALES Y EMBALAJE
// ============================================================================

/// Catálogo de Material Peligroso
class MaterialPeligrosoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/material_peligroso.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('materiales')
        ? (jsonData.first['materiales'] as List).cast<Map<String, dynamic>>()
        : jsonData;
    _byClave = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byClave![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;

  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final q = query.toUpperCase();
    return _data!.where((item) =>
        (item['descripcion'] as String? ?? '').toUpperCase().contains(q) ||
        (item['nombre'] as String? ?? '').toUpperCase().contains(q)
    ).toList();
  }
}

/// Catálogo de Tipo de Embalaje
class TipoEmbalajeCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/tipo_embalaje.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('tipos')
        ? (jsonData.first['tipos'] as List).cast<Map<String, dynamic>>()
        : jsonData;
    _byClave = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byClave![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// Catálogo de Tipo de Permiso
class TipoPermisoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/carta_porte_3/tipo_permiso.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('tipos')
        ? (jsonData.first['tipos'] as List).cast<Map<String, dynamic>>()
        : jsonData;
    _byClave = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byClave![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}
