import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

void main() {
  group('IdentityGenerator', () {
    test('generatePersonaFisica returns valid identity', () {
      final identity = generatePersonaFisica();

      expect(identity['tipo'], equals('persona_fisica'));
      expect(identity['nombre'], isNotEmpty);
      expect(identity['apellido_paterno'], isNotEmpty);
      expect(identity['apellido_materno'], isNotEmpty);
      expect(identity['rfc'], isNotEmpty);
      expect(identity['curp'], isNotEmpty);
      expect(identity['nss'], isNotEmpty);
      expect(identity['clabe'], isNotEmpty);

      // Validate RFC
      expect(validateRFC(identity['rfc'] as String), isTrue);

      // Validate CURP
      expect(validateCURP(identity['curp'] as String), isTrue);

      // Validate NSS
      expect(validateNSS(identity['nss'] as String), isTrue);

      // Validate CLABE
      expect(validateCLABE(identity['clabe'] as String), isTrue);
    });

    test('generatePersonaFisica with male sex', () {
      final identity = generatePersonaFisica(sexo: 'H');

      expect(identity['sexo'], equals('H'));
      expect(identity['sexo_descripcion'], equals('Masculino'));

      // CURP should have H for male
      final curp = identity['curp'] as String;
      expect(curp[10], equals('H'));
    });

    test('generatePersonaFisica with female sex', () {
      final identity = generatePersonaFisica(sexo: 'M');

      expect(identity['sexo'], equals('M'));
      expect(identity['sexo_descripcion'], equals('Femenino'));

      // CURP should have M for female
      final curp = identity['curp'] as String;
      expect(curp[10], equals('M'));
    });

    test('generatePersonaFisica with specific state', () {
      final identity = generatePersonaFisica(estado: 'JC');

      expect(identity['estado_nacimiento_code'], equals('JC'));
      expect(
          (identity['estado_nacimiento'] as String)
              .toUpperCase()
              .contains('JALISCO'),
          isTrue);
    });

    test('generatePersonaMoral returns valid identity', () {
      final identity = generatePersonaMoral();

      expect(identity['tipo'], equals('persona_moral'));
      expect(identity['razon_social'], isNotEmpty);
      expect(identity['nombre_comercial'], isNotEmpty);
      expect(identity['rfc'], isNotEmpty);
      expect(identity['clabe'], isNotEmpty);

      // Validate RFC (should be 12 characters for moral)
      final rfc = identity['rfc'] as String;
      expect(rfc.length, equals(12));
      expect(validateRFC(rfc), isTrue);

      // Validate CLABE
      expect(validateCLABE(identity['clabe'] as String), isTrue);
    });

    test('generateIdentity with tipo fisica', () {
      final identity = generateIdentity(tipo: 'fisica');
      expect(identity['tipo'], equals('persona_fisica'));
      expect(identity['curp'], isNotEmpty);
    });

    test('generateIdentity with tipo moral', () {
      final identity = generateIdentity(tipo: 'moral');
      expect(identity['tipo'], equals('persona_moral'));
      expect(identity['razon_social'], isNotEmpty);
    });

    test('IdentityGenerator class generates valid data', () {
      final generator = IdentityGenerator();

      final fisica = generator.generatePersonaFisica();
      expect(fisica.tipo, equals('persona_fisica'));
      expect(validateRFC(fisica.rfc), isTrue);
      expect(validateCURP(fisica.curp), isTrue);
      expect(validateNSS(fisica.nss), isTrue);
      expect(validateCLABE(fisica.clabe), isTrue);

      final moral = generator.generatePersonaMoral();
      expect(moral.tipo, equals('persona_moral'));
      expect(validateRFC(moral.rfc), isTrue);
      expect(validateCLABE(moral.clabe), isTrue);
    });

    test('multiple generations produce unique identities', () {
      final identities = <String>{};

      for (var i = 0; i < 10; i++) {
        final identity = generatePersonaFisica();
        final rfc = identity['rfc'] as String;
        identities.add(rfc);
      }

      // Most should be unique (very unlikely to have duplicates)
      expect(identities.length, greaterThan(5));
    });

    test('age constraints are respected', () {
      final identity = generatePersonaFisica(minAge: 25, maxAge: 30);
      final age = identity['edad'] as int;

      expect(age, greaterThanOrEqualTo(25));
      expect(age, lessThanOrEqualTo(30));
    });

    test('PersonaFisica toJson returns all fields', () {
      final generator = IdentityGenerator();
      final fisica = generator.generatePersonaFisica();
      final json = fisica.toJson();

      expect(json.containsKey('tipo'), isTrue);
      expect(json.containsKey('nombre'), isTrue);
      expect(json.containsKey('apellido_paterno'), isTrue);
      expect(json.containsKey('apellido_materno'), isTrue);
      expect(json.containsKey('nombre_completo'), isTrue);
      expect(json.containsKey('fecha_nacimiento'), isTrue);
      expect(json.containsKey('edad'), isTrue);
      expect(json.containsKey('sexo'), isTrue);
      expect(json.containsKey('rfc'), isTrue);
      expect(json.containsKey('curp'), isTrue);
      expect(json.containsKey('nss'), isTrue);
      expect(json.containsKey('banco'), isTrue);
      expect(json.containsKey('clabe'), isTrue);
      expect(json.containsKey('direccion'), isTrue);
      expect(json.containsKey('telefono'), isTrue);
      expect(json.containsKey('email'), isTrue);
      expect(json.containsKey('regimen_fiscal'), isTrue);
    });

    test('PersonaMoral toJson returns all fields', () {
      final generator = IdentityGenerator();
      final moral = generator.generatePersonaMoral();
      final json = moral.toJson();

      expect(json.containsKey('tipo'), isTrue);
      expect(json.containsKey('razon_social'), isTrue);
      expect(json.containsKey('nombre_comercial'), isTrue);
      expect(json.containsKey('fecha_constitucion'), isTrue);
      expect(json.containsKey('antiguedad'), isTrue);
      expect(json.containsKey('rfc'), isTrue);
      expect(json.containsKey('banco'), isTrue);
      expect(json.containsKey('clabe'), isTrue);
      expect(json.containsKey('direccion'), isTrue);
      expect(json.containsKey('telefono'), isTrue);
      expect(json.containsKey('email'), isTrue);
      expect(json.containsKey('regimen_fiscal'), isTrue);
    });
  });
}
