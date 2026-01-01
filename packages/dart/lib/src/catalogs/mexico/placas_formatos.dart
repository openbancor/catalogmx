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

    final jsonData =
        BaseCatalog.loadJsonDataSync('mexico/placas_formatos.json');

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('estados')) {
      _data = (jsonData.first['estados'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build indices
    _byEstado = {
      for (var estado in _data!)
        (estado['estado'] as String).toUpperCase(): estado,
    };

    _byCveEstado = {
      for (var estado in _data!) estado['cve_estado'] as String: estado,
    };
  }

  /// Obtiene todos los formatos de placas
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Obtiene formato de placas por nombre de estado
  ///
  /// Args:
  ///   estado: Nombre del estado
  ///
  /// Returns:
  ///   Información de formatos de placas o null si no existe
  static Map<String, dynamic>? getByEstado(String estado) {
    _loadData();
    return _byEstado![estado.toUpperCase()];
  }

  /// Obtiene formato de placas por código de estado
  ///
  /// Args:
  ///   cveEstado: Código INEGI del estado
  ///
  /// Returns:
  ///   Información de formatos de placas o null si no existe
  static Map<String, dynamic>? getByCveEstado(String cveEstado) {
    _loadData();
    return _byCveEstado![cveEstado];
  }

  /// Valida si un formato de placa pertenece a un estado
  ///
  /// Args:
  ///   placa: Placa a validar
  ///   estado: Nombre del estado
  ///
  /// Returns:
  ///   true si el formato coincide, false en caso contrario
  static bool validarFormato(String placa, String estado) {
    final formato = getByEstado(estado);
    if (formato == null) return false;

    final patrones = formato['patrones'] as List?;
    if (patrones == null) return false;

    for (var patron in patrones) {
      final regex = RegExp(patron as String, caseSensitive: false);
      if (regex.hasMatch(placa)) {
        return true;
      }
    }

    return false;
  }

  /// Busca estado por formato de placa
  ///
  /// Args:
  ///   placa: Placa a buscar
  ///
  /// Returns:
  ///   Lista de estados que podrían usar ese formato
  static List<Map<String, dynamic>> buscarPorPlaca(String placa) {
    _loadData();
    final resultados = <Map<String, dynamic>>[];

    for (var estado in _data!) {
      final patrones = estado['patrones'] as List?;
      if (patrones == null) continue;

      for (var patron in patrones) {
        final regex = RegExp(patron as String, caseSensitive: false);
        if (regex.hasMatch(placa)) {
          resultados.add(estado);
          break;
        }
      }
    }

    return resultados;
  }
}
