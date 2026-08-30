import { FormaPagoCatalog } from '../src/catalogs/sat/cfdi_4/forma-pago';
import { EstadoCfdiCatalog } from '../src/catalogs/sat/cfdi_4/estado';
import { NominaCfdiCatalog } from '../src/catalogs/sat/cfdi_4/nomina-cfdi';
import { TipoRegimenCatalog } from '../src/catalogs/sat/nomina/tipo-regimen';
import { PaisCatalog } from '../src/catalogs/sat/comercio_exterior/pais';
import { preloadSmallCatalogData } from '../src/catalogs/preload';
import { clearCatalogCache, clearCatalogJsonData } from '../src/utils/catalog-backend';

describe('browser and Worker catalog preload', () => {
  beforeEach(() => {
    clearCatalogCache();
    clearCatalogJsonData();
  });

  test('registers representative Nómina and CFDI catalogs', () => {
    preloadSmallCatalogData();

    expect(TipoRegimenCatalog.isValid('02')).toBe(true);
    expect(FormaPagoCatalog.isValid('03')).toBe(true);
    expect(EstadoCfdiCatalog.isValid('CMX')).toBe(true);
    expect(EstadoCfdiCatalog.getEstado('cmx')).toEqual({ code: 'CMX' });
    expect(PaisCatalog.isValid('MEX')).toBe(true);
    expect(NominaCfdiCatalog.isValidClaveProdServ('84111505')).toBe(true);
    expect(NominaCfdiCatalog.isValidClaveProdServ('84111504')).toBe(false);
  });

  test('catalog rows cannot mutate subsequent Worker reads', () => {
    preloadSmallCatalogData();
    const estado = EstadoCfdiCatalog.getEstado('CMX');
    expect(estado).toBeDefined();

    expect(() => {
      (estado as { code: string }).code = 'MUTATED';
    }).toThrow(TypeError);
    expect(EstadoCfdiCatalog.getEstado('CMX')?.code).toBe('CMX');
  });
});
