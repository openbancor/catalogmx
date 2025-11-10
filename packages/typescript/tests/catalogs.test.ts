/**
 * Tests for catalogs
 */

import { describe, expect, test } from '@jest/globals';
import {
  BankCatalog,
  InstitucionesFinancieras,
  MonedasDivisas,
  OperadoresMoviles,
  CodigosLADA,
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
  ClaveUnidadCatalog,
  ClaveProdServCatalog,
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

  test('should get all financial institution types', () => {
    const all = InstitucionesFinancieras.getAll();
    expect(all.length).toBeGreaterThan(30); // ~33 types
  });

  test('should get institution by code', () => {
    const inst = InstitucionesFinancieras.getPorCodigo('01');
    expect(inst).toBeDefined();
    expect(inst?.tipo).toContain('Banco');
  });

  test('should get banks (múltiples y desarrollo)', () => {
    const bancos = InstitucionesFinancieras.getBancos();
    expect(bancos.length).toBeGreaterThan(0);
    bancos.forEach(b => {
      expect(b.tipo.toLowerCase()).toContain('banco');
    });
  });

  test('should get SOFOMes', () => {
    const sofomes = InstitucionesFinancieras.getSOFOMes();
    expect(sofomes.length).toBeGreaterThan(0);
    sofomes.forEach(s => {
      expect(s.tipo).toContain('SOFOM');
    });
  });

  test('should get fintech institutions', () => {
    const fintech = InstitucionesFinancieras.getFintech();
    expect(fintech.length).toBeGreaterThan(0);
  });

  test('should get institutions by regulator', () => {
    const cnbv = InstitucionesFinancieras.getPorRegulador('CNBV');
    expect(cnbv.length).toBeGreaterThan(0);
  });

  test('should validate institution code', () => {
    expect(InstitucionesFinancieras.validarCodigo('01')).toBe(true);
    expect(InstitucionesFinancieras.validarCodigo('INVALID')).toBe(false);
  });

  test('should get regulator description', () => {
    const desc = InstitucionesFinancieras.getDescripcionRegulador('CNBV');
    expect(desc).toContain('Comisión');
  });

  test('should get all currencies', () => {
    const all = MonedasDivisas.getAll();
    expect(all.length).toBeGreaterThan(25); // ~30 currencies
  });

  test('should get currency by ISO code', () => {
    const usd = MonedasDivisas.getPorCodigo('USD');
    expect(usd).toBeDefined();
    expect(usd?.moneda.toLowerCase()).toContain('dólar');
  });

  test('should get MXN, USD, EUR', () => {
    const mxn = MonedasDivisas.getMXN();
    const usd = MonedasDivisas.getUSD();
    const eur = MonedasDivisas.getEUR();
    expect(mxn?.codigo_iso).toBe('MXN');
    expect(usd?.codigo_iso).toBe('USD');
    expect(eur?.codigo_iso).toBe('EUR');
  });

  test('should get currencies with Banxico exchange rate', () => {
    const conTipoCambio = MonedasDivisas.getConTipoCambioBanxico();
    expect(conTipoCambio.length).toBeGreaterThan(10); // ~13 currencies
  });

  test('should get currencies with FIX rate', () => {
    const conFIX = MonedasDivisas.getConTipoCambioFIX();
    expect(conFIX.length).toBeGreaterThan(0);
  });

  test('should get principal currencies', () => {
    const principales = MonedasDivisas.getPrincipales();
    expect(principales.length).toBeGreaterThanOrEqual(7);
    const codigos = principales.map(m => m.codigo_iso);
    expect(codigos).toContain('MXN');
    expect(codigos).toContain('USD');
    expect(codigos).toContain('EUR');
  });

  test('should get Latin American currencies', () => {
    const latam = MonedasDivisas.getLatam();
    expect(latam.length).toBeGreaterThan(5);
    const codigos = latam.map(m => m.codigo_iso);
    expect(codigos).toContain('MXN');
    expect(codigos).toContain('BRL');
    expect(codigos).toContain('ARS');
  });

  test('should validate ISO code', () => {
    expect(MonedasDivisas.validarCodigoISO('USD')).toBe(true);
    expect(MonedasDivisas.validarCodigoISO('INVALID')).toBe(false);
  });

  test('should format currency amount', () => {
    const formatted = MonedasDivisas.formatearMonto(1234.56, 'USD');
    expect(formatted).toContain('$');
    expect(formatted).toContain('1,234.56');
  });

  test('should get currency format info', () => {
    const format = MonedasDivisas.getFormatoMoneda('USD');
    expect(format).toBeDefined();
    expect(format?.decimales).toBe(2);
    expect(format?.simbolo).toContain('$');
  });

  test('should search currencies by name', () => {
    const results = MonedasDivisas.buscarPorNombre('dólar');
    expect(results.length).toBeGreaterThan(0);
  });

  test('should get active currencies', () => {
    const activas = MonedasDivisas.getActivas();
    expect(activas.length).toBeGreaterThan(25);
  });

  test('should get FIX rate info', () => {
    const info = MonedasDivisas.getInfoTipoCambioFIX();
    expect(info.horario).toContain('12:00');
    expect(info.descripcion).toContain('Banco de México');
  });
});

describe('IFT Catalogs', () => {
  test('should get all mobile operators', () => {
    const all = OperadoresMoviles.getAll();
    expect(all.length).toBeGreaterThan(15); // ~17 operators
  });

  test('should get active operators', () => {
    const activos = OperadoresMoviles.getActivos();
    expect(activos.length).toBeGreaterThan(15); // ~16 active
  });

  test('should get OMR (network operators)', () => {
    const omr = OperadoresMoviles.getPorTipo('OMR');
    expect(omr.length).toBeGreaterThanOrEqual(4); // At least Telcel, AT&T, Movistar, Weex
  });

  test('should get OMV (virtual operators)', () => {
    const omv = OperadoresMoviles.getPorTipo('OMV');
    expect(omv.length).toBeGreaterThan(10); // ~12 MVNOs
  });

  test('should get operators with 5G', () => {
    const con5G = OperadoresMoviles.getCon5G();
    expect(con5G.length).toBeGreaterThan(0);
    con5G.forEach(op => {
      expect(op.tecnologias).toContain('5G');
    });
  });

  test('should search operator by name', () => {
    const telcel = OperadoresMoviles.buscarPorNombre('Telcel');
    expect(telcel).toBeDefined();
    expect(telcel?.market_share_aprox).toBeGreaterThan(50);
  });

  test('should get operators by business group', () => {
    const americaMovil = OperadoresMoviles.getPorGrupo('América Móvil');
    expect(americaMovil.length).toBeGreaterThan(0);
  });

  test('should get MVNOs by host network', () => {
    const attMVNO = OperadoresMoviles.getOMVsPorRed('AT&T');
    expect(attMVNO.length).toBeGreaterThan(0);
    attMVNO.forEach(op => {
      expect(op.red_anfitriona).toBe('AT&T');
    });
  });

  test('should validate operator', () => {
    expect(OperadoresMoviles.validar('Telcel')).toBe(true);
    expect(OperadoresMoviles.validar('OperadorInexistente')).toBe(false);
  });

  test('should get market share by type', () => {
    const share = OperadoresMoviles.getMarketSharePorTipo();
    expect(share.OMR).toBeGreaterThan(90); // OMR dominan el mercado
    expect(share.OMV).toBeLessThan(10);
  });

  test('should get all LADA codes', () => {
    const all = CodigosLADA.getAll();
    expect(all.length).toBeGreaterThan(200); // ~231 codes
  });

  test('should find LADA code', () => {
    const cdmx = CodigosLADA.buscarPorLADA('55');
    expect(cdmx).toBeDefined();
    expect(cdmx?.ciudad).toContain('México');
  });

  test('should search by city', () => {
    const guadalajara = CodigosLADA.buscarPorCiudad('Guadalajara');
    expect(guadalajara.length).toBeGreaterThan(0);
  });

  test('should get codes by state', () => {
    const jalisco = CodigosLADA.getPorEstado('Jalisco');
    expect(jalisco.length).toBeGreaterThan(5);
  });

  test('should get metropolitan codes', () => {
    const metro = CodigosLADA.getMetropolitanas();
    expect(metro.length).toBeGreaterThan(10);
    metro.forEach(c => {
      expect(c.tipo).toBe('metropolitana');
    });
  });

  test('should get border codes', () => {
    const fronterizas = CodigosLADA.getFronterizas();
    expect(fronterizas.length).toBeGreaterThan(10);
    fronterizas.forEach(c => {
      expect(c.tipo).toBe('fronteriza');
    });
  });

  test('should get tourist codes', () => {
    const turisticas = CodigosLADA.getTuristicas();
    expect(turisticas.length).toBeGreaterThan(10);
    turisticas.forEach(c => {
      expect(c.tipo).toBe('turistica');
    });
  });

  test('should validate phone number (10 digits)', () => {
    const result = CodigosLADA.validarNumero('5512345678');
    expect(result.valid).toBe(true);
    expect(result.lada).toBe('55');
    expect(result.ciudad).toContain('México');
  });

  test('should reject invalid phone number', () => {
    const result = CodigosLADA.validarNumero('123'); // Too short
    expect(result.valid).toBe(false);
    expect(result.error).toBeDefined();
  });

  test('should format phone number', () => {
    const formatted = CodigosLADA.formatearNumero('5512345678');
    expect(formatted).toContain('55');
    expect(formatted.replace(/\s/g, '')).toBe('5512345678');
  });

  test('should get phone number info', () => {
    const info = CodigosLADA.getInfoNumero('5512345678');
    expect(info).toBeDefined();
    expect(info?.lada).toBe('55');
    expect(info?.tipo).toBe('metropolitana');
  });

  test('should get codes by region', () => {
    const noroeste = CodigosLADA.getPorRegion('Noroeste');
    expect(noroeste.length).toBeGreaterThan(0);
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
    expect(moneda?.decimales || moneda?.decimals).toBe(2);
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

describe('SAT CFDI 4.0 - Large Catalogs', () => {
  test('should get total count of units', () => {
    const count = ClaveUnidadCatalog.getTotalCount();
    expect(count).toBeGreaterThan(2000); // ~2,418 units
  });

  test('should get unit by ID', () => {
    const unidad = ClaveUnidadCatalog.getUnidad('H87'); // Pieza
    expect(unidad).toBeDefined();
    expect(unidad?.nombre).toContain('Pieza');
  });

  test('should validate unit code', () => {
    expect(ClaveUnidadCatalog.isValid('H87')).toBe(true);
    expect(ClaveUnidadCatalog.isValid('INVALID')).toBe(false);
  });

  test('should search units by name', () => {
    const results = ClaveUnidadCatalog.searchByName('kilogramo');
    expect(results.length).toBeGreaterThan(0);
  });

  test('should get vigentes units', () => {
    const vigentes = ClaveUnidadCatalog.getVigentes();
    expect(vigentes.length).toBeGreaterThan(1000);
  });

  test('should search units by category', () => {
    const peso = ClaveUnidadCatalog.searchByCategory('peso');
    expect(peso.length).toBeGreaterThan(0);
  });

  test('should get unit statistics', () => {
    const stats = ClaveUnidadCatalog.getStatistics();
    expect(stats.total).toBeGreaterThan(2000);
    expect(stats.vigentes).toBeGreaterThan(0);
  });

  test('should get total count of products/services', () => {
    const count = ClaveProdServCatalog.getTotalCount();
    expect(count).toBeGreaterThan(50000); // ~52,514 products/services
  });

  test('should get product by ID', () => {
    const prod = ClaveProdServCatalog.getClave('01010101');
    expect(prod).toBeDefined();
  });

  test('should validate product code', () => {
    expect(ClaveProdServCatalog.isValid('01010101')).toBe(true);
    expect(ClaveProdServCatalog.isValid('99999999')).toBe(false);
  });

  test('should search products by keyword', () => {
    const results = ClaveProdServCatalog.search('computadora', 10);
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(10);
  });

  test('should get products by prefix', () => {
    const results = ClaveProdServCatalog.getByPrefix('1010', 50);
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(50);
    // All should start with the prefix
    results.forEach(item => {
      expect(item.id.startsWith('1010')).toBe(true);
    });
  });

  test('should get products with frontera estimulo', () => {
    const results = ClaveProdServCatalog.getConEstimuloFronterizo(100);
    expect(results.length).toBeGreaterThan(0);
    results.forEach(item => {
      expect(item.estimuloFranjaFronteriza).toBe('01');
    });
  });

  test('should get product statistics', () => {
    const stats = ClaveProdServCatalog.getStatistics();
    expect(stats.total).toBeGreaterThan(50000);
    expect(stats.vigentes).toBeGreaterThan(0);
  });

  test('should perform advanced search', () => {
    const results = ClaveProdServCatalog.searchAdvanced({
      keyword: 'software',
      vigente: true,
      limit: 20
    });
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(20);
  });
});
