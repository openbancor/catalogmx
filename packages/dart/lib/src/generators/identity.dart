/// Identity Generator for Mexican test data
///
/// Generates complete Mexican identities with realistic data for
/// testing and development purposes.
///
/// Example:
/// ```dart
/// import 'package:faker/faker.dart';
/// import 'package:catalogmx/catalogmx.dart';
///
/// final generator = IdentityGenerator(faker: Faker());
/// final identity = generator.generatePersonaFisica();
/// print(identity.rfc); // Valid RFC
/// print(identity.curp); // Valid CURP
/// print(identity.nss); // Valid NSS
/// ```
library;

import 'dart:math';

import 'package:catalogmx/src/validators/rfc_validator.dart';
import 'package:catalogmx/src/validators/curp_validator.dart';
import 'package:catalogmx/src/validators/nss_validator.dart';
import 'package:catalogmx/src/utils/clabe_utils.dart';
import 'package:catalogmx/src/catalogs/inegi/states.dart';
import 'package:catalogmx/src/catalogs/banxico/banks.dart';
import 'package:catalogmx/src/catalogs/sat/cfdi/regimen_fiscal.dart';

/// Persona Fisica identity data
class PersonaFisica {
  PersonaFisica({
    required this.tipo,
    required this.nombre,
    required this.apellidoPaterno,
    required this.apellidoMaterno,
    required this.nombreCompleto,
    required this.fechaNacimiento,
    required this.edad,
    required this.sexo,
    required this.sexoDescripcion,
    required this.estadoNacimiento,
    required this.estadoNacimientoCode,
    required this.rfc,
    required this.curp,
    required this.nss,
    required this.banco,
    required this.clabe,
    required this.cuenta,
    required this.tarjetaDebito,
    required this.direccion,
    required this.telefono,
    required this.email,
    required this.regimenFiscal,
  });

  final String tipo;
  final String nombre;
  final String apellidoPaterno;
  final String apellidoMaterno;
  final String nombreCompleto;
  final DateTime fechaNacimiento;
  final int edad;
  final String sexo;
  final String sexoDescripcion;
  final String estadoNacimiento;
  final String estadoNacimientoCode;
  final String rfc;
  final String curp;
  final String nss;
  final Map<String, String> banco;
  final String clabe;
  final String cuenta;
  final String tarjetaDebito;
  final Map<String, String> direccion;
  final String telefono;
  final String email;
  final Map<String, String> regimenFiscal;

  Map<String, dynamic> toJson() => {
        'tipo': tipo,
        'nombre': nombre,
        'apellido_paterno': apellidoPaterno,
        'apellido_materno': apellidoMaterno,
        'nombre_completo': nombreCompleto,
        'fecha_nacimiento':
            '${fechaNacimiento.year}-${fechaNacimiento.month.toString().padLeft(2, '0')}-${fechaNacimiento.day.toString().padLeft(2, '0')}',
        'edad': edad,
        'sexo': sexo,
        'sexo_descripcion': sexoDescripcion,
        'estado_nacimiento': estadoNacimiento,
        'estado_nacimiento_code': estadoNacimientoCode,
        'rfc': rfc,
        'curp': curp,
        'nss': nss,
        'banco': banco,
        'clabe': clabe,
        'cuenta': cuenta,
        'tarjeta_debito': tarjetaDebito,
        'direccion': direccion,
        'telefono': telefono,
        'email': email,
        'regimen_fiscal': regimenFiscal,
      };
}

/// Persona Moral identity data
class PersonaMoral {
  PersonaMoral({
    required this.tipo,
    required this.razonSocial,
    required this.nombreComercial,
    required this.fechaConstitucion,
    required this.antiguedad,
    required this.rfc,
    required this.banco,
    required this.clabe,
    required this.cuenta,
    required this.direccion,
    required this.telefono,
    required this.email,
    required this.regimenFiscal,
  });

  final String tipo;
  final String razonSocial;
  final String nombreComercial;
  final DateTime fechaConstitucion;
  final int antiguedad;
  final String rfc;
  final Map<String, String> banco;
  final String clabe;
  final String cuenta;
  final Map<String, String> direccion;
  final String telefono;
  final String email;
  final Map<String, String> regimenFiscal;

  Map<String, dynamic> toJson() => {
        'tipo': tipo,
        'razon_social': razonSocial,
        'nombre_comercial': nombreComercial,
        'fecha_constitucion':
            '${fechaConstitucion.year}-${fechaConstitucion.month.toString().padLeft(2, '0')}-${fechaConstitucion.day.toString().padLeft(2, '0')}',
        'antiguedad': antiguedad,
        'rfc': rfc,
        'banco': banco,
        'clabe': clabe,
        'cuenta': cuenta,
        'direccion': direccion,
        'telefono': telefono,
        'email': email,
        'regimen_fiscal': regimenFiscal,
      };
}

/// Configuration for fake data generation
class FakerConfig {
  FakerConfig({
    required this.firstName,
    required this.lastName,
    required this.streetName,
    required this.buildingNumber,
    required this.city,
    required this.state,
    required this.zipCode,
    required this.phoneNumber,
    required this.email,
    required this.companyName,
    required this.companySuffix,
  });

  final String Function() firstName;
  final String Function() lastName;
  final String Function() streetName;
  final String Function() buildingNumber;
  final String Function() city;
  final String Function() state;
  final String Function() zipCode;
  final String Function() phoneNumber;
  final String Function(String firstName, String lastName) email;
  final String Function() companyName;
  final String Function() companySuffix;
}

/// Identity Generator for Mexican test data
///
/// Generate complete Mexican identities with valid RFC, CURP, NSS, CLABE.
///
/// Example without faker (uses simple random data):
/// ```dart
/// final generator = IdentityGenerator();
/// final identity = generator.generatePersonaFisica();
/// ```
///
/// Example with faker (for realistic names/addresses):
/// ```dart
/// import 'package:faker/faker.dart';
///
/// final faker = Faker(locale: const LocaleType.es);
/// final generator = IdentityGenerator(
///   fakerConfig: FakerConfig(
///     firstName: () => faker.person.firstName(),
///     lastName: () => faker.person.lastName(),
///     streetName: () => faker.address.streetName(),
///     buildingNumber: () => faker.address.buildingNumber(),
///     city: () => faker.address.city(),
///     state: () => faker.address.state(),
///     zipCode: () => faker.address.zipCode(),
///     phoneNumber: () => faker.phoneNumber.us(),
///     email: (fn, ln) => faker.internet.email(firstName: fn, lastName: ln),
///     companyName: () => faker.company.name(),
///     companySuffix: () => faker.company.suffix(),
///   ),
/// );
/// ```
class IdentityGenerator {
  IdentityGenerator({
    this.fakerConfig,
    Random? random,
  }) : _random = random ?? Random();

  final FakerConfig? fakerConfig;
  final Random _random;

  // Common Mexican first names
  static const _maleNames = [
    'Juan',
    'José',
    'Luis',
    'Carlos',
    'Miguel',
    'Francisco',
    'Antonio',
    'Pedro',
    'Manuel',
    'Rafael',
    'Ricardo',
    'Fernando',
    'Jorge',
    'Roberto',
    'Eduardo',
    'Alejandro',
    'Sergio',
    'Daniel',
    'Mario',
    'Arturo',
  ];

  static const _femaleNames = [
    'María',
    'Ana',
    'Rosa',
    'Guadalupe',
    'Carmen',
    'Patricia',
    'Laura',
    'Elena',
    'Teresa',
    'Mónica',
    'Adriana',
    'Claudia',
    'Verónica',
    'Sandra',
    'Gabriela',
    'Leticia',
    'Silvia',
    'Martha',
    'Isabel',
    'Beatriz',
  ];

  static const _lastNames = [
    'García',
    'Hernández',
    'López',
    'Martínez',
    'González',
    'Rodríguez',
    'Pérez',
    'Sánchez',
    'Ramírez',
    'Torres',
    'Flores',
    'Rivera',
    'Gómez',
    'Díaz',
    'Cruz',
    'Morales',
    'Reyes',
    'Jiménez',
    'Ruiz',
    'Ortiz',
  ];

  static const _streetTypes = [
    'Calle',
    'Avenida',
    'Boulevard',
    'Calzada',
    'Paseo',
    'Privada',
    'Cerrada',
    'Circuito',
    'Peatonal',
  ];

  static const _colonias = [
    'Centro',
    'Roma Norte',
    'Condesa',
    'Polanco',
    'Del Valle',
    'Narvarte',
    'Coyoacán',
    'Santa Fe',
    'Anzures',
    'Juárez',
  ];

  static const _companySuffixes = [
    'S.A. de C.V.',
    'S. de R.L. de C.V.',
    'S.C.',
    'A.C.',
    'S.A.P.I. de C.V.',
  ];

  static const _companyTypes = [
    'Comercializadora',
    'Distribuidora',
    'Grupo',
    'Servicios',
    'Consultores',
    'Industrial',
    'Tecnología',
    'Inmobiliaria',
    'Constructora',
    'Transportes',
  ];

  String _randomElement<T>(List<T> list) {
    return list[_random.nextInt(list.length)].toString();
  }

  String _firstName({String? sexo}) {
    if (fakerConfig != null) {
      return fakerConfig!.firstName();
    }
    final isMale = sexo == 'H' || (sexo == null && _random.nextBool());
    return _randomElement(isMale ? _maleNames : _femaleNames);
  }

  String _lastName() {
    if (fakerConfig != null) {
      return fakerConfig!.lastName();
    }
    return _randomElement(_lastNames);
  }

  DateTime _randomDate(int minAge, int maxAge) {
    final now = DateTime.now();
    // Generate date and verify the calculated age is within bounds
    // This accounts for birthdays that haven't occurred yet this year
    for (var attempts = 0; attempts < 100; attempts++) {
      final minYear =
          now.year - maxAge - 1; // -1 to account for birthday not yet passed
      final maxYear = now.year - minAge;
      final year = minYear + _random.nextInt(maxYear - minYear + 1);
      final month = 1 + _random.nextInt(12);
      final day = 1 + _random.nextInt(28);
      final date = DateTime(year, month, day);
      final age = _calculateAge(date);
      if (age >= minAge && age <= maxAge) {
        return date;
      }
    }
    // Fallback: return a date that guarantees age is within bounds
    final safeYear = now.year - minAge - 1;
    return DateTime(safeYear, now.month, now.day);
  }

  int _calculateAge(DateTime birthDate) {
    final now = DateTime.now();
    var age = now.year - birthDate.year;
    if (now.month < birthDate.month ||
        (now.month == birthDate.month && now.day < birthDate.day)) {
      age--;
    }
    return age;
  }

  Map<String, String> _generateAddress() {
    final streetType = _randomElement(_streetTypes);
    final streetName = fakerConfig?.streetName() ?? _randomElement(_lastNames);
    final numero = fakerConfig?.buildingNumber() ??
        (_random.nextInt(9000) + 100).toString();
    final colonia = _randomElement(_colonias);
    final cp = fakerConfig?.zipCode() ??
        (10000 + _random.nextInt(89999)).toString().padLeft(5, '0');
    final municipio = fakerConfig?.city() ?? 'Ciudad de México';
    final estado = fakerConfig?.state() ?? 'Ciudad de México';

    return {
      'calle': '$streetType $streetName',
      'numero_exterior': numero,
      'numero_interior': '',
      'colonia': colonia,
      'codigo_postal': cp,
      'municipio': municipio,
      'estado': estado,
    };
  }

  String _generatePhone() {
    if (fakerConfig != null) {
      return fakerConfig!.phoneNumber().replaceAll(RegExp(r'\D'), '');
    }
    // Generate 10-digit Mexican phone number
    final areaCode = (55 + _random.nextInt(44)).toString().padLeft(2, '0');
    final number = (_random.nextInt(90000000) + 10000000).toString();
    return areaCode + number;
  }

  String _generateEmail(String firstName, String lastName) {
    if (fakerConfig != null) {
      return fakerConfig!.email(firstName, lastName);
    }
    final domains = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com'];
    final fn = firstName.toLowerCase().replaceAll(RegExp(r'[^a-z]'), '');
    final ln = lastName.toLowerCase().replaceAll(RegExp(r'[^a-z]'), '');
    final num = _random.nextInt(100);
    return '$fn$ln$num@${_randomElement(domains)}';
  }

  String _generateDebitCard() {
    // Generate a random 16-digit card number
    final prefix = ['4', '5'][_random.nextInt(2)]; // Visa or Mastercard
    var card = prefix;
    for (var i = 1; i < 16; i++) {
      card += _random.nextInt(10).toString();
    }
    return card;
  }

  Map<String, String> _generateBank() {
    final speiBanks = BanxicoBanks.getSPEIBanks();
    if (speiBanks.isEmpty) {
      return {'code': '002', 'name': 'BANAMEX'};
    }
    final bank = speiBanks[_random.nextInt(speiBanks.length)];
    return {
      'code': bank['code'] as String? ?? '002',
      'name': bank['name'] as String? ?? 'BANAMEX',
    };
  }

  Map<String, String> _generateRegimenFiscal({bool personaMoral = false}) {
    final regimenes = personaMoral
        ? RegimenFiscalCatalog.getParaPersonasMorales()
        : RegimenFiscalCatalog.getParaPersonasFisicas();

    if (regimenes.isEmpty) {
      return personaMoral
          ? {'code': '601', 'name': 'General de Ley Personas Morales'}
          : {
              'code': '612',
              'name':
                  'Personas Físicas con Actividades Empresariales y Profesionales'
            };
    }

    final regimen = regimenes[_random.nextInt(regimenes.length)];
    return {
      'code': regimen['clave'] as String? ?? '612',
      'name': regimen['descripcion'] as String? ?? 'No especificado',
    };
  }

  /// Generate a Persona Fisica identity
  ///
  /// Parameters:
  /// - [sexo]: 'H' for male, 'M' for female, null for random
  /// - [estado]: State code (e.g., 'DF', 'JC'), null for random
  /// - [minAge]: Minimum age (default 18)
  /// - [maxAge]: Maximum age (default 65)
  PersonaFisica generatePersonaFisica({
    String? sexo,
    String? estado,
    int minAge = 18,
    int maxAge = 65,
  }) {
    // Generate or assign sex
    final sex = sexo ?? (_random.nextBool() ? 'H' : 'M');
    final sexDesc = sex == 'H' ? 'Masculino' : 'Femenino';

    // Generate names
    final nombre = _firstName(sexo: sex);
    final apellidoPaterno = _lastName();
    final apellidoMaterno = _lastName();
    final nombreCompleto = '$nombre $apellidoPaterno $apellidoMaterno';

    // Generate birth date
    final fechaNacimiento = _randomDate(minAge, maxAge);
    final edad = _calculateAge(fechaNacimiento);

    // Get state
    final states = InegStates.getAll().where((s) => s['code'] != 'NE').toList();
    final stateData = estado != null
        ? InegStates.getByCode(estado)
        : states[_random.nextInt(states.length)];
    final estadoNacimiento =
        stateData?['name'] as String? ?? 'CIUDAD DE MEXICO';
    final estadoCode = stateData?['code'] as String? ?? 'DF';

    // Generate RFC
    final rfc = RFCGeneratorFisica(
      nombre: nombre,
      apellidoPaterno: apellidoPaterno,
      apellidoMaterno: apellidoMaterno,
      fechaNacimiento: fechaNacimiento,
    ).generate();

    // Generate CURP
    final curp = CURPGenerator(
      nombre: nombre,
      apellidoPaterno: apellidoPaterno,
      apellidoMaterno: apellidoMaterno,
      fechaNacimiento: fechaNacimiento,
      sexo: sex,
      estado: estadoNacimiento,
    ).generate();

    // Generate NSS
    final subdelegation = (_random.nextInt(97) + 1).toString().padLeft(2, '0');
    final regYear = (fechaNacimiento.year + 18).toString().substring(2);
    final birthYear = fechaNacimiento.year.toString().substring(2);
    final sequential = _random.nextInt(10000).toString().padLeft(4, '0');
    final nss = generateNSS(
      subdelegation: subdelegation,
      registrationYear: regYear,
      birthYear: birthYear,
      sequential: sequential,
    );

    // Generate banking data
    final banco = _generateBank();
    final clabe = generateCLABERandom(bankCode: banco['code']);
    final cuenta = clabe.substring(6, 17);
    final tarjeta = _generateDebitCard();

    // Generate contact info
    final direccion = _generateAddress();
    final telefono = _generatePhone();
    final email = _generateEmail(nombre, apellidoPaterno);

    // Generate fiscal regime
    final regimenFiscal = _generateRegimenFiscal();

    return PersonaFisica(
      tipo: 'persona_fisica',
      nombre: nombre,
      apellidoPaterno: apellidoPaterno,
      apellidoMaterno: apellidoMaterno,
      nombreCompleto: nombreCompleto,
      fechaNacimiento: fechaNacimiento,
      edad: edad,
      sexo: sex,
      sexoDescripcion: sexDesc,
      estadoNacimiento: estadoNacimiento,
      estadoNacimientoCode: estadoCode,
      rfc: rfc,
      curp: curp,
      nss: nss,
      banco: banco,
      clabe: clabe,
      cuenta: cuenta,
      tarjetaDebito: tarjeta,
      direccion: direccion,
      telefono: telefono,
      email: email,
      regimenFiscal: regimenFiscal,
    );
  }

  /// Generate a Persona Moral identity
  ///
  /// Parameters:
  /// - [minYears]: Minimum years since constitution (default 1)
  /// - [maxYears]: Maximum years since constitution (default 30)
  PersonaMoral generatePersonaMoral({
    int minYears = 1,
    int maxYears = 30,
  }) {
    // Generate company name
    final companyType =
        fakerConfig?.companyName() ?? _randomElement(_companyTypes);
    final lastName = _lastName();
    final suffix =
        fakerConfig?.companySuffix() ?? _randomElement(_companySuffixes);
    final razonSocial = '$companyType $lastName $suffix';
    final nombreComercial = '$companyType $lastName';

    // Generate constitution date
    final fechaConstitucion = _randomDate(minYears, maxYears);
    final antiguedad = _calculateAge(fechaConstitucion);

    // Generate RFC
    final rfc = RFCGeneratorMoral(
      razonSocial: razonSocial,
      fechaConstitucion: fechaConstitucion,
    ).generate();

    // Generate banking data
    final banco = _generateBank();
    final clabe = generateCLABERandom(bankCode: banco['code']);
    final cuenta = clabe.substring(6, 17);

    // Generate contact info
    final direccion = _generateAddress();
    final telefono = _generatePhone();
    final email = _generateEmail(companyType.toLowerCase(), lastName);

    // Generate fiscal regime
    final regimenFiscal = _generateRegimenFiscal(personaMoral: true);

    return PersonaMoral(
      tipo: 'persona_moral',
      razonSocial: razonSocial,
      nombreComercial: nombreComercial,
      fechaConstitucion: fechaConstitucion,
      antiguedad: antiguedad,
      rfc: rfc,
      banco: banco,
      clabe: clabe,
      cuenta: cuenta,
      direccion: direccion,
      telefono: telefono,
      email: email,
      regimenFiscal: regimenFiscal,
    );
  }
}

/// Convenience function to generate a Persona Fisica identity
///
/// Example:
/// ```dart
/// final identity = generatePersonaFisica();
/// print(identity['rfc']); // Valid RFC
/// ```
Map<String, dynamic> generatePersonaFisica({
  String? sexo,
  String? estado,
  int minAge = 18,
  int maxAge = 65,
}) {
  final generator = IdentityGenerator();
  return generator
      .generatePersonaFisica(
        sexo: sexo,
        estado: estado,
        minAge: minAge,
        maxAge: maxAge,
      )
      .toJson();
}

/// Convenience function to generate a Persona Moral identity
///
/// Example:
/// ```dart
/// final identity = generatePersonaMoral();
/// print(identity['rfc']); // Valid RFC (12 chars)
/// ```
Map<String, dynamic> generatePersonaMoral({
  int minYears = 1,
  int maxYears = 30,
}) {
  final generator = IdentityGenerator();
  return generator
      .generatePersonaMoral(
        minYears: minYears,
        maxYears: maxYears,
      )
      .toJson();
}

/// Convenience function to generate any identity
///
/// Parameters:
/// - [tipo]: 'fisica' or 'moral' (default 'fisica')
///
/// Example:
/// ```dart
/// final fisica = generateIdentity(tipo: 'fisica');
/// final moral = generateIdentity(tipo: 'moral');
/// ```
Map<String, dynamic> generateIdentity({String tipo = 'fisica'}) {
  if (tipo == 'moral') {
    return generatePersonaMoral();
  }
  return generatePersonaFisica();
}
