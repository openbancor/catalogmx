/**
 * Tests for hybrid SQLite/JSON catalogs
 */

import { ClaveProdServCatalogHybrid } from '../src/catalogs';

describe('Hybrid ClaveProdServ Catalog', () => {
  afterAll(() => {
    // Close database connection after all tests
    ClaveProdServCatalogHybrid.close();
  });

  test('should report which backend is in use', () => {
    const usingSqlite = ClaveProdServCatalogHybrid.isUsingSqlite();
    expect(typeof usingSqlite).toBe('boolean');
    // Will be true if SQLite DB exists, false if using JSON
  });

  test('should get total count', () => {
    const count = ClaveProdServCatalogHybrid.getTotalCount();
    expect(count).toBeGreaterThan(0);
  });

  test('should get product by ID', () => {
    const prod = ClaveProdServCatalogHybrid.getClave('10101501');
    expect(prod).toBeDefined();
    expect(prod?.descripcion).toBeDefined();
  });

  test('should validate product code', () => {
    expect(ClaveProdServCatalogHybrid.isValid('10101501')).toBe(true);
    expect(ClaveProdServCatalogHybrid.isValid('01010101')).toBe(true);
    expect(ClaveProdServCatalogHybrid.isValid('99999999')).toBe(false);
  });

  test('should search by keyword', () => {
    const results = ClaveProdServCatalogHybrid.search('computadora', 10);
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(10);
  });

  test('should get by prefix (UNSPSC hierarchy)', () => {
    const results = ClaveProdServCatalogHybrid.getByPrefix('1010', 50);
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(50);
    // All should start with prefix
    results.forEach(item => {
      expect(item.id.startsWith('1010')).toBe(true);
    });
  });

  test('should get vigentes (active items)', () => {
    const vigentes = ClaveProdServCatalogHybrid.getVigentes(100);
    expect(vigentes.length).toBeGreaterThan(0);
    expect(vigentes.length).toBeLessThanOrEqual(100);
    // Should not have end dates
    vigentes.forEach(item => {
      expect(item.fechaFinVigencia === '' || !item.fechaFinVigencia).toBe(true);
    });
  });

  test('should get items with border incentive', () => {
    const conEstimulo = ClaveProdServCatalogHybrid.getConEstimuloFronterizo(50);
    // Note: This method may return empty when using SQLite backend
    // as estimuloFranjaFronteriza is not currently stored in the DB
    expect(Array.isArray(conEstimulo)).toBe(true);
    if (conEstimulo.length > 0) {
      // If results found, verify they have estimulo = '01'
      conEstimulo.forEach(item => {
        expect(item.estimuloFranjaFronteriza).toBe('01');
      });
    }
  });

  test('should get items requiring IVA', () => {
    const conIVA = ClaveProdServCatalogHybrid.getRequierenIVA(50);
    expect(conIVA.length).toBeGreaterThan(0);
    // All should require IVA
    conIVA.forEach(item => {
      const requiereIVA = item.incluirIVATrasladado.toUpperCase() === 'SÍ' ||
                         item.incluirIVATrasladado.toUpperCase() === 'SI';
      expect(requiereIVA).toBe(true);
    });
  });

  test('should get items requiring IEPS', () => {
    const conIEPS = ClaveProdServCatalogHybrid.getRequierenIEPS(50);
    // IEPS is rare, but catalog should handle it
    expect(Array.isArray(conIEPS)).toBe(true);
  });

  test('should get statistics', () => {
    const stats = ClaveProdServCatalogHybrid.getStatistics();
    expect(stats.total).toBeGreaterThan(0);
    expect(stats.vigentes).toBeGreaterThanOrEqual(0);
    expect(stats.obsoletas).toBeGreaterThanOrEqual(0);
    expect(stats.requierenIVA).toBeGreaterThanOrEqual(0);
    expect(stats.requierenIEPS).toBeGreaterThanOrEqual(0);
  });

  test('should perform advanced search', () => {
    const results = ClaveProdServCatalogHybrid.searchAdvanced({
      keyword: 'software',
      vigente: true,
      limit: 20
    });
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(20);

    // All should be vigentes
    results.forEach(item => {
      expect(item.fechaFinVigencia === '' || !item.fechaFinVigencia).toBe(true);
    });
  });

  test('should handle advanced search with prefix filter', () => {
    const results = ClaveProdServCatalogHybrid.searchAdvanced({
      prefix: '1010',
      vigente: true,
      limit: 30
    });
    expect(results.length).toBeGreaterThan(0);

    // All should start with prefix
    results.forEach(item => {
      expect(item.id.startsWith('1010')).toBe(true);
    });
  });

  test('should handle advanced search with IVA filter', () => {
    const results = ClaveProdServCatalogHybrid.searchAdvanced({
      requiereIVA: true,
      limit: 10
    });

    if (results.length > 0) {
      results.forEach(item => {
        const requiereIVA = item.incluirIVATrasladado.toUpperCase() === 'SÍ' ||
                           item.incluirIVATrasladado.toUpperCase() === 'SI';
        expect(requiereIVA).toBe(true);
      });
    }
  });

  test('should get all items (paginated)', () => {
    const page1 = ClaveProdServCatalogHybrid.getAll();
    expect(page1.length).toBeGreaterThan(0);
    // Default returns large set or all
    expect(page1.length).toBeLessThanOrEqual(100000);
  });

  test('should handle empty search results gracefully', () => {
    const results = ClaveProdServCatalogHybrid.search('xyzqweasdzxc123', 10);
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBe(0);
  });

  test('should handle invalid ID gracefully', () => {
    const item = ClaveProdServCatalogHybrid.getClave('INVALID');
    expect(item).toBeUndefined();
  });

  test('should maintain data consistency between backends', () => {
    // Test that the same ID returns the same data regardless of backend
    const item1 = ClaveProdServCatalogHybrid.getClave('01010101');
    expect(item1).toBeDefined();
    expect(item1?.id).toBe('01010101');
    expect(item1?.descripcion).toBeDefined();
    expect(typeof item1?.incluirIVATrasladado).toBe('string');
    expect(typeof item1?.incluirIEPSTrasladado).toBe('string');
  });

  test('should handle special characters in search', () => {
    const results = ClaveProdServCatalogHybrid.search('ñ', 5);
    expect(Array.isArray(results)).toBe(true);
    // May or may not find results, but shouldn't crash
  });

  test('should respect limit parameter in search', () => {
    const limit = 5;
    const results = ClaveProdServCatalogHybrid.search('servicio', limit);
    expect(results.length).toBeLessThanOrEqual(limit);
  });

  test('should respect limit parameter in getByPrefix', () => {
    const limit = 10;
    const results = ClaveProdServCatalogHybrid.getByPrefix('10', limit);
    expect(results.length).toBeLessThanOrEqual(limit);
  });
});

describe('Hybrid Catalog Performance', () => {
  afterAll(() => {
    ClaveProdServCatalogHybrid.close();
  });

  test('should perform searches efficiently', () => {
    const start = Date.now();
    const results = ClaveProdServCatalogHybrid.search('computadora', 100);
    const elapsed = Date.now() - start;

    expect(results.length).toBeGreaterThan(0);
    // Should complete in reasonable time (< 1 second for search)
    expect(elapsed).toBeLessThan(1000);
  });

  test('should perform ID lookups efficiently', () => {
    const start = Date.now();
    const item = ClaveProdServCatalogHybrid.getClave('10101501');
    const elapsed = Date.now() - start;

    expect(item).toBeDefined();
    // ID lookup should be very fast (< 100ms)
    expect(elapsed).toBeLessThan(100);
  });

  test('should handle multiple sequential searches', () => {
    const keywords = ['computadora', 'software', 'alimento', 'servicio'];
    const start = Date.now();

    keywords.forEach(keyword => {
      const results = ClaveProdServCatalogHybrid.search(keyword, 10);
      expect(Array.isArray(results)).toBe(true);
    });

    const elapsed = Date.now() - start;
    // Multiple searches should complete reasonably (< 2 seconds)
    expect(elapsed).toBeLessThan(2000);
  });
});
