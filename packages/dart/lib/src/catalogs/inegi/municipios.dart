/// INEGI Municipios Catalog
///
/// Provides access to Mexican municipalities (municipios) data from INEGI.
/// This is a placeholder implementation. In a full implementation, this would
/// load data from the shared-data JSON files.
library;

/// INEGI Municipios Catalog
class InegMunicipios {
  static List<Map<String, dynamic>>? _data;

  /// Loads the municipios data
  static void _loadData() {
    if (_data != null) return;

    // This is a placeholder. In a real implementation, this would load from
    // packages/shared-data/inegi/municipios.json
    // For Flutter apps, the data would be loaded from assets
    _data = [];
  }

  /// Gets all municipios
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets municipios by state code
  static List<Map<String, dynamic>> getByState(String stateCode) {
    _loadData();
    return _data!
        .where((m) => m['estado_code'] == stateCode.toUpperCase())
        .toList();
  }

  /// Gets a municipio by clave
  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _data!.firstWhere(
      (m) => m['clave'] == clave,
      orElse: () => <String, dynamic>{},
    );
  }

  /// Validates if a clave exists
  static bool isValid(String clave) {
    return getByClave(clave) != null;
  }
}
