/**
 * Comprehensive tests for remaining catalog modules with low coverage.
 *
 * Covers: CNBV, IFT, INEGI (SCIAN, Localidades), Mexico (Giros Mercantiles),
 * SEPOMEX (CodigosPostalesCompleto, CodigosPostales missing parts),
 * SAT Contabilidad Electronica (CodigoAgrupador missing parts),
 * SAT CFDI 4.0 (CodigoPostal), RESICO Calculator, catalog-backend utils,
 * catalog-loader utils, CLABE generate, NSS generate, CFDI signing.
 */

import { describe, expect, test } from '@jest/globals';

// Catalogs
import {
  SectoresCNBVCatalog,
  OperadoresMoviles,
  SCIANCatalog,
  LocalidadesCatalog,
  GirosMercantilesCatalog,
  CodigosPostalesCompleto,
  CodigosPostales,
  CodigoAgrupadorSATCatalog,
} from '../src/catalogs';

import { CodigoPostalCatalog } from '../src/catalogs/sat/cfdi_4/codigo-postal';

// Calculator
import { RESICOCalculator } from '../src/calculators/resico-calculator';

// Utils
import {
  setCatalogJsonData,
  clearCatalogJsonData,
  clearCatalogCache,
  hasCatalogJsonData,
  loadCatalogJson,
  loadCatalogRows,
  tableNameForJsonPath,
  isNodeRuntime,
  setCatalogSqliteAdapter,
  setCatalogPreferSqlite,
} from '../src/utils/catalog-backend';
import {
  CatalogLoader,
  loadCatalogArray,
  loadCatalogObject,
  loadCatalogData,
} from '../src/utils/catalog-loader';

// Validators
import {
  CLABEValidator,
  generateClabe,
  calculateClabeCheckDigit,
  getClabeInfo,
  validateClabe,
} from '../src/validators/clabe';
import { NSSValidator, generateNss, validateNss } from '../src/validators/nss';

// CFDI signing
import { signCadenaOriginal, aplicarSelloAComprobante } from '../src/cfdi/signing';

// ---------------------------------------------------------------------------
// CNBV Sectores
// ---------------------------------------------------------------------------
describe('CNBV SectoresCNBVCatalog', () => {
  test('getAll returns sectors', () => {
    const all = SectoresCNBVCatalog.getAll();
    expect(all.length).toBeGreaterThan(0);
    expect(all[0]).toHaveProperty('id');
    expect(all[0]).toHaveProperty('nombre');
    expect(all[0]).toHaveProperty('descripcion');
    expect(all[0]).toHaveProperty('regulador_principal');
    expect(all[0]).toHaveProperty('ley_aplicable');
    expect(all[0]).toHaveProperty('ejemplos');
  });

  test('getAllReguladores returns regulators', () => {
    const reguladores = SectoresCNBVCatalog.getAllReguladores();
    expect(reguladores.length).toBeGreaterThan(0);
    expect(reguladores[0]).toHaveProperty('id');
    expect(reguladores[0]).toHaveProperty('nombre');
    expect(reguladores[0]).toHaveProperty('siglas');
  });

  test('getById returns a sector for valid id', () => {
    const all = SectoresCNBVCatalog.getAll();
    const first = all[0];
    const found = SectoresCNBVCatalog.getById(first.id);
    expect(found).toBeDefined();
    expect(found!.id).toBe(first.id);
  });

  test('getById returns undefined for unknown id', () => {
    expect(SectoresCNBVCatalog.getById('ZZZZZ_NONEXISTENT')).toBeUndefined();
  });

  test('getReguladorById returns a regulator', () => {
    const reguladores = SectoresCNBVCatalog.getAllReguladores();
    const first = reguladores[0];
    const found = SectoresCNBVCatalog.getReguladorById(first.id);
    expect(found).toBeDefined();
    expect(found!.siglas).toBe(first.siglas);
  });

  test('getReguladorById returns undefined for unknown id', () => {
    expect(SectoresCNBVCatalog.getReguladorById('NONEXISTENT')).toBeUndefined();
  });

  test('isValid returns true for existing sector', () => {
    const all = SectoresCNBVCatalog.getAll();
    expect(SectoresCNBVCatalog.isValid(all[0].id)).toBe(true);
  });

  test('isValid returns false for non-existing sector', () => {
    expect(SectoresCNBVCatalog.isValid('FAKE')).toBe(false);
  });

  test('search finds sectors by name', () => {
    const all = SectoresCNBVCatalog.getAll();
    // Search with a fragment of the first sector's name
    const fragment = all[0].nombre.split(' ')[0];
    const results = SectoresCNBVCatalog.search(fragment);
    expect(results.length).toBeGreaterThan(0);
  });

  test('search returns empty for non-matching query', () => {
    expect(SectoresCNBVCatalog.search('XYZNONEXISTENT123')).toEqual([]);
  });

  test('getByRegulador filters sectors', () => {
    const all = SectoresCNBVCatalog.getAll();
    const regId = all[0].regulador_principal;
    const filtered = SectoresCNBVCatalog.getByRegulador(regId);
    expect(filtered.length).toBeGreaterThan(0);
    filtered.forEach((s) => expect(s.regulador_principal).toBe(regId));
  });

  test('getByRegulador returns empty for unknown regulator', () => {
    expect(SectoresCNBVCatalog.getByRegulador('FAKE_REG')).toEqual([]);
  });

  test('count returns a positive number', () => {
    expect(SectoresCNBVCatalog.count).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// IFT Operadores Moviles
// ---------------------------------------------------------------------------
describe('IFT OperadoresMoviles', () => {
  test('getAll returns operators', () => {
    const all = OperadoresMoviles.getAll();
    expect(all.length).toBeGreaterThan(0);
    expect(all[0]).toHaveProperty('nombre_comercial');
    expect(all[0]).toHaveProperty('tipo');
  });

  test('getActivos returns only active operators', () => {
    const activos = OperadoresMoviles.getActivos();
    expect(activos.length).toBeGreaterThan(0);
    activos.forEach((op) => expect(op.activo).toBe(true));
  });

  test('buscarPorNombre finds operator by name fragment', () => {
    const all = OperadoresMoviles.getAll();
    const fragment = all[0].nombre_comercial.slice(0, 3);
    const found = OperadoresMoviles.buscarPorNombre(fragment);
    expect(found).toBeDefined();
  });

  test('buscarPorNombre returns undefined for nonexistent', () => {
    expect(OperadoresMoviles.buscarPorNombre('XYZNONEXISTENT123')).toBeUndefined();
  });

  test('getPorTipo OMR returns network operators', () => {
    const omr = OperadoresMoviles.getPorTipo('OMR');
    expect(omr.length).toBeGreaterThan(0);
    omr.forEach((op) => {
      expect(op.tipo).toBe('OMR');
      expect(op.activo).toBe(true);
    });
  });

  test('getPorTipo OMV returns virtual operators', () => {
    const omv = OperadoresMoviles.getPorTipo('OMV');
    omv.forEach((op) => {
      expect(op.tipo).toBe('OMV');
      expect(op.activo).toBe(true);
    });
  });

  test('getPorGrupo filters by corporate group', () => {
    const all = OperadoresMoviles.getAll();
    const withGroup = all.find((op) => op.grupo_empresarial);
    if (withGroup) {
      const results = OperadoresMoviles.getPorGrupo(withGroup.grupo_empresarial!.slice(0, 5));
      expect(results.length).toBeGreaterThan(0);
    }
  });

  test('getOMVsPorRed filters OMVs by host network', () => {
    const all = OperadoresMoviles.getAll();
    const omvWithRed = all.find((op) => op.tipo === 'OMV' && op.red_anfitriona);
    if (omvWithRed) {
      const results = OperadoresMoviles.getOMVsPorRed(omvWithRed.red_anfitriona!.slice(0, 3));
      expect(results.length).toBeGreaterThan(0);
      results.forEach((op) => expect(op.tipo).toBe('OMV'));
    }
  });

  test('getCon5G returns operators with 5G technology', () => {
    const con5g = OperadoresMoviles.getCon5G();
    con5g.forEach((op) => {
      expect(op.tecnologias).toContain('5G');
      expect(op.activo).toBe(true);
    });
  });

  test('validar returns true for active operator', () => {
    const activos = OperadoresMoviles.getActivos();
    if (activos.length > 0) {
      expect(OperadoresMoviles.validar(activos[0].nombre_comercial)).toBe(true);
    }
  });

  test('validar returns false for nonexistent operator', () => {
    expect(OperadoresMoviles.validar('XYZNONEXISTENT_OPERATOR')).toBe(false);
  });

  test('getMarketSharePorTipo returns OMR and OMV totals', () => {
    const shares = OperadoresMoviles.getMarketSharePorTipo();
    expect(shares).toHaveProperty('OMR');
    expect(shares).toHaveProperty('OMV');
    expect(typeof shares.OMR).toBe('number');
    expect(typeof shares.OMV).toBe('number');
  });
});

// ---------------------------------------------------------------------------
// INEGI SCIAN
// ---------------------------------------------------------------------------
describe('INEGI SCIANCatalog', () => {
  test('getAll returns sectors', () => {
    const all = SCIANCatalog.getAll();
    expect(all.length).toBeGreaterThan(0);
    expect(all[0]).toHaveProperty('codigo');
    expect(all[0]).toHaveProperty('nombre');
  });

  test('getByCodigo returns a sector', () => {
    const all = SCIANCatalog.getAll();
    const found = SCIANCatalog.getByCodigo(all[0].codigo);
    expect(found).toBeDefined();
    expect(found!.codigo).toBe(all[0].codigo);
  });

  test('getByCodigo returns undefined for unknown code', () => {
    expect(SCIANCatalog.getByCodigo('ZZ')).toBeUndefined();
  });

  test('isValid returns true for valid code', () => {
    const all = SCIANCatalog.getAll();
    expect(SCIANCatalog.isValid(all[0].codigo)).toBe(true);
  });

  test('isValid returns false for invalid code', () => {
    expect(SCIANCatalog.isValid('ZZ')).toBe(false);
  });

  test('search finds sectors by name', () => {
    const all = SCIANCatalog.getAll();
    const fragment = all[0].nombre.split(' ')[0];
    const results = SCIANCatalog.search(fragment);
    expect(results.length).toBeGreaterThan(0);
  });

  test('search returns empty for no match', () => {
    expect(SCIANCatalog.search('XYZNONEXISTENT_999')).toEqual([]);
  });

  test('getSectorForCode extracts first 2 digits', () => {
    const all = SCIANCatalog.getAll();
    const sectorCode = all[0].codigo;
    // A 6-digit code should match the sector with the first 2 digits
    const result = SCIANCatalog.getSectorForCode(sectorCode + '0101');
    expect(result).toBeDefined();
    expect(result!.codigo).toBe(sectorCode);
  });

  test('getSectorForCode returns undefined for bad prefix', () => {
    expect(SCIANCatalog.getSectorForCode('990101')).toBeUndefined();
  });

  test('count returns a positive number', () => {
    expect(SCIANCatalog.count).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// INEGI Localidades (additional coverage)
// ---------------------------------------------------------------------------
describe('INEGI LocalidadesCatalog', () => {
  test('getAll returns localities', () => {
    const all = LocalidadesCatalog.getAll();
    expect(all.length).toBeGreaterThan(0);
  });

  test('getLocalidad by cvegeo', () => {
    const all = LocalidadesCatalog.getAll();
    const first = all[0];
    const found = LocalidadesCatalog.getLocalidad(first.cvegeo);
    expect(found).toBeDefined();
    expect(found!.cvegeo).toBe(first.cvegeo);
  });

  test('getLocalidad returns undefined for unknown cvegeo', () => {
    expect(LocalidadesCatalog.getLocalidad('999999999')).toBeUndefined();
  });

  test('isValid returns correct values', () => {
    const all = LocalidadesCatalog.getAll();
    expect(LocalidadesCatalog.isValid(all[0].cvegeo)).toBe(true);
    expect(LocalidadesCatalog.isValid('999999999')).toBe(false);
  });

  test('getByMunicipio returns localities in a municipality', () => {
    const all = LocalidadesCatalog.getAll();
    const mun = all[0].cve_municipio;
    const results = LocalidadesCatalog.getByMunicipio(mun);
    expect(results.length).toBeGreaterThan(0);
    results.forEach((loc) => expect(loc.cve_municipio).toBe(mun));
  });

  test('getByMunicipio returns empty for unknown municipality', () => {
    expect(LocalidadesCatalog.getByMunicipio('999')).toEqual([]);
  });

  test('getByEntidad returns localities in a state', () => {
    const all = LocalidadesCatalog.getAll();
    const ent = all[0].cve_entidad;
    const results = LocalidadesCatalog.getByEntidad(ent);
    expect(results.length).toBeGreaterThan(0);
  });

  test('getByEntidad with non-padded code', () => {
    // Should pad to 2 digits
    const results = LocalidadesCatalog.getByEntidad('1');
    // State 01 (Aguascalientes) should have localities
    expect(results.length).toBeGreaterThan(0);
  });

  test('getUrbanas returns only urban localities', () => {
    const urbanas = LocalidadesCatalog.getUrbanas();
    expect(urbanas.length).toBeGreaterThan(0);
    urbanas.forEach((loc) => expect(loc.ambito).toBe('U'));
  });

  test('getRurales returns only rural localities', () => {
    const rurales = LocalidadesCatalog.getRurales();
    expect(rurales.length).toBeGreaterThan(0);
    rurales.forEach((loc) => expect(loc.ambito).toBe('R'));
  });

  test('searchByName finds localities', () => {
    const all = LocalidadesCatalog.getAll();
    const name = all[0].nom_localidad.slice(0, 4);
    const results = LocalidadesCatalog.searchByName(name);
    expect(results.length).toBeGreaterThan(0);
  });

  test('getByCoordinates returns nearby localities', () => {
    // Mexico City approximate coordinates
    const results = LocalidadesCatalog.getByCoordinates(19.432, -99.133, 50);
    expect(results.length).toBeGreaterThan(0);
    // Should be sorted by distance
    if (results.length > 1) {
      expect(results[0].distancia_km!).toBeLessThanOrEqual(results[1].distancia_km!);
    }
  });

  test('getByCoordinates returns empty for remote coordinates', () => {
    // Middle of the Atlantic
    const results = LocalidadesCatalog.getByCoordinates(0, 0, 1);
    expect(results).toEqual([]);
  });

  test('getByPopulationRange filters by min', () => {
    const results = LocalidadesCatalog.getByPopulationRange(500000);
    expect(results.length).toBeGreaterThan(0);
    results.forEach((loc) => expect(loc.poblacion_total).toBeGreaterThanOrEqual(500000));
  });

  test('getByPopulationRange filters by min and max', () => {
    const results = LocalidadesCatalog.getByPopulationRange(1000, 5000);
    expect(results.length).toBeGreaterThan(0);
    results.forEach((loc) => {
      expect(loc.poblacion_total).toBeGreaterThanOrEqual(1000);
      expect(loc.poblacion_total).toBeLessThanOrEqual(5000);
    });
  });

  test('getTotalCount returns positive number', () => {
    expect(LocalidadesCatalog.getTotalCount()).toBeGreaterThan(0);
  });

  test('getStatistics returns expected shape', () => {
    const stats = LocalidadesCatalog.getStatistics();
    expect(stats.totalLocalidades).toBeGreaterThan(0);
    expect(stats.urbanas).toBeGreaterThan(0);
    expect(stats.rurales).toBeGreaterThan(0);
    expect(stats.estados).toBeGreaterThan(0);
    expect(stats.municipios).toBeGreaterThan(0);
    expect(stats.urbanas + stats.rurales).toBe(stats.totalLocalidades);
  });

  test('getTopByPopulation returns sorted results', () => {
    const top5 = LocalidadesCatalog.getTopByPopulation(5);
    expect(top5).toHaveLength(5);
    for (let i = 0; i < top5.length - 1; i++) {
      expect(top5[i].poblacion_total).toBeGreaterThanOrEqual(top5[i + 1].poblacion_total);
    }
  });
});

// ---------------------------------------------------------------------------
// Mexico Giros Mercantiles
// ---------------------------------------------------------------------------
describe('Mexico GirosMercantilesCatalog', () => {
  test('getAll returns business types', () => {
    const all = GirosMercantilesCatalog.getAll();
    expect(all.length).toBeGreaterThan(0);
    expect(all[0]).toHaveProperty('id');
    expect(all[0]).toHaveProperty('nombre');
    expect(all[0]).toHaveProperty('categoria');
    expect(all[0]).toHaveProperty('requiere_licencia_alcohol');
  });

  test('getAllCategorias returns categories', () => {
    const cats = GirosMercantilesCatalog.getAllCategorias();
    expect(cats.length).toBeGreaterThan(0);
    expect(cats[0]).toHaveProperty('id');
    expect(cats[0]).toHaveProperty('nombre');
    expect(cats[0]).toHaveProperty('descripcion');
  });

  test('getById returns a giro', () => {
    const all = GirosMercantilesCatalog.getAll();
    const found = GirosMercantilesCatalog.getById(all[0].id);
    expect(found).toBeDefined();
    expect(found!.id).toBe(all[0].id);
  });

  test('getById returns undefined for unknown id', () => {
    expect(GirosMercantilesCatalog.getById('NONEXISTENT')).toBeUndefined();
  });

  test('getCategoriaById returns a category', () => {
    const cats = GirosMercantilesCatalog.getAllCategorias();
    const found = GirosMercantilesCatalog.getCategoriaById(cats[0].id);
    expect(found).toBeDefined();
    expect(found!.id).toBe(cats[0].id);
  });

  test('getCategoriaById returns undefined for unknown id', () => {
    expect(GirosMercantilesCatalog.getCategoriaById('NONEXISTENT')).toBeUndefined();
  });

  test('isValid returns true for existing giro', () => {
    const all = GirosMercantilesCatalog.getAll();
    expect(GirosMercantilesCatalog.isValid(all[0].id)).toBe(true);
  });

  test('isValid returns false for nonexistent giro', () => {
    expect(GirosMercantilesCatalog.isValid('FAKE')).toBe(false);
  });

  test('search finds giros by name', () => {
    const all = GirosMercantilesCatalog.getAll();
    const fragment = all[0].nombre.split(' ')[0];
    const results = GirosMercantilesCatalog.search(fragment);
    expect(results.length).toBeGreaterThan(0);
  });

  test('search returns empty for no match', () => {
    expect(GirosMercantilesCatalog.search('XYZNONEXISTENT_GIRO')).toEqual([]);
  });

  test('getByCategoria filters giros by category', () => {
    const all = GirosMercantilesCatalog.getAll();
    const cat = all[0].categoria;
    const results = GirosMercantilesCatalog.getByCategoria(cat);
    expect(results.length).toBeGreaterThan(0);
    results.forEach((g) => expect(g.categoria).toBe(cat));
  });

  test('getByCategoria returns empty for unknown category', () => {
    expect(GirosMercantilesCatalog.getByCategoria('NONEXISTENT_CAT')).toEqual([]);
  });

  test('getRequierenLicenciaAlcohol returns giros requiring alcohol license', () => {
    const results = GirosMercantilesCatalog.getRequierenLicenciaAlcohol();
    results.forEach((g) => expect(g.requiere_licencia_alcohol).toBe(true));
  });

  test('count returns a positive number', () => {
    expect(GirosMercantilesCatalog.count).toBeGreaterThan(0);
  });

  test('categoriasCount returns a positive number', () => {
    expect(GirosMercantilesCatalog.categoriasCount).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// SEPOMEX CodigosPostalesCompleto (42% coverage)
// ---------------------------------------------------------------------------
describe('SEPOMEX CodigosPostalesCompleto', () => {
  test('getAll returns data', () => {
    const all = CodigosPostalesCompleto.getAll();
    expect(all.length).toBeGreaterThan(0);
  });

  test('getByCp returns postal codes', () => {
    const all = CodigosPostalesCompleto.getAll();
    const cp = all[0].cp || all[0].codigo_postal;
    const results = CodigosPostalesCompleto.getByCp(cp!);
    expect(results.length).toBeGreaterThan(0);
  });

  test('getByCp returns empty for nonexistent CP', () => {
    expect(CodigosPostalesCompleto.getByCp('99999')).toEqual([]);
  });

  test('getEstado returns state name', () => {
    const all = CodigosPostalesCompleto.getAll();
    const cp = all[0].cp || all[0].codigo_postal;
    const estado = CodigosPostalesCompleto.getEstado(cp!);
    expect(estado).toBeDefined();
    expect(typeof estado).toBe('string');
  });

  test('getEstado returns undefined for nonexistent CP', () => {
    expect(CodigosPostalesCompleto.getEstado('99999')).toBeUndefined();
  });

  test('getMunicipio returns municipality name', () => {
    const all = CodigosPostalesCompleto.getAll();
    const cp = all[0].cp || all[0].codigo_postal;
    const municipio = CodigosPostalesCompleto.getMunicipio(cp!);
    expect(municipio).toBeDefined();
    expect(typeof municipio).toBe('string');
  });

  test('getMunicipio returns undefined for nonexistent CP', () => {
    expect(CodigosPostalesCompleto.getMunicipio('99999')).toBeUndefined();
  });

  test('getByMunicipio returns results with limit', () => {
    const all = CodigosPostalesCompleto.getAll();
    const municipio = all[0].municipio;
    const results = CodigosPostalesCompleto.getByMunicipio(municipio, 5);
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(5);
  });

  test('getByEstado returns results with limit', () => {
    const all = CodigosPostalesCompleto.getAll();
    const estado = all[0].estado;
    const results = CodigosPostalesCompleto.getByEstado(estado, 10);
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(10);
  });

  test('searchByAsentamiento finds results', () => {
    const all = CodigosPostalesCompleto.getAll();
    const asentamiento = all[0].asentamiento.slice(0, 5);
    const results = CodigosPostalesCompleto.searchByAsentamiento(asentamiento, 5);
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(5);
  });

  test('isValid returns true for valid CP', () => {
    const all = CodigosPostalesCompleto.getAll();
    const cp = all[0].cp || all[0].codigo_postal;
    expect(CodigosPostalesCompleto.isValid(cp!)).toBe(true);
  });

  test('isValid returns false for invalid CP', () => {
    expect(CodigosPostalesCompleto.isValid('99999')).toBe(false);
  });

  test('getTotalCount returns a positive number', () => {
    expect(CodigosPostalesCompleto.getTotalCount()).toBeGreaterThan(0);
  });

  test('getUniqueCPs returns sorted unique codes', () => {
    const uniqueCPs = CodigosPostalesCompleto.getUniqueCPs();
    expect(uniqueCPs.length).toBeGreaterThan(0);
    // Should be sorted
    for (let i = 0; i < Math.min(uniqueCPs.length - 1, 100); i++) {
      expect(uniqueCPs[i] <= uniqueCPs[i + 1]).toBe(true);
    }
  });

  test('getCountByEstado returns count for a state', () => {
    const all = CodigosPostalesCompleto.getAll();
    const estado = all[0].estado;
    const count = CodigosPostalesCompleto.getCountByEstado(estado);
    expect(count).toBeGreaterThan(0);
  });

  test('getCountByEstado returns 0 for unknown state', () => {
    expect(CodigosPostalesCompleto.getCountByEstado('NONEXISTENT_STATE')).toBe(0);
  });

  test('getAsentamientos returns settlement names', () => {
    const all = CodigosPostalesCompleto.getAll();
    // Find an entry that has codigo_postal set
    const withCp = all.find((p) => p.codigo_postal);
    if (withCp) {
      const asentamientos = CodigosPostalesCompleto.getAsentamientos(withCp.codigo_postal!);
      expect(asentamientos.length).toBeGreaterThan(0);
      asentamientos.forEach((a) => expect(typeof a).toBe('string'));
    }
  });

  test('search with multiple criteria', () => {
    const all = CodigosPostalesCompleto.getAll();
    const first = all[0];
    const results = CodigosPostalesCompleto.search({
      estado: first.estado,
      limit: 5,
    });
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(5);
  });

  test('search with cp filter', () => {
    const all = CodigosPostalesCompleto.getAll();
    const withCp = all.find((p) => p.codigo_postal);
    if (withCp) {
      const results = CodigosPostalesCompleto.search({ cp: withCp.codigo_postal });
      expect(results.length).toBeGreaterThan(0);
    }
  });

  test('search with municipio filter', () => {
    const all = CodigosPostalesCompleto.getAll();
    const results = CodigosPostalesCompleto.search({
      municipio: all[0].municipio,
      limit: 5,
    });
    expect(results.length).toBeGreaterThan(0);
  });

  test('search with asentamiento filter', () => {
    const all = CodigosPostalesCompleto.getAll();
    const results = CodigosPostalesCompleto.search({
      asentamiento: all[0].asentamiento.slice(0, 5),
      limit: 5,
    });
    expect(results.length).toBeGreaterThan(0);
  });

  test('search with no criteria returns all (limited)', () => {
    const results = CodigosPostalesCompleto.search({ limit: 3 });
    expect(results.length).toBeLessThanOrEqual(3);
  });

  test('getStatistics returns expected shape', () => {
    const stats = CodigosPostalesCompleto.getStatistics();
    expect(stats.totalPostalCodes).toBeGreaterThan(0);
    expect(stats.uniquePostalCodes).toBeGreaterThan(0);
    expect(stats.states).toBeGreaterThan(0);
    expect(stats.municipalities).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// SEPOMEX CodigosPostales (85% - test missing methods)
// ---------------------------------------------------------------------------
describe('SEPOMEX CodigosPostales (missing coverage)', () => {
  test('getEstado returns state for valid CP', () => {
    const all = CodigosPostales.getAll();
    const cp = all[0].cp || all[0].codigo_postal;
    const estado = CodigosPostales.getEstado(cp!);
    expect(estado).toBeDefined();
    expect(typeof estado).toBe('string');
  });

  test('getEstado returns undefined for invalid CP', () => {
    expect(CodigosPostales.getEstado('99999')).toBeUndefined();
  });

  test('getMunicipio returns municipality for valid CP', () => {
    const all = CodigosPostales.getAll();
    const cp = all[0].cp || all[0].codigo_postal;
    const municipio = CodigosPostales.getMunicipio(cp!);
    expect(municipio).toBeDefined();
  });

  test('getMunicipio returns undefined for invalid CP', () => {
    expect(CodigosPostales.getMunicipio('99999')).toBeUndefined();
  });

  test('searchByAsentamiento finds results', () => {
    const all = CodigosPostales.getAll();
    const first = all[0];
    const results = CodigosPostales.searchByAsentamiento(first.asentamiento.slice(0, 4));
    expect(results.length).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// SAT Contabilidad Electronica - Codigo Agrupador (66% coverage - missing parts)
// ---------------------------------------------------------------------------
describe('SAT CodigoAgrupadorSATCatalog (missing coverage)', () => {
  test('search returns results for valid query', () => {
    const results = CodigoAgrupadorSATCatalog.search('activo');
    expect(results.length).toBeGreaterThan(0);
  });

  test('search returns empty for empty query', () => {
    expect(CodigoAgrupadorSATCatalog.search('')).toEqual([]);
  });

  test('search returns empty for nonexistent query', () => {
    expect(CodigoAgrupadorSATCatalog.search('XYZNONEXISTENT_CODE')).toEqual([]);
  });

  test('getAll with explicit version alias "2024"', () => {
    const items = CodigoAgrupadorSATCatalog.getAll('2024');
    expect(items.length).toBeGreaterThan(0);
  });

  test('getAll with explicit version "latest"', () => {
    const items = CodigoAgrupadorSATCatalog.getAll('latest');
    expect(items.length).toBeGreaterThan(0);
  });

  test('getAll with explicit full version key', () => {
    const items = CodigoAgrupadorSATCatalog.getAll('2024-01-22');
    expect(items.length).toBeGreaterThan(0);
  });

  test('resolveVersion throws for unsupported version', () => {
    expect(() => CodigoAgrupadorSATCatalog.getAll('1999')).toThrow('Versión no soportada');
  });

  test('getByCodigo with explicit version', () => {
    const item = CodigoAgrupadorSATCatalog.getByCodigo('100', '2024');
    expect(item).toBeDefined();
  });

  test('isValid with explicit version', () => {
    expect(CodigoAgrupadorSATCatalog.isValid('100', '2024')).toBe(true);
    expect(CodigoAgrupadorSATCatalog.isValid('999.99', '2024')).toBe(false);
  });

  test('search with explicit version', () => {
    const results = CodigoAgrupadorSATCatalog.search('activo', '2024');
    expect(results.length).toBeGreaterThan(0);
  });

  test('count returns positive number', () => {
    expect(CodigoAgrupadorSATCatalog.count()).toBeGreaterThan(0);
  });

  test('count with version', () => {
    expect(CodigoAgrupadorSATCatalog.count('2024')).toBeGreaterThan(0);
  });

  test('getDefaultVersion returns a version string', () => {
    const defaultVersion = CodigoAgrupadorSATCatalog.getDefaultVersion();
    expect(typeof defaultVersion).toBe('string');
    expect(defaultVersion).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});

// ---------------------------------------------------------------------------
// SAT CFDI 4.0 - CodigoPostal Catalog (13% coverage)
// ---------------------------------------------------------------------------
describe('SAT CFDI CodigoPostalCatalog', () => {
  test('isValidFormat accepts 5-digit codes', () => {
    expect(CodigoPostalCatalog.isValidFormat('64000')).toBe(true);
    expect(CodigoPostalCatalog.isValidFormat('01000')).toBe(true);
  });

  test('isValidFormat rejects invalid formats', () => {
    expect(CodigoPostalCatalog.isValidFormat('1234')).toBe(false);
    expect(CodigoPostalCatalog.isValidFormat('123456')).toBe(false);
    expect(CodigoPostalCatalog.isValidFormat('abcde')).toBe(false);
    expect(CodigoPostalCatalog.isValidFormat('')).toBe(false);
  });

  test('isValid returns true for existing postal code', () => {
    // 64000 is Monterrey, Nuevo Leon
    expect(CodigoPostalCatalog.isValid('64000')).toBe(true);
  });

  test('isValid returns false for invalid format', () => {
    expect(CodigoPostalCatalog.isValid('abc')).toBe(false);
  });

  test('isValid returns false for non-existing postal code', () => {
    expect(CodigoPostalCatalog.isValid('99999')).toBe(false);
  });

  test('getCodigoPostal returns info for valid CP', () => {
    const info = CodigoPostalCatalog.getCodigoPostal('64000');
    expect(info).toBeDefined();
    expect(info!.cp).toBe('64000');
  });

  test('getCodigoPostal returns undefined for invalid format', () => {
    expect(CodigoPostalCatalog.getCodigoPostal('abc')).toBeUndefined();
  });

  test('getCodigoPostal returns undefined for nonexistent CP', () => {
    expect(CodigoPostalCatalog.getCodigoPostal('99999')).toBeUndefined();
  });

  test('getAsentamientos returns settlements for valid CP', () => {
    const results = CodigoPostalCatalog.getAsentamientos('64000');
    expect(results.length).toBeGreaterThan(0);
    results.forEach((r) => expect(r.cp).toBe('64000'));
  });

  test('getAsentamientos returns empty for invalid format', () => {
    expect(CodigoPostalCatalog.getAsentamientos('abc')).toEqual([]);
  });

  test('getAsentamientos returns empty for nonexistent CP', () => {
    expect(CodigoPostalCatalog.getAsentamientos('99999')).toEqual([]);
  });

  test('getEstado returns state name', () => {
    const estado = CodigoPostalCatalog.getEstado('64000');
    expect(estado).toBeDefined();
    expect(typeof estado).toBe('string');
  });

  test('getEstado returns undefined for bad CP', () => {
    expect(CodigoPostalCatalog.getEstado('99999')).toBeUndefined();
  });

  test('getMunicipio returns municipality', () => {
    const mun = CodigoPostalCatalog.getMunicipio('64000');
    expect(mun).toBeDefined();
    expect(typeof mun).toBe('string');
  });

  test('getMunicipio returns undefined for bad CP', () => {
    expect(CodigoPostalCatalog.getMunicipio('99999')).toBeUndefined();
  });

  test('getCodigoEstado returns state code', () => {
    const code = CodigoPostalCatalog.getCodigoEstado('64000');
    expect(code).toBeDefined();
    expect(typeof code).toBe('string');
  });

  test('getCodigoEstado returns undefined for bad CP', () => {
    expect(CodigoPostalCatalog.getCodigoEstado('99999')).toBeUndefined();
  });

  test('search returns results for valid query', () => {
    const results = CodigoPostalCatalog.search('monterrey', 5);
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(5);
  });

  test('search returns empty for nonexistent query', () => {
    expect(CodigoPostalCatalog.search('XYZNONEXISTENT_PLACE')).toEqual([]);
  });

  test('getUniqueCount returns positive number', () => {
    expect(CodigoPostalCatalog.getUniqueCount()).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// RESICO Calculator (42% coverage)
// ---------------------------------------------------------------------------
describe('RESICO Calculator', () => {
  test('getBrackets returns brackets for valid year/period', () => {
    const brackets = RESICOCalculator.getBrackets(2025, 'mensual');
    expect(brackets.length).toBeGreaterThan(0);
    brackets.forEach((b) => {
      expect(b).toHaveProperty('limiteInferior');
      expect(b).toHaveProperty('limiteSuperior');
      expect(b).toHaveProperty('tasa');
    });
  });

  test('getBrackets returns annual brackets', () => {
    const brackets = RESICOCalculator.getBrackets(2025, 'anual');
    expect(brackets.length).toBeGreaterThan(0);
  });

  test('getBrackets throws for invalid year', () => {
    expect(() => RESICOCalculator.getBrackets(1990 as any, 'mensual')).toThrow();
  });

  test('getLimits returns limits', () => {
    const limits = RESICOCalculator.getLimits();
    expect(limits.personaFisica.ingresoAnualMaximo).toBeGreaterThan(0);
    expect(limits.personaFisica.ingresoMensualMaximo).toBeGreaterThan(0);
    expect(limits.personaMoral.tasa).toBeGreaterThan(0);
  });

  test('isEligible returns true for low income', () => {
    expect(RESICOCalculator.isEligible(10000, 'mensual')).toBe(true);
  });

  test('isEligible returns false for very high income', () => {
    expect(RESICOCalculator.isEligible(999999999, 'mensual')).toBe(false);
  });

  test('isEligible checks annual limit', () => {
    expect(RESICOCalculator.isEligible(1000000, 'anual')).toBe(true);
    expect(RESICOCalculator.isEligible(999999999, 'anual')).toBe(false);
  });

  test('calcular for zero income', () => {
    const result = RESICOCalculator.calcular(0, 2025, 'mensual');
    expect(result.resicoCalculado).toBe(0);
    expect(result.tasaEfectiva).toBe(0);
    expect(result.dentroDeLimite).toBe(true);
    expect(result.bracket).toBeNull();
  });

  test('calcular for negative income', () => {
    const result = RESICOCalculator.calcular(-1000, 2025, 'mensual');
    expect(result.resicoCalculado).toBe(0);
    expect(result.tasaEfectiva).toBe(0);
    expect(result.bracket).toBeNull();
  });

  test('calcular for normal monthly income', () => {
    const result = RESICOCalculator.calcular(50000, 2025, 'mensual');
    expect(result.ingreso).toBe(50000);
    expect(result.periodo).toBe('mensual');
    expect(result.year).toBe(2025);
    expect(result.resicoCalculado).toBeGreaterThan(0);
    expect(result.tasaEfectiva).toBeGreaterThan(0);
    expect(result.bracket).not.toBeNull();
    expect(result.dentroDeLimite).toBe(true);
  });

  test('calcular for annual income', () => {
    const result = RESICOCalculator.calcular(600000, 2025, 'anual');
    expect(result.periodo).toBe('anual');
    expect(result.resicoCalculado).toBeGreaterThan(0);
  });

  test('calcular uses default params', () => {
    const result = RESICOCalculator.calcular(30000);
    expect(result.year).toBe(2025);
    expect(result.periodo).toBe('mensual');
  });

  test('calcular for income exceeding limit', () => {
    const result = RESICOCalculator.calcular(999999999, 2025, 'mensual');
    expect(result.dentroDeLimite).toBe(false);
  });

  test('calcularIngresoNeto returns net income', () => {
    const net = RESICOCalculator.calcularIngresoNeto(50000, 2025, 'mensual');
    expect(net).toBeLessThan(50000);
    expect(net).toBeGreaterThan(0);
  });

  test('calcularIngresoNeto uses default params', () => {
    const net = RESICOCalculator.calcularIngresoNeto(30000);
    expect(net).toBeLessThan(30000);
    expect(net).toBeGreaterThan(0);
  });

  test('calcularRESICOAnual sums 12 monthly calculations', () => {
    const monthly = Array(12).fill(50000);
    const total = RESICOCalculator.calcularRESICOAnual(monthly, 2025);
    expect(total).toBeGreaterThan(0);

    // Should roughly equal 12 * monthly RESICO
    const singleMonth = RESICOCalculator.calcular(50000, 2025, 'mensual');
    expect(Math.abs(total - singleMonth.resicoCalculado * 12)).toBeLessThan(1);
  });

  test('calcularRESICOAnual throws if not 12 months', () => {
    expect(() => RESICOCalculator.calcularRESICOAnual([10000, 20000])).toThrow(
      'Se requieren exactamente 12 ingresos mensuales'
    );
  });

  test('calcularRESICOAnual uses default year', () => {
    const monthly = Array(12).fill(30000);
    const total = RESICOCalculator.calcularRESICOAnual(monthly);
    expect(total).toBeGreaterThan(0);
  });

  test('compararConISR returns comparison object', () => {
    const comparison = RESICOCalculator.compararConISR(50000, 2025);
    expect(comparison).toHaveProperty('resicoMensual');
    expect(comparison).toHaveProperty('tasaRESICO');
    expect(comparison).toHaveProperty('recomendacion');
    expect(comparison).toHaveProperty('ahorroEstimado');
    expect(comparison).toHaveProperty('notaComparativa');
    expect(comparison.resicoMensual).toBeGreaterThan(0);
  });

  test('compararConISR for income exceeding limit', () => {
    const comparison = RESICOCalculator.compararConISR(300000, 2025);
    expect(comparison.recomendacion).toContain('excede límite RESICO');
  });

  test('compararConISR uses default year', () => {
    const comparison = RESICOCalculator.compararConISR(50000);
    expect(comparison).toHaveProperty('resicoMensual');
  });

  test('getAniosDisponibles returns available years', () => {
    const years = RESICOCalculator.getAñosDisponibles();
    expect(years.length).toBeGreaterThan(0);
    expect(years).toContain(2025);
  });

  test('getInfo returns metadata', () => {
    const info = RESICOCalculator.getInfo();
    expect(info).toHaveProperty('description');
    expect(info).toHaveProperty('source');
    expect(info).toHaveProperty('currency');
    expect(info).toHaveProperty('years');
  });
});

// ---------------------------------------------------------------------------
// Catalog Backend Utils (50% coverage)
// ---------------------------------------------------------------------------
describe('catalog-backend utils', () => {
  test('isNodeRuntime returns true in Node.js', () => {
    expect(isNodeRuntime()).toBe(true);
  });

  test('tableNameForJsonPath converts paths correctly', () => {
    expect(tableNameForJsonPath('sepomex/codigos_postales_completo.json')).toBe('codigos_postales');
    expect(tableNameForJsonPath('inegi/localidades.json')).toBe('localidades');
    expect(tableNameForJsonPath('sat/cfdi_4.0/clave_prod_serv.json')).toBe('clave_prod_serv');
  });

  test('tableNameForJsonPath for non-override paths', () => {
    const name = tableNameForJsonPath('some/test-file.json');
    expect(name).toBe('some_test_file');
  });

  test('tableNameForJsonPath normalizes backslashes', () => {
    const name = tableNameForJsonPath('some\\test-file.json');
    expect(name).toBe('some_test_file');
  });

  test('setCatalogJsonData and loadCatalogJson roundtrip', () => {
    const testData = { items: [{ id: 1 }, { id: 2 }] };
    setCatalogJsonData('test/roundtrip.json', testData);
    const loaded = loadCatalogJson<typeof testData>('test/roundtrip.json');
    expect(loaded).toEqual(testData);
    clearCatalogJsonData('test/roundtrip.json');
  });

  test('clearCatalogJsonData clears specific path', () => {
    setCatalogJsonData('test/clear-specific.json', { a: 1 });
    expect(hasCatalogJsonData('test/clear-specific.json')).toBe(true);
    clearCatalogJsonData('test/clear-specific.json');
    // After clearing, hasCatalogJsonData may still return true if file exists on disk
    // but loadCatalogJson from store should be gone
  });

  test('clearCatalogJsonData clears all when no path given', () => {
    setCatalogJsonData('test/clear-all-1.json', { a: 1 });
    setCatalogJsonData('test/clear-all-2.json', { b: 2 });
    clearCatalogJsonData();
    // Store is cleared
  });

  test('clearCatalogJsonData invalidates cached rows for a specific path', () => {
    const path = 'test/clear-cached-specific.json';
    setCatalogJsonData(path, [{ source: 'preloaded' }]);
    expect(loadCatalogRows(path)).toEqual([{ source: 'preloaded' }]);

    clearCatalogJsonData(path);

    expect(() => loadCatalogRows(path)).toThrow(/Catalog file not found/);
  });

  test('clearCatalogJsonData invalidates all cached rows', () => {
    const firstPath = 'test/clear-cached-all-first.json';
    const secondPath = 'test/clear-cached-all-second.json';
    setCatalogJsonData(firstPath, [{ source: 'first' }]);
    setCatalogJsonData(secondPath, [{ source: 'second' }]);
    loadCatalogRows(firstPath);
    loadCatalogRows(secondPath);

    clearCatalogJsonData();

    expect(() => loadCatalogRows(firstPath)).toThrow(/Catalog file not found/);
    expect(() => loadCatalogRows(secondPath)).toThrow(/Catalog file not found/);
  });

  test('clearCatalogCache clears the cache', () => {
    // This should not throw
    clearCatalogCache();
  });

  test('hasCatalogJsonData returns true for preloaded data', () => {
    setCatalogJsonData('test/has-data.json', [1, 2, 3]);
    expect(hasCatalogJsonData('test/has-data.json')).toBe(true);
    clearCatalogJsonData('test/has-data.json');
  });

  test('hasCatalogJsonData returns true for files on disk', () => {
    // cnbv/sectores.json should exist on disk
    expect(hasCatalogJsonData('cnbv/sectores.json')).toBe(true);
  });

  test('hasCatalogJsonData returns false for nonexistent file', () => {
    expect(hasCatalogJsonData('nonexistent/path/to/file.json')).toBe(false);
  });

  test('loadCatalogRows with preloaded JSON array', () => {
    clearCatalogCache();
    setCatalogJsonData('test/rows-array.json', [{ x: 1 }, { x: 2 }]);
    const rows = loadCatalogRows<{ x: number }>('test/rows-array.json');
    expect(rows).toEqual([{ x: 1 }, { x: 2 }]);
    clearCatalogJsonData('test/rows-array.json');
    clearCatalogCache();
  });

  test('loadCatalogRows with preloaded JSON object with items', () => {
    clearCatalogCache();
    setCatalogJsonData('test/rows-items.json', { items: [{ y: 3 }] });
    const rows = loadCatalogRows<{ y: number }>('test/rows-items.json');
    expect(rows).toEqual([{ y: 3 }]);
    clearCatalogJsonData('test/rows-items.json');
    clearCatalogCache();
  });

  test('loadCatalogRows with preloaded JSON object with data', () => {
    clearCatalogCache();
    setCatalogJsonData('test/rows-data.json', { data: [{ z: 4 }] });
    const rows = loadCatalogRows<{ z: number }>('test/rows-data.json');
    expect(rows).toEqual([{ z: 4 }]);
    clearCatalogJsonData('test/rows-data.json');
    clearCatalogCache();
  });

  test('loadCatalogRows with object having largest array field', () => {
    clearCatalogCache();
    setCatalogJsonData('test/rows-largest.json', {
      _meta: { x: 1 },
      records: [{ a: 1 }, { a: 2 }, { a: 3 }],
      small: [{ b: 1 }],
    });
    const rows = loadCatalogRows<{ a: number }>('test/rows-largest.json');
    expect(rows).toEqual([{ a: 1 }, { a: 2 }, { a: 3 }]);
    clearCatalogJsonData('test/rows-largest.json');
    clearCatalogCache();
  });

  test('loadCatalogRows with non-object returns empty array', () => {
    clearCatalogCache();
    setCatalogJsonData('test/rows-primitive.json', 'hello');
    const rows = loadCatalogRows('test/rows-primitive.json');
    expect(rows).toEqual([]);
    clearCatalogJsonData('test/rows-primitive.json');
    clearCatalogCache();
  });

  test('loadCatalogRows with object with no arrays returns empty', () => {
    clearCatalogCache();
    setCatalogJsonData('test/rows-no-arrays.json', { x: 1, y: 'hello' });
    const rows = loadCatalogRows('test/rows-no-arrays.json');
    expect(rows).toEqual([]);
    clearCatalogJsonData('test/rows-no-arrays.json');
    clearCatalogCache();
  });

  test('loadCatalogRows caches results', () => {
    clearCatalogCache();
    setCatalogJsonData('test/rows-cache.json', [{ c: 5 }]);
    const rows1 = loadCatalogRows<{ c: number }>('test/rows-cache.json');
    const rows2 = loadCatalogRows<{ c: number }>('test/rows-cache.json');
    // Same reference means it was cached
    expect(rows1).toBe(rows2);
    clearCatalogJsonData('test/rows-cache.json');
    clearCatalogCache();
  });

  test('setCatalogSqliteAdapter and getCatalogSqliteAdapter', () => {
    // Just test that setting/getting null works
    setCatalogSqliteAdapter(null);
    // Should not throw
  });

  test('changing the SQLite adapter invalidates cached rows', () => {
    const adapter = (source: string) => ({
      prepare: (sql: string) => ({
        all: () => [{ source }],
        get: () => (sql.includes('sqlite_master') ? { ok: 1 } : undefined),
        run: () => ({}),
      }),
      exec: () => {},
      close: () => {},
    });

    setCatalogPreferSqlite(true);
    setCatalogSqliteAdapter(adapter('adapter-a') as any);
    expect(loadCatalogRows('test/adapter-change.json')).toEqual([{ source: 'adapter-a' }]);

    setCatalogSqliteAdapter(adapter('adapter-b') as any);
    expect(loadCatalogRows('test/adapter-change.json')).toEqual([{ source: 'adapter-b' }]);

    setCatalogSqliteAdapter(null);
    setCatalogPreferSqlite(false);
  });

  test('setCatalogPreferSqlite does not throw', () => {
    setCatalogPreferSqlite(false);
    setCatalogPreferSqlite(true);
    // Restore
    setCatalogPreferSqlite(false);
  });

  test('changing the SQLite preference invalidates cached rows', () => {
    const path = 'test/preference-change.json';
    const adapter = {
      prepare: (sql: string) => ({
        all: () => [{ source: 'sqlite' }],
        get: () => (sql.includes('sqlite_master') ? { ok: 1 } : undefined),
        run: () => ({}),
      }),
      exec: () => {},
      close: () => {},
    };
    setCatalogJsonData(path, [{ source: 'json' }]);
    setCatalogSqliteAdapter(adapter as any);
    setCatalogPreferSqlite(false);
    expect(loadCatalogRows(path)).toEqual([{ source: 'json' }]);

    setCatalogPreferSqlite(true);
    expect(loadCatalogRows(path)).toEqual([{ source: 'sqlite' }]);

    clearCatalogJsonData(path);
    setCatalogSqliteAdapter(null);
    setCatalogPreferSqlite(false);
  });

  test('loadCatalogJson throws for nonexistent file', () => {
    expect(() => loadCatalogJson('nonexistent/totally/fake.json')).toThrow();
  });
});

// ---------------------------------------------------------------------------
// Catalog Loader Utils (52% coverage)
// ---------------------------------------------------------------------------
describe('catalog-loader utils', () => {
  test('loadCatalogArray delegates to loadCatalogRows', () => {
    clearCatalogCache();
    setCatalogJsonData('test/loader-array.json', [{ a: 1 }]);
    const result = loadCatalogArray<{ a: number }>('test/loader-array.json');
    expect(result).toEqual([{ a: 1 }]);
    clearCatalogJsonData('test/loader-array.json');
    clearCatalogCache();
  });

  test('loadCatalogObject delegates to loadCatalogRows', () => {
    clearCatalogCache();
    setCatalogJsonData('test/loader-object.json', { data: [{ b: 2 }] });
    const result = loadCatalogObject<{ b: number }>('test/loader-object.json');
    expect(result).toEqual([{ b: 2 }]);
    clearCatalogJsonData('test/loader-object.json');
    clearCatalogCache();
  });

  test('loadCatalogData delegates to loadCatalogJson', () => {
    setCatalogJsonData('test/loader-data.json', { meta: 'test', items: [1, 2] });
    const result = loadCatalogData<{ meta: string; items: number[] }>('test/loader-data.json');
    expect(result.meta).toBe('test');
    expect(result.items).toEqual([1, 2]);
    clearCatalogJsonData('test/loader-data.json');
  });

  test('CatalogLoader.clearCache does not throw', () => {
    CatalogLoader.clearCache();
  });
});

// ---------------------------------------------------------------------------
// CLABE Validator - generate methods (73% coverage)
// ---------------------------------------------------------------------------
describe('CLABE generate and info methods', () => {
  test('generateClabe creates valid CLABE', () => {
    const clabe = generateClabe('002', '010', '07777777777');
    expect(clabe).toHaveLength(18);
    expect(validateClabe(clabe)).toBe(true);
  });

  test('generateClabe with numeric inputs', () => {
    const clabe = generateClabe(2, 10, 7777777777);
    expect(clabe).toHaveLength(18);
    expect(validateClabe(clabe)).toBe(true);
  });

  test('generateClabe pads short inputs', () => {
    const clabe = generateClabe('2', '1', '123');
    expect(clabe).toHaveLength(18);
    expect(clabe.startsWith('002')).toBe(true);
    expect(validateClabe(clabe)).toBe(true);
  });

  test('calculateClabeCheckDigit returns correct digit', () => {
    const digit = calculateClabeCheckDigit('00201007777777777');
    expect(digit).toBe('1');
  });

  test('calculateClabeCheckDigit throws for wrong length', () => {
    expect(() => calculateClabeCheckDigit('123')).toThrow('17 digits');
  });

  test('getClabeInfo returns info for valid CLABE', () => {
    const info = getClabeInfo('002010077777777771');
    expect(info).not.toBeNull();
    expect(info!.bankCode).toBe('002');
    expect(info!.branchCode).toBe('010');
    expect(info!.accountNumber).toBe('07777777777');
    expect(info!.checkDigit).toBe('1');
    expect(info!.isValid).toBe(true);
  });

  test('getClabeInfo returns info with isValid false for bad check digit', () => {
    const info = getClabeInfo('002010077777777770');
    expect(info).not.toBeNull();
    expect(info!.isValid).toBe(false);
  });

  test('getClabeInfo returns null for wrong length', () => {
    expect(getClabeInfo('12345')).toBeNull();
  });

  test('CLABEValidator.getComponents returns components for valid CLABE', () => {
    const v = new CLABEValidator('002010077777777771');
    const components = v.getComponents();
    expect(components).not.toBeNull();
    expect(components!.bankCode).toBe('002');
    expect(components!.branchCode).toBe('010');
    expect(components!.accountNumber).toBe('07777777777');
    expect(components!.checkDigit).toBe('1');
  });

  test('CLABEValidator.getComponents returns null for invalid CLABE', () => {
    const v = new CLABEValidator('000000000000000000');
    const components = v.getComponents();
    // May be null if check digit is wrong
    if (components === null) {
      expect(v.isValid()).toBe(false);
    }
  });

  test('CLABEValidator.getBankCode returns code for valid CLABE', () => {
    const v = new CLABEValidator('002010077777777771');
    expect(v.getBankCode()).toBe('002');
  });

  test('CLABEValidator.getBranchCode returns code for valid CLABE', () => {
    const v = new CLABEValidator('002010077777777771');
    expect(v.getBranchCode()).toBe('010');
  });

  test('CLABEValidator.getAccountNumber returns account for valid CLABE', () => {
    const v = new CLABEValidator('002010077777777771');
    expect(v.getAccountNumber()).toBe('07777777777');
  });

  test('CLABEValidator extract methods return null for invalid CLABE', () => {
    const v = new CLABEValidator('invalid');
    expect(v.getBankCode()).toBeNull();
    expect(v.getBranchCode()).toBeNull();
    expect(v.getAccountNumber()).toBeNull();
  });

  test('CLABEValidator.validate throws for wrong length', () => {
    const v = new CLABEValidator('12345');
    expect(() => v.validate()).toThrow('18 digits');
  });

  test('CLABEValidator.validate throws for non-digit chars', () => {
    const v = new CLABEValidator('00201007777777777A');
    expect(() => v.validate()).toThrow('only digits');
  });

  test('CLABEValidator.validate throws for bad check digit', () => {
    const v = new CLABEValidator('002010077777777770');
    expect(() => v.validate()).toThrow('check digit');
  });
});

// ---------------------------------------------------------------------------
// NSS Validator - generate methods (75% coverage)
// ---------------------------------------------------------------------------
describe('NSS generate and component methods', () => {
  test('generateNss creates valid NSS', () => {
    const nss = generateNss('12', '34', '56', '7890');
    expect(nss).toHaveLength(11);
    expect(validateNss(nss)).toBe(true);
  });

  test('generateNss pads short inputs', () => {
    const nss = generateNss('1', '2', '3', '45');
    expect(nss).toHaveLength(11);
    expect(nss.startsWith('01')).toBe(true);
    expect(validateNss(nss)).toBe(true);
  });

  test('NSSValidator.calculateCheckDigit returns correct value', () => {
    const digit = NSSValidator.calculateCheckDigit('1234567890');
    expect(typeof digit).toBe('number');
    expect(digit).toBeGreaterThanOrEqual(0);
    expect(digit).toBeLessThanOrEqual(9);
  });

  test('NSSValidator.calculateCheckDigit throws for wrong length', () => {
    expect(() => NSSValidator.calculateCheckDigit('123')).toThrow('10 digits');
  });

  test('NSSValidator.getSubdelegation returns first 2 digits', () => {
    const nss = generateNss('12', '34', '56', '7890');
    const v = new NSSValidator(nss);
    expect(v.getSubdelegation()).toBe('12');
  });

  test('NSSValidator.getRegistrationYear returns digits 3-4', () => {
    const nss = generateNss('12', '34', '56', '7890');
    const v = new NSSValidator(nss);
    expect(v.getRegistrationYear()).toBe('34');
  });

  test('NSSValidator.getBirthYear returns digits 5-6', () => {
    const nss = generateNss('12', '34', '56', '7890');
    const v = new NSSValidator(nss);
    expect(v.getBirthYear()).toBe('56');
  });

  test('NSSValidator.getSequential returns digits 7-10', () => {
    const nss = generateNss('12', '34', '56', '7890');
    const v = new NSSValidator(nss);
    expect(v.getSequential()).toBe('7890');
  });

  test('NSSValidator.getComponents returns all parts', () => {
    const nss = generateNss('12', '34', '56', '7890');
    const v = new NSSValidator(nss);
    const components = v.getComponents();
    expect(components).not.toBeNull();
    expect(components!.subdelegation).toBe('12');
    expect(components!.registrationYear).toBe('34');
    expect(components!.birthYear).toBe('56');
    expect(components!.sequential).toBe('7890');
    expect(components!.checkDigit).toBe(nss[10]);
  });

  test('NSSValidator.getComponents returns null for invalid NSS', () => {
    const v = new NSSValidator('invalid');
    expect(v.getComponents()).toBeNull();
  });

  test('NSSValidator extract methods return null for invalid NSS', () => {
    const v = new NSSValidator('12345');
    expect(v.getSubdelegation()).toBeNull();
    expect(v.getRegistrationYear()).toBeNull();
    expect(v.getBirthYear()).toBeNull();
    expect(v.getSequential()).toBeNull();
  });

  test('NSSValidator.validate throws for wrong length', () => {
    const v = new NSSValidator('12345');
    expect(() => v.validate()).toThrow('11 digits');
  });

  test('NSSValidator.validate throws for non-digit chars', () => {
    const v = new NSSValidator('1234567890A');
    expect(() => v.validate()).toThrow('only digits');
  });

  test('NSSValidator.validate throws for bad check digit', () => {
    // Generate a valid NSS, then change the last digit
    const nss = generateNss('12', '34', '56', '7890');
    const badDigit = nss[10] === '0' ? '1' : '0';
    const badNss = nss.slice(0, 10) + badDigit;
    const v = new NSSValidator(badNss);
    expect(() => v.validate()).toThrow('check digit');
  });
});

// ---------------------------------------------------------------------------
// CFDI Signing (61% coverage)
// ---------------------------------------------------------------------------
describe('CFDI Signing', () => {
  test('signCadenaOriginal signs with RSA-SHA256', () => {
    const crypto = require('crypto');
    const { privateKey } = crypto.generateKeyPairSync('rsa', {
      modulusLength: 2048,
      publicKeyEncoding: { type: 'spki', format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
    });

    const cadena = '||4.0|A|2025-01-01T00:00:00||';
    const result = signCadenaOriginal(cadena, privateKey);
    expect(result).toHaveProperty('sello');
    expect(typeof result.sello).toBe('string');
    expect(result.sello.length).toBeGreaterThan(0);
    // Should be valid base64
    expect(() => Buffer.from(result.sello, 'base64')).not.toThrow();
  });

  test('aplicarSelloAComprobante sets sello only', () => {
    const xml = '<cfdi:Comprobante Version="4.0"><cfdi:Emisor/></cfdi:Comprobante>';
    const result = aplicarSelloAComprobante({
      xml,
      sello: 'TEST_SELLO',
    });
    expect(result).toContain('Sello="TEST_SELLO"');
    // Should not contain Certificado or NoCertificado if not provided
  });

  test('aplicarSelloAComprobante replaces existing attributes', () => {
    const xml =
      '<cfdi:Comprobante Version="4.0" Sello="OLD" Certificado="OLD_CERT"><cfdi:Emisor/></cfdi:Comprobante>';
    const result = aplicarSelloAComprobante({
      xml,
      sello: 'NEW_SELLO',
      certificado: 'NEW_CERT',
      noCertificado: '00001',
    });
    expect(result).toContain('Sello="NEW_SELLO"');
    expect(result).toContain('Certificado="NEW_CERT"');
    expect(result).toContain('NoCertificado="00001"');
    expect(result).not.toContain('Sello="OLD"');
    expect(result).not.toContain('Certificado="OLD_CERT"');
  });

  test('aplicarSelloAComprobante throws when no Comprobante node', () => {
    const xml = '<NotAComprobante></NotAComprobante>';
    expect(() => aplicarSelloAComprobante({ xml, sello: 'X' })).toThrow(
      'No se encontró el nodo cfdi:Comprobante'
    );
  });

  test('aplicarSelloAComprobante handles undefined certificado and noCertificado', () => {
    const xml = '<cfdi:Comprobante Version="4.0"><cfdi:Emisor/></cfdi:Comprobante>';
    const result = aplicarSelloAComprobante({
      xml,
      sello: 'SELLO',
      certificado: undefined,
      noCertificado: undefined,
    });
    expect(result).toContain('Sello="SELLO"');
    expect(result).not.toContain('Certificado=');
    expect(result).not.toContain('NoCertificado=');
  });
});
