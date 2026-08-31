import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

double _round(double value) => (value * 1000000).round() / 1000000;

IMSSYear _yearFromInt(int year) {
  switch (year) {
    case 2024:
      return IMSSYear.year2024;
    case 2025:
      return IMSSYear.year2025;
    case 2026:
      return IMSSYear.year2026;
    default:
      throw ArgumentError('Unsupported year: $year');
  }
}

void main() {
  test('Worker cost shared vectors', () {
    final file = File('../shared-data/tests/costo_trabajador_vectors.json');
    final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;

    for (final raw in data) {
      final vector = raw as Map<String, dynamic>;
      final input = vector['input'] as Map<String, dynamic>;
      final result = calcularCostoTotal(
        salarioMensualBruto: (input['salario_mensual_bruto'] as num).toDouble(),
        cveEstado: input['cve_estado'] as String,
        antiguedadAnos: input['antiguedad_anos'] as int,
        diasAguinaldo: input['dias_aguinaldo'] as int,
        incluirPtu: input['incluir_ptu'] as bool,
        porcentajePtu: (input['porcentaje_ptu'] as num).toDouble(),
        year: _yearFromInt(input['year'] as int),
      );
      final expected = vector['expected'] as Map<String, dynamic>;

      expect(_round(result.salarioBrutoMensual),
          expected['salario_bruto_mensual']);
      expect(_round(result.cuotasImssPatronales),
          expected['cuotas_imss_patronales']);
      expect(_round(result.infonavit), expected['infonavit']);
      expect(_round(result.impuestoNomina), expected['impuesto_nomina']);
      expect(_round(result.reservaAguinaldo), expected['reserva_aguinaldo']);
      expect(
        _round(result.reservaPrimaVacacional),
        expected['reserva_prima_vacacional'],
      );
      expect(_round(result.reservaVacaciones), expected['reserva_vacaciones']);
      expect(_round(result.ptuEstimado), expected['ptu_estimado']);
      expect(_round(result.costoTotalMensual), expected['costo_total_mensual']);
      expect(_round(result.costoTotalAnual), expected['costo_total_anual']);
      expect(_round(result.factorCosto), expected['factor_costo']);
    }
  });

  test('Worker cost rejects invalid fiscal options', () {
    expect(
      () => calcularCostoTotal(
        salarioMensualBruto: 15000,
        antiguedadAnos: -1,
      ),
      throwsArgumentError,
    );
    expect(
      () => calcularCostoTotal(
        salarioMensualBruto: 15000,
        diasAguinaldo: 14,
      ),
      throwsArgumentError,
    );
    for (final percentage in <double>[
      double.nan,
      double.infinity,
      double.negativeInfinity,
      -1,
      101,
    ]) {
      expect(
        () => calcularCostoTotal(
          salarioMensualBruto: 15000,
          porcentajePtu: percentage,
        ),
        throwsArgumentError,
      );
    }
  });
}
