/// Catálogo de Formas de Pago (SAT)
///
/// Catálogo c_FormaPago del SAT para CFDI 4.0
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Forma de Pago Catalog
class FormaPagoCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/forma_pago.json');

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('formas_pago')) {
      _data = (jsonData.first['formas_pago'] as List)
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

  /// Obtiene todas las formas de pago
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Obtiene forma de pago por clave
  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byClave![clave];
  }

  /// Valida si una clave de forma de pago existe
  static bool isValid(String clave) {
    return getByClave(clave) != null;
  }

  /// Busca formas de pago por descripción
  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final queryNorm = query.toUpperCase();
    return _data!
        .where((item) =>
            (item['descripcion'] as String).toUpperCase().contains(queryNorm))
        .toList();
  }
}
