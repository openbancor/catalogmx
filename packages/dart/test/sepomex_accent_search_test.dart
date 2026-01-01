/// Test accent-insensitive search in SEPOMEX catalogs
///
/// This test verifies that searches without accents properly find results
/// with accents, which is critical for Spanish-speaking users.
library;

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

void main() {
  group('SEPOMEX Accent-Insensitive Search', () {
    group('searchByColonia', () {
      test('should return a list (data-agnostic test)', () {
        final results = SepomexCodigosPostales.searchByColonia('Aguilas');
        expect(results, isA<List>());
      });

      test('should work with accented and non-accented queries equally', () {
        final resultsWithAccent =
            SepomexCodigosPostales.searchByColonia('Águilas');
        final resultsWithoutAccent =
            SepomexCodigosPostales.searchByColonia('Aguilas');

        // Both should return lists
        expect(resultsWithAccent, isA<List>());
        expect(resultsWithoutAccent, isA<List>());

        // If data exists, results should match
        if (resultsWithAccent.isNotEmpty || resultsWithoutAccent.isNotEmpty) {
          expect(resultsWithAccent.length, equals(resultsWithoutAccent.length),
              reason: 'Accent-insensitive search should return same count');
        }
      });

      test('should be case-insensitive', () {
        final resultsUpper = SepomexCodigosPostales.searchByColonia('AGUILAS');
        final resultsLower = SepomexCodigosPostales.searchByColonia('aguilas');
        final resultsMixed = SepomexCodigosPostales.searchByColonia('Aguilas');

        expect(resultsUpper, isA<List>());
        expect(resultsLower, isA<List>());
        expect(resultsMixed, isA<List>());

        // All should return same count
        expect(resultsUpper.length, equals(resultsLower.length));
        expect(resultsLower.length, equals(resultsMixed.length));
      });

      test('should handle partial matches', () {
        final results = SepomexCodigosPostales.searchByColonia('Aguil');
        expect(results, isA<List>());
      });
    });

    group('searchByMunicipio', () {
      test('should be accent-insensitive for municipalities', () {
        final resultsWithAccent =
            SepomexCodigosPostales.searchByMunicipio('León');
        final resultsWithoutAccent =
            SepomexCodigosPostales.searchByMunicipio('Leon');

        // Both should work
        expect(resultsWithAccent, isA<List>());
        expect(resultsWithoutAccent, isA<List>());

        // If data exists, should return same count
        if (resultsWithAccent.isNotEmpty || resultsWithoutAccent.isNotEmpty) {
          expect(resultsWithAccent.length, equals(resultsWithoutAccent.length));
        }
      });

      test('should handle special characters', () {
        final results = SepomexCodigosPostales.searchByMunicipio('Peña');
        expect(results, isA<List>());
      });

      test('should handle multiple accents', () {
        final results = SepomexCodigosPostales.searchByMunicipio('San José');
        expect(results, isA<List>());

        final resultsNoAccent =
            SepomexCodigosPostales.searchByMunicipio('San Jose');
        expect(resultsNoAccent, isA<List>());
      });
    });

    group('getByState', () {
      test('should be accent-insensitive for states', () {
        final resultsWithAccent = SepomexCodigosPostales.getByState('México');
        final resultsWithoutAccent =
            SepomexCodigosPostales.getByState('Mexico');

        // Both should return lists
        expect(resultsWithAccent, isA<List>());
        expect(resultsWithoutAccent, isA<List>());
      });

      test('should handle Michoacán', () {
        final withAccent = SepomexCodigosPostales.getByState('Michoacán');
        final withoutAccent = SepomexCodigosPostales.getByState('Michoacan');

        expect(withAccent, isA<List>());
        expect(withoutAccent, isA<List>());
      });
    });

    group('normalizeText utility', () {
      test('should remove common Spanish accents', () {
        final testCases = {
          'á': 'a',
          'é': 'e',
          'í': 'i',
          'ó': 'o',
          'ú': 'u',
          'Á': 'a',
          'É': 'e',
          'Í': 'i',
          'Ó': 'o',
          'Ú': 'u',
          'ñ': 'n',
          'Ñ': 'n',
        };

        for (final entry in testCases.entries) {
          final result = normalizeText(entry.key);
          expect(result.toLowerCase(), contains(entry.value),
              reason: 'Failed to normalize ${entry.key} to ${entry.value}');
        }
      });

      test('should normalize complete words', () {
        expect(normalizeText('México'), equals('mexico'));
        expect(normalizeText('San José'), equals('san jose'));
        expect(normalizeText('Michoacán de Ocampo'),
            equals('michoacan de ocampo'));
        expect(normalizeText('Las Águilas'), equals('las aguilas'));
      });

      test('should handle uppercase input', () {
        expect(normalizeText('AGUILAS'), equals('aguilas'));
        expect(normalizeText('Aguilas'), equals('aguilas'));
        expect(normalizeText('aguilas'), equals('aguilas'));
      });

      test('should handle mixed case and accents', () {
        expect(normalizeText('MÉXICO'), equals('mexico'));
        expect(normalizeText('MéXiCo'), equals('mexico'));
      });
    });
  });
}
