/// Inflación Anual Catalog
///
/// Catalog of annual inflation (INPC) from Banco de México
library;

/// Annual Inflation Catalog
class InflacionAnualCatalog {
  static List<Map<String, dynamic>>? _data;

  static void _loadData() {
    if (_data != null) return;
    // TODO: Load from packages/shared-data/banxico/inflacion_anual.json
    _data = [];
  }

  static List<Map<String, dynamic>> getData() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getActual() {
    _loadData();
    if (_data!.isEmpty) return null;
    final sorted = List.from(_data!)
      ..sort((a, b) => (b['fecha'] as String).compareTo(a['fecha'] as String));
    return sorted.first;
  }

  static double? getTasaActual() {
    final record = getActual();
    return record?['inflacion_anual'] as double?;
  }
}
