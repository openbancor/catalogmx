import { describe, expect, test } from '@jest/globals';
import {
  BancoNominaCatalog,
  OrigenRecursoCatalog,
  PeriodicidadPagoCatalog,
  RiesgoPuestoCatalog,
  TipoContratoCatalog,
  TipoDeduccionCatalog,
  TipoHorasCatalog,
  TipoIncapacidadCatalog,
  TipoJornadaCatalog,
  TipoNominaCatalog,
  TipoOtroPagoCatalog,
  TipoPercepcionCatalog,
  TipoRegimenCatalog,
} from '../src/catalogs';

type SimpleNominaCatalogApi = {
  getAll(): Array<{ code: string }>;
  getByCode(code: string): { code: string } | undefined;
  isValid(code: string): boolean;
};

describe('SAT Nómina 1.2 API parity', () => {
  test('exposes all 13 catalog families', () => {
    const samples: Array<[SimpleNominaCatalogApi, string]> = [
      [OrigenRecursoCatalog, 'IP'],
      [TipoDeduccionCatalog, '115'],
      [TipoHorasCatalog, '01'],
      [TipoIncapacidadCatalog, '04'],
      [TipoOtroPagoCatalog, '999'],
      [TipoPercepcionCatalog, '057'],
    ];
    expect(samples).toHaveLength(6);
    for (const [catalog, code] of samples) {
      expect(catalog.getAll().length).toBeGreaterThan(0);
      expect(catalog.isValid(code)).toBe(true);
      expect(catalog.getByCode(code)?.code).toBe(code);
    }

    expect(BancoNominaCatalog.isValid('002')).toBe(true);
    expect(PeriodicidadPagoCatalog.isValid('04')).toBe(true);
    expect(RiesgoPuestoCatalog.isValid('99')).toBe(true);
    expect(TipoContratoCatalog.isValid('10')).toBe(true);
    expect(TipoJornadaCatalog.isValid('08')).toBe(true);
    expect(TipoNominaCatalog.isValid('O')).toBe(true);
    expect(TipoRegimenCatalog.isValid('13')).toBe(true);
  });

  test('fixed compatibility fields are usable', () => {
    expect(BancoNominaCatalog.getRazonSocial('002')).toBeDefined();
    expect(BancoNominaCatalog.searchByName('Banamex')).not.toHaveLength(0);
    expect(TipoRegimenCatalog.getDescription('02')).toBeDefined();
    expect(TipoContratoCatalog.searchByDescription('indeterminado')).not.toHaveLength(0);
    expect(TipoJornadaCatalog.searchByDescription('turnos')).not.toHaveLength(0);
  });

  test('Revision E edges and risk code 99 behave correctly', () => {
    expect(TipoDeduccionCatalog.isValid('115')).toBe(true);
    expect(TipoPercepcionCatalog.isValid('057')).toBe(true);
    expect(RiesgoPuestoCatalog.getPrimaRange('99')).toBeUndefined();
    expect(RiesgoPuestoCatalog.validatePrima('99', 1)).toBe(false);
    expect(TipoNominaCatalog.isOrdinaria('O')).toBe(true);
    expect(TipoNominaCatalog.isOrdinaria('E')).toBe(false);
    expect(TipoNominaCatalog.isExtraordinaria('E')).toBe(true);
  });
});
