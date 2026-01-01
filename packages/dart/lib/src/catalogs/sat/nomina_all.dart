/// Catálogos SAT Nómina 1.2 - Implementación Completa
///
/// Este archivo contiene todos los catálogos del SAT para Nómina 1.2
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

// ============================================================================
// NÓMINA 1.2 - CATÁLOGOS
// ============================================================================

/// Catálogo de Tipos de Nómina
class TipoNominaCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/nomina_1.2/tipo_nomina.json');
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

/// Catálogo de Tipos de Contrato
class TipoContratoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/nomina_1.2/tipo_contrato.json');
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

/// Catálogo de Tipos de Jornada
class TipoJornadaCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/nomina_1.2/tipo_jornada.json');
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

/// Catálogo de Tipos de Régimen
class TipoRegimenCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/nomina_1.2/tipo_regimen.json');
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

/// Catálogo de Periodicidad de Pago
class PeriodicidadPagoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/nomina_1.2/periodicidad_pago.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('periodicidades')
        ? (jsonData.first['periodicidades'] as List)
            .cast<Map<String, dynamic>>()
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

/// Catálogo de Bancos (Nómina)
class BancoNominaCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/nomina_1.2/banco.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('bancos')
        ? (jsonData.first['bancos'] as List).cast<Map<String, dynamic>>()
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
    return _data!
        .where((item) =>
            (item['nombre'] as String? ?? '').toUpperCase().contains(q))
        .toList();
  }
}

/// Catálogo de Riesgo de Puesto
class RiesgoPuestoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/nomina_1.2/riesgo_puesto.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('riesgos')
        ? (jsonData.first['riesgos'] as List).cast<Map<String, dynamic>>()
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
