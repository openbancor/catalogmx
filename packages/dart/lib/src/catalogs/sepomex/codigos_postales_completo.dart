/// SEPOMEX Códigos Postales Completo Catalog
///
/// Provides access to Mexican postal codes with enhanced address data.
/// Includes settlement type, zone (urban/rural), and state/municipality codes.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';
import 'package:catalogmx/src/utils/text_utils.dart';

/// SEPOMEX Postal Codes Completo Catalog (enhanced data)
class SepomexCodigosPostalesCompleto {
  static List<Map<String, dynamic>>? _data;
  static Map<String, List<Map<String, dynamic>>>? _byCP;
  static Map<String, List<Map<String, dynamic>>>? _byState;
  static Map<String, List<Map<String, dynamic>>>? _byMunicipio;
  static Map<String, List<Map<String, dynamic>>>? _byZona;

  /// Loads the postal codes completo data (lazy loading due to large size)
  static void _loadData() {
    if (_data != null) return;

    _data =
        BaseCatalog.loadJsonDataSync('sepomex/codigos_postales_completo.json');

    // Build lookup maps
    _byCP = {};
    _byState = {};
    _byMunicipio = {};
    _byZona = {};

    for (final code in _data!) {
      final cp = code['cp'] as String?;
      final estado = code['estado'] as String?;
      final municipio = code['municipio'] as String?;
      final zona = code['zona'] as String?;

      if (cp != null) {
        _byCP![cp] ??= [];
        _byCP![cp]!.add(code);
      }

      if (estado != null) {
        _byState![estado] ??= [];
        _byState![estado]!.add(code);
      }

      if (municipio != null) {
        _byMunicipio![municipio] ??= [];
        _byMunicipio![municipio]!.add(code);
      }

      if (zona != null) {
        _byZona![zona] ??= [];
        _byZona![zona]!.add(code);
      }
    }
  }

  /// Gets all postal codes (Warning: Large dataset)
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets postal code information by CP (may return multiple settlements)
  static List<Map<String, dynamic>> getByCP(String codigoPostal) {
    _loadData();
    return List.from(_byCP![codigoPostal] ?? []);
  }

  /// Gets all postal codes for a state (accent-insensitive)
  static List<Map<String, dynamic>> getByState(String estado) {
    _loadData();
    // Try exact match first
    final exactMatch = _byState![estado];
    if (exactMatch != null && exactMatch.isNotEmpty) {
      return List.from(exactMatch);
    }

    // Fallback to normalized search
    final normalized = normalizeText(estado);
    for (final entry in _byState!.entries) {
      if (normalizeText(entry.key) == normalized) {
        return List.from(entry.value);
      }
    }
    return [];
  }

  /// Gets all postal codes for a municipality
  static List<Map<String, dynamic>> getByMunicipio(String municipio) {
    _loadData();
    // Try exact match first
    final exactMatch = _byMunicipio![municipio];
    if (exactMatch != null && exactMatch.isNotEmpty) {
      return List.from(exactMatch);
    }

    // Fallback to normalized search
    final normalized = normalizeText(municipio);
    for (final entry in _byMunicipio!.entries) {
      if (normalizeText(entry.key) == normalized) {
        return List.from(entry.value);
      }
    }
    return [];
  }

  /// Gets postal codes by zone (Urbano or Rural)
  static List<Map<String, dynamic>> getByZona(String zona) {
    _loadData();
    return List.from(_byZona![zona] ?? []);
  }

  /// Searches postal codes by settlement name (accent-insensitive)
  static List<Map<String, dynamic>> searchByAsentamiento(
    String query, {
    String? codigoPostal,
    String? estado,
  }) {
    _loadData();
    final normalized = normalizeText(query);

    var searchList = _data!;
    if (codigoPostal != null) {
      searchList = getByCP(codigoPostal);
    } else if (estado != null) {
      searchList = getByState(estado);
    }

    return searchList.where((code) {
      final asentamiento = code['asentamiento'] as String? ?? '';
      return normalizeText(asentamiento).contains(normalized);
    }).toList();
  }

  /// Gets postal codes by settlement type (Colonia, Fraccionamiento, etc.)
  static List<Map<String, dynamic>> getByTipoAsentamiento(String tipo) {
    _loadData();
    final normalized = normalizeText(tipo);
    return _data!.where((code) {
      final tipoAsentamiento = code['tipo_asentamiento'] as String? ?? '';
      return normalizeText(tipoAsentamiento).contains(normalized);
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
    _byMunicipio = null;
    _byZona = null;
    BaseCatalog.clearCacheFor('sepomex/codigos_postales_completo.json');
  }
}
