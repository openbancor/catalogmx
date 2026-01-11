import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

List<Map<String, dynamic>> _loadVectors(String name) {
  final file = File('../shared-data/tests/$name');
  final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;
  return data.cast<Map<String, dynamic>>();
}

void main() {
  test('RFC validator shared vectors', () {
    for (final vector in _loadVectors('rfc_validation.json')) {
      expect(validateRFC(vector['value'] as String), vector['valid']);
    }
  });

  test('CURP validator shared vectors', () {
    for (final vector in _loadVectors('curp_validation.json')) {
      expect(validateCURP(vector['value'] as String), vector['valid']);
    }
  });

  test('CLABE validator shared vectors', () {
    for (final vector in _loadVectors('clabe_validation.json')) {
      expect(validateCLABE(vector['value'] as String), vector['valid']);
    }
  });

  test('NSS validator shared vectors', () {
    for (final vector in _loadVectors('nss_validation.json')) {
      expect(validateNSS(vector['value'] as String), vector['valid']);
    }
  });
}
