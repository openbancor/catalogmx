/// Catálogos SAT CFDI 4.0 - Implementación Completa
///
/// Este archivo contiene todos los catálogos del SAT para CFDI 4.0
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

// ============================================================================
// CATÁLOGOS CFDI 4.0 - CLAVES Y UNIDADES
// ============================================================================

/// Catálogo de Claves de Productos y Servicios (c_ClaveProdServ)
/// NOTA: Este catálogo es muy grande (40,000+ productos)
class ClaveProdServCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/clave_prod_serv.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('productos')
        ? (jsonData.first['productos'] as List).cast<Map<String, dynamic>>()
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
            (item['descripcion'] as String? ?? '').toUpperCase().contains(q) ||
            (item['clave'] as String? ?? '').contains(q))
        .toList();
  }
}

/// Catálogo de Claves de Unidad (c_ClaveUnidad)
class ClaveUnidadCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/clave_unidad.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('unidades')
        ? (jsonData.first['unidades'] as List).cast<Map<String, dynamic>>()
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
// CATÁLOGOS CFDI 4.0 - IMPUESTOS Y MONEDAS
// ============================================================================

/// Catálogo de Impuestos (c_Impuesto)
class ImpuestoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/impuesto.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('impuestos')
        ? (jsonData.first['impuestos'] as List).cast<Map<String, dynamic>>()
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

/// Catálogo de Tipo Factor (c_TipoFactor)
class TipoFactorCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/c_TipoFactor.json');
    _data = jsonData;
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

/// Catálogo de Tasas o Cuotas (c_TasaOCuota)
class TasaOCuotaCatalog {
  static List<Map<String, dynamic>>? _data;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/c_TasaOCuota.json');
    _data = jsonData;
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }
}

/// Catálogo de Objeto de Impuesto (c_ObjetoImp)
class ObjetoImpCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/objeto_imp.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('objetos')
        ? (jsonData.first['objetos'] as List).cast<Map<String, dynamic>>()
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
// CATÁLOGOS CFDI 4.0 - COMPLEMENTOS
// ============================================================================

/// Catálogo de Exportación (c_Exportacion)
class ExportacionCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/exportacion.json');
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('exportaciones')
        ? (jsonData.first['exportaciones'] as List).cast<Map<String, dynamic>>()
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

/// Catálogo de Periodicidad (c_Periodicidad)
class PeriodicidadCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/c_Periodicidad.json');
    _data = jsonData;
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

/// Catálogo de Meses (c_Meses)
class MesesCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/c_Meses.json');
    _data = jsonData;
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

/// Catálogo de Tipo de Relación (c_TipoRelacion)
class TipoRelacionCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData =
        BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/tipo_relacion.json');
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

/// Catálogo de Monedas (c_Moneda)
class MonedaCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/c_Moneda.json');
    _data = jsonData;
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

/// Catálogo de Países (c_Pais)
class PaisCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/c_Pais.json');
    _data = jsonData;
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
            (item['descripcion'] as String? ?? '').toUpperCase().contains(q))
        .toList();
  }
}
