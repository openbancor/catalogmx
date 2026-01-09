import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

double _round(double value) => (value * 1000000).round() / 1000000;

RESICOYear _yearFromInt(int year) {
  switch (year) {
    case 2024:
      return RESICOYear.year2024;
    case 2025:
      return RESICOYear.year2025;
    case 2026:
      return RESICOYear.year2026;
    default:
      throw ArgumentError('Unsupported year: $year');
  }
}

RESICOPeriod _periodFromString(String period) {
  return period == 'anual' ? RESICOPeriod.anual : RESICOPeriod.mensual;
}

void main() {
  test('RESICO shared vectors', () {
    final file = File('../shared-data/tests/resico_vectors.json');
    final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;

    for (final raw in data) {
      final vector = raw as Map<String, dynamic>;
      final result = RESICOCalculator.calculateRESICO(
        (vector['ingreso'] as num).toDouble(),
        year: _yearFromInt(vector['year'] as int),
        periodo: _periodFromString(vector['periodo'] as String),
      );
      final expected = vector['expected'] as Map<String, dynamic>;

      expect(_round(result.resicoCalculado), expected['resicoCalculado']);
      expect(_round(result.tasaEfectiva), expected['tasaEfectiva']);
    }
  });
}
