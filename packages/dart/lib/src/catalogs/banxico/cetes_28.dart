/// CETES 28 días Catalog
///
/// Catalog of CETES 28-day values from Banco de México
library;

/// CETES 28-day Catalog
class Cetes28Catalog {
  static List<Map<String, dynamic>>? _data;

  static void _loadData() {
    if (_data != null) return;
    // TODO: Load from packages/shared-data/banxico/cetes_28.json
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
    return record?['tasa'] as double?;
  }
}
