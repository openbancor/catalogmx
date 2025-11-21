/// CLABE (Clave Bancaria Estandarizada) Validator
///
/// CLABE is the standardized 18-digit bank account number used in Mexico for
/// interbank electronic transfers (SPEI).
///
/// Structure:
/// - 3 digits: Bank code
/// - 3 digits: Branch/Plaza code
/// - 11 digits: Account number
/// - 1 digit: Check digit (modulo 10 algorithm)
///
/// Example: 002010077777777771
/// - 002: Banamex
/// - 010: Branch code
/// - 07777777777: Account number
/// - 1: Check digit
library;

/// Exception for CLABE validation errors
class CLABEException implements Exception {
  final String message;
  CLABEException(this.message);

  @override
  String toString() => 'CLABEException: $message';
}

/// CLABE Validator
class CLABEValidator {
  final String clabe;

  static const int length = 18;

  /// Weights for check digit calculation (positions 0-16)
  /// Pattern repeats: 3,7,1,3,7,1,...
  static const List<int> weights = [
    3,
    7,
    1,
    3,
    7,
    1,
    3,
    7,
    1,
    3,
    7,
    1,
    3,
    7,
    1,
    3,
    7,
  ];

  CLABEValidator(String? clabe) : clabe = clabe?.trim() ?? '';

  /// Validates the CLABE structure and check digit
  bool validate() {
    final value = clabe;

    // Check length
    if (value.length != length) {
      throw CLABEException(
          'CLABE length must be $length digits, got ${value.length}');
    }

    // Check if all characters are digits
    if (!RegExp(r'^\d+$').hasMatch(value)) {
      throw CLABEException('CLABE must contain only digits');
    }

    // Validate check digit
    if (!verifyCheckDigit(value)) {
      throw CLABEException('Invalid CLABE check digit');
    }

    return true;
  }

  /// Checks if CLABE is valid without raising exceptions
  bool isValid() {
    try {
      return validate();
    } catch (e) {
      return false;
    }
  }

  /// Calculates the check digit for a 17-digit CLABE
  ///
  /// Algorithm:
  /// 1. Multiply each digit by its weight (3,7,1 pattern)
  /// 2. Take modulo 10 of each result
  /// 3. Sum all results
  /// 4. Take modulo 10 of the sum
  /// 5. Subtract from 10
  /// 6. Take modulo 10 of the result
  static String calculateCheckDigit(String clabe17) {
    if (clabe17.length != 17) {
      throw CLABEException('Need exactly 17 digits to calculate check digit');
    }

    if (!RegExp(r'^\d+$').hasMatch(clabe17)) {
      throw CLABEException('CLABE must contain only digits');
    }

    // Calculate weighted sum
    int weightedSum = 0;
    for (var i = 0; i < clabe17.length; i++) {
      final digit = int.parse(clabe17[i]);
      final product = digit * weights[i];
      weightedSum += product % 10;
    }

    // Calculate check digit
    final checkDigit = (10 - (weightedSum % 10)) % 10;

    return checkDigit.toString();
  }

  /// Verifies the check digit of an 18-digit CLABE
  static bool verifyCheckDigit(String clabe) {
    if (clabe.length != length) return false;

    final calculated = calculateCheckDigit(clabe.substring(0, 17));
    return calculated == clabe[17];
  }

  /// Extracts the bank code (first 3 digits)
  String? getBankCode() {
    if (clabe.length >= 3) {
      return clabe.substring(0, 3);
    }
    return null;
  }

  /// Extracts the branch/plaza code (digits 4-6)
  String? getBranchCode() {
    if (clabe.length >= 6) {
      return clabe.substring(3, 6);
    }
    return null;
  }

  /// Extracts the account number (digits 7-17)
  String? getAccountNumber() {
    if (clabe.length >= 17) {
      return clabe.substring(6, 17);
    }
    return null;
  }

  /// Extracts the check digit (digit 18)
  String? getCheckDigit() {
    if (clabe.length == length) {
      return clabe[17];
    }
    return null;
  }

  /// Returns all CLABE parts as a map
  Map<String, String?>? getParts() {
    if (!isValid()) return null;

    return {
      'bank_code': getBankCode(),
      'branch_code': getBranchCode(),
      'account_number': getAccountNumber(),
      'check_digit': getCheckDigit(),
      'clabe': clabe,
    };
  }
}

// Helper functions

/// Validates a CLABE
bool validateCLABE(String? clabe) {
  try {
    final validator = CLABEValidator(clabe);
    return validator.validate();
  } catch (e) {
    return false;
  }
}

/// Generates a complete CLABE with check digit
String generateCLABE({
  required String bankCode,
  required String branchCode,
  required String accountNumber,
}) {
  // Ensure all parts are strings and properly formatted
  final bank = bankCode.padLeft(3, '0');
  final branch = branchCode.padLeft(3, '0');
  final account = accountNumber.padLeft(11, '0');

  if (bank.length != 3) {
    throw CLABEException('Bank code must be 3 digits');
  }
  if (branch.length != 3) {
    throw CLABEException('Branch code must be 3 digits');
  }
  if (account.length != 11) {
    throw CLABEException('Account number must be 11 digits');
  }

  final clabe17 = bank + branch + account;
  final checkDigit = CLABEValidator.calculateCheckDigit(clabe17);

  return clabe17 + checkDigit;
}

/// Gets information from a CLABE
Map<String, String?>? getCLABEInfo(String? clabe) {
  final validator = CLABEValidator(clabe);
  return validator.getParts();
}
