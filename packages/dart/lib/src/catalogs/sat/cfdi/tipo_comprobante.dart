/// Catálogo de Tipos de Comprobante (SAT)
///
/// Catálogo c_TipoDeComprobante del SAT para CFDI 4.0
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Tipo de Comprobante Catalog
class TipoComprobanteCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync(
      'sat/cfdi_4.0/tipo_comprobante.json',
    );

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('tipos')) {
      _data = (jsonData.first['tipos'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build index
    _byClave = {for (var item in _data!) item['clave'] as String: item};
  }

  /// Obtiene todos los tipos de comprobante
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Obtiene tipo de comprobante por clave
  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byClave![clave];
  }

  /// Valida si una clave de tipo de comprobante existe
  static bool isValid(String clave) {
    return getByClave(clave) != null;
  }
}
