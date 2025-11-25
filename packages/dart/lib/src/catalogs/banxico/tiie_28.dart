/// TIIE 28 días Catalog
///
/// Catalog of TIIE 28-day values from Banco de México
library;

/// TIIE 28-day Catalog
class Tiie28Catalog {
  static List<Map<String, dynamic>>? _data;

  /// Loads the TIIE data
  static void _loadData() {
    if (_data != null) return;
    // TODO: Load from packages/shared-data/banxico/tiie_28.json
    _data = [];
  }

  /// Gets all TIIE data
  static List<Map<String, dynamic>> getData() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets most recent TIIE rate
  static Map<String, dynamic>? getActual() {
    _loadData();
    if (_data!.isEmpty) return null;
    final sorted = List.from(_data!)
      ..sort((a, b) => (b['fecha'] as String).compareTo(a['fecha'] as String));
    return sorted.first;
  }

  /// Gets TIIE rate for a specific date
  static Map<String, dynamic>? getPorFecha(String fecha) {
    _loadData();
    return _data!.firstWhere(
      (record) => record['fecha'] == fecha,
      orElse: () => <String, dynamic>{},
    );
  }

  /// Gets current TIIE rate value
  static double? getTasaActual() {
    final record = getActual();
    return record?['tasa'] as double?;
  }
}
