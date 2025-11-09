/**
 * Hybrid catalog loader that supports both SQLite (for large catalogs) and JSON (for small catalogs)
 *
 * This maintains API parity between Python and TypeScript implementations.
 */

import * as path from 'path';
import * as fs from 'fs';
import Database from 'better-sqlite3';

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
  protected _db: Database.Database | null = null;
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
    const jsonPath = this.getJsonPath();

    // Check if SQLite database exists
    const hasSqlite = fs.existsSync(sqlitePath);
    const hasJson = fs.existsSync(jsonPath);

    if (!hasSqlite && !hasJson) {
      throw new Error(
        `Neither SQLite nor JSON data found for catalog: ${this.options.catalogName}`
      );
    }

    // Decide which to use
    let useSqlite = false;

    if (hasSqlite && hasJson) {
      // Both exist - check preferences and file sizes
      if (this.options.preferSqlite) {
        useSqlite = true;
      } else {
        // Check JSON file size
        const stats = fs.statSync(jsonPath);
        const sizeMB = stats.size / 1024 / 1024;
        useSqlite = sizeMB > this.options.sizeThresholdMB!;
      }
    } else if (hasSqlite) {
      useSqlite = true;
    }

    // Load from chosen source
    if (useSqlite) {
      this.loadFromSqlite(sqlitePath);
      this._usingSqlite = true;
    } else {
      this.loadFromJson(jsonPath);
      this._usingSqlite = false;
    }
  }

  /**
   * Load data from SQLite database
   */
  protected loadFromSqlite(dbPath: string): void {
    this._db = new Database(dbPath, { readonly: true, fileMustExist: true });
  }

  /**
   * Load data from JSON file
   */
  protected abstract loadFromJson(jsonPath: string): void;

  /**
   * Get full path to SQLite database
   */
  protected getSqlitePath(): string {
    const sqliteDir = path.resolve(
      __dirname,
      '../../../shared-data/sqlite'
    );
    const dbName =
      this.options.sqlitePath || `${this.options.catalogName}.db`;
    return path.join(sqliteDir, dbName);
  }

  /**
   * Get full path to JSON file
   */
  protected getJsonPath(): string {
    return path.resolve(__dirname, '../../../shared-data', this.options.jsonPath);
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
      this._db.close();
      this._db = null;
    }
  }

  /**
   * Get underlying SQLite database (if using SQLite)
   * Returns null if using JSON backend
   */
  protected getDb(): Database.Database | null {
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
  protected query<R = any>(sql: string, params: any[] = []): R[] {
    if (!this._db) {
      throw new Error('SQLite database not initialized');
    }
    return this._db.prepare(sql).all(...params) as R[];
  }

  /**
   * Execute a SQL query and get first result (only if using SQLite)
   */
  protected queryOne<R = any>(sql: string, params: any[] = []): R | undefined {
    if (!this._db) {
      throw new Error('SQLite database not initialized');
    }
    return this._db.prepare(sql).get(...params) as R | undefined;
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
