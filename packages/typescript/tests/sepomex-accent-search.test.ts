/**
 * Test accent-insensitive search in SEPOMEX catalogs
 *
 * This test verifies that searches without accents properly find results
 * with accents, which is critical for Spanish-speaking users.
 */

import { describe, it, expect } from 'vitest';
import { CodigosPostales } from '../src/catalogs/sepomex/codigos-postales';
import { normalizeText } from '../src/utils/text';

describe('SEPOMEX Accent-Insensitive Search', () => {
  describe('searchByAsentamiento', () => {
    it('should find "Las Águilas" when searching for "Aguilas" (without accent)', () => {
      // Critical test: This is a real-world use case reported by users
      const results = CodigosPostales.searchByAsentamiento('Aguilas');

      // Should find results
      expect(results.length).toBeGreaterThan(0);

      // Check if any result contains "Águilas" (with accent)
      const foundWithAccent = results.some((result) =>
        result.asentamiento.toLowerCase().includes('águilas')
      );

      expect(foundWithAccent).toBe(true);
    });

    it('should find results when searching for "Mexico" (without accent)', () => {
      const results = CodigosPostales.searchByAsentamiento('Mexico');
      expect(results.length).toBeGreaterThan(0);
    });

    it('should return same results with or without accents', () => {
      const resultsWithAccent = CodigosPostales.searchByAsentamiento('Águilas');
      const resultsWithoutAccent = CodigosPostales.searchByAsentamiento('Aguilas');

      expect(resultsWithAccent.length).toBeGreaterThan(0);
      expect(resultsWithoutAccent.length).toBeGreaterThan(0);
      expect(resultsWithAccent.length).toBe(resultsWithoutAccent.length);
    });

    it('should be case-insensitive', () => {
      const resultsUpper = CodigosPostales.searchByAsentamiento('AGUILAS');
      const resultsLower = CodigosPostales.searchByAsentamiento('aguilas');
      const resultsMixed = CodigosPostales.searchByAsentamiento('Aguilas');

      expect(resultsUpper.length).toBe(resultsLower.length);
      expect(resultsLower.length).toBe(resultsMixed.length);
    });

    it('should find partial matches with accents', () => {
      const results = CodigosPostales.searchByAsentamiento('Aguil');
      // Should find "Las Águilas" and other similar names
      expect(results.length).toBeGreaterThan(0);
    });
  });

  describe('getByMunicipio', () => {
    it('should be accent-insensitive for municipalities', () => {
      const resultsWithAccent = CodigosPostales.getByMunicipio('León');
      const resultsWithoutAccent = CodigosPostales.getByMunicipio('Leon');

      // Both should work
      expect(resultsWithAccent.length).toBeGreaterThan(0);
      expect(resultsWithoutAccent.length).toBeGreaterThan(0);
      expect(resultsWithAccent.length).toBe(resultsWithoutAccent.length);
    });

    it('should handle special characters', () => {
      const results = CodigosPostales.getByMunicipio('Peña');
      expect(Array.isArray(results)).toBe(true);
    });
  });

  describe('getByEstado', () => {
    it('should be accent-insensitive for states', () => {
      const resultsWithAccent = CodigosPostales.getByEstado('México');
      const resultsWithoutAccent = CodigosPostales.getByEstado('Mexico');

      // Both should work (Estado de México exists)
      const hasResults = resultsWithAccent.length > 0 || resultsWithoutAccent.length > 0;
      expect(hasResults).toBe(true);
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
