import 'package:test/test.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  group('cleanText', () {
    test('converts to uppercase', () {
      expect(cleanText('hello'), equals('HELLO'));
    });

    test('removes accents', () {
      expect(cleanText('José María'), equals('JOSE MARIA'));
      expect(cleanText('Pérez Ñoño'), equals('PEREZ NONO'));
    });

    test('handles empty string', () {
      expect(cleanText(''), equals(''));
    });

    test('handles mixed case with accents', () {
      expect(cleanText('García López'), equals('GARCIA LOPEZ'));
    });
  });

  group('normalizeText', () {
    test('converts to lowercase and trims', () {
      expect(normalizeText('  HELLO  '), equals('hello'));
    });

    test('removes accents', () {
      expect(normalizeText('José María'), equals('jose maria'));
    });

    test('handles empty string', () {
      expect(normalizeText(''), equals(''));
    });
  });

  group('removeExcludedWords', () {
    test('removes excluded words', () {
      final excluded = ['DE', 'LA', 'EL'];
      expect(removeExcludedWords('JUAN DE LA CRUZ', excluded), equals('JUAN CRUZ'));
    });

    test('handles case sensitivity', () {
      final excluded = ['DE', 'LA'];
      expect(removeExcludedWords('juan de la cruz', excluded), equals('juan de la cruz'));
    });

    test('handles empty excluded list', () {
      expect(removeExcludedWords('JUAN DE LA CRUZ', []), equals('JUAN DE LA CRUZ'));
    });

    test('handles empty text', () {
      expect(removeExcludedWords('', ['DE', 'LA']), equals(''));
    });
  });

  group('containsOnlyAllowed', () {
    test('returns true for valid characters', () {
      final allowed = ['A', 'B', 'C', '1', '2', '3'];
      expect(containsOnlyAllowed('ABC123', allowed), isTrue);
    });

    test('returns false for invalid characters', () {
      final allowed = ['A', 'B', 'C'];
      expect(containsOnlyAllowed('ABCD', allowed), isFalse);
    });

    test('handles empty string', () {
      expect(containsOnlyAllowed('', ['A', 'B']), isTrue);
    });

    test('handles empty allowed list', () {
      expect(containsOnlyAllowed('A', []), isFalse);
    });
  });

  group('getFirstVowel', () {
    test('finds first vowel', () {
      expect(getFirstVowel('BCDA'), equals('A'));
    });

    test('finds vowel from startIndex', () {
      expect(getFirstVowel('ABCD', startIndex: 1), equals(null));
      expect(getFirstVowel('ABCDE', startIndex: 1), equals('E'));
    });

    test('returns null if no vowel', () {
      expect(getFirstVowel('BCD'), isNull);
    });

    test('handles empty string', () {
      expect(getFirstVowel(''), isNull);
    });
  });

  group('getFirstConsonant', () {
    test('finds first consonant', () {
      expect(getFirstConsonant('AEBC'), equals('B'));
    });

    test('finds consonant from startIndex', () {
      expect(getFirstConsonant('BCDE', startIndex: 1), equals('C'));
    });

    test('returns null if no consonant', () {
      expect(getFirstConsonant('AEIOU'), isNull);
    });

    test('handles empty string', () {
      expect(getFirstConsonant(''), isNull);
    });
  });

  group('cleanName', () {
    test('removes excluded words and cleans', () {
      final excluded = ['DE', 'LA'];
      final allowed = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ '.split('');
      expect(cleanName('JUAN DE LA CRUZ', excluded, allowed), equals('JUAN CRUZ'));
    });

    test('removes accents', () {
      final excluded = <String>[];
      final allowed = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ '.split('');
      expect(cleanName('José', excluded, allowed), equals('JOSE'));
    });

    test('filters invalid characters', () {
      final excluded = <String>[];
      final allowed = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
      expect(cleanName('JUAN123', excluded, allowed), equals('JUAN'));
    });
  });
}
