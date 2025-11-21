/// SEPOMEX Códigos Postales Catalog
///
/// Provides access to 157,000+ Mexican postal codes with complete address data.
/// Note: This is a very large dataset and uses lazy loading.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// SEPOMEX Postal Codes Catalog (157,000+ records)
class SepomexCodigosPostales {
  static List<Map<String, dynamic>>? _data;
  static Map<String, List<Map<String, dynamic>>>? _byCP;
  static Map<String, List<Map<String, dynamic>>>? _byState;

  /// Loads the postal codes data (lazy loading due to large size)
  static void _loadData() {
    if (_data != null) return;

    _data = BaseCatalog.loadJsonDataSync('sepomex/codigos_postales.json');

    // Build lookup maps
    _byCP = {};
    _byState = {};

    for (final code in _data!) {
      final cp = code['codigo_postal'] as String? ?? code['cp'] as String?;
      final state = code['estado'] as String? ?? code['d_estado'] as String?;

      if (cp != null) {
        _byCP![cp] ??= [];
        _byCP![cp]!.add(code);
      }

      if (state != null) {
        _byState![state] ??= [];
        _byState![state]!.add(code);
      }
    }
  }

  /// Gets all postal codes (Warning: Very large dataset, may use significant memory)
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets postal code information by CP (may return multiple colonias)
  static List<Map<String, dynamic>> getByCP(String codigoPostal) {
    _loadData();
    return _byCP![codigoPostal] ?? [];
  }

  /// Gets all postal codes for a state
  static List<Map<String, dynamic>> getByState(String estado) {
    _loadData();
    return _byState![estado.toUpperCase()] ?? [];
  }

  /// Searches postal codes by colonia name
  static List<Map<String, dynamic>> searchByColonia(String query, {String? codigoPostal}) {
    _loadData();
    final normalized = query.toLowerCase().trim();

    List<Map<String, dynamic>> searchList = _data!;
    if (codigoPostal != null) {
      searchList = getByCP(codigoPostal);
    }

    return searchList.where((code) {
      final colonia = (code['colonia'] as String? ?? code['d_asenta'] as String? ?? '').toLowerCase();
      return colonia.contains(normalized);
    }).toList();
  }

  /// Searches postal codes by municipality
  static List<Map<String, dynamic>> searchByMunicipio(String query) {
    _loadData();
    final normalized = query.toLowerCase().trim();

    return _data!.where((code) {
      final mun = (code['municipio'] as String? ?? code['d_mnpio'] as String? ?? '').toLowerCase();
      return mun.contains(normalized);
    }).toList();
  }

  /// Validates if a postal code exists
  static bool isValid(String codigoPostal) {
    _loadData();
    return _byCP!.containsKey(codigoPostal);
  }

  /// Gets total count of postal codes
  static int get count {
    _loadData();
    return _data!.length;
  }

  /// Clears cached data to free memory
  static void clearCache() {
    _data = null;
    _byCP = null;
    _byState = null;
    BaseCatalog.clearCacheFor('sepomex/codigos_postales.json');
  }
}
