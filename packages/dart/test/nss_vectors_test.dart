import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

void main() {
  test('NSS shared vectors', () {
    final file = File('../shared-data/tests/nss_vectors.json');
    final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;

    for (final raw in data) {
      final vector = raw as Map<String, dynamic>;
      final nss = generateNSS(
        subdelegation: vector['subdelegacion'] as String,
        registrationYear: vector['registro_anio'] as String,
        birthYear: vector['nacimiento_anio'] as String,
        sequential: vector['secuencial'] as String,
      );
      expect(nss, vector['nss']);
    }
  });
}
