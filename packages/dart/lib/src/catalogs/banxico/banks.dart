/// Banxico Banks Catalog
///
/// Catalog of Mexican banks from Banco de México
library;

/// Banxico Banks Catalog
class BanxicoBanks {
  static List<Map<String, dynamic>>? _data;

  /// Loads the banks data
  static void _loadData() {
    if (_data != null) return;

    // This is a placeholder. In a real implementation, this would load from
    // packages/shared-data/banxico/banks.json
    // For Flutter apps, the data would be loaded from assets
    _data = [];
  }

  /// Gets all banks
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets a bank by code (CLABE bank code)
  static Map<String, dynamic>? getByCode(String code) {
    _loadData();
    return _data!.firstWhere(
      (b) => b['code'] == code,
      orElse: () => <String, dynamic>{},
    );
  }

  /// Gets a bank by name
  static Map<String, dynamic>? getByName(String name) {
    _loadData();
    final normalized = name.toLowerCase();
    return _data!.firstWhere(
      (b) => (b['name'] as String).toLowerCase() == normalized,
      orElse: () => <String, dynamic>{},
    );
  }

  /// Validates if a bank code exists
  static bool isValid(String code) {
    return getByCode(code) != null;
  }
}
