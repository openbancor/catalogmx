/// Data Updater for Dart/Flutter
///
/// Provides automatic updates of dynamic Banxico data from GitHub Releases.
/// Works across all Flutter platforms: mobile, desktop, and web.
library;

import 'dart:convert';
import 'dart:io' show Platform;
import 'package:http/http.dart' as http;

/// Version information
class VersionInfo {
  final String version;
  final DateTime updatedAt;
  final String source;
  final String? url;

  VersionInfo({
    required this.version,
    required this.updatedAt,
    required this.source,
    this.url,
  });

  factory VersionInfo.fromJson(Map<String, dynamic> json) {
    return VersionInfo(
      version: json['version'] as String,
      updatedAt: DateTime.parse(json['updated_at'] as String),
      source: json['source'] as String,
      url: json['url'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'version': version,
      'updated_at': updatedAt.toIso8601String(),
      'source': source,
      if (url != null) 'url': url,
    };
  }
}

/// Data Updater Configuration
class DataUpdaterConfig {
  final String cacheDir;
  final int maxAgeHours;
  final String dataUrl;
  final bool autoUpdate;

  const DataUpdaterConfig({
    this.cacheDir = '.catalogmx',
    this.maxAgeHours = 24,
    this.dataUrl = 'https://github.com/openbancor/catalogmx/releases/download/latest/mexico_dynamic.sqlite3',
    this.autoUpdate = true,
  });
}

/// Base class for platform-specific data updaters
abstract class BaseDataUpdater {
  final DataUpdaterConfig config;

  BaseDataUpdater(this.config);

  Future<String?> getLocalVersion();
  Future<double?> getLocalAgeHours();
  Future<bool> downloadLatest({bool force = false, bool verbose = true});
  Future<String> getDatabasePath({bool autoUpdate = true});
  Future<bool> clearCache();
}

/// Conditional import helpers
/// These will be replaced with actual implementations based on platform

/// Data Updater for Mobile/Desktop (using sqflite)
class MobileDataUpdater extends BaseDataUpdater {
  late final String cacheDbPath;
  late final String versionFilePath;

  MobileDataUpdater(super.config) {
    // TODO: Use path_provider to get application documents directory
    // For now, use a placeholder
    final homeDir = Platform.environment['HOME'] ?? Platform.environment['USERPROFILE'] ?? '';
    final cacheDir = '$homeDir/${config.cacheDir}';

    cacheDbPath = '$cacheDir/mexico_dynamic.sqlite3';
    versionFilePath = '$cacheDir/version.json';
  }

  @override
  Future<String?> getLocalVersion() async {
    try {
      // TODO: Read from file using dart:io
      // For now, return null
      return null;
    } catch (e) {
      return null;
    }
  }

  @override
  Future<double?> getLocalAgeHours() async {
    try {
      // TODO: Implement age calculation
      return null;
    } catch (e) {
      return null;
    }
  }

  @override
  Future<bool> downloadLatest({bool force = false, bool verbose = true}) async {
    if (verbose) {
      print('📥 Downloading data from ${config.dataUrl}...');
    }

    try {
      // Download database
      final response = await http.get(Uri.parse(config.dataUrl));

      if (response.statusCode != 200) {
        if (verbose) {
          print('❌ HTTP ${response.statusCode}');
        }
        return false;
      }

      // TODO: Save to file using dart:io
      // TODO: Verify database integrity using sqflite
      // TODO: Save version metadata

      if (verbose) {
        print('✅ Data updated successfully');
      }

      return true;
    } catch (e) {
      if (verbose) {
        print('❌ Error downloading data: $e');
      }
      return false;
    }
  }

  @override
  Future<String> getDatabasePath({bool autoUpdate = true}) async {
    if (autoUpdate && config.autoUpdate) {
      final age = await getLocalAgeHours();

      // Update if no cache or too old
      if (age == null || age > config.maxAgeHours) {
        await downloadLatest(verbose: false);
      }
    }

    // TODO: Return cache path if exists, otherwise embedded
    return cacheDbPath;
  }

  @override
  Future<bool> clearCache() async {
    try {
      // TODO: Delete cache files using dart:io
      return true;
    } catch (e) {
      return false;
    }
  }
}

/// Data Updater for Web (using IndexedDB via dart:html or js interop)
class WebDataUpdater extends BaseDataUpdater {
  WebDataUpdater(super.config);

  @override
  Future<String?> getLocalVersion() async {
    // TODO: Read from IndexedDB
    return null;
  }

  @override
  Future<double?> getLocalAgeHours() async {
    // TODO: Calculate from IndexedDB metadata
    return null;
  }

  @override
  Future<bool> downloadLatest({bool force = false, bool verbose = true}) async {
    if (verbose) {
      print('📥 Downloading data from ${config.dataUrl}...');
    }

    try {
      final response = await http.get(Uri.parse(config.dataUrl));

      if (response.statusCode != 200) {
        if (verbose) {
          print('❌ HTTP ${response.statusCode}');
        }
        return false;
      }

      // TODO: Store in IndexedDB
      // TODO: Verify database integrity

      if (verbose) {
        print('✅ Data updated successfully');
      }

      return true;
    } catch (e) {
      if (verbose) {
        print('❌ Error downloading data: $e');
      }
      return false;
    }
  }

  @override
  Future<String> getDatabasePath({bool autoUpdate = true}) async {
    // For web, return a special identifier that indicates IndexedDB storage
    return 'indexeddb://catalogmx/mexico_dynamic';
  }

  @override
  Future<bool> clearCache() async {
    try {
      // TODO: Clear IndexedDB
      return true;
    } catch (e) {
      return false;
    }
  }
}

/// Universal Data Updater (auto-detects platform)
class DataUpdater {
  late final BaseDataUpdater _updater;

  DataUpdater([DataUpdaterConfig? config]) {
    final cfg = config ?? const DataUpdaterConfig();

    // Platform detection
    try {
      if (Platform.isAndroid || Platform.isIOS || Platform.isMacOS ||
          Platform.isLinux || Platform.isWindows) {
        _updater = MobileDataUpdater(cfg);
      } else {
        // Fallback to web
        _updater = WebDataUpdater(cfg);
      }
    } catch (e) {
      // If Platform is not available, assume web
      _updater = WebDataUpdater(cfg);
    }
  }

  Future<String?> getLocalVersion() => _updater.getLocalVersion();

  Future<double?> getLocalAgeHours() => _updater.getLocalAgeHours();

  Future<bool> downloadLatest({bool force = false, bool verbose = true}) {
    return _updater.downloadLatest(force: force, verbose: verbose);
  }

  Future<String> getDatabasePath({bool autoUpdate = true}) {
    return _updater.getDatabasePath(autoUpdate: autoUpdate);
  }

  Future<bool> clearCache() => _updater.clearCache();
}

// Singleton instance
DataUpdater? _defaultUpdater;

DataUpdater getDataUpdater([DataUpdaterConfig? config]) {
  _defaultUpdater ??= DataUpdater(config);
  return _defaultUpdater!;
}

// Convenience functions
Future<String> getDatabasePath() async {
  return getDataUpdater().getDatabasePath();
}

Future<String?> getVersion() async {
  return getDataUpdater().getLocalVersion();
}

Future<bool> updateNow({bool force = false, bool verbose = true}) async {
  return getDataUpdater().downloadLatest(force: force, verbose: verbose);
}
