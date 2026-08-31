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

ClaseRiesgo _riesgoFromInt(int value) {
  switch (value) {
    case 1:
      return ClaseRiesgo.clase1;
    case 2:
      return ClaseRiesgo.clase2;
    case 3:
      return ClaseRiesgo.clase3;
    case 4:
      return ClaseRiesgo.clase4;
    case 5:
      return ClaseRiesgo.clase5;
    default:
      throw ArgumentError('Unsupported clase riesgo: $value');
  }
}

void main() {
  test('IMSS shared vectors', () {
    final file = File('../shared-data/tests/imss_vectors.json');
    final data = jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;

    for (final raw in data['cuotas_obrero_patronales'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = IMSSCalculator.calcularCuotasObreroPatronales(
        (vector['salario_diario'] as num).toDouble(),
        dias: vector['dias'] as int,
        year: _yearFromInt(vector['year'] as int),
        claseRiesgo: _riesgoFromInt(vector['clase_riesgo'] as int),
        fecha: vector['fecha'] == null
            ? null
            : DateTime.parse(vector['fecha'] as String),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.totalIMSS), expected['total_imss']);
      expect(_round(result.totalPatron), expected['total_patron']);
      expect(_round(result.totalTrabajador), expected['total_trabajador']);
    }

    for (final raw in data['modalidad_40'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = IMSSCalculator.calcularModalidad40(
        (vector['salario_base_cotizacion'] as num).toDouble(),
        ultimoSbcMensual: (vector['ultimo_sbc_mensual'] as num).toDouble(),
        year: _yearFromInt(vector['year'] as int),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.cuotaMensual), expected['cuota_mensual']);
      expect(_round(result.porcentajeTotal), expected['porcentaje_total']);
    }

    for (final raw in data['modalidad_10'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = IMSSCalculator.calcularModalidad10(
        (vector['salario_base_cotizacion'] as num).toDouble(),
        year: _yearFromInt(vector['year'] as int),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.cuotaMensual), expected['cuota_mensual']);
      expect(_round(result.cuotaFijaUma), expected['cuota_fija_uma']);
    }
  });

  test('Modalidad 40 rejects a salary below the last registered SBC', () {
    expect(
      () => IMSSCalculator.calcularModalidad40(10000, ultimoSbcMensual: 12000),
      throwsArgumentError,
    );
  });

  test('Public CEAV selector uses only the applicable wage zone', () {
    expect(
        IMSSCalculator.getCEAVPatronRate(315.04, IMSSYear.year2026,
            zona: ZonaSalario.general),
        closeTo(0.0315, 0.00000001));
    expect(
        IMSSCalculator.getCEAVPatronRate(440.87, IMSSYear.year2026,
            zona: ZonaSalario.general),
        closeTo(0.06613, 0.00000001));
    expect(
        IMSSCalculator.getCEAVPatronRate(440.87, IMSSYear.year2026,
            zona: ZonaSalario.frontera),
        closeTo(0.0315, 0.00000001));
    expect(
        IMSSCalculator.getCEAVPatronRate(315.041, IMSSYear.year2026,
            zona: ZonaSalario.general),
        closeTo(0.06026, 0.00000001));
  });

  test('CEAV and ordinary contributions reject invalid daily SBC', () {
    for (final salary in <double>[
      double.nan,
      double.infinity,
      double.negativeInfinity,
      0,
      -1,
      315.03,
    ]) {
      expect(
        () => IMSSCalculator.getCEAVPatronRate(
          salary,
          IMSSYear.year2026,
          zona: ZonaSalario.general,
        ),
        throwsArgumentError,
      );
      expect(
        () => IMSSCalculator.calcularCuotasObreroPatronales(salary),
        throwsArgumentError,
      );
    }
  });

  test('Ordinary contributions cap daily SBC at 25 UMA', () {
    final cap = IMSSCalculator.getUMA(IMSSYear.year2026).diaria * 25;
    final expected = IMSSCalculator.calcularCuotasObreroPatronales(cap);

    for (final salary in <double>[117.31 * 26, 1e307, 1e308]) {
      final result = IMSSCalculator.calcularCuotasObreroPatronales(salary);
      expect(result.toJson(), expected.toJson());
    }
  });

  test('Modalidad 40 preserves the special one-minimum-wage CEAV row', () {
    final uma = IMSSCalculator.getUMA(IMSSYear.year2026);
    final monthlyMinimum = 315.04 * (uma.mensual / uma.diaria);
    final result = IMSSCalculator.calcularModalidad40(
      monthlyMinimum,
      ultimoSbcMensual: monthlyMinimum,
    );
    expect(result.porcentajeTotal, closeTo(0.10075, 0.00000001));
  });

  test('IMSS calculations reject dates from another exercise', () {
    final wrongDate = DateTime(2025, 12, 31);
    expect(
      () => IMSSCalculator.calcularCuotasObreroPatronales(
        500,
        year: IMSSYear.year2026,
        fecha: wrongDate,
      ),
      throwsArgumentError,
    );
    expect(
      () => IMSSCalculator.calcularModalidad40(
        15000,
        ultimoSbcMensual: 12000,
        year: IMSSYear.year2026,
        fecha: wrongDate,
      ),
      throwsArgumentError,
    );
    expect(
      () => IMSSCalculator.calcularModalidad10(
        10000,
        year: IMSSYear.year2026,
        fecha: wrongDate,
      ),
      throwsArgumentError,
    );
  });

  test('Modalidad 40 rejects non-finite requested salary', () {
    expect(
      () => IMSSCalculator.calcularModalidad40(
        double.nan,
        ultimoSbcMensual: 10000,
      ),
      throwsArgumentError,
    );
    expect(
      () => IMSSCalculator.calcularModalidad40(
        double.infinity,
        ultimoSbcMensual: 10000,
      ),
      throwsArgumentError,
    );
    expect(
      () => IMSSCalculator.calcularModalidad40(
        15000,
        ultimoSbcMensual: double.nan,
      ),
      throwsArgumentError,
    );
    expect(
      () => IMSSCalculator.calcularModalidad40(
        15000,
        ultimoSbcMensual: double.infinity,
      ),
      throwsArgumentError,
    );
  });

  test('Modalidad 10 rejects non-finite or non-positive salary', () {
    for (final salary in <double>[
      double.nan,
      double.infinity,
      double.negativeInfinity,
      0,
      -1,
    ]) {
      expect(
        () => IMSSCalculator.calcularModalidad10(salary),
        throwsArgumentError,
      );
    }
  });
}
