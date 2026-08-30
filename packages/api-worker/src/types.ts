export interface RateLimiterBinding {
  limit(options: { key: string }): Promise<{ success: boolean }>;
}

export interface D1PreparedStatement {
  bind(...values: unknown[]): D1PreparedStatement;
  all<T = Record<string, unknown>>(): Promise<{ results: T[] }>;
  first<T = Record<string, unknown>>(): Promise<T | null>;
}

export interface D1Database {
  prepare(query: string): D1PreparedStatement;
}

export interface Env {
  CATALOGMX_API_KEYS?: string;
  API_RATE_LIMITER?: RateLimiterBinding;
  CATALOG_DB?: D1Database;
}

export interface AuthenticatedClient {
  keyId: string;
}
