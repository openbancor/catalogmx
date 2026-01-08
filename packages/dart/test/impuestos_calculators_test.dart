/// Tests for Tax Calculators: IVA, IEPS, Retenciones, and Impuestos Locales
library;

import 'package:test/test.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  group('IVACalculator', () {
    test('calculates IVA with general rate (16%)', () {
      final result = IVACalculator.calcular(1000.0);

      expect(result.base, equals(1000.0));
      expect(result.tasa, equals(16.0));
      expect(result.iva, equals(160.0));
      expect(result.totalConIva, equals(1160.0));
      expect(result.tipoTasa, equals('general'));
    });

    test('calculates IVA with zero rate', () {
      final result =
          IVACalculator.calcular(1000.0, tipoTasa: IVATipoTasa.tasaCero);

      expect(result.base, equals(1000.0));
      expect(result.tasa, equals(0.0));
      expect(result.iva, equals(0.0));
      expect(result.totalConIva, equals(1000.0));
      expect(result.tipoTasa, equals('tasa_cero'));
    });

    test('calculates included IVA (desglose)', () {
      final result = IVACalculator.calcularIncluido(1160.0);

      expect(result.totalConIva, equals(1160.0));
      expect(result.tasa, equals(16.0));
      expect(result.base, closeTo(1000.0, 0.01));
      expect(result.iva, closeTo(160.0, 0.01));
    });

    test('gets current IVA rate for general type', () {
      final tasa = IVACalculator.getTasaVigente();

      expect(tasa, isNotNull);
      expect(tasa!.tipo, equals('general'));
      expect(tasa.tasa, equals(16.0));
    });

    test('gets all historical IVA rates', () {
      final tasas = IVACalculator.getAllTasas();

      expect(tasas, isNotEmpty);
      expect(tasas.length, greaterThan(3));
      expect(tasas.any((t) => t.tasa == 16.0), isTrue);
      expect(tasas.any((t) => t.tasa == 15.0), isTrue);
      expect(tasas.any((t) => t.tasa == 0.0), isTrue);
    });

    test('result toJson works correctly', () {
      final result = IVACalculator.calcular(1000.0);
      final json = result.toJson();

      expect(json['base'], equals(1000.0));
      expect(json['tasa'], equals(16.0));
      expect(json['iva'], equals(160.0));
      expect(json['total_con_iva'], equals(1160.0));
      expect(json['tipo_tasa'], equals('general'));
    });
  });

  group('IEPSCalculator', () {
    test('calculates ad-valorem IEPS', () {
      final result = IEPSCalculator.calcularAdValorem(1000.0, 53.0);

      expect(result.base, equals(1000.0));
      expect(result.tasa, equals(53.0));
      expect(result.ieps, equals(530.0));
      expect(result.tipoCalculo, equals('ad_valorem'));
    });

    test('calculates fixed-fee IEPS (cuota fija)', () {
      final result = IEPSCalculator.calcularCuotaFija(100.0, 5.117);

      expect(result.base, equals(100.0));
      expect(result.tasa, equals(5.117));
      expect(result.ieps, closeTo(511.7, 0.1));
      expect(result.tipoCalculo, equals('cuota_fija'));
      expect(result.unidad, equals('litro'));
      expect(result.cantidad, equals(100.0));
    });

    test('calculates IEPS for beer (≤14°)', () {
      final result = IEPSCalculator.calcularBebidasAlcoholicas(1000.0, 4.5);

      expect(result.tasa, equals(26.5));
      expect(result.ieps, equals(265.0));
    });

    test('calculates IEPS for wine (14-20°)', () {
      final result = IEPSCalculator.calcularBebidasAlcoholicas(1000.0, 18.0);

      expect(result.tasa, equals(30.0));
      expect(result.ieps, equals(300.0));
    });

    test('calculates IEPS for spirits (>20°)', () {
      final result = IEPSCalculator.calcularBebidasAlcoholicas(1000.0, 40.0);

      expect(result.tasa, equals(53.0));
      expect(result.ieps, equals(530.0));
    });

    test('calculates IEPS for cigarettes', () {
      final result = IEPSCalculator.calcularCigarros(50.0, 20);

      expect(result.base, equals(50.0));
      expect(result.tasa, equals(160.0));
      // 160% of 50 = 80.0 + 20 * 0.508 = 80.0 + 10.16 = 90.16
      expect(result.ieps, closeTo(90.16, 0.01));
      expect(result.cantidad, equals(20.0));
    });

    test('gets IEPS category by name', () {
      final categoria = IEPSCalculator.getCategoria('bebidas_alcoholicas');

      expect(categoria, isNotNull);
      expect(categoria!.categoria, equals('bebidas_alcoholicas'));
      expect(categoria.tasas, isNotEmpty);
    });

    test('gets all IEPS categories', () {
      final categorias = IEPSCalculator.getAllCategorias();

      expect(categorias, isNotEmpty);
      expect(categorias.length, greaterThan(5));
      expect(
          categorias.any((c) => c.categoria == 'bebidas_alcoholicas'), isTrue);
      expect(categorias.any((c) => c.categoria == 'tabacos'), isTrue);
      expect(categorias.any((c) => c.categoria == 'combustibles'), isTrue);
    });
  });

  group('RetencionCalculator', () {
    test('calculates ISR withholding for honorarios (10%)', () {
      final result =
          RetencionCalculator.calcularRetencionISR(10000.0, 'honorarios');

      expect(result.concepto, equals('honorarios'));
      expect(result.base, equals(10000.0));
      expect(result.tasa, equals(10.0));
      expect(result.retencion, equals(1000.0));
    });

    test('calculates ISR withholding for arrendamiento (10%)', () {
      final result =
          RetencionCalculator.calcularRetencionISR(5000.0, 'arrendamiento');

      expect(result.concepto, equals('arrendamiento'));
      expect(result.base, equals(5000.0));
      expect(result.tasa, equals(10.0));
      expect(result.retencion, equals(500.0));
    });

    test('calculates ISR withholding for fletes (4%)', () {
      final result =
          RetencionCalculator.calcularRetencionISR(10000.0, 'fletes');

      expect(result.concepto, equals('fletes'));
      expect(result.base, equals(10000.0));
      expect(result.tasa, equals(4.0));
      expect(result.retencion, equals(400.0));
    });

    test('calculates IVA withholding (2/3 parts)', () {
      final result = RetencionCalculator.calcularRetencionIVA(
          160.0, 'servicios_profesionales');

      expect(result.concepto, equals('servicios_profesionales'));
      expect(result.base, equals(160.0));
      expect(result.tasa, equals(66.67));
      expect(result.retencion, closeTo(106.67, 0.1));
      expect(result.impuestoBase, equals(160.0));
    });

    test('calcularHonorarios convenience method', () {
      final result = RetencionCalculator.calcularHonorarios(10000.0);

      expect(result.concepto, equals('honorarios'));
      expect(result.retencion, equals(1000.0));
    });

    test('calcularArrendamiento convenience method', () {
      final result = RetencionCalculator.calcularArrendamiento(5000.0);

      expect(result.concepto, equals('arrendamiento'));
      expect(result.retencion, equals(500.0));
    });

    test('calcularFletes convenience method', () {
      final result = RetencionCalculator.calcularFletes(10000.0);

      expect(result.concepto, equals('fletes'));
      expect(result.retencion, equals(400.0));
    });

    test('throws error for non-existent ISR concept', () {
      expect(
        () => RetencionCalculator.calcularRetencionISR(1000.0, 'invalid'),
        throwsException,
      );
    });

    test('throws error for variable rate concept', () {
      expect(
        () => RetencionCalculator.calcularRetencionISR(1000.0, 'intereses'),
        throwsException,
      );
    });

    test('gets all ISR withholdings', () {
      final retenciones = RetencionCalculator.getAllRetencionesISR();

      expect(retenciones, isNotEmpty);
      expect(retenciones.length, greaterThan(5));
      expect(retenciones.any((r) => r.concepto == 'honorarios'), isTrue);
      expect(retenciones.any((r) => r.concepto == 'arrendamiento'), isTrue);
    });

    test('gets all IVA withholdings', () {
      final retenciones = RetencionCalculator.getAllRetencionesIVA();

      expect(retenciones, isNotEmpty);
      expect(retenciones.length, greaterThan(2));
      expect(retenciones.any((r) => r.concepto == 'servicios_profesionales'),
          isTrue);
      expect(retenciones.any((r) => r.concepto == 'arrendamiento'), isTrue);
    });
  });

  group('ImpuestosLocalesCalculator', () {
    test('gets payroll tax for CDMX (3%)', () {
      final impuesto = ImpuestosLocalesCalculator.getImpuestoNomina('09');

      expect(impuesto, isNotNull);
      expect(impuesto!.cveEstado, equals('09'));
      expect(impuesto.estado, equals('Ciudad de México'));
      expect(impuesto.tasa, equals(3.0));
    });

    test('calculates payroll tax for CDMX', () {
      final tax =
          ImpuestosLocalesCalculator.calcularImpuestoNomina(100000.0, '09');

      expect(tax, equals(3000.0)); // 3% of 100,000
    });

    test('gets payroll tax with padded state code', () {
      final impuesto = ImpuestosLocalesCalculator.getImpuestoNomina('9');

      expect(impuesto, isNotNull);
      expect(impuesto!.cveEstado, equals('09'));
    });

    test('calculates payroll tax for different states', () {
      final taxCDMX =
          ImpuestosLocalesCalculator.calcularImpuestoNomina(100000.0, '09');
      final taxNL =
          ImpuestosLocalesCalculator.calcularImpuestoNomina(100000.0, '19');

      expect(taxCDMX, equals(3000.0)); // 3%
      expect(taxNL, equals(3000.0)); // 3%
    });

    test('gets lodging tax for Quintana Roo (3%)', () {
      final impuesto = ImpuestosLocalesCalculator.getImpuestoHospedaje('23');

      expect(impuesto, isNotNull);
      expect(impuesto!.cveEstado, equals('23'));
      expect(impuesto.estado, equals('Quintana Roo'));
      expect(impuesto.tasa, equals(3.0));
    });

    test('calculates lodging tax for Quintana Roo', () {
      final tax =
          ImpuestosLocalesCalculator.calcularImpuestoHospedaje(1000.0, '23');

      expect(tax, equals(30.0)); // 3% of 1,000
    });

    test('throws error for invalid state code (payroll)', () {
      expect(
        () => ImpuestosLocalesCalculator.calcularImpuestoNomina(1000.0, '99'),
        throwsException,
      );
    });

    test('throws error for invalid state code (lodging)', () {
      expect(
        () =>
            ImpuestosLocalesCalculator.calcularImpuestoHospedaje(1000.0, '99'),
        throwsException,
      );
    });

    test('gets all payroll taxes', () {
      final impuestos = ImpuestosLocalesCalculator.getAllImpuestosNomina();

      expect(impuestos, isNotEmpty);
      expect(impuestos.length, equals(32)); // All 32 Mexican states
      expect(impuestos.any((i) => i.cveEstado == '09'), isTrue);
      expect(impuestos.any((i) => i.cveEstado == '19'), isTrue);
    });

    test('gets all lodging taxes', () {
      final impuestos = ImpuestosLocalesCalculator.getAllImpuestosHospedaje();

      expect(impuestos, isNotEmpty);
      expect(impuestos.length, equals(32)); // All 32 Mexican states
      expect(impuestos.any((i) => i.cveEstado == '23'), isTrue);
      expect(impuestos.any((i) => i.cveEstado == '03'), isTrue);
    });
  });

  group('Integration Tests', () {
    test('complete invoice calculation with IVA and retenciones', () {
      // Invoice for professional services: $10,000 + IVA
      final subtotal = 10000.0;

      // Calculate IVA
      final ivaResult = IVACalculator.calcular(subtotal);
      expect(ivaResult.iva, equals(1600.0));
      expect(ivaResult.totalConIva, equals(11600.0));

      // Calculate ISR withholding (10%)
      final isrRetencion = RetencionCalculator.calcularHonorarios(subtotal);
      expect(isrRetencion.retencion, equals(1000.0));

      // Calculate IVA withholding (2/3 of IVA)
      final ivaRetencion = RetencionCalculator.calcularRetencionIVA(
          ivaResult.iva, 'servicios_profesionales');
      expect(ivaRetencion.retencion, closeTo(1066.67, 0.1));

      // Net to pay
      final netoPagar = ivaResult.totalConIva -
          isrRetencion.retencion -
          ivaRetencion.retencion;
      expect(netoPagar, closeTo(9533.33, 0.1));
    });

    test('complete payroll calculation with state tax', () {
      // Payroll for CDMX
      final totalPercepciones = 100000.0;
      final payrollTax = ImpuestosLocalesCalculator.calcularImpuestoNomina(
          totalPercepciones, '09');

      expect(payrollTax, equals(3000.0)); // 3% for CDMX

      final netPayroll = totalPercepciones - payrollTax;
      expect(netPayroll, equals(97000.0));
    });
  });
}
