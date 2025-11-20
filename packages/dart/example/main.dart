/// Example usage of catalogmx package
///
/// This example demonstrates how to use the catalogmx validators
/// and catalogs in a Dart/Flutter application.

import 'package:catalogmx/catalogmx.dart';

void main() {
  print('=== catalogmx Dart/Flutter Package Examples ===\n');

  // RFC Examples
  print('--- RFC Validator ---');
  print('Generic RFC: ${validateRFC('XAXX010101000')}'); // true
  print('Persona Física: ${validateRFC('OEAF771012HM8')}'); // true
  print('Invalid RFC: ${validateRFC('INVALID')}\n'); // false

  // Generate RFC
  final rfc = generateRFC(
    nombre: 'Juan',
    apellidoPaterno: 'García',
    apellidoMaterno: 'López',
    fechaNacimiento: DateTime(1990, 5, 15),
  );
  print('Generated RFC: $rfc');
  print('Is valid: ${validateRFC(rfc)}\n');

  // CURP Examples
  print('--- CURP Validator ---');
  print('Valid CURP: ${validateCURP('OEAF771012HMCRGR09')}'); // true
  print('Invalid CURP: ${validateCURP('INVALID')}\n'); // false

  // Generate CURP
  final curp = generateCURP(
    nombre: 'Juan',
    apellidoPaterno: 'García',
    apellidoMaterno: 'López',
    fechaNacimiento: DateTime(1990, 5, 15),
    sexo: 'H',
    estado: 'Jalisco',
  );
  print('Generated CURP: $curp');
  print('Is valid: ${validateCURP(curp)}\n');

  // CLABE Examples
  print('--- CLABE Validator ---');
  print('Valid CLABE: ${validateCLABE('002010077777777771')}'); // true
  print('Invalid CLABE: ${validateCLABE('123')}\n'); // false

  // Generate CLABE
  final clabe = generateCLABE(
    bankCode: '002',
    branchCode: '010',
    accountNumber: '07777777777',
  );
  print('Generated CLABE: $clabe');
  print('Is valid: ${validateCLABE(clabe)}\n');

  // NSS Examples
  print('--- NSS Validator ---');
  print('Valid NSS: ${validateNSS('12345678903')}'); // true
  print('Invalid NSS: ${validateNSS('123')}\n'); // false

  // Generate NSS
  final nss = generateNSS(
    subdelegation: '12',
    year: '34',
    serial: '56',
    sequential: '7890',
  );
  print('Generated NSS: $nss');
  print('Is valid: ${validateNSS(nss)}\n');

  // Catalog Examples
  print('--- INEGI States Catalog ---');
  final states = InegStates.getAll();
  print('Total states: ${states.length}');

  final cdmx = InegStates.getByCode('DF');
  print('CDMX: ${cdmx!['name']} (${cdmx['abbreviation']})');

  final jalisco = InegStates.getByName('Jalisco');
  print('Jalisco code: ${jalisco!['code']}');

  print('\nSearch results for "mexico":');
  final searchResults = InegStates.search('mexico');
  for (final state in searchResults) {
    print('  - ${state['name']} (${state['code']})');
  }
}
