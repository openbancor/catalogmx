/// Catálogo de Códigos LADA de México
///
/// Basado en el Plan de Numeración Nacional del IFT (Instituto Federal de Telecomunicaciones).
/// Incluye mapeo geográfico a códigos INEGI y zonas metropolitanas.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Catálogo de códigos LADA con mapeo geográfico
class CodigosLADACatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byLada;
  static Map<String, List<Map<String, dynamic>>>? _byEntidad;

  /// LADAs de 2 dígitos (principales ciudades metropolitanas)
  static const List<String> ladas2Digitos = ['55', '33', '81'];

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync('ift/codigos_lada.json');

    // Handle the wrapped format with "codigos" key
    if (jsonData.isNotEmpty && jsonData.first.containsKey('codigos')) {
      final codigos = jsonData.first['codigos'];
      if (codigos is List) {
        _data = codigos.cast<Map<String, dynamic>>();
      } else {
        _data = jsonData;
      }
    } else {
      _data = jsonData;
    }

    // Build indexes
    _byLada = {for (var item in _data!) item['lada'] as String: item};

    _byEntidad = {};
    for (var item in _data!) {
      final ent = item['cve_entidad'] as String?;
      if (ent != null) {
        _byEntidad![ent] ??= [];
        _byEntidad![ent]!.add(item);
      }
    }
  }

  /// Obtiene todos los códigos LADA
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Busca información por código LADA
  static Map<String, dynamic>? buscarPorLada(String lada) {
    _loadData();
    return _byLada![lada];
  }

  /// Alias para buscarPorLada
  static Map<String, dynamic>? getByLada(String lada) => buscarPorLada(lada);

  /// Busca códigos LADA por nombre de ciudad
  static List<Map<String, dynamic>> buscarPorCiudad(String ciudad) {
    _loadData();
    final ciudadUpper = ciudad.toUpperCase();
    return _data!
        .where(
          (item) => (item['ciudad'] as String? ?? '')
              .toUpperCase()
              .contains(ciudadUpper),
        )
        .toList();
  }

  /// Obtiene códigos LADA por estado
  static List<Map<String, dynamic>> getPorEstado(String estado) {
    _loadData();
    final estadoUpper = estado.toUpperCase();
    return _data!
        .where(
          (item) => (item['estado'] as String? ?? '')
              .toUpperCase()
              .contains(estadoUpper),
        )
        .toList();
  }

  /// Obtiene códigos LADA por clave de entidad INEGI
  static List<Map<String, dynamic>> getPorCveEntidad(String cveEntidad) {
    _loadData();
    return List.from(_byEntidad![cveEntidad] ?? []);
  }

  /// Obtiene códigos LADA por tipo (metropolitana, fronteriza, turistica, normal)
  static List<Map<String, dynamic>> getPorTipo(String tipo) {
    _loadData();
    return _data!.where((item) => item['tipo'] == tipo).toList();
  }

  /// Obtiene códigos LADA por región
  static List<Map<String, dynamic>> getPorRegion(String region) {
    _loadData();
    return _data!.where((item) => item['region'] == region).toList();
  }

  /// Valida si una LADA existe
  static bool isValid(String lada) {
    _loadData();
    return _byLada!.containsKey(lada);
  }

  /// Valida un número de teléfono mexicano
  static Map<String, dynamic> validarNumero(String numero) {
    _loadData();

    // Clean number
    final numeroClean = numero.replaceAll(RegExp(r'[^\d]'), '');

    final result = <String, dynamic>{
      'numero': numeroClean,
      'valido': false,
      'lada': null,
      'ciudad': null,
      'estado': null,
      'tipo': null,
      'error': null,
    };

    if (numeroClean.length != 10) {
      result['error'] = 'Debe tener 10 dígitos';
      return result;
    }

    // Try 2-digit LADA first (55, 33, 81)
    final lada2 = numeroClean.substring(0, 2);
    if (ladas2Digitos.contains(lada2)) {
      final info = _byLada![lada2];
      if (info != null) {
        result['valido'] = true;
        result['lada'] = lada2;
        result['ciudad'] = info['ciudad'];
        result['estado'] = info['estado'];
        result['tipo'] = info['tipo'];
        return result;
      }
    }

    // Try 3-digit LADA
    final lada3 = numeroClean.substring(0, 3);
    final info = _byLada![lada3];
    if (info != null) {
      result['valido'] = true;
      result['lada'] = lada3;
      result['ciudad'] = info['ciudad'];
      result['estado'] = info['estado'];
      result['tipo'] = info['tipo'];
      return result;
    }

    result['error'] = 'LADA no reconocida';
    return result;
  }

  /// Formatea un número de teléfono mexicano
  static String formatearNumero(String numero) {
    final numeroClean = numero.replaceAll(RegExp(r'[^\d]'), '');

    if (numeroClean.length != 10) {
      return numero;
    }

    // Check if 2-digit LADA
    if (ladas2Digitos.contains(numeroClean.substring(0, 2))) {
      return '${numeroClean.substring(0, 2)} ${numeroClean.substring(2, 6)} ${numeroClean.substring(6)}';
    }

    // 3-digit LADA
    return '${numeroClean.substring(0, 3)} ${numeroClean.substring(3, 6)} ${numeroClean.substring(6)}';
  }

  /// Obtiene LADAs metropolitanas (principales ciudades)
  static List<Map<String, dynamic>> getMetropolitanas() {
    return getPorTipo('metropolitana');
  }

  /// Obtiene LADAs fronterizas
  static List<Map<String, dynamic>> getFronterizas() {
    return getPorTipo('fronteriza');
  }

  /// Obtiene LADAs turísticas
  static List<Map<String, dynamic>> getTuristicas() {
    return getPorTipo('turistica');
  }

  /// Obtiene estadísticas del catálogo
  static Map<String, dynamic> getEstadisticas() {
    _loadData();

    final tipos = <String, int>{};
    final regiones = <String, int>{};
    final estados = <String, int>{};

    for (var item in _data!) {
      final tipo = item['tipo'] as String? ?? 'unknown';
      tipos[tipo] = (tipos[tipo] ?? 0) + 1;

      final region = item['region'] as String? ?? 'unknown';
      regiones[region] = (regiones[region] ?? 0) + 1;

      final estado = item['estado'] as String? ?? 'unknown';
      estados[estado] = (estados[estado] ?? 0) + 1;
    }

    return {
      'total_codigos': _data!.length,
      'por_tipo': tipos,
      'por_region': regiones,
      'estados_cubiertos': estados.length,
    };
  }

  /// Limpia el cache
  static void clearCache() {
    _data = null;
    _byLada = null;
    _byEntidad = null;
  }
}
