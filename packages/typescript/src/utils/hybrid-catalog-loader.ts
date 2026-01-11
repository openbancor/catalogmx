/**
 * Hybrid catalog loader that supports both SQLite (for large catalogs) and JSON (for small catalogs)
 *
 * This maintains API parity between Python and TypeScript implementations.
 */

import {
  getCatalogSqliteAdapter,
  hasCatalogJsonData,
  isNodeRuntime,
  resolveSharedDataPath,
} from './catalog-backend';
import {
  createBetterSqliteAdapter,
  type CatalogSqliteDatabase,
  type SqliteParam,
} from './sqlite-adapter';

export interface HybridLoaderOptions {
  /**
   * Catalog name (e.g., 'clave_prod_serv', 'localidades')
   */
  catalogName: string;

  /**
   * Relative path to JSON file (from shared-data directory)
   */
  jsonPath: string;

  /**
   * Relative path to SQLite DB (from sqlite directory)
   * If not provided, will use catalogName.db
   */
  sqlitePath?: string;

  /**
   * Prefer SQLite over JSON even if both exist
   * Default: true
   */
  preferSqlite?: boolean;

  /**
   * Size threshold in MB - if JSON > threshold, prefer SQLite
   * Default: 5
   */
  sizeThresholdMB?: number;
}

export abstract class HybridCatalogLoader<T> {
  protected _db: CatalogSqliteDatabase | null = null;
  protected _data: T[] | null = null;
  protected _usingSqlite: boolean = false;

  constructor(protected options: HybridLoaderOptions) {
    this.options.preferSqlite = options.preferSqlite ?? true;
    this.options.sizeThresholdMB = options.sizeThresholdMB ?? 5;
  }

  /**
   * Load data from either SQLite or JSON
   * Automatically chooses the best source
   */
  protected loadData(): void {
    if (this._data !== null || this._db !== null) return;

    const sqlitePath = this.getSqlitePath();
    const jsonPath = this.options.jsonPath;
    const jsonFullPath = this.getJsonPath();
    const adapter = getCatalogSqliteAdapter();

    const hasSqlite = adapter ? true : isNodeRuntime() ? nodeFsExists(sqlitePath) : false;
    const hasJson = hasCatalogJsonData(jsonPath);

    if (!hasSqlite && !hasJson) {
      throw new Error(
        `Neither SQLite nor JSON data found for catalog: ${this.options.catalogName}`
      );
    }

    let useSqlite = false;

    if (hasSqlite && hasJson) {
      if (this.options.preferSqlite) {
        useSqlite = true;
      } else if (isNodeRuntime() && !adapter) {
        const stats = nodeFsStat(jsonFullPath);
        const sizeMB = stats.size / 1024 / 1024;
        useSqlite = sizeMB > this.options.sizeThresholdMB!;
      }
    } else if (hasSqlite) {
      useSqlite = true;
    }

    if (useSqlite) {
      if (adapter) {
        this.loadFromSqlite(adapter);
      } else {
        if (!isNodeRuntime()) {
          throw new Error(`SQLite adapter not configured for ${this.options.catalogName}`);
        }
        const betterSqlite3 = getBetterSqlite3();
        const db = new betterSqlite3(sqlitePath, { readonly: false, fileMustExist: false });
        this.loadFromSqlite(createBetterSqliteAdapter(db));
      }
      this._usingSqlite = true;
    } else {
      this.loadFromJson(jsonPath);
      this._usingSqlite = false;
    }
  }

  /**
   * Load data from SQLite database
   */
  protected loadFromSqlite(db: CatalogSqliteDatabase): void {
    // Si el DB no existe o está vacío, creamos un fallback mínimo para pruebas.
    this._db = db;
    this.ensureMinimalSchema(this._db);
  }

  /**
   * Creates minimal schema/seed when database is missing/empty.
   */
  protected ensureMinimalSchema(_db: CatalogSqliteDatabase): void {
    // Por defecto no hace nada; las subclases pueden sobreescribir si requieren seed.
  }

  /**
   * Load data from JSON file
   */
  protected abstract loadFromJson(jsonPath: string): void;

  /**
   * Get full path to SQLite database
   */
  protected getSqlitePath(): string {
    const dbName = this.options.sqlitePath || `${this.options.catalogName}.db`;
    if (!isNodeRuntime()) {
      return `sqlite/${dbName}`;
    }
    return resolveSharedDataPath(`sqlite/${dbName}`);
  }

  /**
   * Get full path to JSON file
   */
  protected getJsonPath(): string {
    if (!isNodeRuntime()) {
      return this.options.jsonPath;
    }
    return resolveSharedDataPath(this.options.jsonPath);
  }

  /**
   * Check if currently using SQLite backend
   */
  public isUsingSqlite(): boolean {
    return this._usingSqlite;
  }

  /**
   * Close SQLite database connection (call when done)
   */
  public close(): void {
    if (this._db) {
      this._db.close?.();
      this._db = null;
    }
  }

  /**
   * Get underlying SQLite database (if using SQLite)
   * Returns null if using JSON backend
   */
  protected getDb(): CatalogSqliteDatabase | null {
    return this._db;
  }

  /**
   * Get in-memory data (if using JSON)
   * Returns null if using SQLite backend
   */
  protected getData(): T[] | null {
    return this._data;
  }

  /**
   * Execute a SQL query (only if using SQLite)
   */
  protected query<R = unknown>(sql: string, params: unknown[] = []): R[] {
    if (!this._db) {
      throw new Error('SQLite database not initialized');
    }
    return this._db.prepare(sql).all(...(params as SqliteParam[])) as R[];
  }

  /**
   * Execute a SQL query and get first result (only if using SQLite)
   */
  protected queryOne<R = unknown>(sql: string, params: unknown[] = []): R | undefined {
    if (!this._db) {
      throw new Error('SQLite database not initialized');
    }
    return this._db.prepare(sql).get(...(params as SqliteParam[])) as R | undefined;
  }

  /**
   * Full-text search (uses FTS5 if SQLite, or fallback to filter if JSON)
   */
  protected abstract search(query: string, limit?: number): T[];

  /**
   * Get all records (paginated)
   */
  public abstract getAll(offset?: number, limit?: number): T[];

  /**
   * Get total count
   */
  public abstract count(): number;
}

function getBetterSqlite3(): typeof import('better-sqlite3') {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  return require('better-sqlite3');
}

function getNodeFs(): typeof import('fs') {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  return require('fs');
}

function nodeFsExists(value: string): boolean {
  if (!isNodeRuntime()) return false;
  const fs = getNodeFs();
  return fs.existsSync(value);
}

function nodeFsStat(value: string): import('fs').Stats {
  const fs = getNodeFs();
  return fs.statSync(value);
}
