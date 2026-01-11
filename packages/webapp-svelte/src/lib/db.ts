/**
 * SQLite database service using sql.js
 * Loads mexico.sqlite3 from GitHub Releases for catalog data
 */
import initSqlJs, { type Database } from 'sql.js';
import { base } from '$app/paths';
import { createSqlJsAdapter, setCatalogPreferSqlite, setCatalogSqliteAdapter } from 'catalogmx/utils';

// Database singleton
let db: Database | null = null;
let dbPromise: Promise<Database> | null = null;

const DB_URL_FALLBACK =
	'https://github.com/openbancor/catalogmx/releases/download/sqlite-assets/mexico.sqlite3';

function getDatabaseUrls(): string[] {
	const urls = [`${base}/data/mexico.sqlite3`, `${base}/mexico.sqlite3`];
	const normalized = urls.map((url) => url.replace(/\/{2,}/g, '/'));
	if (!base) {
		return normalized.concat(DB_URL_FALLBACK);
	}
	return normalized;
}

/**
 * Initialize sql.js and load the database
 */
async function initDatabase(): Promise<Database> {
	// Initialize sql.js with WASM
	const SQL = await initSqlJs({
		// Use CDN for WASM file
		locateFile: (file: string) => `https://sql.js.org/dist/${file}`,
	});

	// Fetch the database file
	const candidates = getDatabaseUrls();
	let response: Response | null = null;
	let lastError: Error | null = null;

	for (const url of candidates) {
		try {
			console.log('Fetching database from:', url);
			const result = await fetch(url);
			if (!result.ok) {
				lastError = new Error(`Failed to fetch database: ${result.status} ${result.statusText}`);
				continue;
			}
			response = result;
			break;
		} catch (err) {
			lastError = err instanceof Error ? err : new Error('Failed to fetch database');
		}
	}

	if (!response) {
		throw lastError ?? new Error('Failed to fetch database');
	}

	const buffer = await response.arrayBuffer();
	console.log('Database loaded:', (buffer.byteLength / 1024 / 1024).toFixed(2), 'MB');

	// Create database from buffer
	return new SQL.Database(new Uint8Array(buffer));
}

/**
 * Get database instance (lazy loaded, singleton)
 */
export async function getDatabase(): Promise<Database> {
	if (db) {
		return db;
	}

	if (!dbPromise) {
		dbPromise = initDatabase()
			.then((database) => {
				db = database;
				setCatalogSqliteAdapter(createSqlJsAdapter(database));
				setCatalogPreferSqlite(true);
				return database;
			})
			.catch((err) => {
				dbPromise = null;
				throw err;
			});
	}

	return dbPromise;
}

/**
 * Execute a query and return results as array of objects
 */
export async function query<T = Record<string, unknown>>(
	sql: string,
	params: (string | number | null)[] = []
): Promise<T[]> {
	const database = await getDatabase();
	const stmt = database.prepare(sql);
	stmt.bind(params);

	const results: T[] = [];
	while (stmt.step()) {
		const row = stmt.getAsObject() as T;
		results.push(row);
	}
	stmt.free();

	return results;
}

/**
 * Execute a query and return first result
 */
export async function queryOne<T = Record<string, unknown>>(
	sql: string,
	params: (string | number | null)[] = []
): Promise<T | null> {
	const results = await query<T>(sql, params);
	return results[0] || null;
}

/**
 * Get count of rows matching query
 */
export async function count(
	table: string,
	where?: string,
	params: (string | number | null)[] = []
): Promise<number> {
	const sql = where
		? `SELECT COUNT(*) as count FROM ${table} WHERE ${where}`
		: `SELECT COUNT(*) as count FROM ${table}`;

	const result = await queryOne<{ count: number }>(sql, params);
	return result?.count || 0;
}

/**
 * Get paginated results
 */
export async function paginate<T = Record<string, unknown>>(
	table: string,
	options: {
		page?: number;
		pageSize?: number;
		orderBy?: string;
		where?: string;
		params?: (string | number | null)[];
	} = {}
): Promise<{ data: T[]; total: number; page: number; pageSize: number; totalPages: number }> {
	const { page = 1, pageSize = 25, orderBy, where, params = [] } = options;
	const offset = (page - 1) * pageSize;

	// Get total count
	const total = await count(table, where, params);

	// Build query
	let sql = `SELECT * FROM ${table}`;
	if (where) sql += ` WHERE ${where}`;
	if (orderBy) sql += ` ORDER BY ${orderBy}`;
	sql += ` LIMIT ? OFFSET ?`;

	const data = await query<T>(sql, [...params, pageSize, offset]);

	return {
		data,
		total,
		page,
		pageSize,
		totalPages: Math.ceil(total / pageSize),
	};
}

/**
 * Search across multiple columns
 */
export async function search<T = Record<string, unknown>>(
	table: string,
	searchTerm: string,
	columns: string[],
	options: {
		page?: number;
		pageSize?: number;
		orderBy?: string;
	} = {}
): Promise<{ data: T[]; total: number; page: number; pageSize: number; totalPages: number }> {
	const { page = 1, pageSize = 25, orderBy } = options;
	const offset = (page - 1) * pageSize;

	// Build search condition
	const searchLower = searchTerm.toLowerCase();
	const whereParts = columns.map(col => `LOWER(${col}) LIKE ?`);
	const where = whereParts.join(' OR ');
	const searchParams = columns.map(() => `%${searchLower}%`);

	// Get total count
	const countSql = `SELECT COUNT(*) as count FROM ${table} WHERE ${where}`;
	const countResult = await queryOne<{ count: number }>(countSql, searchParams);
	const total = countResult?.count || 0;

	// Get data
	let sql = `SELECT * FROM ${table} WHERE ${where}`;
	if (orderBy) sql += ` ORDER BY ${orderBy}`;
	sql += ` LIMIT ? OFFSET ?`;

	const data = await query<T>(sql, [...searchParams, pageSize, offset]);

	return {
		data,
		total,
		page,
		pageSize,
		totalPages: Math.ceil(total / pageSize),
	};
}

/**
 * Get list of all tables in database
 */
export async function getTables(): Promise<string[]> {
	const results = await query<{ name: string }>(
		"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
	);
	return results.map(r => r.name);
}

/**
 * Get table schema
 */
export async function getTableSchema(table: string): Promise<{ name: string; type: string }[]> {
	const results = await query<{ name: string; type: string }>(`PRAGMA table_info(${table})`);
	return results;
}
