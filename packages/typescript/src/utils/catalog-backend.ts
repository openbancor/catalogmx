/**
 * Catalog backend utilities for JSON and SQLite sources.
 * Keeps a sync API while allowing preloaded data and SQLite adapters in the browser.
 */

import type { CatalogSqliteDatabase } from './sqlite-adapter';

const JSON_TABLE_OVERRIDES: Record<string, string> = {
  'sepomex/codigos_postales_completo.json': 'codigos_postales',
  'inegi/localidades.json': 'localidades',
  'sat/cfdi_4.0/clave_prod_serv.json': 'clave_prod_serv',
};

const SKIP_JSON_FILES = new Set([
  'sepomex/codigos_postales.json',
  'banxico/udis.json',
  'banxico/tipo_cambio_usd.json',
  'banxico/tipo_cambio_hist.json',
  'banxico/tiie_28.json',
  'banxico/cetes_28.json',
  'banxico/inflacion_anual.json',
  'banxico/salarios_minimos.json',
]);

const jsonDataStore = new Map<string, unknown>();
const catalogCache = new Map<string, unknown>();

let sqliteAdapter: CatalogSqliteDatabase | null = null;
let preferSqlite = !isNodeRuntime();

export function setCatalogSqliteAdapter(adapter: CatalogSqliteDatabase | null): void {
  sqliteAdapter = adapter;
}

export function getCatalogSqliteAdapter(): CatalogSqliteDatabase | null {
  return sqliteAdapter;
}

export function setCatalogPreferSqlite(value: boolean): void {
  preferSqlite = value;
}

export function setCatalogJsonData(relativePath: string, data: unknown): void {
  jsonDataStore.set(normalizePath(relativePath), data);
}

export function clearCatalogJsonData(relativePath?: string): void {
  if (relativePath) {
    jsonDataStore.delete(normalizePath(relativePath));
    return;
  }
  jsonDataStore.clear();
}

export function clearCatalogCache(): void {
  catalogCache.clear();
}

export function hasCatalogJsonData(relativePath: string): boolean {
  const normalized = normalizePath(relativePath);
  if (jsonDataStore.has(normalized)) return true;
  const sqliteData = tryLoadCatalogJson(normalized);
  if (sqliteData !== null) return true;
  /* istanbul ignore next -- @preserve Browser environment: early return when not Node.js */
  if (!isNodeRuntime()) return false;
  /* istanbul ignore next -- @preserve Node.js file system check */
  const fs = getNodeFs();
  /* istanbul ignore next -- @preserve Node.js file system check */
  const fullPath = resolveSharedDataPath(normalized);
  /* istanbul ignore next -- @preserve Node.js file system check */
  return fs.existsSync(fullPath);
}

export function loadCatalogJson<T>(relativePath: string): T {
  const normalized = normalizePath(relativePath);
  if (jsonDataStore.has(normalized)) {
    return jsonDataStore.get(normalized) as T;
  }
  const sqliteData = tryLoadCatalogJson(normalized);
  if (sqliteData !== null) {
    return sqliteData as T;
  }
  /* istanbul ignore next -- @preserve Browser environment: throws when data not preloaded */
  if (!isNodeRuntime()) {
    throw new Error(
      `Catalog JSON not available in browser: ${normalized}. ` +
        `Use setCatalogJsonData() to preload it.`
    );
  }
  /* istanbul ignore next -- @preserve Node.js file system operations */
  const fs = getNodeFs();
  /* istanbul ignore next -- @preserve Node.js file system operations */
  const fullPath = resolveSharedDataPath(normalized);
  /* istanbul ignore next -- @preserve Node.js file system operations */
  if (!fs.existsSync(fullPath)) {
    throw new Error(`Catalog file not found: ${fullPath}`);
  }
  /* istanbul ignore next -- @preserve Node.js file system operations */
  return JSON.parse(fs.readFileSync(fullPath, 'utf-8')) as T;
}

export function loadCatalogRows<T>(relativePath: string): T[] {
  const normalized = normalizePath(relativePath);
  if (catalogCache.has(normalized)) {
    return catalogCache.get(normalized) as T[];
  }

  const rows = tryLoadFromSqlite<T>(normalized) ?? extractRecords<T>(loadCatalogJson(normalized));
  catalogCache.set(normalized, rows);
  return rows;
}

export function tableNameForJsonPath(relativePath: string): string {
  const normalized = normalizePath(relativePath);
  if (JSON_TABLE_OVERRIDES[normalized]) {
    return JSON_TABLE_OVERRIDES[normalized];
  }
  const parts = normalized.split('/').map((part) => {
    let name = part.toLowerCase().replace(/ /g, '_').replace(/-/g, '_');
    if (name.endsWith('.json')) {
      name = name.slice(0, -'.json'.length);
    }
    name = name.replace(/\./g, '_');
    return name.replace(/_+$/, '');
  });
  return parts.join('_').replace(/_+$/, '');
}

function tryLoadFromSqlite<T>(relativePath: string): T[] | null {
  if (!sqliteAdapter) return null;
  if (!preferSqlite && !SKIP_JSON_FILES.has(relativePath)) {
    return null;
  }
  const tableName = tableNameForJsonPath(relativePath);
  if (!tableExists(tableName)) return null;
  const stmt = sqliteAdapter.prepare(`SELECT * FROM ${quoteIdent(tableName)}`);
  return stmt.all() as T[];
}

function tableExists(tableName: string): boolean {
  if (!sqliteAdapter) return false;
  const stmt = sqliteAdapter.prepare(
    "SELECT 1 AS ok FROM sqlite_master WHERE type='table' AND name=? LIMIT 1"
  );
  return !!stmt.get(tableName);
}

function tryLoadCatalogJson(relativePath: string): unknown | null {
  if (!sqliteAdapter) return null;
  if (!tableExists('catalog_json')) return null;
  const stmt = sqliteAdapter.prepare('SELECT payload FROM catalog_json WHERE path = ? LIMIT 1');
  const row = stmt.get(relativePath) as { payload?: string } | undefined;
  if (!row?.payload) return null;
  return JSON.parse(row.payload) as unknown;
}

function extractRecords<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[];
  if (!data || typeof data !== 'object') {
    return [];
  }
  const obj = data as Record<string, unknown>;
  if (Array.isArray(obj.items)) return obj.items as T[];
  if (Array.isArray(obj.data)) return obj.data as T[];

  const listFields = Object.entries(obj).filter(
    ([, value]) => Array.isArray(value) && value.length
  );
  if (!listFields.length) return [];
  const [, records] = listFields.reduce((max, current) =>
    (current[1] as unknown[]).length > (max[1] as unknown[]).length ? current : max
  );
  return records as T[];
}

function normalizePath(value: string): string {
  return value.replace(/\\/g, '/');
}

function quoteIdent(value: string): string {
  return `"${value.replace(/"/g, '""')}"`;
}

export function resolveSharedDataPath(relativePath: string): string {
  const path = getNodePath();
  return path.resolve(__dirname, '../../../shared-data', relativePath);
}

export function isNodeRuntime(): boolean {
  return typeof process !== 'undefined' && !!process.versions?.node;
}

/* istanbul ignore next -- @preserve Node.js-only: dynamic require not testable in isolated unit tests */
function getNodeFs(): typeof import('fs') {
  return require('fs');
}

/* istanbul ignore next -- @preserve Node.js-only: dynamic require not testable in isolated unit tests */
function getNodePath(): typeof import('path') {
  return require('path');
}
