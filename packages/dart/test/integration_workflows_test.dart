import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

List<Map<String, dynamic>> _loadValidationVectors(String name) {
  final file = File('../shared-data/tests/$name');
  final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;
  return data.cast<Map<String, dynamic>>();
}

String _firstValidValue(String name) {
  final vectors = _loadValidationVectors(name);
  return vectors.firstWhere((vector) => vector['valid'] == true)['value']
      as String;
}

void main() {
  group('integration workflows', () {
    test('validates shared identifiers and calculates ISR', () {
      final validRfc = _firstValidValue('rfc_validation.json');
      final validCurp = _firstValidValue('curp_validation.json');
      final validClabe = _firstValidValue('clabe_validation.json');
      final validNss = _firstValidValue('nss_validation.json');

      expect(validateRFC(validRfc), isTrue);
      expect(validateCURP(validCurp), isTrue);
      expect(validateCLABE(validClabe), isTrue);
      expect(validateNSS(validNss), isTrue);

      final isr = ISRCalculator.calculateISR(
        15000,
        periodo: ISRPeriod.mensual,
        year: ISRYear.year2026,
      );
      expect(isr.isrFinal, greaterThan(0));
      expect(isr.isrFinal, lessThan(isr.ingresoGravable));
    });

    test('reads mexico catalogs in one flow', () {
      final salarios = SalariosMinimosCatalog.getAll();
      final umas = UMACatalog.getAll();

      expect(salarios, isA<List<Map<String, dynamic>>>());
      expect(umas, isA<List<Map<String, dynamic>>>());

      if (salarios.isNotEmpty) {
        final year = (salarios.first['año'] ?? salarios.first['year']) as int;
        final salario = SalariosMinimosCatalog.getByYear(year);
        expect(salario, isNotNull);
        expect(
          (salario?['resto_pais'] ?? salario?['zona_general'] ?? 0) as num,
          greaterThan(0),
        );
      }

      if (umas.isNotEmpty) {
        final year = (umas.first['año'] ?? umas.first['year']) as int;
        final uma = UMACatalog.getByYear(year);
        expect(uma, isNotNull);
        expect((uma?['valor_diario'] ?? uma?['diario'] ?? 0) as num,
            greaterThan(0));
      }
    });
  });
}
