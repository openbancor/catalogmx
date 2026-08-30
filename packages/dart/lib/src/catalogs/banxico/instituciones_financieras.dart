/// Catálogo de Instituciones Financieras (Banxico)
///
/// Catálogo oficial de instituciones financieras registradas ante Banxico
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Instituciones Financieras Catalog
class InstitucionesFinancierasCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;
  static Map<String, Map<String, dynamic>>? _byName;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync(
      'banxico/instituciones_financieras.json',
    );
    final first = jsonData.isNotEmpty ? jsonData.first : null;

    // BaseCatalog unwraps metadata envelopes with a single catalog array. Keep
    // compatibility with older wrapped files too.
    if (first != null && first.containsKey('instituciones')) {
      _data = (first['instituciones'] as List)
          .map((e) => Map<String, dynamic>.from(e as Map))
          .toList();
    } else if (first != null && first.containsKey('tipos_institucion')) {
      _data = (first['tipos_institucion'] as List)
          .map((e) => Map<String, dynamic>.from(e as Map))
          .toList();
    } else {
      _data = jsonData;
    }

    _byCode = {};
    _byName = {};
    for (final item in _data!) {
      final displayName = item['nombre'] ?? item['tipo'];
      if (displayName != null) {
        item['nombre'] = displayName.toString();
        _byName![displayName.toString().toUpperCase()] = item;
      }
      final code = item['codigo'];
      if (code != null) _byCode![code.toString()] = item;
    }
  }

  /// Obtiene todas las instituciones financieras
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Busca institución por código
  static Map<String, dynamic>? getByCode(String codigo) {
    _loadData();
    return _byCode![codigo];
  }

  /// Busca institución por nombre (case-insensitive)
  static Map<String, dynamic>? getByName(String nombre) {
    _loadData();
    return _byName![nombre.toUpperCase()];
  }

  /// Valida si un código de institución existe
  static bool isValid(String codigo) {
    return getByCode(codigo) != null;
  }

  /// Busca instituciones por nombre parcial
  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final queryNorm = query.toUpperCase();
    return _data!.where((inst) {
      final name = inst['nombre']?.toString().toUpperCase() ?? '';
      return name.contains(queryNorm);
    }).toList();
  }

  /// Obtiene instituciones por tipo
  static List<Map<String, dynamic>> getByTipo(String tipo) {
    _loadData();
    return _data!.where((inst) => inst['tipo'] == tipo).toList();
  }
}
