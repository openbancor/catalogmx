/// Catalog helper utilities
///
/// Provides common functions for loading and querying catalog data.
library;

import 'dart:convert';
import 'dart:io';

/// Helper class for loading catalog data from JSON files
class CatalogHelper {
  /// Loads JSON data from a file path
  static Future<List<Map<String, dynamic>>> loadJsonList(String filePath) async {
    try {
      final file = File(filePath);
      final contents = await file.readAsString();
      final data = json.decode(contents);

      if (data is List) {
        return data.map((item) => item as Map<String, dynamic>).toList();
      } else if (data is Map) {
        // Handle both list and dict formats
        if (data.containsKey('items')) {
          final items = data['items'];
          if (items is List) {
            return items.map((item) => item as Map<String, dynamic>).toList();
          }
        }
        // If it's a dict with data, return the values
        return [data as Map<String, dynamic>];
      }

      return [];
    } catch (e) {
      // Return empty list if file doesn't exist or can't be read
      return [];
    }
  }

  /// Loads JSON data synchronously from a file path
  static List<Map<String, dynamic>> loadJsonListSync(String filePath) {
    try {
      final file = File(filePath);
      final contents = file.readAsStringSync();
      final data = json.decode(contents);

      if (data is List) {
        return data.map((item) => item as Map<String, dynamic>).toList();
      } else if (data is Map) {
        // Handle both list and dict formats
        if (data.containsKey('items')) {
          final items = data['items'];
          if (items is List) {
            return items.map((item) => item as Map<String, dynamic>).toList();
          }
        }
        // If it's a dict with data, return the values
        return [data as Map<String, dynamic>];
      }

      return [];
    } catch (e) {
      // Return empty list if file doesn't exist or can't be read
      return [];
    }
  }

  /// Gets the path to shared-data directory
  static String getSharedDataPath() {
    // This will need to be adjusted based on where the package is installed
    // For now, assume it's relative to the package root
    return '../shared-data';
  }
}
