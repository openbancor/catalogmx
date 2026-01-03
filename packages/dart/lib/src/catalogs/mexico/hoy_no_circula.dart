/// Hoy No Circula CDMX
///
/// Programa de restricción vehicular "Hoy No Circula" en la Ciudad de México
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Hoy No Circula Catalog
class HoyNoCirculaCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byDigit;
  static Map<String, Map<String, dynamic>>? _byDay;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync(
      'mexico/hoy_no_circula_cdmx.json',
    );

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('reglas')) {
      _data = (jsonData.first['reglas'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build indices
    _byDigit = {};
    _byDay = {};

    for (var regla in _data!) {
      final digitos = regla['digitos'] as List?;
      if (digitos != null) {
        for (var digito in digitos) {
          _byDigit![digito.toString()] = regla;
        }
      }

      final dia = regla['dia'] as String?;
      if (dia != null) {
        _byDay![dia.toUpperCase()] = regla;
      }
    }
  }

  /// Obtiene todas las reglas de Hoy No Circula
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Obtiene regla por último dígito de placa
  ///
  /// Args:
  ///   digit: Último dígito de la placa (0-9)
  ///
  /// Returns:
  ///   Información de la restricción o null si no existe
  static Map<String, dynamic>? getByDigit(String digit) {
    _loadData();
    return _byDigit![digit];
  }

  /// Obtiene regla por día de la semana
  ///
  /// Args:
  ///   day: Día de la semana (ej: "LUNES", "MARTES", etc.)
  ///
  /// Returns:
  ///   Información de la restricción o null si no existe
  static Map<String, dynamic>? getByDay(String day) {
    _loadData();
    return _byDay![day.toUpperCase()];
  }

  /// Verifica si un vehículo no puede circular un día específico
  ///
  /// Args:
  ///   digit: Último dígito de la placa
  ///   day: Día de la semana
  ///
  /// Returns:
  ///   true si el vehículo NO puede circular, false si sí puede
  static bool noCircula(String digit, String day) {
    final regla = getByDigit(digit);
    if (regla == null) return false;

    final dia = regla['dia'] as String?;
    return dia?.toUpperCase() == day.toUpperCase();
  }

  /// Obtiene dígitos que no circulan un día específico
  ///
  /// Args:
  ///   day: Día de la semana
  ///
  /// Returns:
  ///   Lista de dígitos que no circulan ese día
  static List<String> getDigitosPorDia(String day) {
    final regla = getByDay(day);
    if (regla == null) return [];

    final digitos = regla['digitos'] as List?;
    return digitos?.map((d) => d.toString()).toList() ?? [];
  }
}
