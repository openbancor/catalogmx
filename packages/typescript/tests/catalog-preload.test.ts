import { FormaPagoCatalog } from '../src/catalogs/sat/cfdi_4/forma-pago';
import { TipoRegimenCatalog } from '../src/catalogs/sat/nomina/tipo-regimen';
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
  });
});
