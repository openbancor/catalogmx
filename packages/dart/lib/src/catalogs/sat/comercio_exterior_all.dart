/// Catálogos SAT Comercio Exterior - Implementación Completa
///
/// Este archivo contiene todos los catálogos del SAT para Comercio Exterior
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

// ============================================================================
// COMERCIO EXTERIOR - ADUANAS Y PEDIMENTOS
// ============================================================================

/// Catálogo de Claves de Pedimento
class ClavePedimentoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync(
      'sat/comercio_exterior/claves_pedimento.json',
    );
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('claves')
        ? (jsonData.first['claves'] as List).cast<Map<String, dynamic>>()
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
        .where(
          (item) =>
              (item['descripcion'] as String? ?? '').toUpperCase().contains(q),
        )
        .toList();
  }
}

/// Catálogo de Unidades de Aduana
class UnidadAduanaCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync(
      'sat/comercio_exterior/unidades_aduana.json',
    );
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

  static List<Map<String, dynamic>> getByEstado(String estado) {
    _loadData();
    return _data!.where((item) => item['estado'] == estado).toList();
  }
}

// ============================================================================
// COMERCIO EXTERIOR - INTERNACIONALES
// ============================================================================

/// Catálogo de Países
class PaisComercioExteriorCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync(
      'sat/comercio_exterior/paises.json',
    );
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('paises')
        ? (jsonData.first['paises'] as List).cast<Map<String, dynamic>>()
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
        .where(
          (item) =>
              (item['nombre'] as String? ?? '').toUpperCase().contains(q) ||
              (item['pais'] as String? ?? '').toUpperCase().contains(q),
        )
        .toList();
  }
}

/// Catálogo de Estados de USA y Canadá
class EstadosUSACanadaCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync(
      'sat/comercio_exterior/estados_usa_canada.json',
    );
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('estados')
        ? (jsonData.first['estados'] as List).cast<Map<String, dynamic>>()
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

  static List<Map<String, dynamic>> getByPais(String pais) {
    _loadData();
    return _data!.where((item) => item['pais'] == pais).toList();
  }
}

/// Catálogo de Monedas (Comercio Exterior)
class MonedaComercioExteriorCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync(
      'sat/comercio_exterior/monedas.json',
    );
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('monedas')
        ? (jsonData.first['monedas'] as List).cast<Map<String, dynamic>>()
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

/// Catálogo de INCOTERMS
class IncotermsCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync(
      'sat/comercio_exterior/incoterms.json',
    );
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('incoterms')
        ? (jsonData.first['incoterms'] as List).cast<Map<String, dynamic>>()
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

/// Catálogo de Motivos de Traslado
class MotivoTrasladoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync(
      'sat/comercio_exterior/motivos_traslado.json',
    );
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('motivos')
        ? (jsonData.first['motivos'] as List).cast<Map<String, dynamic>>()
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

/// Catálogo de Registro de Identidad Tributaria
class RegistroIdentTribCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;
    final jsonData = BaseCatalog.loadJsonDataSync(
      'sat/comercio_exterior/registro_ident_trib.json',
    );
    _data = jsonData.isNotEmpty && jsonData.first.containsKey('registros')
        ? (jsonData.first['registros'] as List).cast<Map<String, dynamic>>()
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
