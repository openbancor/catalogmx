/// SAT Aeropuertos Catalog
///
/// Catalog of Mexican airports for Carta Porte (CFDI transportation)
library;

/// SAT Aeropuertos Catalog
class SatAeropuertos {
  static List<Map<String, dynamic>>? _data;

  /// Loads the airports data
  static void _loadData() {
    if (_data != null) return;

    // This is a placeholder. In a real implementation, this would load from
    // packages/shared-data/sat/carta_porte_3/aeropuertos.json
    // For Flutter apps, the data would be loaded from assets
    _data = [];
  }

  /// Gets all airports
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets an airport by SAT code
  static Map<String, dynamic>? getByCode(String code) {
    _loadData();
    return _data!.firstWhere(
      (a) => a['code'] == code,
      orElse: () => <String, dynamic>{},
    );
  }

  /// Gets an airport by IATA code
  static Map<String, dynamic>? getByIATA(String iata) {
    _loadData();
    return _data!.firstWhere(
      (a) => a['iata'] == iata.toUpperCase(),
      orElse: () => <String, dynamic>{},
    );
  }

  /// Gets an airport by ICAO code
  static Map<String, dynamic>? getByICAO(String icao) {
    _loadData();
    return _data!.firstWhere(
      (a) => a['icao'] == icao.toUpperCase(),
      orElse: () => <String, dynamic>{},
    );
  }

  /// Validates if an airport code exists
  static bool isValid(String code) {
    return getByCode(code) != null;
  }
}
