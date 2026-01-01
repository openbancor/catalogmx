/// Catálogo de Operadores Móviles (IFT)
///
/// Catálogo de operadores de telefonía móvil en México
/// registrados ante el Instituto Federal de Telecomunicaciones (IFT)
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Operadores Móviles Catalog
class OperadoresMovilesCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;
  static Map<String, Map<String, dynamic>>? _byName;

  static void _loadData() {
    if (_data != null) return;

    final jsonData =
        BaseCatalog.loadJsonDataSync('ift/operadores_moviles.json');

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('operadores')) {
      _data = (jsonData.first['operadores'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build indices
    _byCode = {
      for (var op in _data!) op['codigo'] as String: op,
    };

    _byName = {
      for (var op in _data!) (op['nombre'] as String).toUpperCase(): op,
    };
  }

  /// Obtiene todos los operadores móviles
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Busca operador por código
  ///
  /// Args:
  ///   codigo: Código del operador
  ///
  /// Returns:
  ///   Información del operador o null si no existe
  static Map<String, dynamic>? getByCode(String codigo) {
    _loadData();
    return _byCode![codigo];
  }

  /// Busca operador por nombre (case-insensitive)
  ///
  /// Args:
  ///   nombre: Nombre del operador
  ///
  /// Returns:
  ///   Información del operador o null si no existe
  static Map<String, dynamic>? getByName(String nombre) {
    _loadData();
    return _byName![nombre.toUpperCase()];
  }

  /// Valida si un código de operador existe
  ///
  /// Args:
  ///   codigo: Código del operador
  ///
  /// Returns:
  ///   true si existe, false en caso contrario
  static bool isValid(String codigo) {
    return getByCode(codigo) != null;
  }

  /// Busca operadores por nombre parcial
  ///
  /// Args:
  ///   query: Texto a buscar
  ///
  /// Returns:
  ///   Lista de operadores que coinciden
  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final queryNorm = query.toUpperCase();
    return _data!
        .where(
            (op) => (op['nombre'] as String).toUpperCase().contains(queryNorm))
        .toList();
  }

  /// Obtiene operadores activos
  static List<Map<String, dynamic>> getActivos() {
    _loadData();
    return _data!.where((op) => op['activo'] == true).toList();
  }

  /// Obtiene operadores por tipo de servicio
  ///
  /// Args:
  ///   tipoServicio: Tipo de servicio (ej: "MOVIL", "MVNO", etc.)
  ///
  /// Returns:
  ///   Lista de operadores que ofrecen ese servicio
  static List<Map<String, dynamic>> getByTipoServicio(String tipoServicio) {
    _loadData();
    return _data!.where((op) => op['tipo_servicio'] == tipoServicio).toList();
  }
}
