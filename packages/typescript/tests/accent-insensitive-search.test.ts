/**
 * Tests for accent-insensitive search across all catalogs
 *
 * Tests the normalizeText utility and accent-insensitive search functionality
 * in all catalogs that support it.
 */

import { normalizeText, normalizeForSearch } from '../src/utils/text';

describe('Text Normalization Utilities', () => {
  describe('normalizeText', () => {
    it('should remove accents from Spanish text', () => {
      expect(normalizeText('México')).toBe('MEXICO');
      expect(normalizeText('Querétaro')).toBe('QUERETARO');
      expect(normalizeText('San José')).toBe('SAN JOSE');
    });

    it('should convert text to uppercase', () => {
      expect(normalizeText('mexico')).toBe('MEXICO');
      expect(normalizeText('MeXiCo')).toBe('MEXICO');
      expect(normalizeText('MEXICO')).toBe('MEXICO');
    });

    it('should handle special characters', () => {
      expect(normalizeText('Ñoño')).toBe('NONO');
      expect(normalizeText('Müller')).toBe('MULLER');
      expect(normalizeText('François')).toBe('FRANCOIS');
    });

    it('should handle empty strings and whitespace', () => {
      expect(normalizeText('')).toBe('');
      expect(normalizeText('  ')).toBe('  ');
      expect(normalizeText('  México  ')).toBe('  MEXICO  ');
    });

    it('should handle all Spanish accented vowels', () => {
      expect(normalizeText('á é í ó ú')).toBe('A E I O U');
      expect(normalizeText('Á É Í Ó Ú')).toBe('A E I O U');
    });

    it('should handle diacriticals and tildes', () => {
      expect(normalizeText('ñ')).toBe('N');
      expect(normalizeText('Ñ')).toBe('N');
      expect(normalizeText('ü')).toBe('U');
      expect(normalizeText('Ü')).toBe('U');
    });
  });

  describe('normalizeForSearch', () => {
    it('should be an alias for normalizeText', () => {
      const testCases = ['México', 'Querétaro', 'San José'];
      testCases.forEach((text) => {
        expect(normalizeForSearch(text)).toBe(normalizeText(text));
      });
    });
  });
});

describe('Accent-Insensitive Search Consistency', () => {
  describe('Multiple accent combinations', () => {
    const testCases: Array<[string, string, string]> = [
      ['México', 'Mexico', 'MEXICO'],
      ['Querétaro', 'Queretaro', 'QUERETARO'],
      ['Michoacán', 'Michoacan', 'MICHOACAN'],
      ['Yucatán', 'Yucatan', 'YUCATAN'],
      ['Jalisco', 'jalisco', 'JALISCO'],
    ];

    testCases.forEach(([withAccent, withoutAccent, expected]) => {
      it(`should normalize ${withAccent} and ${withoutAccent} to ${expected}`, () => {
        expect(normalizeText(withAccent)).toBe(expected);
        expect(normalizeText(withoutAccent)).toBe(expected);
        expect(normalizeText(withAccent)).toBe(normalizeText(withoutAccent));
      });
    });
  });

  describe('Case insensitivity', () => {
    it('should normalize different cases to same result', () => {
      const variations = ['méxico', 'México', 'MÉXICO', 'MéXiCo'];
      const normalized = variations.map((v) => normalizeText(v));
      expect(new Set(normalized).size).toBe(1);
      expect(normalized[0]).toBe('MEXICO');
    });
  });

  describe('Special Mexican names and places', () => {
    it('should handle common Mexican state names', () => {
      expect(normalizeText('Nuevo León')).toBe('NUEVO LEON');
      expect(normalizeText('San Luis Potosí')).toBe('SAN LUIS POTOSI');
      expect(normalizeText('Michoacán de Ocampo')).toBe('MICHOACAN DE OCAMPO');
    });

    it('should handle common Mexican city names', () => {
      expect(normalizeText('Ciudad Juárez')).toBe('CIUDAD JUAREZ');
      expect(normalizeText('Mérida')).toBe('MERIDA');
      expect(normalizeText('Cancún')).toBe('CANCUN');
    });
  });

  describe('Substring matching with accents', () => {
    it('should allow partial matches regardless of accents', () => {
      const normalized1 = normalizeText('José Luis García Pérez');
      const normalized2 = normalizeText('Jose Luis Garcia Perez');
      expect(normalized1).toBe(normalized2);
      expect(normalized1).toContain('JOSE');
      expect(normalized1).toContain('GARCIA');
      expect(normalized1).toContain('PEREZ');
    });
  });

  describe('Edge cases', () => {
    it('should handle numbers and symbols', () => {
      expect(normalizeText('México 123')).toBe('MEXICO 123');
      expect(normalizeText('San José #45')).toBe('SAN JOSE #45');
    });

    it('should handle multiple consecutive accents', () => {
      expect(normalizeText('áéíóú')).toBe('AEIOU');
      expect(normalizeText('ÁÉÍÓÚ')).toBe('AEIOU');
    });

    it('should handle mixed scripts if present', () => {
      // Should handle gracefully even if unusual
      expect(normalizeText('México-USA')).toBe('MEXICO-USA');
    });
  });
});

describe('Performance and Safety', () => {
  it('should handle very long strings', () => {
    const longString = 'á'.repeat(10000);
    const result = normalizeText(longString);
    expect(result).toBe('A'.repeat(10000));
  });

  it('should handle empty array of strings', () => {
    const strings: string[] = [];
    strings.forEach((s) => {
      expect(() => normalizeText(s)).not.toThrow();
    });
  });

  it('should be idempotent', () => {
    const text = 'México';
    const once = normalizeText(text);
    const twice = normalizeText(once);
    expect(once).toBe(twice);
  });
});

describe('Real-world Mexican data patterns', () => {
  it('should handle common postal code locality names', () => {
    const localities = [
      'Colonia Juárez',
      'Centro Histórico',
      'Polanco',
      'Santa María',
      'San Ángel',
    ];

    localities.forEach((locality) => {
      const normalized = normalizeText(locality);
      expect(normalized).toBe(normalized.toUpperCase());
      expect(normalized).not.toMatch(/[áéíóúñü]/i);
    });
  });

  it('should handle state names from INEGI catalog', () => {
    const states = [
      'México',
      'Nuevo León',
      'Querétaro',
      'Yucatán',
      'Michoacán',
      'San Luis Potosí',
    ];

    states.forEach((state) => {
      const normalized = normalizeText(state);
      expect(normalized).not.toMatch(/[áéíóúñ]/);
    });
  });

  it('should handle airport and port names', () => {
    const locations = [
      'Cancún',
      'Ciudad de México',
      'Guadalajara',
      'Monterrey',
      'Mérida',
    ];

    locations.forEach((location) => {
      const withAccents = normalizeText(location);
      const withoutAccents = normalizeText(
        location
          .replace(/á/g, 'a')
          .replace(/é/g, 'e')
          .replace(/í/g, 'i')
          .replace(/ó/g, 'o')
          .replace(/ú/g, 'u')
      );
      expect(withAccents).toBe(withoutAccents);
    });
  });
});
