import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

void main() {
  group('SAT Nómina 1.2 parity', () {
    test('loads all 13 catalog families', () {
      final samples = <List<dynamic>>[
        [BancoNominaCatalog, BancoNominaCatalog.getByCode('002')],
        [OrigenRecursoCatalog, OrigenRecursoCatalog.getByCode('IP')],
        [PeriodicidadPagoCatalog, PeriodicidadPagoCatalog.getByCode('04')],
        [RiesgoPuestoCatalog, RiesgoPuestoCatalog.getByCode('99')],
        [TipoContratoCatalog, TipoContratoCatalog.getByCode('10')],
        [TipoDeduccionCatalog, TipoDeduccionCatalog.getByCode('115')],
        [TipoHorasCatalog, TipoHorasCatalog.getByCode('01')],
        [TipoIncapacidadCatalog, TipoIncapacidadCatalog.getByCode('04')],
        [TipoJornadaCatalog, TipoJornadaCatalog.getByCode('08')],
        [TipoNominaCatalog, TipoNominaCatalog.getByCode('O')],
        [TipoOtroPagoCatalog, TipoOtroPagoCatalog.getByCode('999')],
        [TipoPercepcionCatalog, TipoPercepcionCatalog.getByCode('057')],
        [TipoRegimenCatalog, TipoRegimenCatalog.getByCode('13')],
      ];
      expect(samples, hasLength(13));
      for (final sample in samples) {
        expect(sample[1], isNotNull);
      }
    });

    test('normalizes compatibility aliases', () {
      final contrato = TipoContratoCatalog.getByCode('10')!;
      expect(contrato['code'], equals('10'));
      expect(contrato['clave'], equals('10'));
      expect(contrato['description'], equals(contrato['descripcion']));

      final bank = BancoNominaCatalog.getByCode('002')!;
      expect(bank['full_name'], equals(bank['razon_social']));
      expect(BancoNominaCatalog.search('Banamex'), isNotEmpty);
    });
  });
}
