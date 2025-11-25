let hasNativeSqlite = true;
let CodigosPostalesCompletoSQLite: typeof import('../src/catalogs/sepomex/codigos-postales-completo').CodigosPostalesCompletoSQLite | undefined;

try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  CodigosPostalesCompletoSQLite = require('../src/catalogs/sepomex/codigos-postales-completo').CodigosPostalesCompletoSQLite;
} catch (err) {
  hasNativeSqlite = false;
  // eslint-disable-next-line no-console
  console.warn('[sqlite-tests] skipping sqlite tests:', (err as Error)?.message);
}

// Validate runtime availability (bindings may load but fail at open)
if (hasNativeSqlite && CodigosPostalesCompletoSQLite) {
  try {
    CodigosPostalesCompletoSQLite.isValid('01000');
  } catch (err) {
    hasNativeSqlite = false;
    // eslint-disable-next-line no-console
    console.warn('[sqlite-tests] skipping sqlite tests (runtime):', (err as Error)?.message);
  }
}

const describeIfAvailable = hasNativeSqlite ? describe : describe.skip;
const itIfAvailable = hasNativeSqlite ? it : it.skip;

describeIfAvailable('CodigosPostalesCompletoSQLite', () => {
  itIfAvailable('should connect and retrieve data for a valid postal code', () => {
    const results = CodigosPostalesCompletoSQLite!.getByCp('01000');
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].asentamiento).toBe('San Ángel');
    expect(results[0].municipio).toBe('Álvaro Obregón');
  });

  itIfAvailable('should return an empty array for a non-existent postal code', () => {
    const results = CodigosPostalesCompletoSQLite!.getByCp('99999');
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBe(0);
  });

  itIfAvailable('should validate an existing postal code correctly', () => {
    const isValid = CodigosPostalesCompletoSQLite!.isValid('06700');
    expect(isValid).toBe(true);
  });

  itIfAvailable('should invalidate a non-existent postal code', () => {
    const isValid = CodigosPostalesCompletoSQLite!.isValid('99999');
    expect(isValid).toBe(false);
  });
});
