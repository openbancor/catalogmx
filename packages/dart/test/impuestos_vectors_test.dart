import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

double _round(double value) => (value * 1000000).round() / 1000000;

DateTime _parseDate(String value) {
  final parts = value.split('-');
  if (parts.length != 3) {
    throw FormatException('Expected YYYY-MM-DD date format.');
  }
  final year = int.parse(parts[0]);
  final month = int.parse(parts[1]);
  final day = int.parse(parts[2]);
  return DateTime(year, month, day);
}

IVATipoTasa _ivaTipoFromString(String value) {
  switch (value) {
    case 'general':
      return IVATipoTasa.general;
    case 'frontera':
      return IVATipoTasa.frontera;
    case 'tasa_cero':
      return IVATipoTasa.tasaCero;
    default:
      throw ArgumentError('Unsupported IVA tipo_tasa: $value');
  }
}

void main() {
  test('Impuestos shared vectors', () {
    final ivaFile = File('../shared-data/tests/iva_vectors.json');
    final iepsFile = File('../shared-data/tests/ieps_vectors.json');
    final retencionesFile = File('../shared-data/tests/retenciones_vectors.json');
    final localesFile = File('../shared-data/tests/impuestos_locales_vectors.json');

    final ivaData = jsonDecode(ivaFile.readAsStringSync()) as Map<String, dynamic>;
    final iepsData = jsonDecode(iepsFile.readAsStringSync()) as Map<String, dynamic>;
    final retData = jsonDecode(retencionesFile.readAsStringSync()) as Map<String, dynamic>;
    final localesData = jsonDecode(localesFile.readAsStringSync()) as Map<String, dynamic>;

    for (final raw in ivaData['calcular'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = IVACalculator.calcular(
        (vector['base'] as num).toDouble(),
        tipoTasa: _ivaTipoFromString(vector['tipo_tasa'] as String),
        fecha: _parseDate(vector['fecha'] as String),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.iva), expected['iva']);
      expect(_round(result.totalConIva), expected['total_con_iva']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in ivaData['calcular_incluido'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = IVACalculator.calcularIncluido(
        (vector['total_con_iva'] as num).toDouble(),
        tipoTasa: _ivaTipoFromString(vector['tipo_tasa'] as String),
        fecha: _parseDate(vector['fecha'] as String),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.iva), expected['iva']);
      expect(_round(result.base), expected['base']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in iepsData['ad_valorem'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = IEPSCalculator.calcularAdValorem(
        (vector['base'] as num).toDouble(),
        (vector['tasa'] as num).toDouble(),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.ieps), expected['ieps']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in iepsData['cuota_fija'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = IEPSCalculator.calcularCuotaFija(
        (vector['base'] as num).toDouble(),
        (vector['cuota'] as num).toDouble(),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.ieps), expected['ieps']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in iepsData['bebidas_alcoholicas'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = IEPSCalculator.calcularBebidasAlcoholicas(
        (vector['valor'] as num).toDouble(),
        (vector['grados_alcohol'] as num).toDouble(),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.ieps), expected['ieps']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in iepsData['cigarros'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = IEPSCalculator.calcularCigarros(
        (vector['valor'] as num).toDouble(),
        vector['numero_cigarros'] as int,
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.ieps), expected['ieps']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in retData['isr'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = RetencionCalculator.calcularRetencionISR(
        (vector['base'] as num).toDouble(),
        vector['concepto'] as String,
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.retencion), expected['retencion']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in retData['iva'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = RetencionCalculator.calcularRetencionIVA(
        (vector['iva_trasladado'] as num).toDouble(),
        vector['concepto'] as String,
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.retencion), expected['retencion']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in retData['honorarios'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = RetencionCalculator.calcularHonorarios(
        (vector['monto_sin_iva'] as num).toDouble(),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.retencion), expected['retencion']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in retData['arrendamiento'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = RetencionCalculator.calcularArrendamiento(
        (vector['monto_sin_iva'] as num).toDouble(),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.retencion), expected['retencion']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in retData['fletes'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = RetencionCalculator.calcularFletes(
        (vector['monto_sin_iva'] as num).toDouble(),
      );
      final expected = vector['expected'] as Map<String, dynamic>;
      expect(_round(result.retencion), expected['retencion']);
      expect(_round(result.tasa), expected['tasa']);
    }

    for (final raw in localesData['impuesto_nomina'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = ImpuestosLocalesCalculator.calcularImpuestoNomina(
        (vector['total_percepciones'] as num).toDouble(),
        vector['cve_estado'] as String,
      );
      expect(_round(result), vector['expected']);
    }

    for (final raw in localesData['impuesto_hospedaje'] as List<dynamic>) {
      final vector = raw as Map<String, dynamic>;
      final result = ImpuestosLocalesCalculator.calcularImpuestoHospedaje(
        (vector['monto_hospedaje'] as num).toDouble(),
        vector['cve_estado'] as String,
      );
      expect(_round(result), vector['expected']);
    }
  });
}
