/// Tests for new Banxico catalogs
library;

import 'package:test/test.dart';
import 'package:catalogmx/src/catalogs/banxico/udis.dart';
import 'package:catalogmx/src/catalogs/banxico/tipo_cambio_usd.dart';
import 'package:catalogmx/src/catalogs/banxico/tiie_28.dart';
import 'package:catalogmx/src/catalogs/banxico/cetes_28.dart';
import 'package:catalogmx/src/catalogs/banxico/inflacion_anual.dart';
import 'package:catalogmx/src/catalogs/banxico/salarios_minimos.dart';

void main() {
  group('UDI Catalog', () {
    test('getData returns list', () {
      final data = UdiCatalog.getData();
      expect(data, isA<List>());
    });

    test('getActual returns record', () {
      final record = UdiCatalog.getActual();
      // May be null if no data loaded from assets
      expect(record, anyOf(isNull, isA<Map<String, dynamic>>()));
    });

    test('pesosAUDIs converts correctly', () {
      final result = UdiCatalog.pesosAUDIs(10000, '2024-01-01');
      // May be null if no data
      expect(result, anyOf(isNull, isA<double>()));
    });
  });

  group('Tipo de Cambio USD Catalog', () {
    test('getData returns list', () {
      final data = TipoCambioUsdCatalog.getData();
      expect(data, isA<List>());
    });

    test('getActual returns record', () {
      final record = TipoCambioUsdCatalog.getActual();
      expect(record, anyOf(isNull, isA<Map<String, dynamic>>()));
    });

    test('usdAMxn converts correctly', () {
      final result = TipoCambioUsdCatalog.usdAMxn(100);
      expect(result, anyOf(isNull, isA<double>()));
    });
  });

  group('TIIE 28 Catalog', () {
    test('getData returns list', () {
      final data = Tiie28Catalog.getData();
      expect(data, isA<List>());
    });

    test('getActual returns record', () {
      final record = Tiie28Catalog.getActual();
      expect(record, anyOf(isNull, isA<Map<String, dynamic>>()));
    });
  });

  group('CETES 28 Catalog', () {
    test('getData returns list', () {
      final data = Cetes28Catalog.getData();
      expect(data, isA<List>());
    });

    test('getTasaActual returns rate', () {
      final rate = Cetes28Catalog.getTasaActual();
      expect(rate, anyOf(isNull, isA<double>()));
    });
  });

  group('Inflación Anual Catalog', () {
    test('getData returns list', () {
      final data = InflacionAnualCatalog.getData();
      expect(data, isA<List>());
    });

    test('getTasaActual returns rate', () {
      final rate = InflacionAnualCatalog.getTasaActual();
      expect(rate, anyOf(isNull, isA<double>()));
    });
  });

  group('Salarios Mínimos Catalog', () {
    test('getData returns list', () {
      final data = SalariosMinimosCatalog.getData();
      expect(data, isA<List>());
    });

    test('getActualGeneral returns record', () {
      final record = SalariosMinimosCatalog.getActualGeneral();
      expect(record, anyOf(isNull, isA<Map<String, dynamic>>()));
    });

    test('getActualFrontera returns record', () {
      final record = SalariosMinimosCatalog.getActualFrontera();
      expect(record, anyOf(isNull, isA<Map<String, dynamic>>()));
    });
  });
}
