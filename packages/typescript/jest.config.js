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

  // Coverage thresholds based on actual codebase characteristics:
  // - Heavy catalog data code (35-50% coverage due to infrastructure)
  // - High-value validators and calculators (75-85% coverage)
  // - Thresholds set slightly below actual to allow for minor fluctuations
  coverageThreshold: {
    global: {
      // Global thresholds account for catalog infrastructure code
      // Actual coverage: statements ~53%, branches ~38%, functions ~42%, lines ~56%
      branches: 35,
      functions: 40,
      lines: 50,
      statements: 50,
    },
    // Validators: Core business logic - must maintain high coverage
    // Actual coverage: statements ~81%, branches ~59%, functions ~79%, lines ~78%
    './src/validators/': {
      branches: 55,
      functions: 75,
      lines: 75,
      statements: 75,
    },
    // Calculators: Fiscal calculations - critical accuracy required
    // Actual coverage: statements ~76%, branches ~43%, functions ~72%, lines ~75%
    './src/calculators/': {
      branches: 40,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
