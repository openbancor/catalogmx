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
  test('RFC shared vectors', () {
    final file = File('../shared-data/tests/rfc_vectors.json');
    final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;

    for (final raw in data) {
      final vector = raw as Map<String, dynamic>;
      final fecha = _parseDate(vector['fecha'] as String);

      if (vector['type'] == 'fisica') {
        final rfc = generateRFC(
          nombre: vector['nombre'] as String,
          apellidoPaterno: vector['apellido_paterno'] as String,
          apellidoMaterno: vector['apellido_materno'] as String,
          fechaNacimiento: fecha,
        );
        expect(rfc, vector['rfc']);
      } else {
        final rfc = generateRFCMoral(
          razonSocial: vector['razon_social'] as String,
          fechaConstitucion: fecha,
        );
        expect(rfc, vector['rfc']);
      }
    }
  });
}
