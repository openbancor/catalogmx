import { setCatalogJsonData } from '../utils/catalog-backend';
import { BUNDLED_CATALOG_DATA } from './bundled-data.generated';

/**
 * Preload the bounded catalog set embedded for browsers and Workers.
 *
 * Large product/service and postal-code catalogs are intentionally excluded;
 * use their SQLite/D1-backed adapters instead of embedding them in a Worker.
 */
export function preloadSmallCatalogData(): void {
  for (const source of BUNDLED_CATALOG_DATA) {
    setCatalogJsonData(source.path, source.data);
  }
}
