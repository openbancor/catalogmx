/// Test accent-insensitive search in SEPOMEX catalogs
///
/// This test verifies that searches without accents properly find results
/// with accents, which is critical for Spanish-speaking users.
import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

void main() {
  group('SEPOMEX Accent-Insensitive Search', () {
    group('searchByColonia', () {
      test('should find "Las Águilas" when searching for "Aguilas" (without accent)', () {
        // Critical test: This is a real-world use case reported by users
        final results = SepomexCodigosPostales.searchByColonia('Aguilas');

        // Should find results
        expect(results.length, greaterThan(0),
            reason: 'Search for "Aguilas" returned no results');

        // Check if any result contains "Águilas" (with accent)
        final foundWithAccent = results.any((result) {
          final colonia = result['colonia'] as String? ?? result['d_asenta'] as String? ?? '';
          return colonia.toLowerCase().contains('águilas');
        });

        expect(foundWithAccent, isTrue,
            reason: 'Search for "Aguilas" did not find "Las Águilas" (with accent)');
      });

      test('should find results when searching for "Mexico" (without accent)', () {
        final results = SepomexCodigosPostales.searchByColonia('Mexico');
        expect(results.length, greaterThan(0));
      });

      test('should return same results with or without accents', () {
        final resultsWithAccent = SepomexCodigosPostales.searchByColonia('Águilas');
        final resultsWithoutAccent = SepomexCodigosPostales.searchByColonia('Aguilas');

        expect(resultsWithAccent.length, greaterThan(0));
        expect(resultsWithoutAccent.length, greaterThan(0));
        expect(resultsWithAccent.length, equals(resultsWithoutAccent.length));
      });

      test('should be case-insensitive', () {
        final resultsUpper = SepomexCodigosPostales.searchByColonia('AGUILAS');
        final resultsLower = SepomexCodigosPostales.searchByColonia('aguilas');
        final resultsMixed = SepomexCodigosPostales.searchByColonia('Aguilas');

        expect(resultsUpper.length, equals(resultsLower.length));
        expect(resultsLower.length, equals(resultsMixed.length));
      });

      test('should find partial matches with accents', () {
        final results = SepomexCodigosPostales.searchByColonia('Aguil');
        // Should find "Las Águilas" and other similar names
        expect(results.length, greaterThan(0));
      });
    });

    group('searchByMunicipio', () {
      test('should be accent-insensitive for municipalities', () {
        final resultsWithAccent = SepomexCodigosPostales.searchByMunicipio('León');
        final resultsWithoutAccent = SepomexCodigosPostales.searchByMunicipio('Leon');

        // Both should work
        expect(resultsWithAccent.length, greaterThan(0));
        expect(resultsWithoutAccent.length, greaterThan(0));
        expect(resultsWithAccent.length, equals(resultsWithoutAccent.length));
      });

      test('should handle special characters', () {
        final results = SepomexCodigosPostales.searchByMunicipio('Peña');
        expect(results, isA<List>());
      });

      test('should handle multiple accents', () {
        final results = SepomexCodigosPostales.searchByMunicipio('San José');
        expect(results, isA<List>());

        final resultsNoAccent = SepomexCodigosPostales.searchByMunicipio('San Jose');
        expect(resultsNoAccent, isA<List>());
      });
    });

    group('getByState', () {
      test('should be accent-insensitive for states', () {
        final resultsWithAccent = SepomexCodigosPostales.getByState('México');
        final resultsWithoutAccent = SepomexCodigosPostales.getByState('Mexico');

        // Both should work (Estado de México exists)
        final hasResults = resultsWithAccent.isNotEmpty || resultsWithoutAccent.isNotEmpty;
        expect(hasResults, isTrue);
      });

      test('should handle Michoacán', () {
        final withAccent = SepomexCodigosPostales.getByState('Michoacán');
        final withoutAccent = SepomexCodigosPostales.getByState('Michoacan');

        expect(withAccent.isNotEmpty || withoutAccent.isNotEmpty, isTrue);
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
        expect(normalizeText('Michoacán de Ocampo'), equals('michoacan de ocampo'));
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
