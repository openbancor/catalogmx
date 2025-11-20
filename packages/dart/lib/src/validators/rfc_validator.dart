/// RFC (Registro Federal de Contribuyentes) Validator and Generator
///
/// RFC is Mexico's tax identification number, issued by SAT.
///
/// Structure:
/// - Persona Física (Individual): 13 characters (AAAA-YYMMDD-XXX)
///   - 4 letters from name
///   - 6 digits for birth date (YYMMDD)
///   - 3 alphanumeric characters (homoclave + checksum)
///
/// - Persona Moral (Company): 12 characters (AAA-YYMMDD-XXX)
///   - 3 letters from company name
///   - 6 digits for incorporation date (YYMMDD)
///   - 3 alphanumeric characters (homoclave + checksum)
///
/// Example: XAXX010101000 (Generic RFC)
library;

import 'package:diacritic/diacritic.dart';
import '../utils/date_utils.dart';
import '../utils/text_utils.dart';

/// Exception for RFC validation errors
class RFCException implements Exception {
  final String message;
  RFCException(this.message);

  @override
  String toString() => 'RFCException: $message';
}

/// RFC Validator
class RFCValidator {
  final String rfc;

  static final RegExp _generalRegex = RegExp(r'^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{2}[0-9A]$');
  static const String _homoclaveChars = 'ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789';

  static const Map<String, String> _checksumTable = {
    '0': '00', '1': '01', '2': '02', '3': '03', '4': '04',
    '5': '05', '6': '06', '7': '07', '8': '08', '9': '09',
    'A': '10', 'B': '11', 'C': '12', 'D': '13', 'E': '14',
    'F': '15', 'G': '16', 'H': '17', 'I': '18', 'J': '19',
    'K': '20', 'L': '21', 'M': '22', 'N': '23', '&': '24',
    'O': '25', 'P': '26', 'Q': '27', 'R': '28', 'S': '29',
    'T': '30', 'U': '31', 'V': '32', 'W': '33', 'X': '34',
    'Y': '35', 'Z': '36', ' ': '37', 'Ñ': '38',
  };

  static const Map<String, String> _homoclaveTable = {
    ' ': '00', '0': '00', '1': '01', '2': '02', '3': '03',
    '4': '04', '5': '05', '6': '06', '7': '07', '8': '08',
    '9': '09', '&': '10', 'A': '11', 'B': '12', 'C': '13',
    'D': '14', 'E': '15', 'F': '16', 'G': '17', 'H': '18',
    'I': '19', 'J': '21', 'K': '22', 'L': '23', 'M': '24',
    'N': '25', 'O': '26', 'P': '27', 'Q': '28', 'R': '29',
    'S': '32', 'T': '33', 'U': '34', 'V': '35', 'W': '36',
    'X': '37', 'Y': '38', 'Z': '39', 'Ñ': '40',
  };

  static const List<String> _homoclaveAssignTable = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B',
    'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
  ];

  static const List<String> _cacophonic = [
    'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA',
    'COGE', 'COJA', 'COJE', 'COJI', 'COJO', 'CULO', 'FETO',
    'GUEY', 'JOTO', 'KACA', 'KACO', 'KAGA', 'KAGO', 'KOGE',
    'KOJO', 'KAKA', 'KULO', 'MAME', 'MAMO', 'MEAR', 'MEON',
    'MION', 'MOCO', 'MULA', 'PEDA', 'PEDO', 'PENE', 'PUTA',
    'PUTO', 'QULO', 'RATA', 'RUIN',
  ];

  RFCValidator(String rfc) : rfc = rfc.toUpperCase().trim();

  /// Validates if the RFC is structurally valid
  bool validate({bool strict = true}) {
    if (!validateGeneralRegex()) return false;
    if (!validateDate()) return false;
    if (!validateHomoclave()) return false;
    if (strict && !validateChecksum()) return false;
    return true;
  }

  /// Alias for validate()
  bool isValid({bool strict = true}) => validate(strict: strict);

  /// Validates the general structure using regex
  bool validateGeneralRegex() {
    if (rfc.length != 12 && rfc.length != 13) return false;
    return _generalRegex.hasMatch(rfc);
  }

  /// Validates the date portion
  bool validateDate() {
    if (!validateGeneralRegex()) return false;
    final dateStr = rfc.substring(rfc.length == 13 ? 4 : 3, rfc.length == 13 ? 10 : 9);
    return isValidDateYYMMDD(dateStr);
  }

  /// Validates the homoclave
  bool validateHomoclave() {
    if (!validateGeneralRegex()) return false;
    final homoclave = rfc.substring(rfc.length - 3, rfc.length - 1);
    for (var i = 0; i < homoclave.length; i++) {
      if (!_homoclaveChars.contains(homoclave[i])) {
        return false;
      }
    }
    return true;
  }

  /// Validates the checksum digit
  bool validateChecksum() {
    if (!validateGeneralRegex()) return false;
    if (isGeneric()) return true; // Generic RFCs have incorrect checksums
    final calculated = calculateChecksum(rfc.substring(0, rfc.length - 1));
    return calculated == rfc[rfc.length - 1];
  }

  /// Calculates the checksum digit
  static String calculateChecksum(String rfcWithoutChecksum) {
    String rfcStr = rfcWithoutChecksum.toUpperCase().trim();
    if (rfcStr.length == 11) {
      rfcStr = ' $rfcStr';
    }
    if (rfcStr.length != 12) {
      throw RFCException('RFC must be 11 or 12 characters for checksum calculation');
    }

    int sum = 0;
    int position = 13;

    for (var i = 0; i < rfcStr.length; i++) {
      final char = rfcStr[i];
      final value = int.parse(_checksumTable[char] ?? '00');
      sum += value * position;
      position--;
    }

    final residual = sum % 11;

    if (residual == 0) {
      return '0';
    } else {
      final result = 11 - residual;
      if (result == 10) {
        return 'A';
      } else {
        return result.toString();
      }
    }
  }

  /// Checks if RFC is generic (XAXX010101000 or XEXX010101000)
  bool isGeneric() {
    return rfc == 'XAXX010101000' || rfc == 'XEXX010101000';
  }

  /// Checks if RFC belongs to a Persona Física (individual)
  bool isFisica() {
    if (!validateGeneralRegex()) {
      throw RFCException('Invalid RFC');
    }
    if (isGeneric()) return false;
    final char4 = rfc[3];
    return RegExp(r'[A-Z]').hasMatch(char4);
  }

  /// Checks if RFC belongs to a Persona Moral (company)
  bool isMoral() {
    if (!validateGeneralRegex()) {
      throw RFCException('Invalid RFC');
    }
    final char4 = rfc[3];
    return RegExp(r'[0-9]').hasMatch(char4);
  }

  /// Detects the type of RFC
  String detectType() {
    if (!validateGeneralRegex()) return 'Invalid';
    if (isGeneric()) return 'Generic';
    if (isFisica()) return 'Persona Física';
    if (isMoral()) return 'Persona Moral';
    return 'Unknown';
  }
}

/// RFC Generator for Persona Física (Individual)
class RFCGeneratorFisica {
  final String nombre;
  final String apellidoPaterno;
  final String apellidoMaterno;
  final DateTime fechaNacimiento;

  static const List<String> _excludedWords = [
    'DE', 'LA', 'LAS', 'MC', 'VON', 'DEL', 'LOS', 'Y', 'MAC', 'VAN', 'MI',
  ];

  static const List<String> _allowedChars = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '&',
  ];

  RFCGeneratorFisica({
    required this.nombre,
    required this.apellidoPaterno,
    required this.apellidoMaterno,
    required this.fechaNacimiento,
  });

  /// Generates the RFC
  String generate() {
    final letters = _generateLetters();
    final date = _generateDate();
    final homoclave = _generateHomoclave();
    final partial = letters + date + homoclave;
    final checksum = RFCValidator.calculateChecksum(partial);
    return partial + checksum;
  }

  String _cleanName(String name) {
    return cleanName(name, _excludedWords, _allowedChars);
  }

  String _generateLetters() {
    final paternoClean = _cleanName(apellidoPaterno);
    final maternoClean = _cleanName(apellidoMaterno);
    final nombreClean = _cleanName(nombre);

    // Get nombre iniciales (skip JOSE/MARIA if compound)
    String nombreIniciales = nombreClean;
    final nombreParts = nombreClean.split(' ');
    if (nombreParts.length > 1) {
      if (nombreParts[0] == 'MARIA' || nombreParts[0] == 'JOSE') {
        nombreIniciales = nombreParts.sublist(1).join(' ');
      }
    }

    final clave = StringBuffer();
    bool extraLetter = false;

    // First letter of paterno
    clave.write(paternoClean[0]);

    // First vowel of paterno (after first letter)
    final vowel = getFirstVowel(paternoClean, startIndex: 1);
    if (vowel != null) {
      clave.write(vowel);
    } else {
      extraLetter = true;
    }

    // First letter of materno or handle extra letter
    if (maternoClean.isNotEmpty) {
      clave.write(maternoClean[0]);
    } else {
      if (extraLetter) {
        clave.write(paternoClean.length > 1 ? paternoClean[1] : 'X');
      } else {
        extraLetter = true;
      }
    }

    // First letter of nombre
    clave.write(nombreIniciales[0]);
    if (extraLetter && nombreIniciales.length > 1) {
      clave.write(nombreIniciales[1]);
    }

    String result = clave.toString();

    // Check for cacophonic words
    if (RFCValidator._cacophonic.contains(result)) {
      result = result.substring(0, result.length - 1) + 'X';
    }

    return result;
  }

  String _generateDate() {
    return dateToYYMMDD(fechaNacimiento);
  }

  String _generateHomoclave() {
    final fullName = [
      _cleanName(apellidoPaterno),
      _cleanName(apellidoMaterno),
      _cleanName(nombre),
    ].where((s) => s.isNotEmpty).join(' ');

    // Build homoclave string
    final calcStr = StringBuffer('0');
    for (var i = 0; i < fullName.length; i++) {
      final char = fullName[i];
      calcStr.write(RFCValidator._homoclaveTable[char] ?? '00');
    }

    final cadena = calcStr.toString();
    int suma = 0;
    for (var n = 0; n < cadena.length - 1; n++) {
      final pair = int.parse(cadena.substring(n, n + 2));
      final nextDigit = int.parse(cadena[n + 1]);
      suma += pair * nextDigit;
    }
    suma = suma % 1000;

    final resultado1 = suma ~/ 34;
    final resultado2 = suma % 34;

    return RFCValidator._homoclaveAssignTable[resultado1] +
        RFCValidator._homoclaveAssignTable[resultado2];
  }
}

/// RFC Generator for Persona Moral (Company)
class RFCGeneratorMoral {
  final String razonSocial;
  final DateTime fechaConstitucion;

  static const List<String> _excludedWords = [
    'EL', 'LA', 'DE', 'LOS', 'LAS', 'Y', 'DEL', 'MI',
    'COMPAÑIA', 'COMPAÑÍA', 'CIA', 'CIA.', 'SOCIEDAD', 'SOC', 'SOC.',
    'COOPERATIVA', 'COOP', 'COOP.', 'S.A.', 'SA', 'S.A', 'S. A.', 'S. A',
    'S.A.B.', 'SAB', 'S.A.B', 'S. A. B.', 'S. A. B', 'S. DE R.L.',
    'S DE RL', 'SRL', 'S.R.L.', 'S. R. L.', 'S. EN C.', 'S EN C',
    'S.C.', 'SC', 'S. EN C. POR A.', 'S EN C POR A', 'S. EN N.C.',
    'S EN NC', 'A.C.', 'AC', 'A. C.', 'A. EN P.', 'A EN P',
    'S.C.L.', 'SCL', 'S.N.C.', 'SNC', 'C.V.', 'CV', 'C. V.',
    'SA DE CV', 'S.A. DE C.V.', 'THE', 'OF', 'COMPANY', 'AND',
    'CO', 'CO.', 'MC', 'VON', 'MAC', 'VAN', 'PARA', 'POR',
    'AL', 'E', 'EN', 'CON', 'SUS', 'A',
  ];

  static const List<String> _allowedChars = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '&',
  ];

  RFCGeneratorMoral({
    required this.razonSocial,
    required this.fechaConstitucion,
  });

  /// Generates the RFC
  String generate() {
    final letters = _generateLetters();
    final date = _generateDate();
    final homoclave = _generateHomoclave();
    final partial = letters + date + homoclave;
    final checksum = RFCValidator.calculateChecksum(partial);
    return partial + checksum;
  }

  String _cleanRazonSocial() {
    String razon = razonSocial.toUpperCase().trim();

    // Remove excluded words
    for (final excluded in _excludedWords) {
      razon = razon.replaceAll(' $excluded ', ' ');
      razon = razon.replaceAll(' $excluded,', ' ');
      razon = razon.replaceAll(' $excluded.', ' ');
      if (razon.startsWith('$excluded ')) {
        razon = razon.substring(excluded.length + 1);
      }
      if (razon.endsWith(' $excluded')) {
        razon = razon.substring(0, razon.length - excluded.length - 1);
      }
    }

    // Replace Ñ with X
    razon = razon.replaceAll('Ñ', 'X').replaceAll('ñ', 'X');

    // Keep only allowed characters and spaces
    final result = StringBuffer();
    for (var i = 0; i < razon.length; i++) {
      final char = razon[i];
      if (_allowedChars.contains(char) || char == ' ') {
        result.write(char);
      } else {
        final cleaned = removeDiacritics(char);
        if (_allowedChars.contains(cleaned)) {
          result.write(cleaned);
        } else if (char == ' ') {
          result.write(' ');
        }
      }
    }

    return result.toString().trim();
  }

  String _generateLetters() {
    final cleaned = _cleanRazonSocial();
    if (cleaned.isEmpty) {
      throw RFCException('Company name is empty after cleaning');
    }

    final words = cleaned.split(' ').where((w) => w.isNotEmpty).toList();
    if (words.isEmpty) {
      throw RFCException('No valid words in company name');
    }

    final clave = StringBuffer();

    if (words.length == 1) {
      // Single word: First 3 letters
      final word = words[0];
      clave.write(word.length > 0 ? word[0] : 'X');
      clave.write(word.length > 1 ? word[1] : 'X');
      clave.write(word.length > 2 ? word[2] : 'X');
    } else if (words.length == 2) {
      // Two words: First letter of first word + first two letters of second word
      clave.write(words[0][0]);
      clave.write(words[1][0]);
      clave.write(words[1].length > 1 ? words[1][1] : 'X');
    } else {
      // Three or more words: First letter of each of first three words
      clave.write(words[0][0]);
      clave.write(words[1][0]);
      clave.write(words[2][0]);
    }

    String result = clave.toString();

    // Check for cacophonic words
    if (RFCValidator._cacophonic.contains(result)) {
      result = result.substring(0, result.length - 1) + 'X';
    }

    return result;
  }

  String _generateDate() {
    return dateToYYMMDD(fechaConstitucion);
  }

  String _generateHomoclave() {
    final fullName = _cleanRazonSocial();

    // Build homoclave string
    final calcStr = StringBuffer('0');
    for (var i = 0; i < fullName.length; i++) {
      final char = fullName[i];
      calcStr.write(RFCValidator._homoclaveTable[char] ?? '00');
    }

    final cadena = calcStr.toString();
    int suma = 0;
    for (var n = 0; n < cadena.length - 1; n++) {
      final pair = int.parse(cadena.substring(n, n + 2));
      final nextDigit = int.parse(cadena[n + 1]);
      suma += pair * nextDigit;
    }
    suma = suma % 1000;

    final resultado1 = suma ~/ 34;
    final resultado2 = suma % 34;

    return RFCValidator._homoclaveAssignTable[resultado1] +
        RFCValidator._homoclaveAssignTable[resultado2];
  }
}

// Helper functions

/// Validates an RFC
bool validateRFC(String rfc, {bool strict = true}) {
  try {
    final validator = RFCValidator(rfc);
    return validator.validate(strict: strict);
  } catch (e) {
    return false;
  }
}

/// Generates RFC for Persona Física
String generateRFC({
  required String nombre,
  required String apellidoPaterno,
  required String apellidoMaterno,
  required DateTime fechaNacimiento,
}) {
  final generator = RFCGeneratorFisica(
    nombre: nombre,
    apellidoPaterno: apellidoPaterno,
    apellidoMaterno: apellidoMaterno,
    fechaNacimiento: fechaNacimiento,
  );
  return generator.generate();
}

/// Generates RFC for Persona Moral
String generateRFCMoral({
  required String razonSocial,
  required DateTime fechaConstitucion,
}) {
  final generator = RFCGeneratorMoral(
    razonSocial: razonSocial,
    fechaConstitucion: fechaConstitucion,
  );
  return generator.generate();
}
