/// INEGI Municipios Catalog
///
/// Provides access to all 2,469 Mexican municipalities with INEGI official data.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// INEGI Municipios Catalog (2,469 municipalities)
class InegMunicipios {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byClave;
  static Map<String, List<Map<String, dynamic>>>? _byState;

  // Private constructor - all methods are static
  InegMunicipios._();

  /// Loads the municipios data
  static void _loadData() {
    if (_data != null) return;

    _data = BaseCatalog.loadJsonDataSync('inegi/municipios.json');

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

  /// Gets all municipalities
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
    return _byState![stateCode.padLeft(2, '0')] ?? [];
  }

  /// Gets a municipality by name
  static Map<String, dynamic>? getByName(String name, {String? stateCode}) {
    _loadData();
    final normalized = name.toLowerCase().trim();

    List<Map<String, dynamic>> searchList = _data!;
    if (stateCode != null) {
      searchList = getByState(stateCode);
    }

    for (final muni in searchList) {
      if ((muni['nom_municipio'] as String).toLowerCase().trim() == normalized) {
        return muni;
      }
    }
    return null;
  }

  /// Searches municipalities by partial name match
  static List<Map<String, dynamic>> search(String query, {String? stateCode}) {
    _loadData();
    final normalized = query.toLowerCase().trim();

    List<Map<String, dynamic>> searchList = _data!;
    if (stateCode != null) {
      searchList = getByState(stateCode);
    }

    return searchList.where((muni) {
      return (muni['nom_municipio'] as String).toLowerCase().contains(normalized);
    }).toList();
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
}
