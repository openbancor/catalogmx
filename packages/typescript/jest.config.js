/**
 * Jest configuration for catalogmx TypeScript package
 *
 * Coverage Exclusion Philosophy:
 * We exclude infrastructure/adapter code that:
 * 1. Requires external dependencies (network, databases, file system)
 * 2. Contains platform-specific code (Node.js vs browser)
 * 3. Is pure boilerplate (type definitions, re-exports)
 * 4. Is data loading infrastructure (SQLite wrappers, catalog loaders)
 *
 * All business logic (validators, calculators, data transformations)
 * MUST be tested. The core functionality coverage remains high.
 *
 * Coverage Breakdown (as of 2025-01):
 * - Validators: ~80% (high-value business logic)
 * - Calculators: ~75% (fiscal calculations)
 * - Catalogs: ~35-50% (data loading, much is infrastructure)
 * - Utils: ~55% (mix of testable logic and platform code)
 */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',

    // =========================================================================
    // TYPE DEFINITIONS - No runtime code
    // =========================================================================
    '!src/**/*.d.ts',
    '!src/types/**/*',

    // =========================================================================
    // INFRASTRUCTURE: Network & Database Adapters
    // Requires mocking external services (fetch, SQLite bindings)
    // =========================================================================

    // HTTP VFS: Browser-only, requires fetch API and localStorage mocking
    '!src/data/http-vfs-updater.ts',

    // SQLite adapters: Pure bridge code wrapping better-sqlite3/sql.js
    // These are thin wrappers that delegate to external libraries
    '!src/utils/sqlite-adapter.ts',

    // =========================================================================
    // INFRASTRUCTURE: Catalog Data Loaders
    // SQLite-based catalog variants - pure data retrieval, no business logic
    // The JSON versions of these catalogs ARE tested
    // =========================================================================

    // Banxico SQLite loaders - time-series data from database
    '!src/catalogs/banxico/*-sqlite.ts',

    // =========================================================================
    // RE-EXPORT INDEX FILES - No logic, just module organization
    // =========================================================================
    '!src/index.ts',
    '!src/catalogs/**/index.ts',
    '!src/calculators/index.ts',
    '!src/validators/index.ts',
  ],
  coverageReporters: ['text', 'lcov', 'json-summary', 'html'],
  coverageDirectory: 'coverage',

  coverageThreshold: {
    global: {
      branches: 58,
      functions: 82,
      lines: 82,
      statements: 80,
    },
    './src/validators/': {
      branches: 58,
      functions: 79,
      lines: 80,
      statements: 77,
    },
    './src/calculators/': {
      branches: 43,
      functions: 72,
      lines: 75,
      statements: 76,
    },
  },
};
