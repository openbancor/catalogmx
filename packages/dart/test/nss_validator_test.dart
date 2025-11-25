import 'package:test/test.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  group('NSS Validator', () {
    test('validates valid NSS numbers', () {
      expect(validateNSS('12345678903'), isTrue);
      expect(validateNSS('97031612340'), isTrue);
    });

    test('rejects invalid NSS numbers', () {
      expect(validateNSS(''), isFalse);
      expect(validateNSS('12345'), isFalse);
      expect(validateNSS('1234567890'), isFalse); // Too short
      expect(validateNSS('123456789012'), isFalse); // Too long
    });

    test('rejects NSS with non-digits', () {
      expect(validateNSS('1234567890A'), isFalse);
      expect(validateNSS('ABC45678903'), isFalse);
    });

    test('rejects NSS with invalid check digit', () {
      expect(validateNSS('12345678900'), isFalse);
      expect(validateNSS('12345678909'), isFalse);
    });

    test('extracts subdelegation', () {
      final validator = NSSValidator('12345678903');
      expect(validator.getSubdelegation(), equals('12'));
    });

    test('extracts registration year', () {
      final validator = NSSValidator('12345678903');
      expect(validator.getRegistrationYear(), equals('34'));
    });

    test('extracts birth year', () {
      final validator = NSSValidator('12345678903');
      expect(validator.getBirthYear(), equals('56'));
    });

    test('extracts sequential', () {
      final validator = NSSValidator('12345678903');
      expect(validator.getSequential(), equals('7890'));
    });

    test('extracts check digit', () {
      final validator = NSSValidator('12345678903');
      expect(validator.getCheckDigit(), equals('3'));
    });

    test('gets all parts', () {
      final validator = NSSValidator('12345678903');
      final parts = validator.getParts();

      expect(parts, isNotNull);
      expect(parts!['subdelegation'], equals('12'));
      expect(parts['registration_year'], equals('34'));
      expect(parts['birth_year'], equals('56'));
      expect(parts['sequential'], equals('7890'));
      expect(parts['check_digit'], equals('3'));
    });

    test('calculates check digit correctly', () {
      expect(NSSValidator.calculateCheckDigit('1234567890'), equals('3'));
      expect(NSSValidator.calculateCheckDigit('9703161234'), equals('0'));
    });
  });

  group('NSS Generator', () {
    test('generates valid NSS', () {
      final nss = generateNSS(
        subdelegation: '12',
        registrationYear: '34',
        birthYear: '56',
        sequential: '7890',
      );

      expect(nss, equals('12345678903'));
      expect(validateNSS(nss), isTrue);
    });

    test('pads short values', () {
      final nss = generateNSS(
        subdelegation: '1',
        registrationYear: '2',
        birthYear: '3',
        sequential: '456',
      );

      expect(validateNSS(nss), isTrue);
    });

    test('throws on invalid lengths', () {
      expect(
        () => generateNSS(
          subdelegation: '123',
          registrationYear: '34',
          birthYear: '56',
          sequential: '7890',
        ),
        throwsA(isA<NSSException>()),
      );
    });
  });
}
