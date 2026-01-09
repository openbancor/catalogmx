import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

void main() {
  test('CLABE shared vectors', () {
    final file = File('../shared-data/tests/clabe_vectors.json');
    final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;

    for (final raw in data) {
      final vector = raw as Map<String, dynamic>;
      final clabe = generateCLABE(
        bankCode: vector['bank_code'] as String,
        branchCode: vector['branch_code'] as String,
        accountNumber: vector['account_number'] as String,
      );
      expect(clabe, vector['clabe']);
    }
  });
}
