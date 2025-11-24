declare module 'sql.js' {
  export interface Database {
    prepare(sql: string): Statement;
    run(sql: string, params?: unknown[]): void;
    exec(sql: string): QueryExecResult[];
    close(): void;
  }

  export interface Statement {
    bind(params?: unknown[]): boolean;
    step(): boolean;
    get(params?: unknown[]): (string | number | null)[];
    getAsObject(): Record<string, unknown>;
    getColumnNames(): string[];
    free(): boolean;
    reset(): void;
  }

  export interface QueryExecResult {
    columns: string[];
    values: unknown[][];
  }

  export interface SqlJsStatic {
    Database: new (data?: ArrayLike<number> | Buffer | null) => Database;
  }

  export interface SqlJsConfig {
    locateFile?: (filename: string) => string;
    wasmBinary?: ArrayBuffer;
  }

  export default function initSqlJs(config?: SqlJsConfig): Promise<SqlJsStatic>;
}

declare module 'sql.js/dist/sql-wasm.js' {
  import { SqlJsConfig, SqlJsStatic } from 'sql.js';
  const initSqlJs: (config?: SqlJsConfig) => Promise<SqlJsStatic>;
  export default initSqlJs;
}
