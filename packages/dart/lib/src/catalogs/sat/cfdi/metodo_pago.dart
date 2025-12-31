/// Catálogo de Métodos de Pago (SAT)
///
/// Catálogo c_MetodoPago del SAT para CFDI 4.0
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Método de Pago Catalog
class MetodoPagoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/metodo_pago.json');

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('metodos_pago')) {
      _data = (jsonData.first['metodos_pago'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build index
    _byClave = {
      for (var item in _data!)
        item['clave'] as String: item,
    };
  }

  /// Obtiene todos los métodos de pago
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Obtiene método de pago por clave
  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byClave![clave];
  }

  /// Valida si una clave de método de pago existe
  static bool isValid(String clave) {
    return getByClave(clave) != null;
  }
}
