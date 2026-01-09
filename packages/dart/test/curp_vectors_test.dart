import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

DateTime _parseDate(String value) {
  final parts = value.split('-');
  if (parts.length != 3) {
    throw FormatException('Expected YYYY-MM-DD date format.');
  }
  final year = int.parse(parts[0]);
  final month = int.parse(parts[1]);
  final day = int.parse(parts[2]);
  return DateTime(year, month, day);
}

void main() {
  test('CURP shared vectors', () {
    final file = File('../shared-data/tests/curp_vectors.json');
    final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;

    for (final raw in data) {
      final vector = raw as Map<String, dynamic>;
      final curp = generateCURP(
        nombre: vector['nombre'] as String,
        apellidoPaterno: vector['apellido_paterno'] as String,
        apellidoMaterno: vector['apellido_materno'] as String,
        fechaNacimiento: _parseDate(vector['fecha'] as String),
        sexo: (vector['sexo'] as String),
        estado: vector['estado'] as String,
      );
      expect(curp, vector['curp']);
    }
  });
}
