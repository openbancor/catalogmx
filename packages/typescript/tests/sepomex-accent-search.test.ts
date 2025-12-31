/**
 * Test accent-insensitive search in SEPOMEX catalogs
 *
 * This test verifies that searches without accents properly find results
 * with accents, which is critical for Spanish-speaking users.
 */

import { CodigosPostales } from '../src/catalogs/sepomex/codigos-postales';
import { normalizeText } from '../src/utils/text';

describe('SEPOMEX Accent-Insensitive Search', () => {
  describe('searchByAsentamiento', () => {
    it('should normalize text correctly for searching', () => {
      // This test verifies the normalization function works correctly
      // regardless of whether we have full SEPOMEX data loaded
      const normalizedWithAccent = normalizeText('Águilas');
      const normalizedWithoutAccent = normalizeText('Aguilas');

      expect(normalizedWithAccent).toBe(normalizedWithoutAccent);
      expect(normalizedWithAccent).toBe('AGUILAS');
    });

    it('should search case-insensitively', () => {
      // Test that search is case-insensitive (works with any data)
      const resultsUpper = CodigosPostales.searchByAsentamiento('CIUDAD');
      const resultsLower = CodigosPostales.searchByAsentamiento('ciudad');
      const resultsMixed = CodigosPostales.searchByAsentamiento('Ciudad');

      // All should return same results
      expect(resultsUpper.length).toBe(resultsLower.length);
      expect(resultsLower.length).toBe(resultsMixed.length);
    });

    it('should handle searches with accents the same as without', () => {
      // Test bidirectional accent-insensitive search
      const resultsWithAccent = CodigosPostales.searchByAsentamiento('México');
      const resultsWithoutAccent = CodigosPostales.searchByAsentamiento('Mexico');

      // Both should return same results (even if empty in test data)
      expect(resultsWithAccent.length).toBe(resultsWithoutAccent.length);
    });

    it('should work with test data available', () => {
      // Test with data that exists in test dataset
      const results = CodigosPostales.searchByAsentamiento('Centro');

      // Should return an array (empty or with results)
      expect(Array.isArray(results)).toBe(true);

      // If we have data, verify accent-insensitive search works
      if (results.length > 0) {
        const withAccent = CodigosPostales.searchByAsentamiento('Ángel');
        const withoutAccent = CodigosPostales.searchByAsentamiento('Angel');
        expect(withAccent.length).toBe(withoutAccent.length);
      }
    });
  });

  describe('getByMunicipio', () => {
    it('should be accent-insensitive for municipalities', () => {
      const resultsWithAccent = CodigosPostales.getByMunicipio('León');
      const resultsWithoutAccent = CodigosPostales.getByMunicipio('Leon');

      // Both should return same results (even if empty in test data)
      expect(resultsWithAccent.length).toBe(resultsWithoutAccent.length);
    });

    it('should return an array for any search', () => {
      const results = CodigosPostales.getByMunicipio('Peña');
      expect(Array.isArray(results)).toBe(true);
    });
  });

  describe('getByEstado', () => {
    it('should be accent-insensitive for states', () => {
      const resultsWithAccent = CodigosPostales.getByEstado('México');
      const resultsWithoutAccent = CodigosPostales.getByEstado('Mexico');

      // Both should return same results
      expect(resultsWithAccent.length).toBe(resultsWithoutAccent.length);
    });
  });

  describe('normalizeText utility', () => {
    it('should remove common Spanish accents', () => {
      const testCases: Record<string, string> = {
        'á': 'A',
        'é': 'E',
        'í': 'I',
        'ó': 'O',
        'ú': 'U',
        'Á': 'A',
        'É': 'E',
        'Í': 'I',
        'Ó': 'O',
        'Ú': 'U',
        'ñ': 'N',
        'Ñ': 'N',
      };

      for (const [accented, expected] of Object.entries(testCases)) {
        const result = normalizeText(accented);
        expect(result).toContain(expected);
      }
    });

    it('should normalize complete words', () => {
      expect(normalizeText('México')).toBe('MEXICO');
      expect(normalizeText('San José')).toBe('SAN JOSE');
      expect(normalizeText('Michoacán de Ocampo')).toBe('MICHOACAN DE OCAMPO');
      expect(normalizeText('Las Águilas')).toBe('LAS AGUILAS');
    });

    it('should convert to uppercase', () => {
      expect(normalizeText('aguilas')).toBe('AGUILAS');
      expect(normalizeText('AGUILAS')).toBe('AGUILAS');
      expect(normalizeText('Aguilas')).toBe('AGUILAS');
    });
  });
});
