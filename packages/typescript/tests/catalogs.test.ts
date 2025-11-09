/**
 * Tests for catalogs
 */

import {
  BankCatalog,
  StateCatalog,
  MunicipiosCatalog,
  MunicipiosCompletoCatalog,
  LocalidadesCatalog,
  CodigosPostales,
  CodigosPostalesCompleto,
  RegimenFiscalCatalog,
  UsoCFDICatalog,
  FormaPagoCatalog,
  MetodoPagoCatalog,
  IncotermsValidator,
  ClavePedimentoCatalog,
  MonedaCatalog,
  PaisCatalog,
  MotivoTrasladoCatalog,
  RegistroIdentTribCatalog,
  UnidadAduanaCatalog,
  AeropuertosCatalog,
  CarreterasCatalog,
  MaterialPeligrosoCatalog,
  TipoEmbalajeCatalog,
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

  test('should get localidad by cvegeo', () => {
    const localidad = LocalidadesCatalog.getLocalidad('010010001');
    expect(localidad).toBeDefined();
    expect(localidad?.nom_localidad).toBe('Aguascalientes');
  });

  test('should validate localidad cvegeo', () => {
    expect(LocalidadesCatalog.isValid('010010001')).toBe(true);
    expect(LocalidadesCatalog.isValid('999999999')).toBe(false);
  });

  test('should get localidades by municipio', () => {
    const localidades = LocalidadesCatalog.getByMunicipio('001');
    expect(localidades.length).toBeGreaterThan(0);
  });

  test('should get localidades by entidad', () => {
    const localidades = LocalidadesCatalog.getByEntidad('01');
    expect(localidades.length).toBeGreaterThan(0);
  });

  test('should filter urbanas and rurales', () => {
    const urbanas = LocalidadesCatalog.getUrbanas();
    const rurales = LocalidadesCatalog.getRurales();
    expect(urbanas.length).toBeGreaterThan(0);
    expect(rurales.length).toBeGreaterThan(0);
  });

  test('should search localidades by name', () => {
    const results = LocalidadesCatalog.searchByName('Aguascalientes');
    expect(results.length).toBeGreaterThan(0);
  });

  test('should get localidades by coordinates', () => {
    // Coordenadas cerca de CDMX
    const results = LocalidadesCatalog.getByCoordinates(19.4326, -99.1332, 50);
    expect(results.length).toBeGreaterThan(0);
    // Debe estar ordenado por distancia
    if (results.length > 1) {
      expect(results[0].distancia_km).toBeLessThanOrEqual(results[1].distancia_km!);
    }
  });

  test('should get localidades by population range', () => {
    const results = LocalidadesCatalog.getByPopulationRange(100000, 200000);
    expect(results.length).toBeGreaterThan(0);
    results.forEach(loc => {
      expect(loc.poblacion_total).toBeGreaterThanOrEqual(100000);
      expect(loc.poblacion_total).toBeLessThanOrEqual(200000);
    });
  });

  test('should get top localidades by population', () => {
    const top10 = LocalidadesCatalog.getTopByPopulation(10);
    expect(top10.length).toBe(10);
    // Debe estar ordenado de mayor a menor
    for (let i = 0; i < top10.length - 1; i++) {
      expect(top10[i].poblacion_total).toBeGreaterThanOrEqual(top10[i + 1].poblacion_total);
    }
  });

  test('should get localidades statistics', () => {
    const stats = LocalidadesCatalog.getStatistics();
    expect(stats.totalLocalidades).toBeGreaterThan(10000);
    expect(stats.urbanas).toBeGreaterThan(0);
    expect(stats.rurales).toBeGreaterThan(0);
    expect(stats.estados).toBe(32);
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

describe('Complete Catalogs', () => {
  test('should get total count of municipalities', () => {
    const count = MunicipiosCompletoCatalog.getTotalCount();
    expect(count).toBeGreaterThan(2400); // Should have ~2,469 municipalities
  });

  test('should get municipality by code', () => {
    const mun = MunicipiosCompletoCatalog.getMunicipio('14039');
    expect(mun).toBeDefined();
  });

  test('should get unique states from municipalities', () => {
    const states = MunicipiosCompletoCatalog.getUniqueStates();
    expect(states.length).toBeGreaterThan(30); // 32 states
  });

  test('should get total count of postal codes', () => {
    const count = CodigosPostalesCompleto.getTotalCount();
    expect(count).toBeGreaterThan(100000); // Should have ~150,000 postal codes
  });

  test('should get statistics from complete postal codes', () => {
    const stats = CodigosPostalesCompleto.getStatistics();
    expect(stats.totalPostalCodes).toBeGreaterThan(100000);
    expect(stats.states).toBeGreaterThan(30);
  });

  test('should validate postal code in complete catalog', () => {
    expect(CodigosPostalesCompleto.isValid('06700')).toBe(true);
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

  test('should validate motivo traslado', () => {
    const allMotivos = MotivoTrasladoCatalog.getAll();
    expect(allMotivos.length).toBeGreaterThan(0);
  });

  test('should validate registro ident trib', () => {
    const allRegistros = RegistroIdentTribCatalog.getAll();
    expect(allRegistros.length).toBeGreaterThan(0);
  });

  test('should validate unidad aduana', () => {
    const allUnidades = UnidadAduanaCatalog.getAll();
    expect(allUnidades.length).toBeGreaterThan(0);
  });
});

describe('SAT Carta Porte Catalogs', () => {
  test('should get airport by IATA code', () => {
    const airport = AeropuertosCatalog.getByIATA('MEX');
    if (airport) {
      expect(airport.iata).toBe('MEX');
    }
  });

  test('should validate carreteras', () => {
    const allCarreteras = CarreterasCatalog.getAll();
    expect(allCarreteras.length).toBeGreaterThan(0);
  });

  test('should validate material peligroso', () => {
    const allMateriales = MaterialPeligrosoCatalog.getAll();
    expect(allMateriales.length).toBeGreaterThan(0);
  });

  test('should validate tipo embalaje', () => {
    const allTipos = TipoEmbalajeCatalog.getAll();
    expect(allTipos.length).toBeGreaterThan(0);
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
