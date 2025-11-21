/// INEGI Localidades Catalog
///
/// Provides access to 300K+ Mexican localities with GPS coordinates.
/// Note: This is a large dataset and uses lazy loading.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// INEGI Localidades Catalog (300,000+ localities with GPS)
class InegLocalidades {
  static List<Map<String, dynamic>>? _data;
  static Map<String, List<Map<String, dynamic>>>? _byMunicipality;

  /// Loads the localidades data (lazy loading due to large size)
  static void _loadData() {
    if (_data != null) return;

    _data = BaseCatalog.loadJsonDataSync('inegi/localidades.json');

    // Build lookup by municipality
    _byMunicipality = {};
    for (final loc in _data!) {
      final munClave = loc['cve_completa'] as String? ?? loc['cve_mun'] as String?;
      if (munClave != null) {
        _byMunicipality![munClave] ??= [];
        _byMunicipality![munClave]!.add(loc);
      }
    }
  }

  /// Gets all localities (Warning: Large dataset, may use significant memory)
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets localities for a specific municipality
  static List<Map<String, dynamic>> getByMunicipality(String claveMunicipio) {
    _loadData();
    return _byMunicipality![claveMunicipio] ?? [];
  }

  /// Searches localities by name within a municipality
  static List<Map<String, dynamic>> search(String query, {String? claveMunicipio}) {
    _loadData();
    final normalized = query.toLowerCase().trim();

    List<Map<String, dynamic>> searchList = _data!;
    if (claveMunicipio != null) {
      searchList = getByMunicipality(claveMunicipio);
    }

    return searchList.where((loc) {
      final name = (loc['nom_localidad'] as String? ?? loc['name'] as String? ?? '').toLowerCase();
      return name.contains(normalized);
    }).toList();
  }

  /// Gets localities with GPS coordinates
  static List<Map<String, dynamic>> getWithGPS() {
    _loadData();
    return _data!.where((loc) {
      return loc.containsKey('latitud') && loc.containsKey('longitud') ||
          loc.containsKey('lat') && loc.containsKey('lon');
    }).toList();
  }

  /// Gets total count of localities
  static int get count {
    _loadData();
    return _data!.length;
  }

  /// Clears cached data to free memory
  static void clearCache() {
    _data = null;
    _byMunicipality = null;
    BaseCatalog.clearCacheFor('inegi/localidades.json');
  }
}
