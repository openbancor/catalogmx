import { BankCatalog } from '../src/catalogs/banxico/banks';

const HISTORICAL = ['143', '608', '630'];

describe('BankCatalog SPEI participant codes', () => {
  test('lookup by 5-digit SPEI code', () => {
    const bank = BankCatalog.getBankBySpeiCode('40012');
    expect(bank?.code).toBe('012');
    expect(bank?.spei_code).toBe('40012');
    expect(bank?.status).toBe('active');
  });

  test('lookup by 3-digit CLABE code keeps compatibility', () => {
    expect(BankCatalog.getBankByClabeCode('012')).toBe(BankCatalog.getBankByCode('012'));
  });

  test('rejects unknown and malformed SPEI codes', () => {
    expect(BankCatalog.getBankBySpeiCode('99999')).toBeUndefined();
    expect(BankCatalog.getBankBySpeiCode('012')).toBeUndefined();
  });

  test('BANXICO uses its official 4-digit key', () => {
    expect(BankCatalog.getBankBySpeiCode('2001')?.code).toBe('001');
  });

  test('validateSpeiCode checks the 3-digit suffix', () => {
    expect(BankCatalog.validateSpeiCode('40012', '012')).toBe(true);
    expect(BankCatalog.validateSpeiCode('40012', '014')).toBe(false);
    expect(BankCatalog.validateSpeiCode('40012')).toBe(true);
    expect(BankCatalog.validateSpeiCode('90000')).toBe(false);
  });

  test('new participants carry no invented data', () => {
    const expected: Record<string, string> = {
      '40170': 'REVOLUT BANK',
      '90660': 'Altor',
      '90714': 'PPBALANCEMX',
    };
    for (const [speiCode, name] of Object.entries(expected)) {
      const bank = BankCatalog.getBankBySpeiCode(speiCode);
      expect(bank?.name).toBe(name);
      expect(bank?.code).toBe(speiCode.slice(-3));
      expect(bank?.spei).toBe(true);
      expect(bank?.full_name).toBeNull();
      expect(bank?.rfc).toBeNull();
    }
  });

  test.each(HISTORICAL)('disaffiliated %s resolves by 3 digits with historical mark', (code) => {
    const bank = BankCatalog.getBankByCode(code);
    expect(bank?.status).toBe('historical');
    expect(bank?.spei_code).toBeNull();
    expect(bank?.spei).toBe(false);
    expect(bank?.spei_disaffiliated).toBe(true);
    expect(BankCatalog.supportsSPEI(code)).toBe(false);
  });

  test('active listing excludes historical; flag includes them', () => {
    const active = BankCatalog.getSPEIBanks().map((b) => b.code);
    expect(active.filter((c) => HISTORICAL.includes(c))).toEqual([]);
    expect(active).toHaveLength(97);
    const all = BankCatalog.getSPEIBanks(true).map((b) => b.code);
    expect(HISTORICAL.every((c) => all.includes(c))).toBe(true);
    expect(all).toHaveLength(100);
    for (const bank of BankCatalog.getSPEIBanks()) {
      expect(bank.code).toBe(bank.spei_code?.slice(-3));
    }
  });

  test('default listing excludes historical rows even when spei is true', () => {
    const rows = [
      { code: '999', name: 'OLD', spei: true, status: 'historical', spei_code: null },
      { code: '998', name: 'NEW', spei: true, status: 'active', spei_code: '40998' },
    ];
    const spy = jest
      .spyOn(BankCatalog as unknown as { getData: () => unknown }, 'getData')
      .mockReturnValue(rows);
    try {
      expect(BankCatalog.getSPEIBanks().map((b) => b.code)).toEqual(['998']);
      expect(BankCatalog.getSPEIBanks(true).map((b) => b.code)).toEqual(['999', '998']);
    } finally {
      spy.mockRestore();
    }
  });
});
