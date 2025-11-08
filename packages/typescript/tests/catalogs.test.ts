/**
 * Tests for catalogs
 */

import {
  BankCatalog,
  StateCatalog,
  MunicipiosCatalog,
  CodigosPostales,
  RegimenFiscalCatalog,
  UsoCFDICatalog,
  FormaPagoCatalog,
  MetodoPagoCatalog,
  IncotermsValidator,
  ClavePedimentoCatalog,
  MonedaCatalog,
  PaisCatalog,
  AeropuertosCatalog,
  TipoNominaCatalog,
  PeriodicidadPagoCatalog,
  RiesgoPuestoCatalog
} from '../src/catalogs';

describe('Banxico Catalogs', () => {
  test('should get bank by code', () => {
    const bank = BankCatalog.getBankByCode('002');
    expect(bank).toBeDefined();
    expect(bank?.name).toBe('BANAMEX');
  });

  test('should validate bank code', () => {
    expect(BankCatalog.isValidCode('002')).toBe(true);
    expect(BankCatalog.isValidCode('999')).toBe(false);
  });

  test('should check SPEI support', () => {
    expect(BankCatalog.supportsSPEI('002')).toBe(true);
  });

  test('should search banks', () => {
    const banks = BankCatalog.searchBanks('BANAMEX');
    expect(banks.length).toBeGreaterThan(0);
  });
});

describe('INEGI Catalogs', () => {
  test('should get state by code', () => {
    const state = StateCatalog.getStateByCode('JC');
    expect(state).toBeDefined();
    expect(state?.name).toBe('JALISCO');
  });

  test('should get state by name', () => {
    const state = StateCatalog.getStateByName('JALISCO');
    expect(state).toBeDefined();
    expect(state?.code).toBe('JC');
  });

  test('should validate state code', () => {
    expect(StateCatalog.isValidCode('JC')).toBe(true);
    expect(StateCatalog.isValidCode('XX')).toBe(false);
  });

  test('should get municipalities by state', () => {
    const municipios = MunicipiosCatalog.getByEntidad('14');
    expect(municipios.length).toBeGreaterThan(0);
  });
});

describe('SEPOMEX Catalogs', () => {
  test('should get postal code info', () => {
    const cps = CodigosPostales.getByCp('06700');
    expect(cps.length).toBeGreaterThan(0);
  });

  test('should validate postal code', () => {
    expect(CodigosPostales.isValid('06700')).toBe(true);
  });

  test('should get state from postal code', () => {
    const estado = CodigosPostales.getEstado('06700');
    expect(estado).toBeDefined();
  });
});

describe('SAT CFDI 4.0 Catalogs', () => {
  test('should validate regimen fiscal', () => {
    const regimen = RegimenFiscalCatalog.getRegimen('601');
    expect(regimen).toBeDefined();
    expect(RegimenFiscalCatalog.isValid('601')).toBe(true);
  });

  test('should check persona moral validity', () => {
    expect(RegimenFiscalCatalog.isValidForPersonaMoral('601')).toBe(true);
  });

  test('should validate uso CFDI', () => {
    const uso = UsoCFDICatalog.getUso('G03');
    expect(uso).toBeDefined();
    expect(UsoCFDICatalog.isValid('G03')).toBe(true);
  });

  test('should validate forma de pago', () => {
    const forma = FormaPagoCatalog.getForma('03');
    expect(forma).toBeDefined();
    expect(FormaPagoCatalog.isValid('03')).toBe(true);
  });

  test('should validate metodo de pago', () => {
    expect(MetodoPagoCatalog.isPUE('PUE')).toBe(true);
    expect(MetodoPagoCatalog.isPPD('PPD')).toBe(true);
  });
});

describe('SAT Comercio Exterior Catalogs', () => {
  test('should validate INCOTERM', () => {
    const incoterm = IncotermsValidator.getIncoterm('CIF');
    expect(incoterm).toBeDefined();
    expect(IncotermsValidator.isValid('CIF')).toBe(true);
  });

  test('should check insurance payment responsibility', () => {
    expect(IncotermsValidator.sellerPaysInsurance('CIF')).toBe(true);
  });

  test('should validate clave pedimento', () => {
    const clave = ClavePedimentoCatalog.getClave('A1');
    expect(clave).toBeDefined();
    expect(ClavePedimentoCatalog.isValid('A1')).toBe(true);
  });

  test('should validate currency', () => {
    const moneda = MonedaCatalog.getMoneda('USD');
    expect(moneda).toBeDefined();
    expect(moneda?.decimals).toBe(2);
  });

  test('should validate USD conversion', () => {
    const result = MonedaCatalog.validateConversionUsd({
      moneda: 'USD',
      total: 100.00,
      tipo_cambio_usd: 1.0,
      total_usd: 100.00
    });
    expect(result.valid).toBe(true);
  });

  test('should validate country code', () => {
    expect(PaisCatalog.isValid('MEX')).toBe(true);
    expect(PaisCatalog.isMexico('MEX')).toBe(true);
  });
});

describe('SAT Carta Porte Catalogs', () => {
  test('should get airport by IATA code', () => {
    const airport = AeropuertosCatalog.getByIATA('MEX');
    if (airport) {
      expect(airport.iata).toBe('MEX');
    }
  });
});

describe('SAT Nómina Catalogs', () => {
  test('should validate tipo nomina', () => {
    expect(TipoNominaCatalog.isValid('O')).toBe(true);
  });

  test('should get payment frequency days', () => {
    const days = PeriodicidadPagoCatalog.getDays('04');
    expect(days).toBe(15); // Quincenal
  });

  test('should validate IMSS risk premium', () => {
    const valid = RiesgoPuestoCatalog.validatePrima('3', 2.5);
    expect(valid).toBe(true);
  });

  test('should get prima media', () => {
    const prima = RiesgoPuestoCatalog.getPrimaMedia('3');
    expect(prima).toBeGreaterThan(0);
  });
});
