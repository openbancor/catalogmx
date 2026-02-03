/// SAT Anexo 24 - Código agrupador de cuentas
library;

import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/src/catalogs/base_catalog.dart';

class CodigoAgrupadorSATCatalog {
  static const String _defaultVersion = '2026-01-13';

  static const Map<String, String> _versionFiles = {
    '2024-01-22': 'sat/contabilidad_electronica/codigo_agrupador_2024.json',
    '2026-01-13': 'sat/contabilidad_electronica/codigo_agrupador_2026.json',
  };

  static const Map<String, String> _versionAliases = {
    '2024': '2024-01-22',
    '2026': '2026-01-13',
    'latest': _defaultVersion,
  };

  static final Map<String, List<Map<String, dynamic>>> _dataByVersion = {};
  static final Map<String, Map<String, Map<String, dynamic>>> _byCodigo = {};

  static String _resolveVersion(String? version) {
    if (version == null || version.trim().isEmpty) {
      return _defaultVersion;
    }
    final normalized = version.trim().toLowerCase();
    if (_versionAliases.containsKey(normalized)) {
      return _versionAliases[normalized]!;
    }
    if (_versionFiles.containsKey(version)) {
      return version;
    }
    throw ArgumentError('Versión no soportada: $version');
  }

  static List<Map<String, dynamic>> _load(String version) {
    if (_dataByVersion.containsKey(version)) {
      return _dataByVersion[version]!;
    }
    final items = BaseCatalog.loadJsonDataSync(_versionFiles[version]!);
    _dataByVersion[version] = items;
    _byCodigo[version] = {
      for (final item in items) item['codigo'] as String: item,
    };
    return items;
  }

  static List<String> getVersions() => _versionFiles.keys.toList();

  static String getDefaultVersion() => _defaultVersion;

  static List<Map<String, dynamic>> getAll({String? version}) {
    final resolved = _resolveVersion(version);
    return List<Map<String, dynamic>>.from(_load(resolved));
  }

  static Map<String, dynamic>? getByCodigo(
    String codigo, {
    String? version,
  }) {
    final resolved = _resolveVersion(version);
    _load(resolved);
    return _byCodigo[resolved]?[codigo];
  }

  static bool isValid(String codigo, {String? version}) {
    return getByCodigo(codigo, version: version) != null;
  }

  static List<Map<String, dynamic>> search(String query, {String? version}) {
    if (query.trim().isEmpty) return [];
    final resolved = _resolveVersion(version);
    final data = _load(resolved);
    final normalized = query.toLowerCase();
    return data.where((item) {
      final nombre = (item['nombre'] as String? ?? '').toLowerCase();
      return nombre.contains(normalized);
    }).toList();
  }

  static int count({String? version}) => getAll(version: version).length;

  static Map<String, dynamic> getDiff2024_2026() {
    final path =
        '${BaseCatalog.sharedDataPath}/sat/contabilidad_electronica/codigo_agrupador_diff_2024_2026.json';
    try {
      final file = File(path);
      final payload = json.decode(file.readAsStringSync());
      return payload as Map<String, dynamic>;
    } catch (_) {
      return <String, dynamic>{};
    }
  }
}
