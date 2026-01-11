/**
 * SQLite adapter utilities for Node (better-sqlite3) and browser (sql.js).
 */

import type { Database as SqlJsDatabase, Statement as SqlJsStatement } from 'sql.js';

export type SqliteParam = string | number | null;

export interface CatalogSqliteStatement {
  all(...params: SqliteParam[]): Record<string, unknown>[];
  get(...params: SqliteParam[]): Record<string, unknown> | undefined;
  run?(params?: SqliteParam[] | Record<string, unknown>): void;
}

export interface CatalogSqliteDatabase {
  prepare(sql: string): CatalogSqliteStatement;
  exec(sql: string): void;
  close?: () => void;
}

export function createBetterSqliteAdapter(db: {
  prepare: (sql: string) => unknown;
  exec: (sql: string) => void;
  close?: () => void;
}): CatalogSqliteDatabase {
  return {
    prepare: (sql: string) => {
      const stmt = db.prepare(sql) as {
        all: (...params: SqliteParam[]) => Record<string, unknown>[];
        get: (...params: SqliteParam[]) => Record<string, unknown> | undefined;
        run: (params?: SqliteParam[] | Record<string, unknown>) => void;
      };
      return {
        all: (...params: SqliteParam[]) => stmt.all(...params),
        get: (...params: SqliteParam[]) => stmt.get(...params),
        run: (params?: SqliteParam[] | Record<string, unknown>) => stmt.run(params),
      };
    },
    exec: (sql: string) => db.exec(sql),
    close: () => {
      db.close?.();
    },
  };
}

export function createSqlJsAdapter(db: SqlJsDatabase): CatalogSqliteDatabase {
  return {
    prepare: (sql: string) => {
      const stmt = db.prepare(sql);
      return createSqlJsStatement(stmt);
    },
    exec: (sql: string) => {
      db.exec(sql);
    },
    close: () => {
      db.close();
    },
  };
}

function createSqlJsStatement(stmt: SqlJsStatement): CatalogSqliteStatement {
  const bindAndCollect = (params: SqliteParam[], takeFirst: boolean) => {
    const rows: Record<string, unknown>[] = [];
    stmt.bind(params);
    while (stmt.step()) {
      const row = stmt.getAsObject() as Record<string, unknown>;
      rows.push(row);
      if (takeFirst) break;
    }
    stmt.reset();
    return rows;
  };

  return {
    all: (...params: SqliteParam[]) => {
      const rows = bindAndCollect(params, false);
      return rows;
    },
    get: (...params: SqliteParam[]) => {
      const rows = bindAndCollect(params, true);
      return rows[0];
    },
    run: (params?: SqliteParam[] | Record<string, unknown>) => {
      if (params) {
        stmt.bind(params as unknown as SqliteParam[]);
      }
      stmt.step();
      stmt.reset();
    },
  };
}
