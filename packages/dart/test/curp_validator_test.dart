import 'package:test/test.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  group('CURP Validator', () {
    test('validates valid CURPs', () {
      expect(validateCURP('OEAF771012HMCRGR09'), isTrue);
      expect(validateCURP('PEGJ900515HJCRRN05'), isTrue);
      expect(validateCURP('MEHL850101MMCRRS08'), isTrue);
    });

    test('rejects invalid CURPs', () {
      expect(validateCURP(''), isFalse);
      expect(validateCURP('INVALID'), isFalse);
      expect(validateCURP('OEAF771012HMCRGR0'), isFalse); // Too short
      expect(validateCURP('OEAF771012HMCRGR099'), isFalse); // Too long
    });

    test('rejects CURP with invalid structure', () {
      expect(validateCURP('1EAF771012HMCRGR09'), isFalse); // First char must be letter
      expect(validateCURP('OEAF991332HMCRGR09'), isFalse); // Invalid date
      expect(validateCURP('OEAF771012XMCRGR09'), isFalse); // Invalid gender
    });

    test('validates check digit', () {
      final validator = CURPValidator('OEAF771012HMCRGR09');
      expect(validator.validateCheckDigit(), isTrue);
    });

    test('extracts birth date', () {
      final validator = CURPValidator('OEAF771012HMCRGR09');
      final date = validator.getBirthDate();

      expect(date, isNotNull);
      expect(date!.year, equals(1977));
      expect(date.month, equals(10));
      expect(date.day, equals(12));
    });

    test('extracts gender', () {
      final validator1 = CURPValidator('OEAF771012HMCRGR09');
      expect(validator1.getGender(), equals('Hombre'));

      final validator2 = CURPValidator('MEHL850101MMCRRS08');
      expect(validator2.getGender(), equals('Mujer'));
    });

    test('extracts state code', () {
      final validator = CURPValidator('OEAF771012HMCRGR09');
      expect(validator.getStateCode(), equals('MC'));
    });
  });

  group('CURP Generator', () {
    test('generates valid CURP', () {
      final curp = generateCURP(
        nombre: 'Juan',
        apellidoPaterno: 'García',
        apellidoMaterno: 'López',
        fechaNacimiento: DateTime(1990, 5, 15),
        sexo: 'H',
        estado: 'Jalisco',
      );

      expect(curp.length, equals(18));
      expect(validateCURP(curp), isTrue);
    });

    test('generates CURP with accents', () {
      final curp = generateCURP(
        nombre: 'José María',
        apellidoPaterno: 'Pérez',
        apellidoMaterno: 'García',
        fechaNacimiento: DateTime(1990, 5, 15),
        sexo: 'H',
        estado: 'México',
      );

      expect(validateCURP(curp), isTrue);
    });

    test('generates CURP without materno', () {
      final curp = generateCURP(
        nombre: 'Juan',
        apellidoPaterno: 'García',
        apellidoMaterno: null,
        fechaNacimiento: DateTime(1990, 5, 15),
        sexo: 'H',
        estado: 'Jalisco',
      );

      expect(validateCURP(curp), isTrue);
      expect(curp[2], equals('X')); // Should have X for missing materno
    });

    test('generates CURP for female', () {
      final curp = generateCURP(
        nombre: 'María',
        apellidoPaterno: 'Hernández',
        apellidoMaterno: 'López',
        fechaNacimiento: DateTime(1985, 1, 1),
        sexo: 'M',
        estado: 'México',
      );

      expect(validateCURP(curp), isTrue);
      expect(curp[10], equals('M'));
    });

    test('handles state codes', () {
      final curp1 = generateCURP(
        nombre: 'Juan',
        apellidoPaterno: 'García',
        apellidoMaterno: 'López',
        fechaNacimiento: DateTime(1990, 5, 15),
        sexo: 'H',
        estado: 'Ciudad de México',
      );
      expect(curp1.substring(11, 13), equals('DF'));

      final curp2 = generateCURP(
        nombre: 'Juan',
        apellidoPaterno: 'García',
        apellidoMaterno: 'López',
        fechaNacimiento: DateTime(1990, 5, 15),
        sexo: 'H',
        estado: 'Jalisco',
      );
      expect(curp2.substring(11, 13), equals('JC'));
    });

    test('handles born abroad', () {
      final curp = generateCURP(
        nombre: 'Juan',
        apellidoPaterno: 'García',
        apellidoMaterno: 'López',
        fechaNacimiento: DateTime(1990, 5, 15),
        sexo: 'H',
        estado: null,
      );

      expect(curp.substring(11, 13), equals('NE'));
    });

    test('calculates check digit correctly', () {
      final checkDigit = CURPGenerator.calculateCheckDigit('OEAF771012HMCRGR0');
      expect(checkDigit, equals('9'));
    });
  });
}
