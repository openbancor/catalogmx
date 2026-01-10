/**
 * Catalog data loader utilities
 * Loads catalog data from JSON or SQLite backends
 */

import { clearCatalogCache, loadCatalogJson, loadCatalogRows } from './catalog-backend';

/**
 * Base class for lazy-loading catalogs
 */
export abstract class CatalogLoader<T> {
  private static _cache: Map<string, unknown> = new Map();
  protected abstract getDataPath(): string;

  /**
   * Load catalog data (with caching)
   */
  protected loadData(): T[] {
    const dataPath = this.getDataPath();

    // Check cache first
    if (CatalogLoader._cache.has(dataPath)) {
      return CatalogLoader._cache.get(dataPath) as T[];
    }

    const data = loadCatalogRows<T>(dataPath);

    // Cache the data
    CatalogLoader._cache.set(dataPath, data);

    return data;
  }

  /**
   * Clear all cached catalog data
   */
  static clearCache(): void {
    this._cache.clear();
    clearCatalogCache();
  }
}

// For JSON files that are an array at the root: `[...]`
export function loadCatalogArray<T>(relativePath: string): T[] {
  return loadCatalogRows<T>(relativePath);
}

// For JSON files that are an object with a 'data' property: `{ "data": [...] }`
export function loadCatalogObject<T>(relativePath: string): T[] {
  return loadCatalogRows<T>(relativePath);
}

/**
 * Load catalog data regardless of its JSON shape.
 * Useful when the file exports additional metadata along with the catalog payload.
 */
export function loadCatalogData<T>(relativePath: string): T {
  return loadCatalogJson<T>(relativePath);
}
