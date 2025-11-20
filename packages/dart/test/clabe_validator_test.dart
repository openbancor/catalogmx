import 'package:test/test.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  group('CLABE Validator', () {
    test('validates valid CLABEs', () {
      expect(validateCLABE('002010077777777771'), isTrue);
      expect(validateCLABE('012180001234567897'), isTrue);
      expect(validateCLABE('014028000005300534'), isTrue);
    });

    test('rejects invalid CLABEs', () {
      expect(validateCLABE(''), isFalse);
      expect(validateCLABE('12345'), isFalse);
      expect(validateCLABE('00201007777777777'), isFalse); // Too short
      expect(validateCLABE('0020100777777777711'), isFalse); // Too long
    });

    test('rejects CLABE with non-digits', () {
      expect(validateCLABE('00201007777777777A'), isFalse);
      expect(validateCLABE('ABC010077777777771'), isFalse);
    });

    test('rejects CLABE with invalid check digit', () {
      expect(validateCLABE('002010077777777770'), isFalse);
      expect(validateCLABE('002010077777777779'), isFalse);
    });

    test('extracts bank code', () {
      final validator = CLABEValidator('002010077777777771');
      expect(validator.getBankCode(), equals('002'));
    });

    test('extracts branch code', () {
      final validator = CLABEValidator('002010077777777771');
      expect(validator.getBranchCode(), equals('010'));
    });

    test('extracts account number', () {
      final validator = CLABEValidator('002010077777777771');
      expect(validator.getAccountNumber(), equals('07777777777'));
    });

    test('extracts check digit', () {
      final validator = CLABEValidator('002010077777777771');
      expect(validator.getCheckDigit(), equals('1'));
    });

    test('gets all parts', () {
      final validator = CLABEValidator('002010077777777771');
      final parts = validator.getParts();

      expect(parts, isNotNull);
      expect(parts!['bank_code'], equals('002'));
      expect(parts['branch_code'], equals('010'));
      expect(parts['account_number'], equals('07777777777'));
      expect(parts['check_digit'], equals('1'));
    });

    test('calculates check digit correctly', () {
      expect(CLABEValidator.calculateCheckDigit('00201007777777777'), equals('1'));
      expect(CLABEValidator.calculateCheckDigit('01218000123456789'), equals('7'));
      expect(CLABEValidator.calculateCheckDigit('01402800000530053'), equals('4'));
    });
  });

  group('CLABE Generator', () {
    test('generates valid CLABE', () {
      final clabe = generateCLABE(
        bankCode: '002',
        branchCode: '010',
        accountNumber: '07777777777',
      );

      expect(clabe, equals('002010077777777771'));
      expect(validateCLABE(clabe), isTrue);
    });

    test('pads short values', () {
      final clabe = generateCLABE(
        bankCode: '2',
        branchCode: '10',
        accountNumber: '7777777777',
      );

      expect(validateCLABE(clabe), isTrue);
    });

    test('throws on invalid lengths', () {
      expect(
        () => generateCLABE(
          bankCode: '1234',
          branchCode: '010',
          accountNumber: '07777777777',
        ),
        throwsA(isA<CLABEException>()),
      );
    });
  });
}
