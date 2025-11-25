/// UDI (Unidades de Inversión) Catalog
///
/// Catalog of UDI values from Banco de México
library;

/// UDI Catalog
class UdiCatalog {
  static List<Map<String, dynamic>>? _data;

  /// Loads the UDI data
  static void _loadData() {
    if (_data != null) return;

    // TODO: Load from packages/shared-data/banxico/udis.json
    // In Flutter apps, this would be loaded from assets
    _data = [];
  }

  /// Gets all UDI data
  static List<Map<String, dynamic>> getData() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets most recent UDI value
  static Map<String, dynamic>? getActual() {
    _loadData();
    if (_data!.isEmpty) return null;

    // Sort by date descending and return first
    final sorted = List.from(_data!)
      ..sort((a, b) => (b['fecha'] as String).compareTo(a['fecha'] as String));
    return sorted.first;
  }

  /// Gets UDI value for a specific date
  static Map<String, dynamic>? getPorFecha(String fecha) {
    _loadData();
    return _data!.firstWhere(
      (record) => record['fecha'] == fecha,
      orElse: () => <String, dynamic>{},
    );
  }

  /// Converts pesos to UDIs
  static double? pesosAUDIs(double pesos, String fecha) {
    final record = getPorFecha(fecha);
    if (record == null || record.isEmpty) return null;

    final valor = record['valor'] as double?;
    if (valor == null) return null;

    return pesos / valor;
  }

  /// Converts UDIs to pesos
  static double? udisAPesos(double udis, String fecha) {
    final record = getPorFecha(fecha);
    if (record == null || record.isEmpty) return null;

    final valor = record['valor'] as double?;
    if (valor == null) return null;

    return udis * valor;
  }
}
