/// USD/MXN Exchange Rate FIX Catalog
///
/// Catalog of USD/MXN exchange rate FIX values from Banco de México
library;

/// USD/MXN Exchange Rate Catalog
class TipoCambioUsdCatalog {
  static List<Map<String, dynamic>>? _data;

  /// Loads the exchange rate data
  static void _loadData() {
    if (_data != null) return;

    // TODO: Load from packages/shared-data/banxico/tipo_cambio_usd.json
    // In Flutter apps, this would be loaded from assets
    _data = [];
  }

  /// Gets all exchange rate data
  static List<Map<String, dynamic>> getData() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets most recent exchange rate
  static Map<String, dynamic>? getActual() {
    _loadData();
    if (_data!.isEmpty) return null;

    final sorted = List.from(_data!)
      ..sort((a, b) => (b['fecha'] as String).compareTo(a['fecha'] as String));
    return sorted.first;
  }

  /// Gets exchange rate for a specific date
  static Map<String, dynamic>? getPorFecha(String fecha) {
    _loadData();
    return _data!.firstWhere(
      (record) => record['fecha'] == fecha,
      orElse: () => <String, dynamic>{},
    );
  }

  /// Gets current exchange rate value
  static double? getValorActual() {
    final record = getActual();
    return record?['tipo_cambio'] as double?;
  }

  /// Converts USD to MXN
  static double? usdAMxn(double usd, [String? fecha]) {
    final record = fecha != null ? getPorFecha(fecha) : getActual();
    if (record == null || record.isEmpty) return null;

    final rate = record['tipo_cambio'] as double?;
    if (rate == null) return null;

    return usd * rate;
  }

  /// Converts MXN to USD
  static double? mxnAUsd(double mxn, [String? fecha]) {
    final record = fecha != null ? getPorFecha(fecha) : getActual();
    if (record == null || record.isEmpty) return null;

    final rate = record['tipo_cambio'] as double?;
    if (rate == null) return null;

    return mxn / rate;
  }
}
