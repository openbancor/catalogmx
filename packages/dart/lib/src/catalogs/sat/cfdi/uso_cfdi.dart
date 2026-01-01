/// Catálogo de Uso de CFDI (SAT)
///
/// Catálogo c_UsoCFDI del SAT para CFDI 4.0
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Uso de CFDI Catalog
class UsoCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/uso_cfdi.json');

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('usos')) {
      _data = (jsonData.first['usos'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build index
    _byClave = {
      for (var item in _data!) item['clave'] as String: item,
    };
  }

  /// Obtiene todos los usos de CFDI
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Obtiene uso de CFDI por clave
  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byClave![clave];
  }

  /// Valida si una clave de uso de CFDI existe
  static bool isValid(String clave) {
    return getByClave(clave) != null;
  }

  /// Busca usos de CFDI por descripción
  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final queryNorm = query.toUpperCase();
    return _data!
        .where((item) =>
            (item['descripcion'] as String).toUpperCase().contains(queryNorm))
        .toList();
  }

  /// Obtiene usos de CFDI aplicables para personas físicas
  static List<Map<String, dynamic>> getParaPersonasFisicas() {
    _loadData();
    return _data!
        .where((item) =>
            item['persona_fisica'] == true ||
            item['aplicaPersonaFisica'] == 'Sí')
        .toList();
  }

  /// Obtiene usos de CFDI aplicables para personas morales
  static List<Map<String, dynamic>> getParaPersonasMorales() {
    _loadData();
    return _data!
        .where((item) =>
            item['persona_moral'] == true || item['aplicaPersonaMoral'] == 'Sí')
        .toList();
  }
}
