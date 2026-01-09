import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

double _round(double value) => (value * 1000000).round() / 1000000;

ISRYear _yearFromInt(int year) {
  switch (year) {
    case 2024:
      return ISRYear.year2024;
    case 2025:
      return ISRYear.year2025;
    case 2026:
      return ISRYear.year2026;
    default:
      throw ArgumentError('Unsupported year: $year');
  }
}

void main() {
  test('ISR shared vectors', () {
    final file = File('../shared-data/tests/isr_vectors.json');
    final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;

    for (final raw in data) {
      final vector = raw as Map<String, dynamic>;
      final result = ISRCalculator.calculateISR(
        (vector['ingreso'] as num).toDouble(),
        periodo: ISRPeriod.mensual,
        year: _yearFromInt(vector['year'] as int),
      );
      final expected = vector['expected'] as Map<String, dynamic>;

      expect(_round(result.isrFinal), expected['isrFinal']);
      expect(_round(result.subsidio), expected['subsidio']);
      expect(_round(result.isrAntesSubsidio), expected['isrAntesSubsidio']);
      expect(_round(result.tasaEfectiva), expected['tasaEfectiva']);
    }
  });
}
