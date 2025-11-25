/// NSS (Número de Seguridad Social) Validator
///
/// NSS is the 11-digit social security number issued by IMSS
/// (Instituto Mexicano del Seguro Social).
///
/// Structure:
/// - 2 digits: Subdelegation code (IMSS office)
/// - 2 digits: Registration year (last 2 digits)
/// - 2 digits: Birth year (last 2 digits)
/// - 4 digits: Sequential number
/// - 1 digit: Check digit (modified Luhn algorithm)
///
/// Example: 12345678903
/// - 12: Subdelegation
/// - 34: Registration year (2034 or 1934)
/// - 56: Birth year (2056 or 1956)
/// - 7890: Sequential
/// - 3: Check digit
library;

/// Exception for NSS validation errors
class NSSException implements Exception {
  final String message;
  NSSException(this.message);

  @override
  String toString() => 'NSSException: $message';
}

/// NSS Validator
class NSSValidator {
  final String nss;

  static const int length = 11;

  NSSValidator(String? nss) : nss = nss?.trim() ?? '';

  /// Validates the NSS structure and check digit
  bool validate() {
    final value = nss;

    // Check length
    if (value.length != length) {
      throw NSSException(
          'NSS length must be $length digits, got ${value.length}');
    }

    // Check if all characters are digits
    if (!RegExp(r'^\d+$').hasMatch(value)) {
      throw NSSException('NSS must contain only digits');
    }

    // Validate check digit
    if (!verifyCheckDigit(value)) {
      throw NSSException('Invalid NSS check digit');
    }

    return true;
  }

  /// Checks if NSS is valid without raising exceptions
  bool isValid() {
    try {
      return validate();
    } catch (e) {
      return false;
    }
  }

  /// Calculates the check digit for a 10-digit NSS using modified Luhn algorithm
  ///
  /// Algorithm (modified Luhn):
  /// 1. Starting from the right, multiply alternating digits by 2 and 1
  /// 2. If the product is > 9, sum its digits
  /// 3. Sum all results
  /// 4. The check digit is (10 - (sum % 10)) % 10
  static String calculateCheckDigit(String nss10) {
    if (nss10.length != 10) {
      throw NSSException('Need exactly 10 digits to calculate check digit');
    }

    if (!RegExp(r'^\d+$').hasMatch(nss10)) {
      throw NSSException('NSS must contain only digits');
    }

    // Process digits from right to left
    int total = 0;
    final reversed = nss10.split('').reversed.toList();

    for (var i = 0; i < reversed.length; i++) {
      int n = int.parse(reversed[i]);

      // Alternate between multiplying by 2 and 1 (starting with 2 for rightmost)
      if (i % 2 == 0) {
        n = n * 2;
        // If result is > 9, sum its digits (e.g., 12 -> 1+2 = 3)
        if (n > 9) {
          n = n ~/ 10 + n % 10;
        }
      }

      total += n;
    }

    // Calculate check digit
    final checkDigit = (10 - (total % 10)) % 10;

    return checkDigit.toString();
  }

  /// Verifies the check digit of an 11-digit NSS
  static bool verifyCheckDigit(String nss) {
    if (nss.length != length) return false;

    final calculated = calculateCheckDigit(nss.substring(0, 10));
    return calculated == nss[10];
  }

  /// Extracts the subdelegation code (first 2 digits)
  String? getSubdelegation() {
    if (nss.length >= 2) {
      return nss.substring(0, 2);
    }
    return null;
  }

  /// Extracts the registration year (digits 3-4, last 2 digits of year)
  /// Note: This is ambiguous - could be 19XX or 20XX
  String? getRegistrationYear() {
    if (nss.length >= 4) {
      return nss.substring(2, 4);
    }
    return null;
  }

  /// Extracts the birth year (digits 5-6, last 2 digits of year)
  String? getBirthYear() {
    if (nss.length >= 6) {
      return nss.substring(4, 6);
    }
    return null;
  }

  /// Extracts the sequential number (digits 7-10)
  String? getSequential() {
    if (nss.length >= 10) {
      return nss.substring(6, 10);
    }
    return null;
  }

  /// Extracts the check digit (digit 11)
  String? getCheckDigit() {
    if (nss.length == length) {
      return nss[10];
    }
    return null;
  }

  /// Returns all NSS parts as a map
  Map<String, String?>? getParts() {
    if (!isValid()) return null;

    return {
      'subdelegation': getSubdelegation(),
      'registration_year': getRegistrationYear(),
      'birth_year': getBirthYear(),
      'sequential': getSequential(),
      'check_digit': getCheckDigit(),
      'nss': nss,
    };
  }
}

// Helper functions

/// Validates an NSS
bool validateNSS(String? nss) {
  try {
    final validator = NSSValidator(nss);
    return validator.validate();
  } catch (e) {
    return false;
  }
}

/// Generates a complete NSS with check digit
String generateNSS({
  required String subdelegation,
  required String registrationYear,
  required String birthYear,
  required String sequential,
}) {
  // Ensure all parts are strings and properly formatted
  final sub = subdelegation.padLeft(2, '0');
  final regYr = registrationYear.padLeft(2, '0');
  final birthYr = birthYear.padLeft(2, '0');
  final seq = sequential.padLeft(4, '0');

  if (sub.length != 2) {
    throw NSSException('Subdelegation must be 2 digits');
  }
  if (regYr.length != 2) {
    throw NSSException('Registration year must be 2 digits');
  }
  if (birthYr.length != 2) {
    throw NSSException('Birth year must be 2 digits');
  }
  if (seq.length != 4) {
    throw NSSException('Sequential must be 4 digits');
  }

  final nss10 = sub + regYr + birthYr + seq;
  final checkDigit = NSSValidator.calculateCheckDigit(nss10);

  return nss10 + checkDigit;
}

/// Gets information from an NSS
Map<String, String?>? getNSSInfo(String? nss) {
  final validator = NSSValidator(nss);
  return validator.getParts();
}
