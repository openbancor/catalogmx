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

import sqlWasmUrl from 'sql.js/dist/sql-wasm.wasm?url';

type InitSqlJsFn = (config?: { locateFile?: (file: string) => string }) => Promise<SqlJsStatic>;

let SQL: SqlJsStatic | null = null;
let sqlInitPromise: Promise<SqlJsStatic> | null = null;

const databases: Map<string, SqlJsDatabase> = new Map();

async function initSQL(): Promise<SqlJsStatic> {
  if (SQL) {
    return SQL;
  }

  if (!sqlInitPromise) {
    sqlInitPromise = import('sql.js/dist/sql-wasm.js')
      .then((module) => {
        const initSqlJs =
          (module as { default?: InitSqlJsFn }).default ??
          ((module as unknown) as InitSqlJsFn);

        if (typeof initSqlJs !== 'function') {
          console.error('[database] sql.js module exports:', module);
          throw new Error('Failed to load sql.js initializer.');
        }

        return initSqlJs({
          locateFile: (file: string) => (file === 'sql-wasm.wasm' ? sqlWasmUrl : file)
        });
      })
      .then((instance) => {
        SQL = instance;
        return instance;
      })
      .catch((error) => {
        console.error('[database] sql.js init failed', error);
        sqlInitPromise = null;
        throw error;
      });
  }

  return sqlInitPromise;
}

export async function loadDatabase(name: string): Promise<SqlJsDatabase> {
  const trimmedName = name.trim();
  const normalizedKey = trimmedName.replace(/\.(db|sqlite3?|sqlite)$/i, '');

  if (databases.has(normalizedKey)) {
    return databases.get(normalizedKey)!;
  }

  const sql = await initSQL();

  const fileCandidates = /\.(db|sqlite3?|sqlite)$/i.test(trimmedName)
    ? [trimmedName]
    : [`${trimmedName}.db`, `${trimmedName}.sqlite3`, `${trimmedName}.sqlite`];

  let response: Response | null = null;
  let resolvedFile = '';

  for (const candidate of fileCandidates) {
    const res = await fetch(`/data/${candidate}`);
    if (res.ok) {
      response = res;
      resolvedFile = candidate;
      break;
    }
  }

  if (!response) {
    throw new Error(`Failed to load ${trimmedName}. Place ${fileCandidates.join(', ')} in /public/data.`);
  }

  const buffer = await response.arrayBuffer();
  if (buffer.byteLength === 0) {
    throw new Error(`${resolvedFile} is empty or corrupt.`);
  }

  const db = new sql.Database(new Uint8Array(buffer));
  databases.set(normalizedKey, db);
  return db;
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

export interface TableInfoColumn {
  cid: number;
  name: string;
  type: string;
  notnull: number;
  dflt_value: string | null;
  pk: number;
}

export async function listTables(dbName: string): Promise<string[]> {
  const db = await loadDatabase(dbName);
  const stmt = db.prepare(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
  );
  const tables: string[] = [];
  while (stmt.step()) {
    const name = stmt.get()[0] as string;
    if (/(_fts(_data|_idx|_docsize|_config)?)$/i.test(name)) {
      continue;
    }
    tables.push(name);
  }
  stmt.free();
  return tables.sort((a, b) => a.localeCompare(b));
}

export async function getTableInfo(dbName: string, table: string): Promise<TableInfoColumn[]> {
  const db = await loadDatabase(dbName);
  const stmt = db.prepare(`PRAGMA table_info(${table})`);
  const cols: TableInfoColumn[] = [];
  while (stmt.step()) {
    const row = stmt.get();
    cols.push({
      cid: row[0] as number,
      name: row[1] as string,
      type: (row[2] as string) || '',
      notnull: row[3] as number,
      dflt_value: row[4] as string | null,
      pk: row[5] as number,
    });
  }
  stmt.free();
  return cols;
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
  const { page = 1, pageSize = 50, search = '', searchColumns = [], orderBy = '' } = options;
  const db = await loadDatabase(dbName);

  const textColumns = searchColumns;
  let whereClause = '';
  const params: (string | number)[] = [];
  const normalizedSearch = search ? normalizeText(search) : '';

  if (normalizedSearch && textColumns.length > 0) {
    const conditions = textColumns.map((col) => `${normalizeSqlExpr(col)} LIKE ?`);
    whereClause = `WHERE ${conditions.join(' OR ')}`;
    const likeValue = `%${normalizedSearch}%`;
    textColumns.forEach(() => params.push(likeValue));
  }

  const countSql = `SELECT COUNT(*) as count FROM ${table} ${whereClause}`;
  const countStmt = db.prepare(countSql);
  if (params.length > 0) countStmt.bind(params);
  countStmt.step();
  const total = (countStmt.get()[0] as number) ?? 0;
  countStmt.free();

  const offset = (page - 1) * pageSize;
  const orderClause = orderBy ? `ORDER BY ${orderBy}` : '';
  const dataSql = `SELECT * FROM ${table} ${whereClause} ${orderClause} LIMIT ? OFFSET ?`;
  const dataStmt = db.prepare(dataSql);
  dataStmt.bind([...params, pageSize, offset]);

  const rows: Record<string, unknown>[] = [];
  const columns = dataStmt.getColumnNames();
  while (dataStmt.step()) {
    const row = dataStmt.get();
    const obj: Record<string, unknown> = {};
    columns.forEach((col, i) => {
      obj[col] = row[i];
    });
    rows.push(obj);
  }
  dataStmt.free();

  return {
    data: rows,
    total,
    page,
    pageSize,
    totalPages: Math.max(1, Math.ceil(total / pageSize)),
  };
}

// Database-specific query helpers
export interface PostalCode {
  cp: string;
  asentamiento: string;
  tipo_asentamiento: string;
  municipio: string;
  estado: string;
  ciudad: string;
  cp_oficina: string;
  codigo_estado: string;
  codigo_municipio: string;
  zona?: string | null;
}

export interface Localidad {
  cvegeo: string;
  cve_entidad: string;
  cve_municipio: string;
  cve_localidad: string;
  nom_localidad: string;
  nom_municipio: string;
  nom_entidad: string;
  latitud: number;
  longitud: number;
  altitud: number;
  poblacion_total: number;
}

export interface ProductoServicio {
  id: string;
  descripcion: string;
  incluirIVATrasladado: string;
  incluirIEPSTrasladado: string;
  complementoQueDebeIncluir: string;
  fechaInicioVigencia: string;
  fechaFinVigencia: string;
  estimuloFranjaFronteriza: string;
  palabrasSimilares: string;
}

export async function searchPostalCodes(
  search: string,
  page = 1,
  pageSize = 50
): Promise<PaginatedResult<PostalCode>> {
  return queryPaginated<PostalCode>('mexico', 'codigos_postales_completo', {
    page,
    pageSize,
    search,
    searchColumns: ['cp', 'asentamiento', 'municipio', 'estado', 'ciudad'],
    orderBy: 'cp',
  });
}

export async function searchLocalidades(
  search: string,
  page = 1,
  pageSize = 50
): Promise<PaginatedResult<Localidad>> {
  return queryPaginated<Localidad>('mexico', 'localidades', {
    page,
    pageSize,
    search,
    searchColumns: ['nom_localidad', 'nom_municipio', 'nom_entidad', 'cve_localidad'],
    orderBy: 'nom_localidad'
  });
}

export async function searchProductos(
  search: string,
  page = 1,
  pageSize = 50
): Promise<PaginatedResult<ProductoServicio>> {
  return queryPaginated<ProductoServicio>('mexico', 'clave_prod_serv', {
    page,
    pageSize,
    search,
    searchColumns: ['id', 'descripcion', 'palabrasSimilares'],
    orderBy: 'id'
  });
}

export async function querySqlTable<T>(
  dbName: string,
  table: string,
  opts: {
    page?: number;
    pageSize?: number;
    search?: string;
    searchColumns?: string[];
    orderBy?: string;
  } = {}
): Promise<PaginatedResult<T>> {
  return queryPaginated<T>(dbName, table, opts);
}

export async function queryJsonArrayTable<T extends Record<string, unknown>>(
  dbName: string,
  table: string,
  column: string,
  {
    page = 1,
    pageSize = 50,
    search = '',
    searchColumns = [],
  }: {
    page?: number;
    pageSize?: number;
    search?: string;
    searchColumns?: string[];
  } = {}
): Promise<PaginatedResult<T>> {
  const db = await loadDatabase(dbName);
  const stmt = db.prepare(`SELECT ${column} FROM ${table} LIMIT 1`);
  stmt.step();
  const raw = stmt.get()[0];
  stmt.free();

  let records: T[] = [];
  if (typeof raw === 'string') {
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        records = parsed as T[];
      }
    } catch (error) {
      console.error('[database] Failed to parse JSON column', { table, column, error });
    }
  }

  const normalizedSearch = search ? normalizeText(search) : '';
  let filtered = records;
  if (normalizedSearch && searchColumns.length > 0) {
    filtered = records.filter((row) =>
      searchColumns.some((key) => {
        const value = row[key];
        return typeof value === 'string' && normalizeText(value).includes(normalizedSearch);
      })
    );
  }

  const total = filtered.length;
  const start = (page - 1) * pageSize;
  const slice = filtered.slice(start, start + pageSize);

  return {
    data: slice,
    total,
    page,
    pageSize,
    totalPages: Math.max(1, Math.ceil(total / pageSize)),
  };
}
