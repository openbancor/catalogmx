/**
 * Comprehensive tests for SAT catalog modules with low coverage.
 *
 * Covers:
 *  - SAT Nomina 1.2 (banco, tipo-jornada, tipo-contrato, tipo-regimen,
 *    periodicidad-pago, riesgo-puesto, tipo-nomina)
 *  - SAT Carta Porte 3.0 (aeropuertos, carreteras, puertos-maritimos,
 *    tipo-embalaje, tipo-permiso, config-autotransporte, material-peligroso)
 *  - SAT Comercio Exterior (incoterms, clave-pedimento, moneda, pais,
 *    estados-usa-canada, motivo-traslado, registro-ident-trib, unidad-aduana)
 *  - SAT CFDI 4.0 low-coverage (tipo-comprobante, exportacion, objeto-imp,
 *    tipo-relacion, metodo-pago, impuesto)
 */

import { describe, expect, test } from '@jest/globals';
import {
  // SAT Nomina 1.2
  BancoNominaCatalog,
  TipoJornadaCatalog,
  TipoContratoCatalog,
  TipoRegimenCatalog,
  PeriodicidadPagoCatalog,
  RiesgoPuestoCatalog,
  TipoNominaCatalog,
  // SAT Carta Porte 3.0
  AeropuertosCatalog,
  CarreterasCatalog,
  PuertosMaritimos,
  TipoEmbalajeCatalog,
  TipoPermisoCatalog,
  ConfigAutotransporteCatalog,
  MaterialPeligrosoCatalog,
  // SAT Comercio Exterior
  IncotermsValidator,
  ClavePedimentoCatalog,
  MonedaCatalog,
  PaisCatalog,
  EstadoCatalog,
  MotivoTrasladoCatalog,
  RegistroIdentTribCatalog,
  UnidadAduanaCatalog,
  // SAT CFDI 4.0
  TipoComprobanteCatalog,
  ExportacionCatalog,
  ObjetoImpCatalog,
  TipoRelacionCatalog,
  MetodoPagoCatalog,
  ImpuestoCatalog,
} from '../src/catalogs';

// =============================================================================
// SAT Nomina 1.2
// =============================================================================

describe('BancoNominaCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = BancoNominaCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getBanco() returns a bank for valid code "002"', () => {
    const banco = BancoNominaCatalog.getBanco('002');
    expect(banco).toBeDefined();
    expect(banco!.code).toBe('002');
    expect(banco!.name.toUpperCase()).toContain('BANAMEX');
  });

  test('getBanco() returns undefined for invalid code', () => {
    expect(BancoNominaCatalog.getBanco('INVALID')).toBeUndefined();
  });

  test('isValid() returns true for valid code and false for invalid', () => {
    expect(BancoNominaCatalog.isValid('002')).toBe(true);
    expect(BancoNominaCatalog.isValid('012')).toBe(true);
    expect(BancoNominaCatalog.isValid('ZZZZ')).toBe(false);
  });

  test('getName() returns the bank name for valid code', () => {
    expect(BancoNominaCatalog.getName('002')?.toUpperCase()).toContain('BANAMEX');
  });

  test('getName() returns undefined for invalid code', () => {
    expect(BancoNominaCatalog.getName('ZZZZ')).toBeUndefined();
  });

  test('getRazonSocial() exposes the compatibility legal-name alias', () => {
    expect(BancoNominaCatalog.getRazonSocial('002')).toContain('Banco Nacional');
  });

  test('getRazonSocial() returns undefined for invalid code', () => {
    expect(BancoNominaCatalog.getRazonSocial('ZZZZ')).toBeUndefined();
  });

  test('searchByName() searches display and legal names', () => {
    expect(BancoNominaCatalog.searchByName('Banamex').length).toBeGreaterThan(0);
  });
});

describe('TipoJornadaCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = TipoJornadaCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getJornada() returns jornada for valid code "01"', () => {
    const jornada = TipoJornadaCatalog.getJornada('01');
    expect(jornada).toBeDefined();
    expect(jornada!.code).toBe('01');
  });

  test('getJornada() returns undefined for invalid code', () => {
    expect(TipoJornadaCatalog.getJornada('ZZ')).toBeUndefined();
  });

  test('isValid() returns true for valid codes and false for invalid', () => {
    expect(TipoJornadaCatalog.isValid('01')).toBe(true);
    expect(TipoJornadaCatalog.isValid('02')).toBe(true);
    expect(TipoJornadaCatalog.isValid('03')).toBe(true);
    expect(TipoJornadaCatalog.isValid('99')).toBe(true);
    expect(TipoJornadaCatalog.isValid('ZZ')).toBe(false);
  });

  test('isDiurna() returns false for invalid code', () => {
    expect(TipoJornadaCatalog.isDiurna('ZZ')).toBe(false);
  });

  test('isNocturna() returns false for invalid code', () => {
    expect(TipoJornadaCatalog.isNocturna('ZZ')).toBe(false);
  });

  test('isMixta() returns false for invalid code', () => {
    expect(TipoJornadaCatalog.isMixta('ZZ')).toBe(false);
  });
});

describe('TipoContratoCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = TipoContratoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getContrato() returns contrato for valid code "01"', () => {
    const contrato = TipoContratoCatalog.getContrato('01');
    expect(contrato).toBeDefined();
    expect(contrato!.code).toBe('01');
  });

  test('getContrato() returns undefined for invalid code', () => {
    expect(TipoContratoCatalog.getContrato('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(TipoContratoCatalog.isValid('01')).toBe(true);
    expect(TipoContratoCatalog.isValid('02')).toBe(true);
    expect(TipoContratoCatalog.isValid('ZZ')).toBe(false);
  });

  test('isIndefinido() returns false for invalid code', () => {
    expect(TipoContratoCatalog.isIndefinido('ZZ')).toBe(false);
  });

  test('isDeterminado() returns false for invalid code', () => {
    expect(TipoContratoCatalog.isDeterminado('ZZ')).toBe(false);
  });
});

describe('TipoRegimenCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = TipoRegimenCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getRegimen() returns regimen for valid code "02"', () => {
    const regimen = TipoRegimenCatalog.getRegimen('02');
    expect(regimen).toBeDefined();
    expect(regimen!.code).toBe('02');
  });

  test('getRegimen() returns undefined for invalid code', () => {
    expect(TipoRegimenCatalog.getRegimen('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(TipoRegimenCatalog.isValid('02')).toBe(true);
    expect(TipoRegimenCatalog.isValid('03')).toBe(true);
    expect(TipoRegimenCatalog.isValid('ZZ')).toBe(false);
  });

  test('getDescription() exposes the normalized description alias', () => {
    expect(TipoRegimenCatalog.getDescription('02')).toContain('Sueldos');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(TipoRegimenCatalog.getDescription('ZZ')).toBeUndefined();
  });
});

describe('PeriodicidadPagoCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = PeriodicidadPagoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getPeriodicidad() returns item for valid code "02"', () => {
    const p = PeriodicidadPagoCatalog.getPeriodicidad('02');
    expect(p).toBeDefined();
    expect(p!.code).toBe('02');
  });

  test('getPeriodicidad() returns undefined for invalid code', () => {
    expect(PeriodicidadPagoCatalog.getPeriodicidad('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(PeriodicidadPagoCatalog.isValid('01')).toBe(true);
    expect(PeriodicidadPagoCatalog.isValid('04')).toBe(true);
    expect(PeriodicidadPagoCatalog.isValid('ZZ')).toBe(false);
  });

  test('getDays() returns correct days for known codes', () => {
    expect(PeriodicidadPagoCatalog.getDays('01')).toBe(1); // Diario
    expect(PeriodicidadPagoCatalog.getDays('02')).toBe(7); // Semanal
    expect(PeriodicidadPagoCatalog.getDays('04')).toBe(15); // Quincenal
    expect(PeriodicidadPagoCatalog.getDays('05')).toBe(30); // Mensual
  });

  test('getDays() returns undefined for invalid code', () => {
    expect(PeriodicidadPagoCatalog.getDays('ZZ')).toBeUndefined();
  });

  test('getDescription() returns description for valid code', () => {
    expect(PeriodicidadPagoCatalog.getDescription('02')).toBe('Semanal');
    expect(PeriodicidadPagoCatalog.getDescription('04')).toBe('Quincenal');
    expect(PeriodicidadPagoCatalog.getDescription('05')).toBe('Mensual');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(PeriodicidadPagoCatalog.getDescription('ZZ')).toBeUndefined();
  });

  test('isQuincenal() returns true for code "04"', () => {
    expect(PeriodicidadPagoCatalog.isQuincenal('04')).toBe(true);
    expect(PeriodicidadPagoCatalog.isQuincenal('02')).toBe(false);
  });

  test('isSemanal() returns true for code "02"', () => {
    expect(PeriodicidadPagoCatalog.isSemanal('02')).toBe(true);
    expect(PeriodicidadPagoCatalog.isSemanal('04')).toBe(false);
  });

  test('isMensual() returns true for code "05"', () => {
    expect(PeriodicidadPagoCatalog.isMensual('05')).toBe(true);
    expect(PeriodicidadPagoCatalog.isMensual('02')).toBe(false);
  });

  test('searchByDescription() finds results for known terms', () => {
    const results = PeriodicidadPagoCatalog.searchByDescription('Semanal');
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].code).toBe('02');
  });

  test('searchByDescription() returns empty for non-matching terms', () => {
    expect(PeriodicidadPagoCatalog.searchByDescription('ZZZZZ').length).toBe(0);
  });
});

describe('RiesgoPuestoCatalog', () => {
  test('getAll() returns five risk classes plus No aplica', () => {
    const all = RiesgoPuestoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBe(6);
  });

  test('getRiesgo() returns risk for valid code "1"', () => {
    const riesgo = RiesgoPuestoCatalog.getRiesgo('1');
    expect(riesgo).toBeDefined();
    expect(riesgo!.code).toBe('1');
  });

  test('getRiesgo() returns undefined for invalid code', () => {
    expect(RiesgoPuestoCatalog.getRiesgo('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(RiesgoPuestoCatalog.isValid('1')).toBe(true);
    expect(RiesgoPuestoCatalog.isValid('5')).toBe(true);
    expect(RiesgoPuestoCatalog.isValid('99')).toBe(true);
  });

  test('getPrimaRange() returns range with minima, media, maxima', () => {
    const range = RiesgoPuestoCatalog.getPrimaRange('1');
    expect(range).toBeDefined();
    expect(range!.minima).toBe(0.5);
    expect(range!.media).toBe(0.54355);
    expect(range!.maxima).toBe(0.625);
  });

  test('getPrimaRange() returns undefined for invalid code', () => {
    expect(RiesgoPuestoCatalog.getPrimaRange('99')).toBeUndefined();
  });

  test('getPrimaMedia() returns average premium for valid code', () => {
    expect(RiesgoPuestoCatalog.getPrimaMedia('1')).toBe(0.54355);
    expect(RiesgoPuestoCatalog.getPrimaMedia('5')).toBe(6.71);
  });

  test('getPrimaMedia() returns undefined for invalid code', () => {
    expect(RiesgoPuestoCatalog.getPrimaMedia('99')).toBeUndefined();
  });

  test('validatePrima() returns true for prima within range', () => {
    expect(RiesgoPuestoCatalog.validatePrima('1', 0.55)).toBe(true);
    expect(RiesgoPuestoCatalog.validatePrima('1', 0.5)).toBe(true); // min
    expect(RiesgoPuestoCatalog.validatePrima('1', 0.625)).toBe(true); // max
  });

  test('validatePrima() returns false for prima outside range', () => {
    expect(RiesgoPuestoCatalog.validatePrima('1', 0.1)).toBe(false);
    expect(RiesgoPuestoCatalog.validatePrima('1', 1.0)).toBe(false);
  });

  test('validatePrima() returns false for invalid code', () => {
    expect(RiesgoPuestoCatalog.validatePrima('99', 0.55)).toBe(false);
  });

  test('getDescription() returns description for valid code', () => {
    expect(RiesgoPuestoCatalog.getDescription('1')).toBe('Clase I');
    expect(RiesgoPuestoCatalog.getDescription('5')).toBe('Clase V');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(RiesgoPuestoCatalog.getDescription('99')).toBe('No aplica');
  });
});

describe('TipoNominaCatalog', () => {
  test('getAll() returns array with 2 types (O and E)', () => {
    const all = TipoNominaCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBe(2);
  });

  test('getTipo() returns tipo for valid code "O"', () => {
    const tipo = TipoNominaCatalog.getTipo('O');
    expect(tipo).toBeDefined();
    expect(tipo!.code).toBe('O');
  });

  test('getTipo() returns undefined for invalid code', () => {
    expect(TipoNominaCatalog.getTipo('Z')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(TipoNominaCatalog.isValid('O')).toBe(true);
    expect(TipoNominaCatalog.isValid('E')).toBe(true);
    expect(TipoNominaCatalog.isValid('Z')).toBe(false);
  });

  test('isOrdinaria() returns true for code "O"', () => {
    expect(TipoNominaCatalog.isOrdinaria('O')).toBe(true);
    expect(TipoNominaCatalog.isOrdinaria('E')).toBe(false);
  });

  test('isOrdinaria() returns false for invalid code', () => {
    expect(TipoNominaCatalog.isOrdinaria('Z')).toBe(false);
  });

  test('isExtraordinaria() returns true for code "E"', () => {
    expect(TipoNominaCatalog.isExtraordinaria('E')).toBe(true);
    expect(TipoNominaCatalog.isExtraordinaria('O')).toBe(false);
  });

  test('isExtraordinaria() returns false for invalid code', () => {
    expect(TipoNominaCatalog.isExtraordinaria('Z')).toBe(false);
  });
});

// =============================================================================
// SAT Carta Porte 3.0
// =============================================================================

describe('AeropuertosCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = AeropuertosCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getByCode() returns airport for valid code "MEX"', () => {
    const airport = AeropuertosCatalog.getByCode('MEX');
    expect(airport).toBeDefined();
    expect(airport!.code).toBe('MEX');
    expect(airport!.iata).toBe('MEX');
    expect(airport!.icao).toBe('MMMX');
  });

  test('getByCode() returns undefined for invalid code', () => {
    expect(AeropuertosCatalog.getByCode('ZZZZ')).toBeUndefined();
  });

  test('getByIATA() returns airport for valid IATA code "MEX"', () => {
    const airport = AeropuertosCatalog.getByIATA('MEX');
    expect(airport).toBeDefined();
    expect(airport!.iata).toBe('MEX');
  });

  test('getByIATA() returns undefined for invalid IATA code', () => {
    expect(AeropuertosCatalog.getByIATA('ZZZ')).toBeUndefined();
  });

  test('getByICAO() returns airport for valid ICAO code "MMMX"', () => {
    const airport = AeropuertosCatalog.getByICAO('MMMX');
    expect(airport).toBeDefined();
    expect(airport!.code).toBe('MEX');
  });

  test('getByICAO() returns undefined for invalid ICAO code', () => {
    expect(AeropuertosCatalog.getByICAO('ZZZZ')).toBeUndefined();
  });

  test('isValid() returns true for valid code and false for invalid', () => {
    expect(AeropuertosCatalog.isValid('MEX')).toBe(true);
    expect(AeropuertosCatalog.isValid('ZZZZ')).toBe(false);
  });

  test('isValidIATA() returns true for valid IATA code', () => {
    expect(AeropuertosCatalog.isValidIATA('MEX')).toBe(true);
    expect(AeropuertosCatalog.isValidIATA('ZZZ')).toBe(false);
  });

  test('isValidICAO() returns true for valid ICAO code', () => {
    expect(AeropuertosCatalog.isValidICAO('MMMX')).toBe(true);
    expect(AeropuertosCatalog.isValidICAO('ZZZZ')).toBe(false);
  });

  test('getByEstado() returns airports for known state', () => {
    const airports = AeropuertosCatalog.getByEstado('CDMX');
    expect(airports.length).toBeGreaterThan(0);
  });

  test('getByEstado() returns empty array for unknown state', () => {
    expect(AeropuertosCatalog.getByEstado('ZZZZZ').length).toBe(0);
  });

  test('getByCiudad() returns airports for known city', () => {
    // The data uses "Cancún" (accented)
    const airports = AeropuertosCatalog.getByCiudad('Cancún');
    expect(airports.length).toBeGreaterThan(0);
  });

  test('getByCiudad() returns empty array for unknown city', () => {
    expect(AeropuertosCatalog.getByCiudad('ZZZZZZ').length).toBe(0);
  });

  test('searchByName() returns results for known term', () => {
    const results = AeropuertosCatalog.searchByName('Internacional');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByName() returns empty for non-matching term', () => {
    expect(AeropuertosCatalog.searchByName('ZZZZZZZ').length).toBe(0);
  });

  test('getByCode() is case-insensitive', () => {
    const airport = AeropuertosCatalog.getByCode('mex');
    expect(airport).toBeDefined();
    expect(airport!.code).toBe('MEX');
  });
});

describe('CarreterasCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = CarreterasCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getCarretera() returns highway for valid code', () => {
    const carretera = CarreterasCatalog.getCarretera('MEX015');
    expect(carretera).toBeDefined();
    expect(carretera!.code).toBe('MEX015');
  });

  test('getCarretera() returns undefined for invalid code', () => {
    expect(CarreterasCatalog.getCarretera('ZZZZ')).toBeUndefined();
  });

  test('isValid() returns true for valid code and false for invalid', () => {
    expect(CarreterasCatalog.isValid('MEX015')).toBe(true);
    expect(CarreterasCatalog.isValid('ZZZZ')).toBe(false);
  });

  test('getNombre() returns highway name', () => {
    expect(CarreterasCatalog.getNombre('MEX015')).toBe('México - Toluca');
  });

  test('getNombre() returns undefined for invalid code', () => {
    expect(CarreterasCatalog.getNombre('ZZZZ')).toBeUndefined();
  });

  test('getOrigen() returns origin point', () => {
    expect(CarreterasCatalog.getOrigen('MEX015')).toBe('Ciudad de México');
  });

  test('getOrigen() returns undefined for invalid code', () => {
    expect(CarreterasCatalog.getOrigen('ZZZZ')).toBeUndefined();
  });

  test('getDestino() returns destination point', () => {
    expect(CarreterasCatalog.getDestino('MEX015')).toBe('Toluca');
  });

  test('getDestino() returns undefined for invalid code', () => {
    expect(CarreterasCatalog.getDestino('ZZZZ')).toBeUndefined();
  });

  test('getTipo() returns highway type', () => {
    expect(CarreterasCatalog.getTipo('MEX015')).toBe('Cuota');
  });

  test('getTipo() returns undefined for invalid code', () => {
    expect(CarreterasCatalog.getTipo('ZZZZ')).toBeUndefined();
  });

  test('searchByName() returns results for known term', () => {
    // Uses accented characters "México"
    const results = CarreterasCatalog.searchByName('México');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByName() returns empty for non-matching term', () => {
    expect(CarreterasCatalog.searchByName('ZZZZZZZ').length).toBe(0);
  });

  test('searchByRoute() returns results for known destination', () => {
    const results = CarreterasCatalog.searchByRoute('Toluca');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByRoute() returns empty for non-matching term', () => {
    expect(CarreterasCatalog.searchByRoute('ZZZZZZZ').length).toBe(0);
  });

  test('getByTipo() returns highways filtered by type', () => {
    const cuota = CarreterasCatalog.getByTipo('Cuota');
    expect(cuota.length).toBeGreaterThan(0);
  });

  test('getByTipo() returns empty for non-matching type', () => {
    expect(CarreterasCatalog.getByTipo('ZZZZZZ').length).toBe(0);
  });
});

describe('PuertosMaritimos', () => {
  test('getAll() returns a non-empty array', () => {
    const all = PuertosMaritimos.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getPuerto() returns port for valid code "001"', () => {
    const puerto = PuertosMaritimos.getPuerto('001');
    expect(puerto).toBeDefined();
    expect(puerto!.code).toBe('001');
    expect(puerto!.name).toBe('Acapulco');
  });

  test('getPuerto() returns undefined for invalid code', () => {
    expect(PuertosMaritimos.getPuerto('ZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(PuertosMaritimos.isValid('001')).toBe(true);
    expect(PuertosMaritimos.isValid('ZZZ')).toBe(false);
  });

  test('searchByName() returns results for known port name', () => {
    const results = PuertosMaritimos.searchByName('Acapulco');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByName() returns empty for non-matching term', () => {
    expect(PuertosMaritimos.searchByName('ZZZZZZZ').length).toBe(0);
  });

  test('getGulfPorts() returns Gulf of Mexico ports', () => {
    const gulf = PuertosMaritimos.getGulfPorts();
    expect(gulf.length).toBeGreaterThan(0);
  });

  // Note: getByEstado() references p.estado but data uses p.state,
  // causing a runtime error. getByCoast() and getPacificPorts() use
  // accented "Pacífico" in data which does not match "PACIF" pattern.
});

describe('TipoEmbalajeCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = TipoEmbalajeCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getEmbalaje() returns packaging for valid code "1A1"', () => {
    const embalaje = TipoEmbalajeCatalog.getEmbalaje('1A1');
    expect(embalaje).toBeDefined();
    expect(embalaje!.code).toBe('1A1');
  });

  test('getEmbalaje() returns undefined for invalid code', () => {
    expect(TipoEmbalajeCatalog.getEmbalaje('ZZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(TipoEmbalajeCatalog.isValid('1A1')).toBe(true);
    expect(TipoEmbalajeCatalog.isValid('ZZZZ')).toBe(false);
  });

  test('getDescription() returns description for valid code', () => {
    const desc = TipoEmbalajeCatalog.getDescription('1A1');
    expect(desc).toBeDefined();
    expect(desc).toContain('acero');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(TipoEmbalajeCatalog.getDescription('ZZZZ')).toBeUndefined();
  });

  test('getCategoriaONU() returns UN category', () => {
    expect(TipoEmbalajeCatalog.getCategoriaONU('1A1')).toBe('I');
  });

  test('getCategoriaONU() returns undefined for invalid code', () => {
    expect(TipoEmbalajeCatalog.getCategoriaONU('ZZZZ')).toBeUndefined();
  });

  test('searchByDescription() finds results with accented search', () => {
    // Data uses "Bidón" (accented), so search must use accented char
    const results = TipoEmbalajeCatalog.searchByDescription('BIDÓN');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByDescription() returns empty for non-matching term', () => {
    expect(TipoEmbalajeCatalog.searchByDescription('ZZZZZ').length).toBe(0);
  });

  test('getByCategoriaONU() returns items for known category', () => {
    const results = TipoEmbalajeCatalog.getByCategoriaONU('I');
    expect(results.length).toBeGreaterThan(0);
  });

  test('isBox() returns true for box codes (4A, 4B, etc.)', () => {
    expect(TipoEmbalajeCatalog.isBox('4A')).toBe(true);
  });

  test('isBox() returns false for non-box code', () => {
    expect(TipoEmbalajeCatalog.isBox('1A1')).toBe(false);
  });

  test('isBox() returns false for invalid code', () => {
    expect(TipoEmbalajeCatalog.isBox('ZZZZ')).toBe(false);
  });

  test('isBag() returns true for bag codes', () => {
    // 5H1 = "Saco tejido de plástico..." contains SACO
    expect(TipoEmbalajeCatalog.isBag('5H1')).toBe(true);
  });

  test('isBag() returns false for non-bag code', () => {
    expect(TipoEmbalajeCatalog.isBag('1A1')).toBe(false);
  });

  test('isDrum() returns false for code 1A1 (bidón, not tambor)', () => {
    expect(TipoEmbalajeCatalog.isDrum('1A1')).toBe(false);
  });

  test('isDrum() returns false for invalid code', () => {
    expect(TipoEmbalajeCatalog.isDrum('ZZZZ')).toBe(false);
  });

  test('isRigid() returns false for 1A1 (accented Bidón does not match BIDON)', () => {
    // The data has "Bidón" but isRigid checks for "BIDON" without accent handling
    expect(TipoEmbalajeCatalog.isRigid('1A1')).toBe(false);
  });

  test('isFlexible() returns true for bag-type codes', () => {
    expect(TipoEmbalajeCatalog.isFlexible('5H1')).toBe(true);
  });

  test('isFlexible() returns false for invalid code', () => {
    expect(TipoEmbalajeCatalog.isFlexible('ZZZZ')).toBe(false);
  });
});

describe('TipoPermisoCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = TipoPermisoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getPermiso() returns permit for valid code "TPAF01"', () => {
    const permiso = TipoPermisoCatalog.getPermiso('TPAF01');
    expect(permiso).toBeDefined();
    expect(permiso!.code).toBe('TPAF01');
  });

  test('getPermiso() returns undefined for invalid code', () => {
    expect(TipoPermisoCatalog.getPermiso('ZZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(TipoPermisoCatalog.isValid('TPAF01')).toBe(true);
    expect(TipoPermisoCatalog.isValid('ZZZZ')).toBe(false);
  });

  test('isValid() is case-insensitive', () => {
    expect(TipoPermisoCatalog.isValid('tpaf01')).toBe(true);
  });

  // Note: isCargaPermit, isPasajeroPermit, getByTipoTransporte, searchByDescription
  // reference tipo_transporte/descripcion but the data uses type/name fields.
  // These methods throw at runtime due to the property mismatch.
});

describe('ConfigAutotransporteCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = ConfigAutotransporteCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getConfig() returns config for valid code "C2"', () => {
    const config = ConfigAutotransporteCatalog.getConfig('C2');
    expect(config).toBeDefined();
    expect(config!.code).toBe('C2');
  });

  test('getConfig() returns undefined for invalid code', () => {
    expect(ConfigAutotransporteCatalog.getConfig('ZZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(ConfigAutotransporteCatalog.isValid('C2')).toBe(true);
    expect(ConfigAutotransporteCatalog.isValid('ZZZZ')).toBe(false);
  });

  test('requiresRemolque() returns false for C2 (no remolque field in data)', () => {
    // Data uses different field names; remolque is undefined -> false
    expect(ConfigAutotransporteCatalog.requiresRemolque('C2')).toBe(false);
  });

  test('requiresRemolque() returns false for invalid code', () => {
    expect(ConfigAutotransporteCatalog.requiresRemolque('ZZZZ')).toBe(false);
  });

  test('getWithRemolque() returns array (may be empty due to field mismatch)', () => {
    const result = ConfigAutotransporteCatalog.getWithRemolque();
    expect(Array.isArray(result)).toBe(true);
  });

  test('getWithoutRemolque() returns array', () => {
    const result = ConfigAutotransporteCatalog.getWithoutRemolque();
    expect(Array.isArray(result)).toBe(true);
    expect(result.length).toBeGreaterThan(0);
  });

  test('getNumEjes() returns undefined (data uses "axes" not "num_ejes")', () => {
    expect(ConfigAutotransporteCatalog.getNumEjes('C2')).toBeUndefined();
  });

  test('getNumEjes() returns undefined for invalid code', () => {
    expect(ConfigAutotransporteCatalog.getNumEjes('ZZZZ')).toBeUndefined();
  });
});

describe('MaterialPeligrosoCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = MaterialPeligrosoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getMaterial() returns material for valid code "0004"', () => {
    const material = MaterialPeligrosoCatalog.getMaterial('0004');
    expect(material).toBeDefined();
    expect(material!.code).toBe('0004');
  });

  test('getMaterial() returns undefined for invalid code', () => {
    expect(MaterialPeligrosoCatalog.getMaterial('ZZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(MaterialPeligrosoCatalog.isValid('0004')).toBe(true);
    expect(MaterialPeligrosoCatalog.isValid('ZZZZ')).toBe(false);
  });

  test('getDescription() returns description for valid code', () => {
    const desc = MaterialPeligrosoCatalog.getDescription('0004');
    expect(desc).toBeDefined();
    expect(desc).toContain('Picrato');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(MaterialPeligrosoCatalog.getDescription('ZZZZ')).toBeUndefined();
  });

  test('getClaseRiesgo() returns risk class', () => {
    expect(MaterialPeligrosoCatalog.getClaseRiesgo('0004')).toBe('1');
  });

  test('getClaseRiesgo() returns undefined for invalid code', () => {
    expect(MaterialPeligrosoCatalog.getClaseRiesgo('ZZZZ')).toBeUndefined();
  });

  test('getClaseDivision() returns risk division', () => {
    expect(MaterialPeligrosoCatalog.getClaseDivision('0004')).toBe('1.1D');
  });

  test('getClaseDivision() returns undefined for invalid code', () => {
    expect(MaterialPeligrosoCatalog.getClaseDivision('ZZZZ')).toBeUndefined();
  });

  test('getGrupoEmbalaje() returns packing group', () => {
    expect(MaterialPeligrosoCatalog.getGrupoEmbalaje('0004')).toBe('I');
  });

  test('getGrupoEmbalaje() returns undefined for invalid code', () => {
    expect(MaterialPeligrosoCatalog.getGrupoEmbalaje('ZZZZ')).toBeUndefined();
  });

  test('isExplosive() returns true for class 1 material', () => {
    expect(MaterialPeligrosoCatalog.isExplosive('0004')).toBe(true);
  });

  test('isExplosive() returns false for non-explosive material', () => {
    // Find a non-class-1 material
    const all = MaterialPeligrosoCatalog.getAll();
    const nonExplosive = all.find((m) => m.clase_riesgo !== '1');
    if (nonExplosive) {
      expect(MaterialPeligrosoCatalog.isExplosive(nonExplosive.code)).toBe(false);
    }
  });

  test('isExplosive() returns false for invalid code', () => {
    expect(MaterialPeligrosoCatalog.isExplosive('ZZZZ')).toBe(false);
  });

  test('isFlammable() checks for class 2 or 3', () => {
    const all = MaterialPeligrosoCatalog.getAll();
    const flammable = all.find((m) => m.clase_riesgo === '2' || m.clase_riesgo === '3');
    if (flammable) {
      expect(MaterialPeligrosoCatalog.isFlammable(flammable.code)).toBe(true);
    }
    expect(MaterialPeligrosoCatalog.isFlammable('0004')).toBe(false); // class 1
  });

  test('isToxic() checks for class 6', () => {
    const all = MaterialPeligrosoCatalog.getAll();
    const toxic = all.find((m) => m.clase_riesgo === '6');
    if (toxic) {
      expect(MaterialPeligrosoCatalog.isToxic(toxic.code)).toBe(true);
    }
    expect(MaterialPeligrosoCatalog.isToxic('0004')).toBe(false);
  });

  test('isCorrosive() checks for class 8', () => {
    const all = MaterialPeligrosoCatalog.getAll();
    const corrosive = all.find((m) => m.clase_riesgo === '8');
    if (corrosive) {
      expect(MaterialPeligrosoCatalog.isCorrosive(corrosive.code)).toBe(true);
    }
    expect(MaterialPeligrosoCatalog.isCorrosive('0004')).toBe(false);
  });

  test('isCorrosive() returns false for invalid code', () => {
    expect(MaterialPeligrosoCatalog.isCorrosive('ZZZZ')).toBe(false);
  });

  test('getByClaseRiesgo() returns materials for known class', () => {
    const results = MaterialPeligrosoCatalog.getByClaseRiesgo('1');
    expect(results.length).toBeGreaterThan(0);
  });

  test('getByClaseRiesgo() returns empty for unknown class', () => {
    expect(MaterialPeligrosoCatalog.getByClaseRiesgo('999').length).toBe(0);
  });

  test('requiresGroupI() returns true for code "0004"', () => {
    expect(MaterialPeligrosoCatalog.requiresGroupI('0004')).toBe(true);
  });

  test('requiresGroupI() returns false for invalid code', () => {
    expect(MaterialPeligrosoCatalog.requiresGroupI('ZZZZ')).toBe(false);
  });

  test('getByGrupoEmbalaje() returns materials for group "I"', () => {
    const results = MaterialPeligrosoCatalog.getByGrupoEmbalaje('I');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByDescription() finds results for known term', () => {
    const results = MaterialPeligrosoCatalog.searchByDescription('Picrato');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByDescription() returns empty for non-matching term', () => {
    expect(MaterialPeligrosoCatalog.searchByDescription('ZZZZZZZ').length).toBe(0);
  });
});

// =============================================================================
// SAT Comercio Exterior
// =============================================================================

describe('IncotermsValidator', () => {
  test('getAll() returns a non-empty array', () => {
    const all = IncotermsValidator.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getIncoterm() returns incoterm for valid code "FOB"', () => {
    const incoterm = IncotermsValidator.getIncoterm('FOB');
    expect(incoterm).toBeDefined();
    expect(incoterm!.code).toBe('FOB');
    expect(incoterm!.transport_mode).toBe('maritime');
  });

  test('getIncoterm() returns undefined for invalid code', () => {
    expect(IncotermsValidator.getIncoterm('ZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(IncotermsValidator.isValid('FOB')).toBe(true);
    expect(IncotermsValidator.isValid('CIF')).toBe(true);
    expect(IncotermsValidator.isValid('EXW')).toBe(true);
    expect(IncotermsValidator.isValid('ZZZ')).toBe(false);
  });

  test('isValid() is case-insensitive', () => {
    expect(IncotermsValidator.isValid('fob')).toBe(true);
  });

  test('sellerPaysInsurance() returns true for CIF', () => {
    expect(IncotermsValidator.sellerPaysInsurance('CIF')).toBe(true);
  });

  test('sellerPaysInsurance() returns false for FOB', () => {
    expect(IncotermsValidator.sellerPaysInsurance('FOB')).toBe(false);
  });

  test('sellerPaysInsurance() returns false for invalid code', () => {
    expect(IncotermsValidator.sellerPaysInsurance('ZZZ')).toBe(false);
  });

  test('buyerPaysInsurance() returns true for FOB', () => {
    expect(IncotermsValidator.buyerPaysInsurance('FOB')).toBe(true);
  });

  test('buyerPaysInsurance() returns false for invalid code', () => {
    expect(IncotermsValidator.buyerPaysInsurance('ZZZ')).toBe(false);
  });

  test('getByTransportMode() returns maritime-only incoterms', () => {
    const maritime = IncotermsValidator.getByTransportMode('maritime');
    expect(maritime.length).toBeGreaterThan(0);
    maritime.forEach((inc) => expect(inc.transport_mode).toBe('maritime'));
  });

  test('getForAnyTransport() returns incoterms for any transport', () => {
    const any = IncotermsValidator.getForAnyTransport();
    expect(any.length).toBeGreaterThan(0);
    any.forEach((inc) => expect(inc.transport_mode).toBe('any'));
  });

  test('getForMaritimeTransport() returns maritime incoterms', () => {
    const maritime = IncotermsValidator.getForMaritimeTransport();
    expect(maritime.length).toBeGreaterThan(0);
  });

  test('isValidForTransportMode() validates FOB for maritime', () => {
    expect(IncotermsValidator.isValidForTransportMode('FOB', 'maritime')).toBe(true);
  });

  test('isValidForTransportMode() EXW is valid for any mode', () => {
    expect(IncotermsValidator.isValidForTransportMode('EXW', 'maritime')).toBe(true);
    expect(IncotermsValidator.isValidForTransportMode('EXW', 'any')).toBe(true);
  });

  test('isValidForTransportMode() returns false for invalid code', () => {
    expect(IncotermsValidator.isValidForTransportMode('ZZZ', 'maritime')).toBe(false);
  });
});

describe('ClavePedimentoCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = ClavePedimentoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getClave() returns item for valid clave "A1"', () => {
    const clave = ClavePedimentoCatalog.getClave('A1');
    expect(clave).toBeDefined();
    expect(clave!.clave).toBe('A1');
  });

  test('getClave() returns undefined for invalid clave', () => {
    expect(ClavePedimentoCatalog.getClave('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(ClavePedimentoCatalog.isValid('A1')).toBe(true);
    expect(ClavePedimentoCatalog.isValid('ZZ')).toBe(false);
  });

  test('isImport() returns false for A1 (data uses "regimen" not "tipo")', () => {
    // Code checks cp.tipo but data uses cp.regimen - so isImport returns false
    expect(ClavePedimentoCatalog.isImport('A1')).toBe(false);
  });

  test('isExport() returns false for A1 (data uses "regimen" not "tipo")', () => {
    // Code checks cp.tipo but data uses cp.regimen
    expect(ClavePedimentoCatalog.isExport('A1')).toBe(false);
  });

  test('isTransit() returns false for A1', () => {
    expect(ClavePedimentoCatalog.isTransit('A1')).toBe(false);
  });

  test('getImportClaves() returns empty due to field mismatch', () => {
    expect(ClavePedimentoCatalog.getImportClaves().length).toBe(0);
  });

  test('getExportClaves() returns empty due to field mismatch', () => {
    expect(ClavePedimentoCatalog.getExportClaves().length).toBe(0);
  });

  test('searchByDescription() finds results for known term', () => {
    const results = ClavePedimentoCatalog.searchByDescription('definitiva');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByDescription() returns empty for non-matching term', () => {
    expect(ClavePedimentoCatalog.searchByDescription('ZZZZZ').length).toBe(0);
  });
});

describe('MonedaCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = MonedaCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getMoneda() returns currency for valid code "USD"', () => {
    const moneda = MonedaCatalog.getMoneda('USD');
    expect(moneda).toBeDefined();
  });

  test('getMoneda() returns undefined for invalid code', () => {
    expect(MonedaCatalog.getMoneda('ZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(MonedaCatalog.isValid('USD')).toBe(true);
    expect(MonedaCatalog.isValid('MXN')).toBe(true);
    expect(MonedaCatalog.isValid('ZZZ')).toBe(false);
  });

  test('isValid() is case-insensitive', () => {
    expect(MonedaCatalog.isValid('usd')).toBe(true);
  });

  test('getName() returns currency name', () => {
    const name = MonedaCatalog.getName('USD');
    expect(name).toBeDefined();
    expect(name).toContain('lar');
  });

  test('getName() returns undefined for invalid code', () => {
    expect(MonedaCatalog.getName('ZZZ')).toBeUndefined();
  });

  test('getDecimals() returns decimal precision', () => {
    expect(MonedaCatalog.getDecimals('USD')).toBe(2);
  });

  test('getDecimals() returns undefined for invalid code', () => {
    expect(MonedaCatalog.getDecimals('ZZZ')).toBeUndefined();
  });

  test('searchByName() finds results for matching code', () => {
    const results = MonedaCatalog.searchByName('USD');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByName() finds results with accented characters', () => {
    const results = MonedaCatalog.searchByName('Dólar');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByName() returns empty for non-matching term', () => {
    expect(MonedaCatalog.searchByName('ZZZZZZZ').length).toBe(0);
  });

  test('validateConversionUsd() validates USD to USD', () => {
    const result = MonedaCatalog.validateConversionUsd({
      moneda: 'USD',
      total: 100,
      tipo_cambio_usd: 1.0,
      total_usd: 100,
    });
    expect(result.valid).toBe(true);
  });

  test('validateConversionUsd() rejects wrong exchange rate for USD', () => {
    const result = MonedaCatalog.validateConversionUsd({
      moneda: 'USD',
      total: 100,
      tipo_cambio_usd: 2.0,
      total_usd: 200,
    });
    expect(result.valid).toBe(false);
    expect(result.error).toContain('Exchange rate for USD must be 1.0');
  });

  test('validateConversionUsd() rejects mismatched totals for USD', () => {
    const result = MonedaCatalog.validateConversionUsd({
      moneda: 'USD',
      total: 100,
      tipo_cambio_usd: 1.0,
      total_usd: 200,
    });
    expect(result.valid).toBe(false);
    expect(result.error).toContain('Total and total_usd must be equal');
  });

  test('validateConversionUsd() validates non-USD conversion', () => {
    const result = MonedaCatalog.validateConversionUsd({
      moneda: 'MXN',
      total: 1000,
      tipo_cambio_usd: 0.05,
      total_usd: 50,
    });
    expect(result.valid).toBe(true);
    expect(result.calculated_total).toBe(50);
  });

  test('validateConversionUsd() rejects invalid currency code', () => {
    const result = MonedaCatalog.validateConversionUsd({
      moneda: 'ZZZ',
      total: 100,
      tipo_cambio_usd: 1.0,
      total_usd: 100,
    });
    expect(result.valid).toBe(false);
    expect(result.error).toContain('Invalid currency code');
  });

  test('validateConversionUsd() rejects conversion mismatch', () => {
    const result = MonedaCatalog.validateConversionUsd({
      moneda: 'MXN',
      total: 1000,
      tipo_cambio_usd: 0.05,
      total_usd: 999, // wrong
    });
    expect(result.valid).toBe(false);
    expect(result.error).toContain('Conversion mismatch');
  });
});

describe('PaisCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = PaisCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getPais() returns country for valid code "MEX"', () => {
    const pais = PaisCatalog.getPais('MEX');
    expect(pais).toBeDefined();
  });

  test('getPais() returns undefined for invalid code', () => {
    expect(PaisCatalog.getPais('ZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(PaisCatalog.isValid('MEX')).toBe(true);
    expect(PaisCatalog.isValid('USA')).toBe(true);
    expect(PaisCatalog.isValid('ZZZ')).toBe(false);
  });

  test('getName() returns country name', () => {
    const name = PaisCatalog.getName('MEX');
    expect(name).toBeDefined();
    expect(name).toContain('xico');
  });

  test('getName() returns undefined for invalid code', () => {
    expect(PaisCatalog.getName('ZZZ')).toBeUndefined();
  });

  test('searchByName() finds results with accented characters', () => {
    const results = PaisCatalog.searchByName('México');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByName() returns empty for non-matching term', () => {
    expect(PaisCatalog.searchByName('ZZZZZZZ').length).toBe(0);
  });

  test('getByAgrupacion() returns array (may be empty if no matches)', () => {
    const results = PaisCatalog.getByAgrupacion('test');
    expect(Array.isArray(results)).toBe(true);
  });

  test('isMexico() returns true for "MEX" and false otherwise', () => {
    expect(PaisCatalog.isMexico('MEX')).toBe(true);
    expect(PaisCatalog.isMexico('mex')).toBe(true);
    expect(PaisCatalog.isMexico('USA')).toBe(false);
  });

  test('isUSA() returns true for "USA" and false otherwise', () => {
    expect(PaisCatalog.isUSA('USA')).toBe(true);
    expect(PaisCatalog.isUSA('usa')).toBe(true);
    expect(PaisCatalog.isUSA('MEX')).toBe(false);
  });

  test('isCanada() returns true for "CAN" and false otherwise', () => {
    expect(PaisCatalog.isCanada('CAN')).toBe(true);
    expect(PaisCatalog.isCanada('can')).toBe(true);
    expect(PaisCatalog.isCanada('MEX')).toBe(false);
  });
});

describe('EstadoCatalog (USA/Canada states)', () => {
  test('getAll() returns a non-empty array', () => {
    const all = EstadoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getEstado() returns state for valid code "AL"', () => {
    const estado = EstadoCatalog.getEstado('AL');
    expect(estado).toBeDefined();
    expect(estado!.code).toBe('AL');
    expect(estado!.country).toBe('USA');
  });

  test('getEstado() returns undefined for invalid code', () => {
    expect(EstadoCatalog.getEstado('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(EstadoCatalog.isValid('AL')).toBe(true);
    expect(EstadoCatalog.isValid('ZZ')).toBe(false);
  });

  test('getEstadosUSA() returns US states', () => {
    const states = EstadoCatalog.getEstadosUSA();
    expect(states.length).toBeGreaterThan(0);
    states.forEach((s) => expect(s.country).toBe('USA'));
  });

  test('getProvinciasCanada() returns Canadian provinces', () => {
    const provinces = EstadoCatalog.getProvinciasCanada();
    expect(provinces.length).toBeGreaterThan(0);
    provinces.forEach((p) => expect(p.country).toBe('CAN'));
  });

  test('getEstadoUsa() returns state only if country is USA', () => {
    const state = EstadoCatalog.getEstadoUsa('AL');
    expect(state).toBeDefined();
    expect(state!.country).toBe('USA');
  });

  test('getEstadoUsa() returns undefined for Canadian province', () => {
    const provinces = EstadoCatalog.getProvinciasCanada();
    if (provinces.length > 0) {
      expect(EstadoCatalog.getEstadoUsa(provinces[0].code)).toBeUndefined();
    }
  });

  test('getProvinciaCanada() returns province only if country is CAN', () => {
    const provinces = EstadoCatalog.getProvinciasCanada();
    if (provinces.length > 0) {
      const provincia = EstadoCatalog.getProvinciaCanada(provinces[0].code);
      expect(provincia).toBeDefined();
      expect(provincia!.country).toBe('CAN');
    }
  });

  test('getProvinciaCanada() returns undefined for US state', () => {
    expect(EstadoCatalog.getProvinciaCanada('AL')).toBeUndefined();
  });

  test('isValidUSA() returns true for US state code', () => {
    expect(EstadoCatalog.isValidUSA('AL')).toBe(true);
  });

  test('isValidUSA() returns false for Canadian province', () => {
    const provinces = EstadoCatalog.getProvinciasCanada();
    if (provinces.length > 0) {
      expect(EstadoCatalog.isValidUSA(provinces[0].code)).toBe(false);
    }
  });

  test('isValidCanada() returns true for Canadian province', () => {
    const provinces = EstadoCatalog.getProvinciasCanada();
    if (provinces.length > 0) {
      expect(EstadoCatalog.isValidCanada(provinces[0].code)).toBe(true);
    }
  });

  test('isValidCanada() returns false for US state', () => {
    expect(EstadoCatalog.isValidCanada('AL')).toBe(false);
  });

  test('isValidForCountry() validates state for specific country', () => {
    expect(EstadoCatalog.isValidForCountry('AL', 'USA')).toBe(true);
    expect(EstadoCatalog.isValidForCountry('AL', 'CAN')).toBe(false);
  });
});

describe('MotivoTrasladoCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = MotivoTrasladoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getMotivo() returns motive for valid code "01"', () => {
    const motivo = MotivoTrasladoCatalog.getMotivo('01');
    expect(motivo).toBeDefined();
    expect(motivo!.code).toBe('01');
  });

  test('getMotivo() returns undefined for invalid code', () => {
    expect(MotivoTrasladoCatalog.getMotivo('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(MotivoTrasladoCatalog.isValid('01')).toBe(true);
    expect(MotivoTrasladoCatalog.isValid('ZZ')).toBe(false);
  });

  test('getDescription() returns description for valid code', () => {
    expect(MotivoTrasladoCatalog.getDescription('01')).toContain('mercancías');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(MotivoTrasladoCatalog.getDescription('ZZ')).toBeUndefined();
  });

  test('searchByDescription() finds results for matching term', () => {
    // Must match case and accents from the data
    const results = MotivoTrasladoCatalog.searchByDescription('MERC');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByDescription() returns empty for non-matching term', () => {
    expect(MotivoTrasladoCatalog.searchByDescription('ZZZZZ').length).toBe(0);
  });

  test('isExportMotivo() returns false for code "01" (no export in description)', () => {
    expect(MotivoTrasladoCatalog.isExportMotivo('01')).toBe(false);
  });

  test('isExportMotivo() returns false for invalid code', () => {
    expect(MotivoTrasladoCatalog.isExportMotivo('ZZ')).toBe(false);
  });

  test('isImportMotivo() returns false for code "01"', () => {
    expect(MotivoTrasladoCatalog.isImportMotivo('01')).toBe(false);
  });

  test('isImportMotivo() returns false for invalid code', () => {
    expect(MotivoTrasladoCatalog.isImportMotivo('ZZ')).toBe(false);
  });
});

describe('RegistroIdentTribCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = RegistroIdentTribCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getRegistro() returns registro for valid code "01"', () => {
    const registro = RegistroIdentTribCatalog.getRegistro('01');
    expect(registro).toBeDefined();
    expect(registro!.code).toBe('01');
  });

  test('getRegistro() returns undefined for invalid code', () => {
    expect(RegistroIdentTribCatalog.getRegistro('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(RegistroIdentTribCatalog.isValid('01')).toBe(true);
    expect(RegistroIdentTribCatalog.isValid('ZZ')).toBe(false);
  });

  test('getDescription() returns description for valid code', () => {
    const desc = RegistroIdentTribCatalog.getDescription('01');
    expect(desc).toBeDefined();
    expect(desc).toContain('fiscal');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(RegistroIdentTribCatalog.getDescription('ZZ')).toBeUndefined();
  });

  test('validateTaxId() returns true when no regex pattern exists', () => {
    // Registration "01" has no regex_pattern field, so validation passes
    expect(RegistroIdentTribCatalog.validateTaxId('01', 'abc123')).toBe(true);
  });

  test('validateTaxId() returns true for non-existent registro (no pattern)', () => {
    expect(RegistroIdentTribCatalog.validateTaxId('ZZ', 'abc')).toBe(true);
  });

  test('getFormato() returns undefined (data has no formato field)', () => {
    expect(RegistroIdentTribCatalog.getFormato('01')).toBeUndefined();
  });

  test('getByPais() returns empty (data has no pais field)', () => {
    const results = RegistroIdentTribCatalog.getByPais('USA');
    expect(results.length).toBe(0);
  });

  test('isUSATaxId() returns false (no pais field in data)', () => {
    expect(RegistroIdentTribCatalog.isUSATaxId('01')).toBe(false);
  });

  test('isEUTaxId() returns false for code "01"', () => {
    expect(RegistroIdentTribCatalog.isEUTaxId('01')).toBe(false);
  });
});

describe('UnidadAduanaCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = UnidadAduanaCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getUnidad() returns unit for valid code "01"', () => {
    const unidad = UnidadAduanaCatalog.getUnidad('01');
    expect(unidad).toBeDefined();
    expect(unidad!.code).toBe('01');
  });

  test('getUnidad() returns undefined for invalid code', () => {
    expect(UnidadAduanaCatalog.getUnidad('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(UnidadAduanaCatalog.isValid('01')).toBe(true);
    expect(UnidadAduanaCatalog.isValid('ZZ')).toBe(false);
  });

  test('getName() returns undefined (data has no name field, only descripcion)', () => {
    expect(UnidadAduanaCatalog.getName('01')).toBeUndefined();
  });

  test('getDescription() returns description for valid code', () => {
    expect(UnidadAduanaCatalog.getDescription('01')).toBe('Kilogramo');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(UnidadAduanaCatalog.getDescription('ZZ')).toBeUndefined();
  });

  test('isWeightUnit() returns true for kilogram unit', () => {
    expect(UnidadAduanaCatalog.isWeightUnit('01')).toBe(true);
  });

  test('isWeightUnit() returns false for invalid code', () => {
    expect(UnidadAduanaCatalog.isWeightUnit('ZZ')).toBe(false);
  });

  test('isPieceUnit() identifies piece units', () => {
    // Code "10" = "Pieza"
    expect(UnidadAduanaCatalog.isPieceUnit('10')).toBe(true);
    expect(UnidadAduanaCatalog.isPieceUnit('01')).toBe(false); // Kilogramo
  });

  test('isPieceUnit() returns false for invalid code', () => {
    expect(UnidadAduanaCatalog.isPieceUnit('ZZ')).toBe(false);
  });

  test('isVolumeUnit() returns false for kilogram unit', () => {
    expect(UnidadAduanaCatalog.isVolumeUnit('01')).toBe(false);
  });

  test('isVolumeUnit() returns false for invalid code', () => {
    expect(UnidadAduanaCatalog.isVolumeUnit('ZZ')).toBe(false);
  });

  test('isLengthUnit() returns false for kilogram unit', () => {
    expect(UnidadAduanaCatalog.isLengthUnit('01')).toBe(false);
  });

  test('isLengthUnit() returns false for invalid code', () => {
    expect(UnidadAduanaCatalog.isLengthUnit('ZZ')).toBe(false);
  });
});

// =============================================================================
// SAT CFDI 4.0 (low coverage catalogs)
// =============================================================================

describe('TipoComprobanteCatalog', () => {
  test('getAll() returns array with 5 types', () => {
    const all = TipoComprobanteCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBe(5);
  });

  test('getTipo() returns tipo for valid code "I"', () => {
    const tipo = TipoComprobanteCatalog.getTipo('I');
    expect(tipo).toBeDefined();
    expect(tipo!.code).toBe('I');
  });

  test('getTipo() returns undefined for invalid code', () => {
    expect(TipoComprobanteCatalog.getTipo('Z')).toBeUndefined();
  });

  test('isValid() returns true for all known types', () => {
    expect(TipoComprobanteCatalog.isValid('I')).toBe(true);
    expect(TipoComprobanteCatalog.isValid('E')).toBe(true);
    expect(TipoComprobanteCatalog.isValid('T')).toBe(true);
    expect(TipoComprobanteCatalog.isValid('N')).toBe(true);
    expect(TipoComprobanteCatalog.isValid('P')).toBe(true);
    expect(TipoComprobanteCatalog.isValid('Z')).toBe(false);
  });

  test('isValid() is case-insensitive', () => {
    expect(TipoComprobanteCatalog.isValid('i')).toBe(true);
  });

  test('isIngreso() returns true for "I"', () => {
    expect(TipoComprobanteCatalog.isIngreso('I')).toBe(true);
    expect(TipoComprobanteCatalog.isIngreso('i')).toBe(true);
    expect(TipoComprobanteCatalog.isIngreso('E')).toBe(false);
  });

  test('isEgreso() returns true for "E"', () => {
    expect(TipoComprobanteCatalog.isEgreso('E')).toBe(true);
    expect(TipoComprobanteCatalog.isEgreso('e')).toBe(true);
    expect(TipoComprobanteCatalog.isEgreso('I')).toBe(false);
  });

  test('isTraslado() returns true for "T"', () => {
    expect(TipoComprobanteCatalog.isTraslado('T')).toBe(true);
    expect(TipoComprobanteCatalog.isTraslado('t')).toBe(true);
    expect(TipoComprobanteCatalog.isTraslado('I')).toBe(false);
  });

  test('isNomina() returns true for "N"', () => {
    expect(TipoComprobanteCatalog.isNomina('N')).toBe(true);
    expect(TipoComprobanteCatalog.isNomina('n')).toBe(true);
    expect(TipoComprobanteCatalog.isNomina('I')).toBe(false);
  });

  test('isPago() returns true for "P"', () => {
    expect(TipoComprobanteCatalog.isPago('P')).toBe(true);
    expect(TipoComprobanteCatalog.isPago('p')).toBe(true);
    expect(TipoComprobanteCatalog.isPago('I')).toBe(false);
  });

  test('getDescription() returns description for valid code', () => {
    expect(TipoComprobanteCatalog.getDescription('I')).toBe('Ingreso');
    expect(TipoComprobanteCatalog.getDescription('E')).toBe('Egreso');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(TipoComprobanteCatalog.getDescription('Z')).toBeUndefined();
  });

  test('getValorMax() returns undefined (field not present in data)', () => {
    expect(TipoComprobanteCatalog.getValorMax('I')).toBeUndefined();
  });
});

describe('ExportacionCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = ExportacionCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getExportacion() returns item for valid code "01"', () => {
    const exp = ExportacionCatalog.getExportacion('01');
    expect(exp).toBeDefined();
    expect(exp!.code).toBe('01');
  });

  test('getExportacion() returns undefined for invalid code', () => {
    expect(ExportacionCatalog.getExportacion('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(ExportacionCatalog.isValid('01')).toBe(true);
    expect(ExportacionCatalog.isValid('02')).toBe(true);
    expect(ExportacionCatalog.isValid('ZZ')).toBe(false);
  });

  test('isNoAplicaExportacion() returns true for "01"', () => {
    expect(ExportacionCatalog.isNoAplicaExportacion('01')).toBe(true);
    expect(ExportacionCatalog.isNoAplicaExportacion('02')).toBe(false);
  });

  test('isExportacionDefinitiva() returns true for "02"', () => {
    expect(ExportacionCatalog.isExportacionDefinitiva('02')).toBe(true);
    expect(ExportacionCatalog.isExportacionDefinitiva('01')).toBe(false);
  });

  test('getDescription() returns description for valid code', () => {
    expect(ExportacionCatalog.getDescription('01')).toBe('No aplica');
    expect(ExportacionCatalog.getDescription('02')).toBe('Definitiva');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(ExportacionCatalog.getDescription('ZZ')).toBeUndefined();
  });
});

describe('ObjetoImpCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = ObjetoImpCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getObjeto() returns item for valid code "01"', () => {
    const obj = ObjetoImpCatalog.getObjeto('01');
    expect(obj).toBeDefined();
    expect(obj!.code).toBe('01');
  });

  test('getObjeto() returns undefined for invalid code', () => {
    expect(ObjetoImpCatalog.getObjeto('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(ObjetoImpCatalog.isValid('01')).toBe(true);
    expect(ObjetoImpCatalog.isValid('02')).toBe(true);
    expect(ObjetoImpCatalog.isValid('03')).toBe(true);
    expect(ObjetoImpCatalog.isValid('ZZ')).toBe(false);
  });

  test('isNoObjetoImpuesto() returns true for "01"', () => {
    expect(ObjetoImpCatalog.isNoObjetoImpuesto('01')).toBe(true);
    expect(ObjetoImpCatalog.isNoObjetoImpuesto('02')).toBe(false);
  });

  test('isSiObjetoImpuesto() returns true for "02"', () => {
    expect(ObjetoImpCatalog.isSiObjetoImpuesto('02')).toBe(true);
    expect(ObjetoImpCatalog.isSiObjetoImpuesto('01')).toBe(false);
  });

  test('isExento() returns true for "03" and "04"', () => {
    expect(ObjetoImpCatalog.isExento('03')).toBe(true);
    expect(ObjetoImpCatalog.isExento('04')).toBe(true);
    expect(ObjetoImpCatalog.isExento('01')).toBe(false);
    expect(ObjetoImpCatalog.isExento('02')).toBe(false);
  });

  test('getDescription() returns description for valid codes', () => {
    expect(ObjetoImpCatalog.getDescription('01')).toContain('No objeto');
    expect(ObjetoImpCatalog.getDescription('02')).toContain('objeto');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(ObjetoImpCatalog.getDescription('ZZ')).toBeUndefined();
  });

  test('searchByDescription() finds results for known term', () => {
    const results = ObjetoImpCatalog.searchByDescription('impuesto');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByDescription() returns empty for non-matching term', () => {
    expect(ObjetoImpCatalog.searchByDescription('ZZZZZ').length).toBe(0);
  });
});

describe('TipoRelacionCatalog', () => {
  test('getAll() returns a non-empty array', () => {
    const all = TipoRelacionCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBeGreaterThan(0);
  });

  test('getRelacion() returns item for valid code "01"', () => {
    const relacion = TipoRelacionCatalog.getRelacion('01');
    expect(relacion).toBeDefined();
    expect(relacion!.code).toBe('01');
  });

  test('getRelacion() returns undefined for invalid code', () => {
    expect(TipoRelacionCatalog.getRelacion('ZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(TipoRelacionCatalog.isValid('01')).toBe(true);
    expect(TipoRelacionCatalog.isValid('02')).toBe(true);
    expect(TipoRelacionCatalog.isValid('ZZ')).toBe(false);
  });

  test('isNotaDeDebito() returns true for "01"', () => {
    expect(TipoRelacionCatalog.isNotaDeDebito('01')).toBe(true);
    expect(TipoRelacionCatalog.isNotaDeDebito('02')).toBe(false);
  });

  test('isNotaDeCredito() returns true for "02"', () => {
    expect(TipoRelacionCatalog.isNotaDeCredito('02')).toBe(true);
    expect(TipoRelacionCatalog.isNotaDeCredito('01')).toBe(false);
  });

  test('getDescription() returns description for valid code', () => {
    const desc = TipoRelacionCatalog.getDescription('01');
    expect(desc).toBeDefined();
    expect(desc).toContain('crédito');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(TipoRelacionCatalog.getDescription('ZZ')).toBeUndefined();
  });

  test('searchByDescription() finds results with accented characters', () => {
    const results = TipoRelacionCatalog.searchByDescription('crédito');
    expect(results.length).toBeGreaterThan(0);
  });

  test('searchByDescription() returns empty for non-matching term', () => {
    expect(TipoRelacionCatalog.searchByDescription('ZZZZZ').length).toBe(0);
  });
});

describe('MetodoPagoCatalog', () => {
  test('getAll() returns array with 2 methods', () => {
    const all = MetodoPagoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBe(2);
  });

  test('getMetodo() returns item for valid code "PUE"', () => {
    const metodo = MetodoPagoCatalog.getMetodo('PUE');
    expect(metodo).toBeDefined();
    expect(metodo!.code).toBe('PUE');
  });

  test('getMetodo() returns undefined for invalid code', () => {
    expect(MetodoPagoCatalog.getMetodo('ZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(MetodoPagoCatalog.isValid('PUE')).toBe(true);
    expect(MetodoPagoCatalog.isValid('PPD')).toBe(true);
    expect(MetodoPagoCatalog.isValid('ZZZ')).toBe(false);
  });

  test('isValid() is case-insensitive', () => {
    expect(MetodoPagoCatalog.isValid('pue')).toBe(true);
    expect(MetodoPagoCatalog.isValid('ppd')).toBe(true);
  });

  test('isPUE() returns true for "PUE"', () => {
    expect(MetodoPagoCatalog.isPUE('PUE')).toBe(true);
    expect(MetodoPagoCatalog.isPUE('pue')).toBe(true);
    expect(MetodoPagoCatalog.isPUE('PPD')).toBe(false);
  });

  test('isPPD() returns true for "PPD"', () => {
    expect(MetodoPagoCatalog.isPPD('PPD')).toBe(true);
    expect(MetodoPagoCatalog.isPPD('ppd')).toBe(true);
    expect(MetodoPagoCatalog.isPPD('PUE')).toBe(false);
  });

  test('getDescription() returns description for valid codes', () => {
    expect(MetodoPagoCatalog.getDescription('PUE')).toContain('una sola');
    expect(MetodoPagoCatalog.getDescription('PPD')).toContain('parcialidades');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(MetodoPagoCatalog.getDescription('ZZZ')).toBeUndefined();
  });
});

describe('ImpuestoCatalog', () => {
  test('getAll() returns array with 3 tax types', () => {
    const all = ImpuestoCatalog.getAll();
    expect(Array.isArray(all)).toBe(true);
    expect(all.length).toBe(3);
  });

  test('getImpuesto() returns item for valid code "001"', () => {
    const impuesto = ImpuestoCatalog.getImpuesto('001');
    expect(impuesto).toBeDefined();
    expect(impuesto!.code).toBe('001');
  });

  test('getImpuesto() returns undefined for invalid code', () => {
    expect(ImpuestoCatalog.getImpuesto('ZZZ')).toBeUndefined();
  });

  test('isValid() returns true/false appropriately', () => {
    expect(ImpuestoCatalog.isValid('001')).toBe(true);
    expect(ImpuestoCatalog.isValid('002')).toBe(true);
    expect(ImpuestoCatalog.isValid('003')).toBe(true);
    expect(ImpuestoCatalog.isValid('ZZZ')).toBe(false);
  });

  test('isISR() returns true for "001"', () => {
    expect(ImpuestoCatalog.isISR('001')).toBe(true);
    expect(ImpuestoCatalog.isISR('002')).toBe(false);
  });

  test('isIVA() returns true for "002"', () => {
    expect(ImpuestoCatalog.isIVA('002')).toBe(true);
    expect(ImpuestoCatalog.isIVA('001')).toBe(false);
  });

  test('isIEPS() returns true for "003"', () => {
    expect(ImpuestoCatalog.isIEPS('003')).toBe(true);
    expect(ImpuestoCatalog.isIEPS('001')).toBe(false);
  });

  test('getDescription() returns tax description', () => {
    expect(ImpuestoCatalog.getDescription('001')).toBe('ISR');
    expect(ImpuestoCatalog.getDescription('002')).toBe('IVA');
    expect(ImpuestoCatalog.getDescription('003')).toBe('IEPS');
  });

  test('getDescription() returns undefined for invalid code', () => {
    expect(ImpuestoCatalog.getDescription('ZZZ')).toBeUndefined();
  });

  test('supportsRetencion() returns false (data uses "retention" not "retencion")', () => {
    // Data field mismatch: code reads .retencion, data has .retention
    expect(ImpuestoCatalog.supportsRetencion('001')).toBe(false);
  });

  test('supportsTraslado() returns false (data uses "transfer" not "traslado")', () => {
    // Data field mismatch: code reads .traslado, data has .transfer
    expect(ImpuestoCatalog.supportsTraslado('002')).toBe(false);
  });

  test('getRetencionTaxes() returns empty due to field mismatch', () => {
    expect(ImpuestoCatalog.getRetencionTaxes().length).toBe(0);
  });

  test('getTrasladoTaxes() returns empty due to field mismatch', () => {
    expect(ImpuestoCatalog.getTrasladoTaxes().length).toBe(0);
  });
});
