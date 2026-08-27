/// Formatos de Placas Vehiculares por Estado
///
/// Catálogo de formatos de placas vehiculares utilizadas en cada estado de México
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Placas Formatos Catalog
class PlacasFormatosCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byEstado;
  static Map<String, Map<String, dynamic>>? _byCveEstado;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync(
      'mexico/placas_formatos.json',
    );

    if (jsonData.isNotEmpty && jsonData.first.containsKey('estados')) {
      _data = (jsonData.first['estados'] as List)
          .map((e) => Map<String, dynamic>.from(e as Map))
          .toList();
    } else {
      _data = jsonData;
    }

    // Current shared data is one row per plate format, so multiple rows may
    // belong to the same state. Preserve the historical single-row lookup by
    // returning the first row while validation/search scan all matching rows.
    _byEstado = <String, Map<String, dynamic>>{};
    _byCveEstado = <String, Map<String, dynamic>>{};
    for (final item in _data!) {
      final state = item['estado']?.toString();
      if (state != null) {
        _byEstado!.putIfAbsent(state.toUpperCase(), () => item);
      }
      final rawStateCode = item['cve_estado'] ?? item['codigo_estado'];
      final stateCode = rawStateCode?.toString();
      if (stateCode != null) {
        _byCveEstado!.putIfAbsent(stateCode, () => item);
      }
    }
  }

  /// Obtiene todos los formatos de placas
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Obtiene el primer formato de placas registrado para un estado.
  static Map<String, dynamic>? getByEstado(String estado) {
    _loadData();
    return _byEstado![estado.toUpperCase()];
  }

  /// Obtiene el primer formato por código de estado.
  static Map<String, dynamic>? getByCveEstado(String cveEstado) {
    _loadData();
    return _byCveEstado![cveEstado];
  }

  static Iterable<String> _patterns(Map<String, dynamic> item) sync* {
    final patterns = item['patrones'];
    if (patterns is List) {
      for (final pattern in patterns) {
        if (pattern != null) yield pattern.toString();
      }
    }
    final pattern = item['pattern'];
    if (pattern != null) yield pattern.toString();
  }

  /// Valida si algún formato de placa registrado para el estado coincide.
  static bool validarFormato(String placa, String estado) {
    _loadData();
    final normalizedState = estado.toUpperCase();
    for (final item in _data!) {
      if ((item['estado']?.toString().toUpperCase() ?? '') != normalizedState) {
        continue;
      }
      for (final pattern in _patterns(item)) {
        if (RegExp(pattern, caseSensitive: false).hasMatch(placa)) return true;
      }
    }
    return false;
  }

  /// Busca formatos/estados compatibles con una placa.
  static List<Map<String, dynamic>> buscarPorPlaca(String placa) {
    _loadData();
    final resultados = <Map<String, dynamic>>[];
    for (final item in _data!) {
      for (final pattern in _patterns(item)) {
        if (RegExp(pattern, caseSensitive: false).hasMatch(placa)) {
          resultados.add(item);
          break;
        }
      }
    }
    return resultados;
  }
}
