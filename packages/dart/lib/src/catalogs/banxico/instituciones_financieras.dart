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

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('instituciones')) {
      _data = (jsonData.first['instituciones'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build indices
    _byCode = {
      for (var inst in _data!)
        inst['codigo'] as String: inst,
    };

    _byName = {
      for (var inst in _data!)
        (inst['nombre'] as String).toUpperCase(): inst,
    };
  }

  /// Obtiene todas las instituciones financieras
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Busca institución por código
  ///
  /// Args:
  ///   codigo: Código de la institución
  ///
  /// Returns:
  ///   Información de la institución o null si no existe
  static Map<String, dynamic>? getByCode(String codigo) {
    _loadData();
    return _byCode![codigo];
  }

  /// Busca institución por nombre (case-insensitive)
  ///
  /// Args:
  ///   nombre: Nombre de la institución
  ///
  /// Returns:
  ///   Información de la institución o null si no existe
  static Map<String, dynamic>? getByName(String nombre) {
    _loadData();
    return _byName![nombre.toUpperCase()];
  }

  /// Valida si un código de institución existe
  ///
  /// Args:
  ///   codigo: Código de la institución
  ///
  /// Returns:
  ///   true si existe, false en caso contrario
  static bool isValid(String codigo) {
    return getByCode(codigo) != null;
  }

  /// Busca instituciones por nombre parcial
  ///
  /// Args:
  ///   query: Texto a buscar
  ///
  /// Returns:
  ///   Lista de instituciones que coinciden
  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final queryNorm = query.toUpperCase();
    return _data!
        .where((inst) =>
            (inst['nombre'] as String).toUpperCase().contains(queryNorm))
        .toList();
  }

  /// Obtiene instituciones por tipo
  ///
  /// Args:
  ///   tipo: Tipo de institución (ej: "BANCO", "CASA DE BOLSA", etc.)
  ///
  /// Returns:
  ///   Lista de instituciones de ese tipo
  static List<Map<String, dynamic>> getByTipo(String tipo) {
    _loadData();
    return _data!
        .where((inst) => inst['tipo'] == tipo)
        .toList();
  }
}
