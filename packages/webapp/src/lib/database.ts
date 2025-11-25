/**
 * SQLite database loader using @sqlite.org/sqlite-wasm with HTTP VFS
 * This enables efficient HTTP Range requests - only downloads needed pages
 */

type SqliteDB = any; // We'll type this properly when implementing

let sqlite3: any = null;
let initPromise: Promise<any> | null = null;

const databases = new Map<string, SqliteDB>();

async function initSQLite() {
  if (sqlite3) return sqlite3;
  
  if (!initPromise) {
    initPromise = (async () => {
      try {
        // @ts-ignore - Dynamic import of WASM module
        const module = await import('@sqlite.org/sqlite-wasm');
        const sqlite3InitModule = module.default;
        const instance = await sqlite3InitModule({
          print: console.log,
          printErr: console.error,
        });
        sqlite3 = instance;
        return instance;
      } catch (error) {
        console.error('[database] Failed to initialize SQLite WASM:', error);
        initPromise = null;
        throw error;
      }
    })();
  }
  
  return initPromise;
}

export async function loadDatabase(name: string): Promise<SqliteDB> {
  const normalizedName = name.replace(/\.(db|sqlite3?|sqlite)$/i, '');
  
  if (databases.has(normalizedName)) {
    return databases.get(normalizedName)!;
  }

  const sqlite3Module = await initSQLite();
  const baseUrl = import.meta.env.BASE_URL || '/';
  const base = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  
  // Try different file extensions
  const candidates = [`${normalizedName}.sqlite3`, `${normalizedName}.db`, `${normalizedName}.sqlite`];
  
  let dbUrl = '';
  for (const candidate of candidates) {
    const url = `${base}/data/${candidate}`;
    try {
      const response = await fetch(url, { method: 'HEAD' });
      if (response.ok) {
        dbUrl = url;
        break;
      }
    } catch (e) {
      // Continue trying
    }
  }
  
  if (!dbUrl) {
    throw new Error(`Database not found: ${normalizedName}. Tried: ${candidates.join(', ')}`);
  }

  console.log(`[database] Loading ${dbUrl} with HTTP VFS...`);
  
  // Use opfs-sahpool for local dev, http for production
  const vfsMode = window.location.protocol === 'file:' ? 'opfs' : 'opfs-sahpool';
  
  try {
    // Create database with HTTP VFS
    const db = new sqlite3Module.oo1.DB(dbUrl, vfsMode);
    databases.set(normalizedName, db);
    console.log(`[database] ✓ Loaded ${normalizedName} successfully`);
    return db;
  } catch (error) {
    console.error(`[database] Failed to open ${dbUrl}:`, error);
    throw new Error(`Failed to open database: ${error instanceof Error ? error.message : String(error)}`);
  }
}

export interface QueryResult {
  columns: string[];
  values: (string | number | null)[][];
}

const normalizeText = (value: string): string =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .replace(/ñ/g, 'n');

const normalizeSqlExpr = (col: string) =>
  `replace(replace(replace(replace(replace(replace(lower(${col}), 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u'), 'ñ', 'n')`;

export async function queryDatabase(
  dbName: string,
  sql: string,
  params: (string | number)[] = []
): Promise<QueryResult> {
  const db = await loadDatabase(dbName);
  
  try {
    const result = db.exec({
      sql,
      bind: params,
      rowMode: 'array',
      returnValue: 'resultRows'
    });
    
    // Get column names
    const stmt = db.prepare(sql);
    const columns = stmt.getColumnNames();
    stmt.finalize();
    
    return {
      columns: columns || [],
      values: result || []
    };
  } catch (error) {
    console.error('[database] Query failed:', error);
    throw error;
  }
}

export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export async function queryPaginated<T>(
  dbName: string,
  table: string,
  options: {
    page?: number;
    pageSize?: number;
    search?: string;
    searchColumns?: string[];
    orderBy?: string;
  } = {}
): Promise<PaginatedResult<T>> {
  const {
    page = 1,
    pageSize = 50,
    search = '',
    searchColumns = [],
    orderBy = ''
  } = options;

  const db = await loadDatabase(dbName);

  // Build WHERE clause for search (accent-insensitive)
  const params: (string | number)[] = [];
  const normalizedSearch = search ? normalizeText(search) : '';
  let whereClause = '';

  if (normalizedSearch && searchColumns.length > 0) {
    const conditions = searchColumns.map((col) => `${normalizeSqlExpr(col)} LIKE ?`);
    whereClause = `WHERE ${conditions.join(' OR ')}`;
    searchColumns.forEach(() => params.push(`%${normalizedSearch}%`));
  }

  // Get total count
  const countSql = `SELECT COUNT(*) as count FROM ${table} ${whereClause}`;
  const countResult = db.exec({
    sql: countSql,
    bind: params,
    rowMode: 'object',
    returnValue: 'resultRows'
  });
  const total = (countResult[0]?.count as number) ?? 0;

  // Get paginated data
  const offset = (page - 1) * pageSize;
  const orderClause = orderBy ? `ORDER BY ${orderBy}` : '';
  const dataSql = `SELECT * FROM ${table} ${whereClause} ${orderClause} LIMIT ? OFFSET ?`;
  
  const dataParams = [...params, pageSize, offset];
  const rows = db.exec({
    sql: dataSql,
    bind: dataParams,
    rowMode: 'object',
    returnValue: 'resultRows'
  });

  return {
    data: rows as T[],
    total,
    page,
    pageSize,
    totalPages: Math.max(1, Math.ceil(total / pageSize)),
  };
}

export async function listTables(dbName: string): Promise<string[]> {
  const db = await loadDatabase(dbName);
  const result = db.exec({
    sql: "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
    rowMode: 'array',
    returnValue: 'resultRows'
  });
  
  return result
    .map((row: any[]) => row[0] as string)
    .filter((name: string) => !/_fts(_data|_idx|_docsize|_config)?$/i.test(name));
}

export async function getTableInfo(dbName: string, table: string): Promise<any[]> {
  const db = await loadDatabase(dbName);
  return db.exec({
    sql: `PRAGMA table_info(${table})`,
    rowMode: 'object',
    returnValue: 'resultRows'
  });
}

export async function getTableCount(dbName: string, table: string): Promise<number> {
  const db = await loadDatabase(dbName);
  const result = db.exec({
    sql: `SELECT COUNT(*) as total FROM ${table}`,
    rowMode: 'object',
    returnValue: 'resultRows'
  });
  return (result[0]?.total as number) ?? 0;
}

export async function queryTable(
  dbName: string,
  table: string,
  options: {
    page?: number;
    pageSize?: number;
    search?: string;
    searchColumns?: string[];
    orderBy?: string;
  } = {}
): Promise<PaginatedResult<Record<string, unknown>>> {
  return queryPaginated<Record<string, unknown>>(dbName, table, options);
}

// Legacy aliases for compatibility
export const querySqlTable = queryPaginated;

// Type definitions for specialized queries
export interface PostalCode {
  d_codigo?: string;
  d_asenta?: string;
  d_tipo_asenta?: string;
  d_mnpio?: string;
  d_estado?: string;
  d_zona?: string;
  cp?: string;
  asentamiento?: string;
  tipo_asentamiento?: string;
  municipio?: string;
  estado?: string;
  ciudad?: string;
  zona?: string;
}

export interface Localidad {
  cve_ent?: string;
  cve_mun?: string;
  cve_loc?: string;
  cve_entidad?: string;
  cve_municipio?: string;
  cve_localidad?: string;
  nombre?: string;
  nom_localidad?: string;
  nom_municipio?: string;
  nom_entidad?: string;
  ambito?: string;
  latitud?: number;
  longitud?: number;
  altitud?: number;
  poblacion_total?: number;
}

export interface ProductoServicio {
  c_clave_prod_serv?: string;
  clave?: string;
  descripcion?: string;
  incluir_iva_trasladado?: string;
  incluir_ieps_trasladado?: string;
  incluye_iva?: number | string;
  incluye_ieps?: number | string;
  complemento?: string;
  estimulo_franja_fronteriza?: string;
  palabras_similares?: string;
}

// Specialized queries
export async function searchPostalCodes(
  search: string,
  page = 1,
  pageSize = 50
): Promise<PaginatedResult<PostalCode>> {
  return queryPaginated<PostalCode>('mexico', 'codigos_postales', {
    page,
    pageSize,
    search,
    searchColumns: ['d_codigo', 'd_asenta', 'd_mnpio', 'd_estado'],
    orderBy: 'd_codigo',
  });
}

export async function searchLocalidades(
  search: string,
  page = 1,
  pageSize = 50
): Promise<PaginatedResult<Localidad>> {
  return queryPaginated<Localidad>('mexico', 'inegi_localidades', {
    page,
    pageSize,
    search,
    searchColumns: ['nombre', 'cve_ent', 'cve_mun'],
    orderBy: 'nombre'
  });
}

export async function searchProductos(
  search: string,
  page = 1,
  pageSize = 50
): Promise<PaginatedResult<ProductoServicio>> {
  return queryPaginated<ProductoServicio>('mexico', 'sat_cfdi_4_0_c_claveprodserv', {
    page,
    pageSize,
    search,
    searchColumns: ['c_clave_prod_serv', 'descripcion', 'palabras_similares'],
    orderBy: 'c_clave_prod_serv'
  });
}

// Note: queryJsonArrayTable is deprecated with SQLite WASM
// All data should be in SQL tables now
export async function queryJsonArrayTable<T>(
  dbName: string,
  table: string,
  _column?: string,
  options: {
    page?: number;
    pageSize?: number;
    search?: string;
    searchColumns?: string[];
  } = {}
): Promise<PaginatedResult<T>> {
  // Just delegate to regular query - no JSON columns with new structure
  return queryPaginated<T>(dbName, table, options);
}
