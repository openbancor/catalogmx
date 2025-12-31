/// UMA - Unidad de Medida y Actualización
///
/// Catálogo histórico de valores de la UMA (Unidad de Medida y Actualización)
/// que sustituyó al salario mínimo como referencia para obligaciones y
/// supuestos previstos en leyes federales.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// UMA Catalog
class UMACatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<int, Map<String, dynamic>>? _byYear;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync('mexico/uma.json');

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('valores')) {
      _data = (jsonData.first['valores'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build index by year
    _byYear = {
      for (var item in _data!)
        (item['año'] ?? item['year']) as int: item,
    };
  }

  /// Obtiene todos los valores históricos de UMA
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Obtiene valor de UMA por año
  ///
  /// Args:
  ///   year: Año
  ///
  /// Returns:
  ///   Información de UMA para ese año o null si no existe
  static Map<String, dynamic>? getByYear(int year) {
    _loadData();
    return _byYear![year];
  }

  /// Obtiene valor actual de UMA (último año disponible)
  static Map<String, dynamic>? getCurrent() {
    _loadData();
    if (_data!.isEmpty) return null;
    return _data!.last;
  }

  /// Obtiene valor de UMA diaria para un año
  ///
  /// Args:
  ///   year: Año
  ///
  /// Returns:
  ///   Valor diario o null si no existe
  static double? getValorDiario(int year) {
    final uma = getByYear(year);
    if (uma == null) return null;
    return (uma['diario'] ?? uma['valor_diario']) as double?;
  }

  /// Obtiene valor de UMA mensual para un año
  ///
  /// Args:
  ///   year: Año
  ///
  /// Returns:
  ///   Valor mensual o null si no existe
  static double? getValorMensual(int year) {
    final uma = getByYear(year);
    if (uma == null) return null;
    return (uma['mensual'] ?? uma['valor_mensual']) as double?;
  }

  /// Obtiene valor de UMA anual para un año
  ///
  /// Args:
  ///   year: Año
  ///
  /// Returns:
  ///   Valor anual o null si no existe
  static double? getValorAnual(int year) {
    final uma = getByYear(year);
    if (uma == null) return null;
    return (uma['anual'] ?? uma['valor_anual']) as double?;
  }
}
