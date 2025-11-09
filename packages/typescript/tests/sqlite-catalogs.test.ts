import { CodigosPostalesCompletoSQLite } from '../src/catalogs/sepomex/codigos-postales-completo';

describe('CodigosPostalesCompletoSQLite', () => {
  it('should connect and retrieve data for a valid postal code', () => {
    const results = CodigosPostalesCompletoSQLite.getByCp('01000');
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].asentamiento).toBe('San Ángel');
    expect(results[0].municipio).toBe('Álvaro Obregón');
  });

  it('should return an empty array for a non-existent postal code', () => {
    const results = CodigosPostalesCompletoSQLite.getByCp('99999');
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBe(0);
  });

  it('should validate an existing postal code correctly', () => {
    const isValid = CodigosPostalesCompletoSQLite.isValid('06700');
    expect(isValid).toBe(true);
  });

  it('should invalidate a non-existent postal code', () => {
    const isValid = CodigosPostalesCompletoSQLite.isValid('99999');
    expect(isValid).toBe(false);
  });
});
