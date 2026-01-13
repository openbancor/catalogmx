/**
 * SQLite database service using sql.js-httpvfs.
 * Streams only needed pages via HTTP range requests.
 */
import { createDbWorker } from 'sql.js-httpvfs';
import { base } from '$app/paths';

type SqliteParam = string | number | null;

type SqliteStatement = {
	bind: (params?: SqliteParam[]) => Promise<boolean>;
	step: () => Promise<boolean>;
	getAsObject: (params?: Record<string, unknown>) => Promise<Record<string, unknown>>;
	free: () => Promise<boolean>;
	reset: () => Promise<void>;
};

type SqliteDatabase = {
	exec: (sql: string) => Promise<{ columns: string[]; values: unknown[][] }[]>;
	prepare: (sql: string) => Promise<SqliteStatement>;
};

type SqliteWorker = {
	db: SqliteDatabase;
	worker: { bytesRead: number | Promise<number> };
	configs: unknown[];
};

// Database singleton
let dbWorker: SqliteWorker | null = null;
let dbPromise: Promise<SqliteWorker> | null = null;

const DB_URL_FALLBACK =
	'https://github.com/openbancor/catalogmx/releases/download/sqlite-assets/mexico.sqlite3';

const WORKER_URL = new URL('sql.js-httpvfs/dist/sqlite.worker.js', import.meta.url);
const WASM_URL = new URL('sql.js-httpvfs/dist/sql-wasm.wasm', import.meta.url);

function getDatabaseUrls(): string[] {
	const urls = [`${base}/data/mexico.sqlite3`, `${base}/mexico.sqlite3`];
	const normalized = urls.map((url) => url.replace(/\/{2,}/g, '/'));
	if (!base) {
		return normalized.concat(DB_URL_FALLBACK);
	}
	return normalized;
}

async function probeDatabaseUrl(url: string): Promise<boolean> {
	try {
		const head = await fetch(url, { method: 'HEAD' });
		if (head.ok) return true;
		if (head.status !== 405) return false;
		const range = await fetch(url, { headers: { Range: 'bytes=0-0' } });
		return range.ok;
	} catch {
		return false;
	}
}

async function resolveDatabaseUrl(): Promise<string> {
	const candidates = getDatabaseUrls();
	let lastError: Error | null = null;

	for (const url of candidates) {
		const ok = await probeDatabaseUrl(url);
		if (ok) return url;
		lastError = new Error(`Failed to reach database: ${url}`);
	}

	throw lastError ?? new Error('Failed to fetch database');
}

function parseContentRange(value: string | null): number | null {
	if (!value) return null;
	const match = /\/(\d+)\s*$/.exec(value);
	if (!match) return null;
	return Number(match[1]);
}

async function getDatabaseLength(url: string): Promise<number> {
	try {
		const rangeResponse = await fetch(url, { headers: { Range: 'bytes=0-0' } });
		if (rangeResponse.ok) {
			const total = parseContentRange(rangeResponse.headers.get('Content-Range'));
			if (total) return total;
		}
	} catch {
		// Fall through to HEAD check.
	}

	const head = await fetch(url, { method: 'HEAD' });
	if (!head.ok) {
		throw new Error(`Failed to probe database length: ${head.status} ${head.statusText}`);
	}
	const encoding = head.headers.get('Content-Encoding');
	if (encoding && encoding !== 'identity') {
		throw new Error('Database server returned encoded length; cannot determine size safely.');
	}
	const length = head.headers.get('Content-Length');
	if (!length) {
		throw new Error('Database length not available from server headers.');
	}
	return Number(length);
}

/**
 * Initialize sql.js-httpvfs worker and attach database.
 */
async function initDatabase(): Promise<SqliteWorker> {
	const url = await resolveDatabaseUrl();
	const databaseLengthBytes = await getDatabaseLength(url);
	console.log('Opening database via httpvfs:', url);
	return createDbWorker(
		[
			{
				from: 'inline',
				config: {
					serverMode: 'full',
					requestChunkSize: 4096,
					url,
					databaseLengthBytes
				}
			}
		],
		WORKER_URL.toString(),
		WASM_URL.toString()
	) as Promise<SqliteWorker>;
}

/**
 * Get database instance (lazy loaded, singleton)
 */
export async function getDatabase(): Promise<SqliteDatabase> {
	if (dbWorker) {
		return dbWorker.db;
	}

	if (!dbPromise) {
		dbPromise = initDatabase()
			.then((worker) => {
				dbWorker = worker;
				return worker;
			})
			.catch((err) => {
				dbPromise = null;
				throw err;
			});
	}

	const worker = await dbPromise;
	return worker.db;
}

/**
 * Execute a query and return results as array of objects
 */
export async function query<T = Record<string, unknown>>(
	sql: string,
	params: SqliteParam[] = []
): Promise<T[]> {
	const database = await getDatabase();
	const stmt = await database.prepare(sql);
	if (params.length) {
		await stmt.bind(params);
	}

	const results: T[] = [];
	while (await stmt.step()) {
		const row = (await stmt.getAsObject()) as T;
		results.push(row);
	}
	await stmt.free();

	return results;
}

/**
 * Execute a query and return first result
 */
export async function queryOne<T = Record<string, unknown>>(
	sql: string,
	params: SqliteParam[] = []
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
	params: SqliteParam[] = []
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
		params?: SqliteParam[];
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
