/// CLABE Generator Quick Reference
///
/// This file demonstrates the most common CLABE generation use cases.

import 'package:catalogmx/catalogmx.dart';

void main() {
  print('CLABE Generator Quick Reference\n');
  print('=' * 60);

  // ============================================================================
  // 1. BASIC GENERATION - Generate complete CLABE
  // ============================================================================
  print('\n1. BASIC GENERATION');
  print('-' * 60);

  final clabe = generateCLABE(
    bankCode: '002', // Banamex
    branchCode: '010', // Branch code
    accountNumber: '07777777777', // 11-digit account
  );

  print('generateCLABE(');
  print('  bankCode: "002",');
  print('  branchCode: "010",');
  print('  accountNumber: "07777777777",');
  print(')');
  print('Result: $clabe');
  print('Valid: ${validateCLABE(clabe)}');

  // ============================================================================
  // 2. WITH AUTOMATIC PADDING
  // ============================================================================
  print('\n2. WITH AUTOMATIC PADDING');
  print('-' * 60);

  final clabe2 = generateCLABE(
    bankCode: '2', // Will be padded to "002"
    branchCode: '10', // Will be padded to "010"
    accountNumber: '7777777777', // Will be padded to "07777777777"
  );

  print('generateCLABE(');
  print('  bankCode: "2",        → padded to "002"');
  print('  branchCode: "10",      → padded to "010"');
  print('  accountNumber: "7777777777", → padded to "07777777777"');
  print(')');
  print('Result: $clabe2');

  // ============================================================================
  // 3. CALCULATE CHECK DIGIT ONLY
  // ============================================================================
  print('\n3. CALCULATE CHECK DIGIT ONLY');
  print('-' * 60);

  const clabe17 = '01218000123456789'; // 17 digits (without check digit)
  final checkDigit = CLABEValidator.calculateCheckDigit(clabe17);

  print('CLABEValidator.calculateCheckDigit("$clabe17")');
  print('Check Digit: $checkDigit');
  print('Complete CLABE: $clabe17$checkDigit');

  // ============================================================================
  // 4. VALIDATION
  // ============================================================================
  print('\n4. VALIDATION');
  print('-' * 60);

  final validClabe = '002010077777777771';
  final invalidClabe = '002010077777777770';

  print('validateCLABE("$validClabe"): ${validateCLABE(validClabe)}');
  print('validateCLABE("$invalidClabe"): ${validateCLABE(invalidClabe)}');

  // ============================================================================
  // 5. EXTRACT PARTS
  // ============================================================================
  print('\n5. EXTRACT PARTS');
  print('-' * 60);

  final validator = CLABEValidator(validClabe);
  print('CLABE: $validClabe');
  print('  Bank Code:      ${validator.getBankCode()}');
  print('  Branch Code:    ${validator.getBranchCode()}');
  print('  Account Number: ${validator.getAccountNumber()}');
  print('  Check Digit:    ${validator.getCheckDigit()}');

  // ============================================================================
  // 6. RANDOM GENERATION (Advanced - from clabe_utils.dart)
  // ============================================================================
  print('\n6. RANDOM GENERATION');
  print('-' * 60);

  // Fully random CLABE
  final randomClabe = generateCLABERandom();
  print('generateCLABERandom()');
  print('Result: $randomClabe');

  // Random CLABE for specific bank
  final bbvaClabe = generateCLABERandom(bankCode: '012');
  print('\ngenerateCLABERandom(bankCode: "012")');
  print('Result: $bbvaClabe');

  // ============================================================================
  // 7. DECODE CLABE (Advanced - from clabe_utils.dart)
  // ============================================================================
  print('\n7. DECODE CLABE');
  print('-' * 60);

  final info = decodeCLABE(validClabe);
  if (info != null) {
    print('decodeCLABE("$validClabe")');
    print('  Bank Code:      ${info.bankCode}');
    print('  Plaza Code:     ${info.plazaCode}');
    print('  Account Number: ${info.accountNumber}');
    print('  Check Digit:    ${info.checkDigit}');
    print('  Is Valid:       ${info.isValid}');
  }

  // ============================================================================
  // 8. FORMAT CLABE (Advanced - from clabe_utils.dart)
  // ============================================================================
  print('\n8. FORMAT CLABE');
  print('-' * 60);

  final formatted = formatCLABE(validClabe);
  print('formatCLABE("$validClabe")');
  print('Result: $formatted');

  final formattedSpace = formatCLABE(validClabe, separator: ' ');
  print('\nformatCLABE("$validClabe", separator: " ")');
  print('Result: $formattedSpace');

  // ============================================================================
  // SUMMARY
  // ============================================================================
  print('\n' + '=' * 60);
  print('SUMMARY OF FUNCTIONS');
  print('=' * 60);
  print('''
Core Functions (from clabe_validator.dart):
  ✓ generateCLABE() - Generate complete CLABE with check digit
  ✓ CLABEValidator.calculateCheckDigit() - Calculate check digit only
  ✓ validateCLABE() - Validate a CLABE
  ✓ getCLABEInfo() - Extract all parts from a CLABE

Advanced Functions (from clabe_utils.dart):
  ✓ generateCLABERandom() - Random CLABE generation
  ✓ generateCLABEForBank() - Generate by bank name
  ✓ decodeCLABE() - Full CLABE decoding with bank/plaza info
  ✓ formatCLABE() - Format with separators
  ✓ describeCLABE() - Human-readable description
  ✓ getCommonBanks() - List of SPEI banks
  ✓ getPlazaSuggestions() - Search plazas

Check Digit Algorithm:
  1. Multiply each of first 17 digits by weight [3,7,1] repeating
  2. Take modulo 10 of each product
  3. Sum all results
  4. Check digit = (10 - (sum % 10)) % 10

Example: 002010077777777777 → Check digit = 1 → 002010077777777771
''');
}
