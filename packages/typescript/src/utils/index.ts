/**
 * catalogmx - Utilities
 */

// Text utilities
export { normalizeText } from './text';

// CLABE utilities
export {
  decodeClabe,
  generateClabeRandom,
  generateClabeExamples,
  generateClabeForBank,
  getCommonBanks,
  getPlazaSuggestions,
  formatClabe,
  describeClabe,
} from './clabe-utils';

export type { BankInfo, PlazaInfo, DecodedCLABE, GenerateClabeOptions } from './clabe-utils';

// Catalog backend utilities
export * from './catalog-loader';
export {
  clearCatalogCache,
  clearCatalogJsonData,
  getCatalogSqliteAdapter,
  hasCatalogJsonData,
  isNodeRuntime,
  loadCatalogJson,
  loadCatalogRows,
  setCatalogJsonData,
  setCatalogPreferSqlite,
  setCatalogSqliteAdapter,
  tableNameForJsonPath,
} from './catalog-backend';
export {
  createBetterSqliteAdapter,
  createSqlJsAdapter,
  type CatalogSqliteDatabase,
  type CatalogSqliteStatement,
  type SqliteParam,
} from './sqlite-adapter';
