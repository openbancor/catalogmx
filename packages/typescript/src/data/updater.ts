/**
 * Data Updater for TypeScript/JavaScript
 *
 * Provides automatic updates of dynamic Banxico data from GitHub Releases
 * Works in both Node.js and browser environments
 */

// Environment detection
const isNode = typeof process !== 'undefined' && process.versions?.node;
const isBrowser = typeof window !== 'undefined';

interface VersionInfo {
  version: string;
  updated_at: string;
  source: string;
  url?: string;
}

interface DataUpdaterConfig {
  cacheDir?: string;
  maxAgeHours?: number;
  dataUrl?: string;
  autoUpdate?: boolean;
}

const DEFAULT_CONFIG: Required<DataUpdaterConfig> = {
  cacheDir: '.catalogmx',
  maxAgeHours: 24,
  dataUrl: 'https://github.com/openbancor/catalogmx/releases/download/latest/mexico_dynamic.sqlite3',
  autoUpdate: true,
};

/**
 * Data Updater for Node.js environment
 */
class NodeDataUpdater {
  private config: Required<DataUpdaterConfig>;
  private cacheDbPath: string;
  private versionFilePath: string;

  constructor(config: DataUpdaterConfig = {}) {
    if (!isNode) {
      throw new Error('NodeDataUpdater can only be used in Node.js environment');
    }

    this.config = { ...DEFAULT_CONFIG, ...config };

    const os = require('os');
    const path = require('path');
    const cacheDir = path.join(os.homedir(), this.config.cacheDir);

    this.cacheDbPath = path.join(cacheDir, 'mexico_dynamic.sqlite3');
    this.versionFilePath = path.join(cacheDir, 'version.json');
  }

  async getLocalVersion(): Promise<string | null> {
    const fs = require('fs').promises;
    try {
      const data = await fs.readFile(this.versionFilePath, 'utf-8');
      const info: VersionInfo = JSON.parse(data);
      return info.version;
    } catch {
      return null;
    }
  }

  async getLocalAgeHours(): Promise<number | null> {
    const fs = require('fs').promises;
    try {
      const data = await fs.readFile(this.versionFilePath, 'utf-8');
      const info: VersionInfo = JSON.parse(data);
      const updated = new Date(info.updated_at);
      const now = new Date();
      return (now.getTime() - updated.getTime()) / (1000 * 60 * 60);
    } catch {
      return null;
    }
  }

  async downloadLatest(force = false, verbose = true): Promise<boolean> {
    const fs = require('fs').promises;
    const path = require('path');
    const https = require('https');

    if (verbose) {
      console.log(`📥 Downloading data from ${this.config.dataUrl}...`);
    }

    try {
      // Ensure cache directory exists
      const cacheDir = path.dirname(this.cacheDbPath);
      await fs.mkdir(cacheDir, { recursive: true });

      // Download to temporary file
      const tempPath = `${this.cacheDbPath}.tmp`;
      const file = await fs.open(tempPath, 'w');

      await new Promise<void>((resolve, reject) => {
        https.get(this.config.dataUrl, (response: any) => {
          if (response.statusCode !== 200) {
            reject(new Error(`HTTP ${response.statusCode}`));
            return;
          }

          const writeStream = require('fs').createWriteStream('', { fd: file.fd });
          response.pipe(writeStream);

          writeStream.on('finish', () => resolve());
          writeStream.on('error', reject);
        }).on('error', reject);
      });

      await file.close();

      // Verify database integrity
      const betterSqlite3 = require('better-sqlite3');
      const db = betterSqlite3(tempPath, { readonly: true });
      const row = db.prepare('SELECT value FROM _metadata WHERE key = ?').get('version');
      const version = row?.value;
      db.close();

      if (!version) {
        await fs.unlink(tempPath);
        if (verbose) console.error('❌ Downloaded database is invalid');
        return false;
      }

      // Move to cache
      await fs.rename(tempPath, this.cacheDbPath);

      // Save metadata
      const versionInfo: VersionInfo = {
        version,
        updated_at: new Date().toISOString(),
        source: 'github_releases',
        url: this.config.dataUrl,
      };
      await fs.writeFile(this.versionFilePath, JSON.stringify(versionInfo, null, 2));

      if (verbose) {
        console.log(`✅ Data updated to version ${version}`);
      }
      return true;
    } catch (error) {
      if (verbose) {
        console.error(`❌ Error downloading data:`, error);
      }
      return false;
    }
  }

  async autoUpdate(verbose = false): Promise<string> {
    if (!this.config.autoUpdate) {
      const fs = require('fs');
      if (fs.existsSync(this.cacheDbPath)) {
        return this.cacheDbPath;
      }
      // Fallback to embedded
      return require.resolve('catalogmx/dist/data/mexico_dynamic.sqlite3');
    }

    const age = await this.getLocalAgeHours();

    // Update if no cache or too old
    if (age === null || age > this.config.maxAgeHours) {
      await this.downloadLatest(false, verbose);
    }

    // Return cache if exists
    const fs = require('fs');
    if (fs.existsSync(this.cacheDbPath)) {
      return this.cacheDbPath;
    }

    // Fallback to embedded
    if (verbose) {
      console.warn('⚠️  Using embedded data (may be outdated)');
    }
    return require.resolve('catalogmx/dist/data/mexico_dynamic.sqlite3');
  }

  async getDatabasePath(autoUpdate = true): Promise<string> {
    if (autoUpdate) {
      return this.autoUpdate();
    }

    const fs = require('fs');
    if (fs.existsSync(this.cacheDbPath)) {
      return this.cacheDbPath;
    }

    return require.resolve('catalogmx/dist/data/mexico_dynamic.sqlite3');
  }

  async clearCache(): Promise<boolean> {
    const fs = require('fs').promises;
    try {
      await fs.unlink(this.cacheDbPath);
      await fs.unlink(this.versionFilePath);
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Data Updater for Browser environment using IndexedDB cache
 */
class BrowserDataUpdater {
  private config: Required<DataUpdaterConfig>;
  private dbName = 'catalogmx_cache';
  private storeName = 'database';

  constructor(config: DataUpdaterConfig = {}) {
    if (!isBrowser) {
      throw new Error('BrowserDataUpdater can only be used in browser environment');
    }

    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  private openDB(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName);
        }
      };
    });
  }

  async getLocalVersion(): Promise<string | null> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(this.storeName, 'readonly');
      const store = tx.objectStore(this.storeName);
      const request = store.get('version');

      request.onsuccess = () => {
        const info: VersionInfo | undefined = request.result;
        resolve(info?.version ?? null);
      };
      request.onerror = () => reject(request.error);
    });
  }

  async getLocalAgeHours(): Promise<number | null> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(this.storeName, 'readonly');
      const store = tx.objectStore(this.storeName);
      const request = store.get('version');

      request.onsuccess = () => {
        const info: VersionInfo | undefined = request.result;
        if (!info?.updated_at) {
          resolve(null);
          return;
        }
        const updated = new Date(info.updated_at);
        const now = new Date();
        resolve((now.getTime() - updated.getTime()) / (1000 * 60 * 60));
      };
      request.onerror = () => reject(request.error);
    });
  }

  async downloadLatest(force = false, verbose = true): Promise<boolean> {
    if (verbose) {
      console.log(`📥 Downloading data from ${this.config.dataUrl}...`);
    }

    try {
      const response = await fetch(this.config.dataUrl);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const buffer = await response.arrayBuffer();
      const data = new Uint8Array(buffer);

      // Verify using sql.js
      const SQL = await import('sql.js');
      const sqljs = await SQL.default({
        locateFile: (file: string) => `https://sql.js.org/dist/${file}`,
      });

      const db = new sqljs.Database(data);
      const result = db.exec('SELECT value FROM _metadata WHERE key = "version"');
      const version = result[0]?.values[0]?.[0] as string;
      db.close();

      if (!version) {
        if (verbose) console.error('❌ Downloaded database is invalid');
        return false;
      }

      // Store in IndexedDB
      const idb = await this.openDB();
      const tx = idb.transaction(this.storeName, 'readwrite');
      const store = tx.objectStore(this.storeName);

      const versionInfo: VersionInfo = {
        version,
        updated_at: new Date().toISOString(),
        source: 'github_releases',
        url: this.config.dataUrl,
      };

      store.put(versionInfo, 'version');
      store.put(data, 'database');

      await new Promise<void>((resolve, reject) => {
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      });

      if (verbose) {
        console.log(`✅ Data updated to version ${version}`);
      }
      return true;
    } catch (error) {
      if (verbose) {
        console.error(`❌ Error downloading data:`, error);
      }
      return false;
    }
  }

  async getDatabaseBuffer(): Promise<Uint8Array | null> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(this.storeName, 'readonly');
      const store = tx.objectStore(this.storeName);
      const request = store.get('database');

      request.onsuccess = () => resolve(request.result ?? null);
      request.onerror = () => reject(request.error);
    });
  }

  async autoUpdate(verbose = false): Promise<Uint8Array> {
    if (this.config.autoUpdate) {
      const age = await this.getLocalAgeHours();

      // Update if no cache or too old
      if (age === null || age > this.config.maxAgeHours) {
        await this.downloadLatest(false, verbose);
      }
    }

    // Try cached version
    const cached = await this.getDatabaseBuffer();
    if (cached) {
      return cached;
    }

    // Fallback: download embedded or throw
    if (verbose) {
      console.warn('⚠️  No cached data, downloading...');
    }
    await this.downloadLatest(false, verbose);

    const buffer = await this.getDatabaseBuffer();
    if (!buffer) {
      throw new Error('Failed to load database');
    }

    return buffer;
  }

  async clearCache(): Promise<boolean> {
    try {
      const db = await this.openDB();
      const tx = db.transaction(this.storeName, 'readwrite');
      const store = tx.objectStore(this.storeName);
      store.delete('version');
      store.delete('database');

      await new Promise<void>((resolve, reject) => {
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      });

      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Universal Data Updater (auto-detects environment)
 */
export class DataUpdater {
  private updater: NodeDataUpdater | BrowserDataUpdater;

  constructor(config: DataUpdaterConfig = {}) {
    if (isNode) {
      this.updater = new NodeDataUpdater(config);
    } else if (isBrowser) {
      this.updater = new BrowserDataUpdater(config);
    } else {
      throw new Error('Unsupported environment');
    }
  }

  async getLocalVersion(): Promise<string | null> {
    return this.updater.getLocalVersion();
  }

  async getLocalAgeHours(): Promise<number | null> {
    return this.updater.getLocalAgeHours();
  }

  async downloadLatest(force = false, verbose = true): Promise<boolean> {
    return this.updater.downloadLatest(force, verbose);
  }

  async clearCache(): Promise<boolean> {
    return this.updater.clearCache();
  }

  /**
   * For Node.js: returns file path
   * For Browser: returns Uint8Array buffer
   */
  async getDatabasePath(): Promise<string | Uint8Array> {
    if (this.updater instanceof NodeDataUpdater) {
      return this.updater.getDatabasePath();
    } else {
      return (this.updater as BrowserDataUpdater).autoUpdate();
    }
  }
}

// Singleton instance
let _defaultUpdater: DataUpdater | null = null;

export function getDataUpdater(config?: DataUpdaterConfig): DataUpdater {
  if (!_defaultUpdater) {
    _defaultUpdater = new DataUpdater(config);
  }
  return _defaultUpdater;
}

// Convenience functions
export async function getDatabasePath(): Promise<string | Uint8Array> {
  return getDataUpdater().getDatabasePath();
}

export async function getVersion(): Promise<string | null> {
  return getDataUpdater().getLocalVersion();
}

export async function updateNow(force = false, verbose = true): Promise<boolean> {
  return getDataUpdater().downloadLatest(force, verbose);
}
