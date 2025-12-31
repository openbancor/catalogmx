/// Catálogo de Códigos de Plaza CLABE
///
/// Códigos de plaza para el sistema CLABE (Clave Bancaria Estandarizada).
/// Los códigos de plaza son identificadores de 3 dígitos que indican la ubicación
/// geográfica de las sucursales bancarias en México.
///
/// Fuente: Banco de México (BANXICO) / Sistema de Pagos Electrónicos Interbancarios (SPEI)
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Códigos de Plaza CLABE Catalog
class CodigosPlazaCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, List<Map<String, dynamic>>>? _byCode;
  static Map<String, List<Map<String, dynamic>>>? _byEstado;
  static Map<String, List<Map<String, dynamic>>>? _byPlaza;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync('banxico/codigos_plaza.json');

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('plazas')) {
      _data = (jsonData.first['plazas'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build indices
    _byCode = {};
    _byEstado = {};
    _byPlaza = {};

    for (var plaza in _data!) {
      final codigo = plaza['codigo'] as String;
      final estado = plaza['estado'] as String;
      final plazaName = plaza['plaza'] as String;

      // By codigo (puede haber múltiples plazas con el mismo código)
      _byCode!.putIfAbsent(codigo, () => []).add(plaza);

      // By estado
      _byEstado!.putIfAbsent(estado, () => []).add(plaza);

      // By plaza name (normalized, case-insensitive)
      final plazaNorm = plazaName.toUpperCase();
      _byPlaza!.putIfAbsent(plazaNorm, () => []).add(plaza);
    }
  }

  /// Obtiene todos los códigos de plaza
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Busca plazas por código
  ///
  /// Args:
  ///   codigo: Código de plaza (3 dígitos)
  ///
  /// Returns:
  ///   Lista de plazas con ese código (puede haber múltiples)
  static List<Map<String, dynamic>> buscarPorCodigo(String codigo) {
    _loadData();
    final codigoPadded = codigo.padLeft(3, '0');
    return _byCode![codigoPadded] ?? [];
  }

  /// Busca códigos por nombre de plaza (case-insensitive)
  ///
  /// Args:
  ///   nombrePlaza: Nombre de la plaza/ciudad
  ///
  /// Returns:
  ///   Lista de códigos para esa plaza
  static List<Map<String, dynamic>> buscarPorPlaza(String nombrePlaza) {
    _loadData();
    final plazaNorm = nombrePlaza.toUpperCase();
    return _byPlaza![plazaNorm] ?? [];
  }

  /// Obtiene todas las plazas de un estado
  ///
  /// Args:
  ///   estado: Nombre del estado
  ///
  /// Returns:
  ///   Lista de plazas en ese estado
  static List<Map<String, dynamic>> getPorEstado(String estado) {
    _loadData();
    return _byEstado![estado] ?? [];
  }

  /// Obtiene todas las plazas por código INEGI de entidad
  ///
  /// Args:
  ///   cveEntidad: Código INEGI del estado (2 dígitos)
  ///
  /// Returns:
  ///   Lista de plazas en esa entidad
  static List<Map<String, dynamic>> getPorCveEntidad(String cveEntidad) {
    _loadData();
    return _data!
        .where((p) => p['cve_entidad'] == cveEntidad)
        .toList();
  }

  /// Valida un código de plaza dentro de una CLABE
  ///
  /// Args:
  ///   codigoPlaza: Código de plaza (3 dígitos)
  ///
  /// Returns:
  ///   Mapa con información de validación
  static Map<String, dynamic> validarCodigoCLABE(String codigoPlaza) {
    final codigoPadded = codigoPlaza.padLeft(3, '0');
    final plazas = buscarPorCodigo(codigoPadded);

    return {
      'valido': plazas.isNotEmpty,
      'codigo': codigoPadded,
      'plazas': plazas,
      'num_plazas': plazas.length,
    };
  }

  /// Busca plazas por nombre parcial (case-insensitive)
  ///
  /// Args:
  ///   query: Texto a buscar
  ///
  /// Returns:
  ///   Lista de plazas que coinciden
  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final queryNorm = query.toUpperCase();
    return _data!
        .where((p) => (p['plaza'] as String).toUpperCase().contains(queryNorm))
        .toList();
  }

  /// Obtiene estadísticas del catálogo
  ///
  /// Returns:
  ///   Mapa con estadísticas
  static Map<String, dynamic> getEstadisticas() {
    _loadData();

    final estados = <String>{};
    for (var p in _data!) {
      estados.add(p['estado'] as String);
    }

    final plazasDuplicadas = <String, List<Map<String, dynamic>>>{};
    for (var entry in _byPlaza!.entries) {
      if (entry.value.length > 1) {
        plazasDuplicadas[entry.key] = entry.value;
      }
    }

    return {
      'total_plazas': _data!.length,
      'codigos_unicos': _byCode!.length,
      'estados_cubiertos': estados.length,
      'plazas_duplicadas': plazasDuplicadas.length,
    };
  }
}
