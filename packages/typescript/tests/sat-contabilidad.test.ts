import { describe, expect, test } from '@jest/globals';
import { CodigoAgrupadorSATCatalog } from '../src/catalogs';

describe('SAT Código Agrupador (Anexo 24)', () => {
  test('loads default version', () => {
    const items = CodigoAgrupadorSATCatalog.getAll();
    expect(items.length).toBeGreaterThan(1000);
  });

  test('gets item by code', () => {
    const item = CodigoAgrupadorSATCatalog.getByCodigo('100');
    expect(item).toBeDefined();
    expect(item?.nombre.toLowerCase()).toBe('activo');
  });

  test('validates code', () => {
    expect(CodigoAgrupadorSATCatalog.isValid('101.01')).toBe(true);
    expect(CodigoAgrupadorSATCatalog.isValid('999.99')).toBe(false);
  });

  test('versions and diff', () => {
    const versions = CodigoAgrupadorSATCatalog.getVersions();
    expect(versions).toContain('2024-01-22');
    expect(versions).toContain('2026-01-13');
    const diff = CodigoAgrupadorSATCatalog.getDiff2024_2026();
    expect(diff).toHaveProperty('added');
  });
});
