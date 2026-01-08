/// INEGI Municipios Completo Catalog
///
/// Provides access to all 2,469 Mexican municipalities with complete census data.
/// Includes population, housing, and geographic data from INEGI.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// INEGI Municipios Completo Catalog (2,469 municipalities with census data)
class InegMunicipiosCompleto {
  // Private constructor - all methods are static
  InegMunicipiosCompleto._();

  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;
  static Map<String, List<Map<String, dynamic>>>? _byState;

  /// Loads the municipios completo data
  static void _loadData() {
    if (_data != null) return;

    _data = BaseCatalog.loadJsonDataSync('inegi/municipios_completo.json');

    // Build lookup maps
    _byClave = {};
    _byState = {};

    for (final muni in _data!) {
      final clave = muni['cve_completa'] as String;
      final stateCode = muni['cve_entidad'] as String;

      _byClave![clave] = muni;

      _byState![stateCode] ??= [];
      _byState![stateCode]!.add(muni);
    }
  }

  /// Gets all municipalities with complete data
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets a municipality by complete clave (5 digits: state + municipality)
  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byClave![clave];
  }

  /// Gets all municipalities for a state
  static List<Map<String, dynamic>> getByState(String stateCode) {
    _loadData();
    return List.from(_byState![stateCode.padLeft(2, '0')] ?? []);
  }

  /// Gets a municipality by name
  static Map<String, dynamic>? getByName(String name, {String? stateCode}) {
    _loadData();
    final normalized = name.toLowerCase().trim();

    var searchList = _data!;
    if (stateCode != null) {
      searchList = getByState(stateCode);
    }

    for (final muni in searchList) {
      if ((muni['nom_municipio'] as String).toLowerCase().trim() ==
          normalized) {
        return muni;
      }
    }
    return null;
  }

  /// Searches municipalities by partial name match
  static List<Map<String, dynamic>> search(String query, {String? stateCode}) {
    _loadData();
    final normalized = query.toLowerCase().trim();

    var searchList = _data!;
    if (stateCode != null) {
      searchList = getByState(stateCode);
    }

    return searchList.where((muni) {
      return (muni['nom_municipio'] as String).toLowerCase().contains(
            normalized,
          );
    }).toList();
  }

  /// Gets municipalities by population range
  static List<Map<String, dynamic>> getByPopulationRange({
    int? minPopulation,
    int? maxPopulation,
  }) {
    _loadData();
    return _data!.where((muni) {
      final pop = muni['poblacion_total'] as int? ?? 0;
      if (minPopulation != null && pop < minPopulation) return false;
      if (maxPopulation != null && pop > maxPopulation) return false;
      return true;
    }).toList();
  }

  /// Gets total population of a state
  static int getStatePopulation(String stateCode) {
    _loadData();
    final munis = getByState(stateCode);
    return munis.fold(0, (sum, muni) {
      return sum + (muni['poblacion_total'] as int? ?? 0);
    });
  }

  /// Validates if a clave exists
  static bool isValid(String clave) {
    return getByClave(clave) != null;
  }

  /// Gets total count of municipalities
  static int get count {
    _loadData();
    return _data!.length;
  }

  /// Clears cached data to free memory
  static void clearCache() {
    _data = null;
    _byClave = null;
    _byState = null;
    BaseCatalog.clearCacheFor('inegi/municipios_completo.json');
  }
}
