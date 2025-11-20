/// Base catalog class for lazy-loading JSON data
///
/// Provides common functionality for all catalog implementations
library;

import 'dart:convert';
import 'dart:io';

/// Base class for all catalogs with lazy loading support
abstract class BaseCatalog<T> {
  /// Cached data
  static final Map<String, List<Map<String, dynamic>>> _cache = {};

  /// Path to shared-data directory (relative to package root)
  static String sharedDataPath = '../../shared-data';

  /// Loads JSON data from file path with caching
  static Future<List<Map<String, dynamic>>> loadJsonData(String relativePath) async {
    if (_cache.containsKey(relativePath)) {
      return _cache[relativePath]!;
    }

    try {
      final file = File('$sharedDataPath/$relativePath');
      final contents = await file.readAsString();
      final data = json.decode(contents);

      List<Map<String, dynamic>> items;
      if (data is List) {
        items = data.map((item) => item as Map<String, dynamic>).toList();
      } else if (data is Map) {
        // Handle both list and dict formats
        if (data.containsKey('items')) {
          final itemsData = data['items'];
          if (itemsData is List) {
            items = itemsData.map((item) => item as Map<String, dynamic>).toList();
          } else {
            items = [data as Map<String, dynamic>];
          }
        } else {
          items = [data as Map<String, dynamic>];
        }
      } else {
        items = [];
      }

      _cache[relativePath] = items;
      return items;
    } catch (e) {
      // Return empty list if file doesn't exist or can't be read
      _cache[relativePath] = [];
      return [];
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
      final data = json.decode(contents);

      List<Map<String, dynamic>> items;
      if (data is List) {
        items = data.map((item) => item as Map<String, dynamic>).toList();
      } else if (data is Map) {
        if (data.containsKey('items')) {
          final itemsData = data['items'];
          if (itemsData is List) {
            items = itemsData.map((item) => item as Map<String, dynamic>).toList();
          } else {
            items = [data as Map<String, dynamic>];
          }
        } else {
          items = [data as Map<String, dynamic>];
        }
      } else {
        items = [];
      }

      _cache[relativePath] = items;
      return items;
    } catch (e) {
      _cache[relativePath] = [];
      return [];
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
