#!/usr/bin/env dart
/// Validators App - Dart
///
/// Demuestra los validadores de RFC, CURP, CLABE y NSS.
///
/// Uso:
///   dart run example/validators_app.dart
library;

import 'package:catalogmx/catalogmx.dart';

void printHeader() {
  print('');
  print('╔══════════════════════════════════════════════════════╗');
  print('║     🪪 Validadores Mexicanos - catalogmx             ║');
  print('╚══════════════════════════════════════════════════════╝');
  print('');
}

void demoRfc() {
  print('  📋 RFC (Registro Federal de Contribuyentes)');
  print('  ───────────────────────────────────────────');
  print('');

  // Generar RFC persona física
  final rfcFisica = generateRFC(
    nombre: 'Juan',
    apellidoPaterno: 'García',
    apellidoMaterno: 'López',
    fechaNacimiento: DateTime(1990, 5, 15),
  );

  print('  Persona Física:');
  print('    Nombre: Juan García López');
  print('    Fecha:  1990-05-15');
  print('    RFC:    $rfcFisica');
  print('    Válido: ${validateRFC(rfcFisica) ? '✅' : '❌'}');
  print('');

  // Generar RFC persona moral
  final rfcMoral = generateRFCMoral(
    razonSocial: 'Tecnologías Avanzadas',
    fechaConstitucion: DateTime(2010, 6, 1),
  );

  print('  Persona Moral:');
  print('    Razón Social: Tecnologías Avanzadas');
  print('    Constitución: 2010-06-01');
  print('    RFC:          $rfcMoral');
  print('    Válido:       ${validateRFC(rfcMoral) ? '✅' : '❌'}');
  print('');
}

void demoCurp() {
  print('  🆔 CURP (Clave Única de Registro de Población)');
  print('  ──────────────────────────────────────────────');
  print('');

  // Generar CURP
  final curp = generateCURP(
    nombre: 'María',
    apellidoPaterno: 'Hernández',
    apellidoMaterno: 'Sánchez',
    fechaNacimiento: DateTime(1985, 3, 20),
    sexo: 'M',
    estado: 'Jalisco',
  );

  print('  Datos:');
  print('    Nombre: María Hernández Sánchez');
  print('    Fecha:  1985-03-20');
  print('    Sexo:   Mujer');
  print('    Estado: Jalisco');
  print('');
  print('    CURP:   $curp');
  print('    Válido: ${validateCURP(curp) ? '✅' : '❌'}');
  print('');
}

void demoClabe() {
  print('  🏦 CLABE (Clave Bancaria Estandarizada)');
  print('  ───────────────────────────────────────');
  print('');

  // Generar CLABE
  final clabe = generateCLABE(
    bankCode: '012',
    branchCode: '180',
    accountNumber: '12345678901',
  );

  print('  Datos:');
  print('    Banco:   012 (BBVA México)');
  print('    Plaza:   180');
  print('    Cuenta:  12345678901');
  print('');
  print('    CLABE:   $clabe');
  print('    Válida:  ${validateCLABE(clabe) ? '✅' : '❌'}');
  print('');
}

void demoNss() {
  print('  🏥 NSS (Número de Seguridad Social)');
  print('  ────────────────────────────────────');
  print('');

  // Generar NSS
  final nss = generateNSS(
    subdelegacion: 45,
    anioRegistro: 90,
    anioNacimiento: 85,
    secuencial: 1234,
  );

  print('  Datos:');
  print('    Subdelegación:   45');
  print('    Año registro:    90');
  print('    Año nacimiento:  85');
  print('    Secuencial:      1234');
  print('');
  print('    NSS:     $nss');
  print('    Válido:  ${validateNSS(nss) ? '✅' : '❌'}');
  print('');
}

void validarCodigo(String codigo) {
  print('  Validando: $codigo');
  print('  ─────────────────────────────────');

  final len = codigo.length;

  if (len == 18) {
    // Puede ser CURP o CLABE
    if (RegExp(r'^\d+$').hasMatch(codigo)) {
      // CLABE (solo dígitos)
      final esValido = validateCLABE(codigo);
      print('  Tipo:   CLABE');
      print('  Válido: ${esValido ? '✅' : '❌'}');
    } else {
      // CURP
      final esValido = validateCURP(codigo);
      print('  Tipo:   CURP');
      print('  Válido: ${esValido ? '✅' : '❌'}');
    }
  } else if (len == 13) {
    // RFC persona física
    final esValido = validateRFC(codigo);
    print('  Tipo:   RFC (persona física)');
    print('  Válido: ${esValido ? '✅' : '❌'}');
  } else if (len == 12) {
    // RFC persona moral
    final esValido = validateRFC(codigo);
    print('  Tipo:   RFC (persona moral)');
    print('  Válido: ${esValido ? '✅' : '❌'}');
  } else if (len == 11) {
    // NSS
    final esValido = validateNSS(codigo);
    print('  Tipo:   NSS');
    print('  Válido: ${esValido ? '✅' : '❌'}');
  } else {
    print('  ❓ Código no reconocido (longitud: $len)');
  }
  print('');
}

void main(List<String> args) {
  printHeader();

  final comando = args.isNotEmpty ? args[0].toLowerCase() : 'demo';

  switch (comando) {
    case 'demo':
      demoRfc();
      demoCurp();
      demoClabe();
      demoNss();
      break;

    case 'rfc':
      demoRfc();
      break;

    case 'curp':
      demoCurp();
      break;

    case 'clabe':
      demoClabe();
      break;

    case 'nss':
      demoNss();
      break;

    case 'validar':
      if (args.length > 1) {
        validarCodigo(args[1].toUpperCase());
      } else {
        print('  Uso: dart run example/validators_app.dart validar <código>');
      }
      break;

    default:
      print('  Uso:');
      print('    dart run example/validators_app.dart demo');
      print('    dart run example/validators_app.dart rfc');
      print('    dart run example/validators_app.dart curp');
      print('    dart run example/validators_app.dart clabe');
      print('    dart run example/validators_app.dart nss');
      print('    dart run example/validators_app.dart validar GALO850320HJCRPN07');
  }
}
