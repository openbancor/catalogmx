declare module 'sql.js-httpvfs' {
  export interface SqliteHttpVfsConfigInline {
    serverMode: 'full' | 'chunked';
    requestChunkSize: number;
    url: string;
    cacheBust?: string;
  }

  export interface SqliteHttpVfsConfig {
    from: 'inline' | 'jsonconfig';
    config?: SqliteHttpVfsConfigInline;
    configUrl?: string;
    virtualFilename?: string;
  }

  export interface SqliteHttpVfsStatement {
    bind(params?: (string | number | null)[]): Promise<boolean>;
    step(): Promise<boolean>;
    getAsObject(params?: Record<string, unknown>): Promise<Record<string, unknown>>;
    free(): Promise<boolean>;
    reset(): Promise<void>;
  }

  export interface SqliteHttpVfsDatabase {
    exec(sql: string): Promise<{ columns: string[]; values: unknown[][] }[]>;
    prepare(sql: string): Promise<SqliteHttpVfsStatement>;
  }

  export interface SqliteHttpVfsWorker {
    db: SqliteHttpVfsDatabase;
    worker: { bytesRead: number | Promise<number> };
    configs: SqliteHttpVfsConfig[];
  }

  export function createDbWorker(
    configs: SqliteHttpVfsConfig[],
    workerUrl: string,
    wasmUrl: string,
    maxBytesToRead?: number
  ): Promise<SqliteHttpVfsWorker>;
}
