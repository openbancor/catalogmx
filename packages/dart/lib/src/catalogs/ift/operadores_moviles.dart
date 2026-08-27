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

    final jsonData = BaseCatalog.loadJsonDataSync(
      'ift/operadores_moviles.json',
    );

    if (jsonData.isNotEmpty && jsonData.first.containsKey('operadores')) {
      _data = (jsonData.first['operadores'] as List)
          .map((e) => Map<String, dynamic>.from(e as Map))
          .toList();
    } else {
      _data = jsonData;
    }

    // The current IFT convenience dataset identifies operators by commercial
    // name and does not assign a synthetic numeric code. Keep code lookup
    // optional instead of inventing regulatory identifiers.
    _byCode = {
      for (final op in _data!)
        if (op['codigo'] != null) op['codigo'].toString(): op,
    };
    _byName = {
      for (final op in _data!)
        if ((op['nombre'] ?? op['nombre_comercial']) != null)
          (op['nombre'] ?? op['nombre_comercial']).toString().toUpperCase(): op,
    };
  }

  /// Obtiene todos los operadores móviles
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Busca operador por código cuando la fuente proporciona uno.
  static Map<String, dynamic>? getByCode(String codigo) {
    _loadData();
    return _byCode![codigo];
  }

  /// Busca operador por nombre comercial (case-insensitive)
  static Map<String, dynamic>? getByName(String nombre) {
    _loadData();
    return _byName![nombre.toUpperCase()];
  }

  /// Valida si un código de operador existe
  static bool isValid(String codigo) {
    return getByCode(codigo) != null;
  }

  /// Busca operadores por nombre parcial
  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final queryNorm = query.toUpperCase();
    return _data!.where((op) {
      final name = (op['nombre'] ?? op['nombre_comercial'] ?? '')
          .toString()
          .toUpperCase();
      final legalName = (op['razon_social'] ?? '').toString().toUpperCase();
      return name.contains(queryNorm) || legalName.contains(queryNorm);
    }).toList();
  }

  /// Obtiene operadores activos
  static List<Map<String, dynamic>> getActivos() {
    _loadData();
    return _data!.where((op) => op['activo'] == true).toList();
  }

  /// Obtiene operadores por tipo de servicio / operador.
  static List<Map<String, dynamic>> getByTipoServicio(String tipoServicio) {
    _loadData();
    return _data!
        .where(
          (op) =>
              op['tipo_servicio'] == tipoServicio || op['tipo'] == tipoServicio,
        )
        .toList();
  }
}
