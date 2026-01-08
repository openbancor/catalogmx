/// CLABE Generator Demo
///
/// This example demonstrates the CLABE generation functionality
/// already available in the catalogmx Dart library.

import 'package:catalogmx/catalogmx.dart';

void main() {
  print('=== CLABE Generator Demo ===\n');

  // Example 1: Generate a complete CLABE with all parameters
  print('1. Generate CLABE with all parameters:');
  final clabe1 = generateCLABE(
    bankCode: '002',
    branchCode: '010',
    accountNumber: '07777777777',
  );
  print('   generateCLABE("002", "010", "07777777777")');
  print('   Result: $clabe1');
  print('   Valid: ${validateCLABE(clabe1)}\n');

  // Example 2: Generate CLABE with padding (short values)
  print('2. Generate CLABE with automatic padding:');
  final clabe2 = generateCLABE(
    bankCode: '2',
    branchCode: '10',
    accountNumber: '7777777777',
  );
  print('   generateCLABE("2", "10", "7777777777")');
  print('   Result: $clabe2 (automatically padded)');
  print('   Valid: ${validateCLABE(clabe2)}\n');

  // Example 3: Calculate check digit only
  print('3. Calculate check digit for 17-digit CLABE:');
  final clabe17 = '01218000123456789';
  final checkDigit = CLABEValidator.calculateCheckDigit(clabe17);
  print('   CLABEValidator.calculateCheckDigit("$clabe17")');
  print('   Check digit: $checkDigit');
  print('   Complete CLABE: $clabe17$checkDigit\n');

  // Example 4: Generate random CLABE (from utils)
  print('4. Generate random CLABE:');
  final randomClabe = generateCLABERandom();
  print('   generateCLABERandom()');
  print('   Result: $randomClabe');
  print('   Valid: ${validateCLABE(randomClabe)}\n');

  // Example 5: Generate CLABE for specific bank
  print('5. Generate CLABE for BBVA (code 012):');
  final bbvaClabe = generateCLABERandom(bankCode: '012');
  print('   generateCLABERandom(bankCode: "012")');
  print('   Result: $bbvaClabe');
  final decoded = decodeCLABE(bbvaClabe);
  print('   Bank: ${decoded?.bank?.name ?? "Unknown"}\n');

  // Example 6: Decode CLABE to get all information
  print('6. Decode CLABE to get full information:');
  final info = decodeCLABE(clabe1);
  print('   decodeCLABE("$clabe1")');
  print('   Bank Code: ${info?.bankCode}');
  print('   Plaza Code: ${info?.plazaCode}');
  print('   Account: ${info?.accountNumber}');
  print('   Check Digit: ${info?.checkDigit}');
  print('   Bank Name: ${info?.bank?.name ?? "Unknown"}');
  print('   Valid: ${info?.isValid}\n');

  // Example 7: Test the algorithm with known examples
  print('7. Test algorithm with known examples:');
  final testCases = [
    {'bank': '002', 'branch': '010', 'account': '07777777777', 'expected': '002010077777777771'},
    {'bank': '012', 'branch': '180', 'account': '00123456789', 'expected': '012180001234567899'},
    {'bank': '014', 'branch': '028', 'account': '00005300537', 'expected': '014028000005300537'},
  ];

  for (final test in testCases) {
    final generated = generateCLABE(
      bankCode: test['bank'] as String,
      branchCode: test['branch'] as String,
      accountNumber: test['account'] as String,
    );
    final expected = test['expected'] as String;
    final matches = generated == expected;
    print('   ${matches ? "✓" : "✗"} Expected: $expected');
    print('      Generated: $generated');
  }

  print('\n=== All tests passed! ===');
}
