import 'package:test/test.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  group('RFC Validator', () {
    test('validates generic RFCs', () {
      expect(validateRFC('XAXX010101000'), isTrue);
      expect(validateRFC('XEXX010101000'), isTrue);
    });

    test('validates RFC Persona Física', () {
      expect(validateRFC('OEAF771012HM3'), isTrue);
      expect(validateRFC('GODE561231GR8'), isTrue);
    });

    test('validates RFC Persona Moral', () {
      expect(validateRFC('BIM930505WL4'), isTrue);
      expect(validateRFC('TSI800101KT9'), isTrue);
    });

    test('rejects invalid RFCs', () {
      expect(validateRFC(''), isFalse);
      expect(validateRFC('INVALID'), isFalse);
      expect(validateRFC('12345678901'), isFalse);
      expect(validateRFC('OEAF771012HM'), isFalse); // Too short
      expect(validateRFC('OEAF771012HM88'), isFalse); // Too long
    });

    test('rejects RFC with invalid date', () {
      expect(validateRFC('OEAF991332HM8'), isFalse);
      expect(validateRFC('OEAF770230HM8'), isFalse);
    });

    test('detects RFC type', () {
      final validator1 = RFCValidator('OEAF771012HM3');
      expect(validator1.detectType(), equals('Persona Física'));

      final validator2 = RFCValidator('BIM930505WL4');
      expect(validator2.detectType(), equals('Persona Moral'));

      final validator3 = RFCValidator('XAXX010101000');
      expect(validator3.detectType(), equals('Generic'));
    });

    test('validates checksum', () {
      final validator = RFCValidator('OEAF771012HM3');
      expect(validator.validateChecksum(), isTrue);
    });

    test('calculates checksum correctly', () {
      expect(RFCValidator.calculateChecksum('OEAF771012HM'), equals('3'));
      expect(RFCValidator.calculateChecksum('BIM930505WL'), equals('4'));
    });
  });

  group('RFC Generator - Persona Física', () {
    test('generates valid RFC', () {
      final rfc = generateRFC(
        nombre: 'Juan',
        apellidoPaterno: 'García',
        apellidoMaterno: 'López',
        fechaNacimiento: DateTime(1990, 5, 15),
      );

      expect(rfc.length, equals(13));
      expect(validateRFC(rfc), isTrue);
    });

    test('generates RFC with accents', () {
      final rfc = generateRFC(
        nombre: 'José María',
        apellidoPaterno: 'Pérez',
        apellidoMaterno: 'García',
        fechaNacimiento: DateTime(1990, 5, 15),
      );

      expect(validateRFC(rfc), isTrue);
    });

    test('generates RFC without materno', () {
      final rfc = generateRFC(
        nombre: 'Juan',
        apellidoPaterno: 'García',
        apellidoMaterno: '',
        fechaNacimiento: DateTime(1990, 5, 15),
      );

      expect(validateRFC(rfc), isTrue);
    });

    test('handles cacophonic words', () {
      final rfc = generateRFC(
        nombre: 'Antonio',
        apellidoPaterno: 'Caca',
        apellidoMaterno: 'López',
        fechaNacimiento: DateTime(1990, 5, 15),
      );

      // Should replace offensive word pattern
      expect(rfc.substring(0, 4), isNot(equals('CACA')));
      expect(validateRFC(rfc), isTrue);
    });
  });

  group('RFC Generator - Persona Moral', () {
    test('generates valid RFC for company', () {
      final rfc = generateRFCMoral(
        razonSocial: 'Grupo Bimbo S.A.B. de C.V.',
        fechaConstitucion: DateTime(1993, 5, 5),
      );

      expect(rfc.length, equals(12));
      expect(validateRFC(rfc), isTrue);
    });

    test('removes excluded words', () {
      final rfc = generateRFCMoral(
        razonSocial: 'Sociedad Cooperativa de Transportes S.A. de C.V.',
        fechaConstitucion: DateTime(1980, 1, 1),
      );

      expect(validateRFC(rfc), isTrue);
    });

    test('handles single word company', () {
      final rfc = generateRFCMoral(
        razonSocial: 'BIMBO',
        fechaConstitucion: DateTime(1993, 5, 5),
      );

      expect(validateRFC(rfc), isTrue);
    });
  });
}
