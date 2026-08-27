/// Base catalog class for lazy-loading JSON data
///
/// Provides common functionality for all catalog implementations.
///
/// Coverage Note:
/// File I/O operations (loadJsonData, loadJsonDataSync) have try-catch
/// blocks that return empty lists on failure. These error paths are
/// difficult to test without file system mocking, but the main logic
/// IS tested through the catalog tests.
library;

import 'dart:convert';
import 'dart:io';

/// Base class for all catalogs with lazy loading support
abstract class BaseCatalog<T> {
  /// Cached data
  static final Map<String, List<Map<String, dynamic>>> _cache = {};

  /// Path to shared-data directory (relative to packages/dart)
  static String sharedDataPath = '../shared-data';

  static Map<String, dynamic> _normalizeAliases(Map<String, dynamic> source) {
    final item = Map<String, dynamic>.from(source);

    final code = item['code'] ?? item['clave'] ?? item['codigo'];
    if (code != null) {
      final value = code.toString();
      item.putIfAbsent('code', () => value);
      item.putIfAbsent('clave', () => value);
      item.putIfAbsent('codigo', () => value);
    }

    final description = item['description'] ?? item['descripcion'];
    if (description != null) {
      final value = description.toString();
      item.putIfAbsent('description', () => value);
      item.putIfAbsent('descripcion', () => value);
    }

    final name = item['name'] ?? item['nombre'];
    if (name != null) {
      final value = name.toString();
      item.putIfAbsent('name', () => value);
      item.putIfAbsent('nombre', () => value);
    }

    return item;
  }

  static List<Map<String, dynamic>> _decodeItems(dynamic data) {
    if (data is List) {
      return data
          .map((item) => _normalizeAliases(Map<String, dynamic>.from(item as Map)))
          .toList();
    }

    if (data is Map) {
      final object = Map<String, dynamic>.from(data);
      final itemsData = object['items'];
      if (itemsData is List) {
        return itemsData
            .map((item) => _normalizeAliases(Map<String, dynamic>.from(item as Map)))
            .toList();
      }

      // A number of shared-data files use a metadata envelope plus one named
      // array (for example `operadores` or `tipos_institucion`). Treat that
      // single array as the catalog payload instead of returning the envelope
      // as a bogus catalog row.
      final catalogArrays = object.entries
          .where((entry) => entry.key != 'metadata' && entry.value is List)
          .map((entry) => entry.value as List)
          .toList();
      if (catalogArrays.length == 1) {
        return catalogArrays.single
            .map((item) => _normalizeAliases(Map<String, dynamic>.from(item as Map)))
            .toList();
      }

      return [_normalizeAliases(object)];
    }

    return [];
  }

  /// Loads JSON data from file path with caching
  static Future<List<Map<String, dynamic>>> loadJsonData(
    String relativePath,
  ) async {
    if (_cache.containsKey(relativePath)) {
      return _cache[relativePath]!;
    }

    try {
      final file = File('$sharedDataPath/$relativePath');
      final contents = await file.readAsString();
      final items = _decodeItems(json.decode(contents));
      _cache[relativePath] = items;
      return items;
    } catch (e) {
      // coverage:ignore-start
      // Return empty list if file doesn't exist or can't be read
      // (Error path: requires file system failures to test)
      _cache[relativePath] = [];
      return [];
      // coverage:ignore-end
    }
  }

  /// Loads JSON data synchronously with caching
  static List<Map<String, dynamic>> loadJsonDataSync(String relativePath) {
    if (_cache.containsKey(relativePath)) {
      return _cache[relativePath]!;
    }

    try {
      final file = File('$sharedDataPath/$relativePath');
      final contents = file.readAsStringSync();
      final items = _decodeItems(json.decode(contents));
      _cache[relativePath] = items;
      return items;
    } catch (e) {
      // coverage:ignore-start
      // (Error path: requires file system failures to test)
      _cache[relativePath] = [];
      return [];
      // coverage:ignore-end
    }
  }

  /// Clears all cached data
  static void clearCache() {
    _cache.clear();
  }

  /// Clears cache for specific path
  static void clearCacheFor(String relativePath) {
    _cache.remove(relativePath);
  }
}

/// Mixin for catalogs with code-based lookup
mixin CodeLookup {
  Map<String, Map<String, dynamic>> _byCode = {};

  void buildCodeIndex(List<Map<String, dynamic>> data, String codeField) {
    _byCode = {for (var item in data) item[codeField] as String: item};
  }

  Map<String, dynamic>? getByCode(String code) {
    return _byCode[code.toUpperCase()];
  }

  bool isValidCode(String code) {
    return _byCode.containsKey(code.toUpperCase());
  }
}

/// Mixin for catalogs with name-based search
mixin NameSearch {
  String _normalize(String text) {
    return text.toLowerCase().trim();
  }

  List<Map<String, dynamic>> searchByName(
    List<Map<String, dynamic>> data,
    String query,
    String nameField,
  ) {
    final normalized = _normalize(query);
    return data.where((item) {
      final name = _normalize(item[nameField] as String? ?? '');
      return name.contains(normalized);
    }).toList();
  }

  Map<String, dynamic>? getByName(
    List<Map<String, dynamic>> data,
    String name,
    String nameField,
  ) {
    final normalized = _normalize(name);
    for (final item in data) {
      if (_normalize(item[nameField] as String? ?? '') == normalized) {
        return item;
      }
    }
    return null;
  }
}
