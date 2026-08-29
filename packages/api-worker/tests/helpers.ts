export const TEST_API_KEY = 'test-api-key';
export const TEST_API_KEY_DIGEST =
  '4c806362b613f7496abf284146efd31da90e4b16169fe001841ca17290f427c4';

import type { D1Database, D1PreparedStatement } from '../src/types';

export class RecordingD1 implements D1Database {
  readonly queries: Array<{ sql: string; values: unknown[] }> = [];
  rows: Record<string, unknown>[] = [];

  prepare(sql: string): D1PreparedStatement {
    const statement: D1PreparedStatement = {
      bind: (...values: unknown[]): D1PreparedStatement => {
        this.queries.push({ sql, values });
        return statement;
      },
      all: async <T>(): Promise<{ results: T[] }> => ({ results: this.rows as T[] }),
      first: async <T>(): Promise<T | null> => (this.rows[0] as T | undefined) ?? null,
    };
    return statement;
  }
}

export function authorizedEnv(): Record<string, unknown> {
  return {
    CATALOGMX_API_KEYS: JSON.stringify([
      { id: 'test-client', active: true, digest: TEST_API_KEY_DIGEST },
    ]),
    API_RATE_LIMITER: {
      limit: async () => ({ success: true }),
    },
  };
}
