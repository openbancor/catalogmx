/// Tests for the 5-digit SPEI participant code model of BanxicoBanks
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';
import 'package:catalogmx/src/catalogs/banxico/banks.dart';
import 'package:test/test.dart';

void main() {
  const historical = ['143', '608', '630'];

  test('lookup by 5-digit SPEI code', () {
    final bank = BanxicoBanks.getBySpeiCode('40012');
    expect(bank, isNotNull);
    expect(bank!['code'], '012');
    expect(bank['spei_code'], '40012');
    expect(BanxicoBanks.getBankBySpeiCode('40012')!.speiCode, '40012');
    expect(BanxicoBanks.getBankBySpeiCode('40012')!.status, 'active');
  });

  test('lookup by 3-digit CLABE code keeps compatibility', () {
    expect(BanxicoBanks.getByClabeCode('012'), BanxicoBanks.getByCode('012'));
    expect(BanxicoBanks.getByCode('12')!['spei_code'], '40012');
  });

  test('rejects unknown and malformed SPEI codes', () {
    expect(BanxicoBanks.getBySpeiCode('99999'), isNull);
    expect(BanxicoBanks.getBySpeiCode('012'), isNull);
    expect(BanxicoBanks.getBankBySpeiCode('abcde'), isNull);
  });

  test('BANXICO uses its official 4-digit key', () {
    expect(BanxicoBanks.getBySpeiCode('2001')!['code'], '001');
  });

  test('validateSpeiCode checks the 3-digit suffix', () {
    expect(BanxicoBanks.validateSpeiCode('40012', '012'), isTrue);
    expect(BanxicoBanks.validateSpeiCode('40012', '014'), isFalse);
    expect(BanxicoBanks.validateSpeiCode('40012'), isTrue);
    expect(BanxicoBanks.validateSpeiCode('90000'), isFalse);
    expect(BanxicoBanks.validateSpeiCode('2001', '1'), isTrue);
  });

  test('new participants carry no invented data', () {
    const expected = {
      '40170': 'REVOLUT BANK',
      '90660': 'Altor',
      '90714': 'PPBALANCEMX',
    };
    expected.forEach((speiCode, name) {
      final bank = BanxicoBanks.getBankBySpeiCode(speiCode)!;
      expect(bank.name, name);
      expect(bank.code, speiCode.substring(speiCode.length - 3));
      expect(bank.spei, isTrue);
      expect(bank.fullName, isNull);
      expect(bank.rfc, isNull);
    });
  });

  test('disaffiliated banks resolve by 3 digits with historical mark', () {
    for (final code in historical) {
      final bank = BanxicoBanks.getBankByCode(code)!;
      expect(bank.status, 'historical');
      expect(bank.speiCode, isNull);
      expect(bank.spei, isFalse);
      expect(bank.speiDisaffiliated, isTrue);
      expect(BanxicoBanks.supportsSPEI(code), isFalse);
      expect(bank.toJson()['status'], 'historical');
    }
  });

  test('active listing excludes historical; flag includes them', () {
    final active = BanxicoBanks.getSPEIBanks().map((b) => b['code']).toSet();
    expect(active.intersection(historical.toSet()), isEmpty);
    final withHistorical = BanxicoBanks.getSPEIBanks(includeHistorical: true)
        .map((b) => b['code'])
        .toSet();
    expect(withHistorical.containsAll(historical), isTrue);
    expect(withHistorical.length, active.length + 3);
    expect(BanxicoBanks.getAllSPEIBanks().length, active.length);
    expect(BanxicoBanks.getAllSPEIBanks(includeHistorical: true).length,
        withHistorical.length);
  });

  test('every active record has a spei_code ending in its code', () {
    final banks = BanxicoBanks.getSPEIBanks();
    expect(banks.length, 97);
    for (final bank in banks) {
      final speiCode = bank['spei_code'] as String;
      expect(speiCode.endsWith(bank['code'] as String), isTrue);
    }
    expect(BanxicoBanks.getAll().length, 100);
  });

  test('default listing excludes historical rows even when spei is true', () {
    final data = BanxicoBanks.getAll();
    final raw = BaseCatalog.loadJsonDataSync('banxico/banks.json');
    raw.add({
      'code': '999',
      'name': 'OLD',
      'spei': true,
      'status': 'historical',
      'spei_code': null,
    });
    try {
      expect(data, isNotEmpty);
      final codes = BanxicoBanks.getSPEIBanks().map((b) => b['code']);
      expect(codes, isNot(contains('999')));
      final all = BanxicoBanks.getSPEIBanks(includeHistorical: true)
          .map((b) => b['code']);
      expect(all, contains('999'));
    } finally {
      raw.removeLast();
    }
  });
}
