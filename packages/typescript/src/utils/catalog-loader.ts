/**
 * Catalog data loader utilities
 * Loads JSON catalog data from shared-data directory
 */

import * as path from 'path';
import * as fs from 'fs';

/**
 * Base class for lazy-loading catalogs
 */
export abstract class CatalogLoader<T> {
  private static _cache: Map<string, any> = new Map();
  protected abstract getDataPath(): string;

  /**
   * Load catalog data (with caching)
   */
  protected loadData(): T[] {
    const dataPath = this.getDataPath();

    // Check cache first
    if (CatalogLoader._cache.has(dataPath)) {
      return CatalogLoader._cache.get(dataPath);
    }

    // Load from file
    const fullPath = path.resolve(__dirname, '../../../../shared-data', dataPath);

    if (!fs.existsSync(fullPath)) {
      throw new Error(`Catalog file not found: ${fullPath}`);
    }

    const data = JSON.parse(fs.readFileSync(fullPath, 'utf-8'));

    // Cache the data
    CatalogLoader._cache.set(dataPath, data);

    return data;
  }

  /**
   * Clear all cached catalog data
   */
  static clearCache(): void {
    this._cache.clear();
  }
}

/**
 * Helper function to load JSON catalog
 */
export function loadCatalog<T>(relativePath: string): T[] {
  const fullPath = path.resolve(__dirname, '../../../../shared-data', relativePath);

  if (!fs.existsSync(fullPath)) {
    throw new Error(`Catalog file not found: ${fullPath}`);
  }

  return JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
}
