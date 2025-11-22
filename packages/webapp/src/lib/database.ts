/**
 * SQLite database loader using sql.js for browser-based queries
 */

// Type definitions for sql.js
interface SqlJsDatabase {
  prepare(sql: string): SqlJsStatement;
  run(sql: string, params?: unknown[]): void;
  close(): void;
}

interface SqlJsStatement {
  bind(params?: unknown[]): boolean;
  step(): boolean;
  get(params?: unknown[]): (string | number | null)[];
  getColumnNames(): string[];
  free(): boolean;
}

interface SqlJsStatic {
  Database: new (data?: ArrayLike<number> | null) => SqlJsDatabase;
}

let SQL: SqlJsStatic | null = null;

const databases: Map<string, SqlJsDatabase> = new Map();

async function initSQL(): Promise<SqlJsStatic> {
  if (!SQL) {
    // Dynamic import for sql.js
    const sqlPromise = (await import('sql.js')) as unknown as { default: (config?: { locateFile?: (file: string) => string }) => Promise<SqlJsStatic> };
    const initSqlJs = sqlPromise.default;
    SQL = await initSqlJs({
      locateFile: (file: string) => `https://sql.js.org/dist/${file}`
    });
  }
  return SQL;
}

export async function loadDatabase(name: string): Promise<SqlJsDatabase> {
  if (databases.has(name)) {
    return databases.get(name)!;
  }

  const sql = await initSQL();
  const response = await fetch(`/data/${name}.db`);
  const buffer = await response.arrayBuffer();
  const db = new sql.Database(new Uint8Array(buffer));
  databases.set(name, db);
  return db;
}

export interface QueryResult {
  columns: string[];
  values: (string | number | null)[][];
}

export async function queryDatabase(
  dbName: string,
  sql: string,
  params: (string | number)[] = []
): Promise<QueryResult> {
  const db = await loadDatabase(dbName);
  const stmt = db.prepare(sql);
  stmt.bind(params);

  const columns: string[] = stmt.getColumnNames();
  const values: (string | number | null)[][] = [];

  while (stmt.step()) {
    values.push(stmt.get());
  }

  stmt.free();
  return { columns, values };
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

  // Build WHERE clause for search
  let whereClause = '';
  const params: string[] = [];

  if (search && searchColumns.length > 0) {
    const conditions = searchColumns.map(col => `${col} LIKE ?`);
    whereClause = `WHERE ${conditions.join(' OR ')}`;
    searchColumns.forEach(() => params.push(`%${search}%`));
  }

  // Get total count
  const countSql = `SELECT COUNT(*) as count FROM ${table} ${whereClause}`;
  const countStmt = db.prepare(countSql);
  if (params.length > 0) countStmt.bind(params);
  countStmt.step();
  const total = countStmt.get()[0] as number;
  countStmt.free();

  // Get paginated data
  const offset = (page - 1) * pageSize;
  const orderClause = orderBy ? `ORDER BY ${orderBy}` : '';
  const dataSql = `SELECT * FROM ${table} ${whereClause} ${orderClause} LIMIT ? OFFSET ?`;

  const dataParams = [...params, pageSize, offset];
  const dataStmt = db.prepare(dataSql);
  dataStmt.bind(dataParams);

  const columns: string[] = dataStmt.getColumnNames();
  const data: T[] = [];

  while (dataStmt.step()) {
    const row = dataStmt.get();
    const obj: Record<string, unknown> = {};
    columns.forEach((col: string, i: number) => {
      obj[col] = row[i];
    });
    data.push(obj as T);
  }

  dataStmt.free();

  return {
    data,
    total,
    page,
    pageSize,
    totalPages: Math.ceil(total / pageSize)
  };
}

// Database-specific query helpers
export interface PostalCode {
  d_codigo: string;
  d_asenta: string;
  d_tipo_asenta: string;
  D_mnpio: string;
  d_estado: string;
  d_ciudad: string;
  d_CP: string;
  c_estado: string;
  c_oficina: string;
  c_CP: string;
  c_tipo_asenta: string;
  c_mnpio: string;
  id_asenta_cpcons: string;
  d_zona: string;
  c_cve_ciudad: string;
}

export interface Localidad {
  cve_ent: string;
  cve_mun: string;
  cve_loc: string;
  nom_loc: string;
  nom_mun: string;
  nom_ent: string;
  lat_decimal: number;
  lon_decimal: number;
  altitud: number;
  pob_total: number;
}

export interface ProductoServicio {
  c_ClaveProdServ: string;
  Descripcion: string;
  Incluir_IVA_trasladado: string;
  Incluir_IEPS_trasladado: string;
  Complemento_que_debe_incluir: string;
  FechaInicioVigencia: string;
  FechaFinVigencia: string;
  Estimulo_Franja_Fronteriza: string;
  Palabras_similares: string;
}

export async function searchPostalCodes(
  search: string,
  page = 1,
  pageSize = 50
): Promise<PaginatedResult<PostalCode>> {
  return queryPaginated<PostalCode>('sepomex', 'codigos_postales', {
    page,
    pageSize,
    search,
    searchColumns: ['d_codigo', 'd_asenta', 'D_mnpio', 'd_estado', 'd_ciudad'],
    orderBy: 'd_codigo'
  });
}

export async function searchLocalidades(
  search: string,
  page = 1,
  pageSize = 50
): Promise<PaginatedResult<Localidad>> {
  return queryPaginated<Localidad>('localidades', 'localidades', {
    page,
    pageSize,
    search,
    searchColumns: ['nom_loc', 'nom_mun', 'nom_ent', 'cve_loc'],
    orderBy: 'nom_loc'
  });
}

export async function searchProductos(
  search: string,
  page = 1,
  pageSize = 50
): Promise<PaginatedResult<ProductoServicio>> {
  return queryPaginated<ProductoServicio>('clave_prod_serv', 'c_ClaveProdServ', {
    page,
    pageSize,
    search,
    searchColumns: ['c_ClaveProdServ', 'Descripcion', 'Palabras_similares'],
    orderBy: 'c_ClaveProdServ'
  });
}
