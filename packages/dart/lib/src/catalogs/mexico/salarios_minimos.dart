/// Salarios Mínimos Históricos
///
/// Catálogo histórico de salarios mínimos en México
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Salarios Mínimos Catalog
class SalariosMinimosCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<int, Map<String, dynamic>>? _byYear;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync(
      'mexico/salarios_minimos.json',
    );

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('salarios')) {
      _data = (jsonData.first['salarios'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build index by year
    _byYear = {
      for (var item in _data!) (item['año'] ?? item['year']) as int: item,
    };
  }

  /// Obtiene todos los salarios mínimos históricos
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Obtiene salario mínimo por año
  ///
  /// Args:
  ///   year: Año
  ///
  /// Returns:
  ///   Información de salario mínimo para ese año o null si no existe
  static Map<String, dynamic>? getByYear(int year) {
    _loadData();
    return _byYear![year];
  }

  /// Obtiene salario mínimo actual (último año disponible)
  static Map<String, dynamic>? getCurrent() {
    _loadData();
    if (_data!.isEmpty) return null;
    final sorted = List<Map<String, dynamic>>.from(_data!)
      ..sort((a, b) {
        final yearA = (a['año'] ?? a['year'] ?? 0) as int;
        final yearB = (b['año'] ?? b['year'] ?? 0) as int;
        return yearB.compareTo(yearA);
      });
    return sorted.first;
  }

  /// Obtiene salario mínimo diario para un año
  ///
  /// Args:
  ///   year: Año
  ///
  /// Returns:
  ///   Salario diario o null si no existe
  static double? getSalarioDiario(int year) {
    final salario = getByYear(year);
    if (salario == null) return null;
    final value = salario['diario'] ??
        salario['salario_diario'] ??
        salario['resto_pais'] ??
        salario['zona_general'];
    if (value is num) return value.toDouble();
    return null;
  }

  /// Obtiene salario mínimo mensual para un año
  ///
  /// Args:
  ///   year: Año
  ///
  /// Returns:
  ///   Salario mensual o null si no existe
  static double? getSalarioMensual(int year) {
    final salario = getByYear(year);
    if (salario == null) return null;
    final value = salario['mensual'] ?? salario['salario_mensual'];
    if (value is num) return value.toDouble();
    final diario = getSalarioDiario(year);
    return diario != null ? diario * 30.4 : null;
  }

  /// Obtiene información de zona fronteriza para un año
  ///
  /// Args:
  ///   year: Año
  ///
  /// Returns:
  ///   Información de zona fronteriza o null si no existe
  static Map<String, dynamic>? getZonaFronteriza(int year) {
    final salario = getByYear(year);
    if (salario == null) return null;
    final zona = salario['zona_fronteriza'];
    if (zona is Map<String, dynamic>) return zona;

    final value = salario['zona_frontera_norte'];
    if (value is num) {
      final diario = value.toDouble();
      return {
        'diario': diario,
        'mensual': diario * 30.4,
        'anual': diario * 365,
      };
    }
    return null;
  }
}
