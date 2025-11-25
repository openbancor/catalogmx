/// Salarios Mínimos Catalog
///
/// Catalog of minimum wage data from Banco de México
library;

/// Minimum Wage Catalog
class SalariosMinimosCatalog {
  static List<Map<String, dynamic>>? _data;

  static void _loadData() {
    if (_data != null) return;
    // TODO: Load from packages/shared-data/banxico/salarios_minimos.json
    _data = [];
  }

  static List<Map<String, dynamic>> getData() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getActualGeneral() {
    _loadData();
    if (_data!.isEmpty) return null;

    final generalRecords = _data!.where((r) => r['zona'] == 'general').toList();
    if (generalRecords.isEmpty) return null;

    generalRecords
        .sort((a, b) => (b['fecha'] as String).compareTo(a['fecha'] as String));
    return generalRecords.first;
  }

  static Map<String, dynamic>? getActualFrontera() {
    _loadData();
    if (_data!.isEmpty) return null;

    final fronteraRecords =
        _data!.where((r) => r['zona'] == 'frontera_norte').toList();
    if (fronteraRecords.isEmpty) return null;

    fronteraRecords
        .sort((a, b) => (b['fecha'] as String).compareTo(a['fecha'] as String));
    return fronteraRecords.first;
  }

  static double? getSalarioActualZona(String zona) {
    final record =
        zona == 'frontera_norte' ? getActualFrontera() : getActualGeneral();
    return record?['salario_minimo'] as double?;
  }
}
