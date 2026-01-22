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
import 'package:catalogmx/src/utils/date_utils.dart';
import 'package:catalogmx/src/utils/text_utils.dart';

/// Exception for RFC validation errors
class RFCException implements Exception {
  RFCException(this.message);

  final String message;

  @override
  String toString() => 'RFCException: $message';
}

/// RFC Validator
class RFCValidator {
  RFCValidator(String rfc) : rfc = rfc.toUpperCase().trim();

  final String rfc;

  static final RegExp _generalRegex = RegExp(
    r'^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{2}[0-9A]$',
  );
  static const String _homoclaveChars = 'ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789';

  static const Map<String, String> _checksumTable = {
    '0': '00',
    '1': '01',
    '2': '02',
    '3': '03',
    '4': '04',
    '5': '05',
    '6': '06',
    '7': '07',
    '8': '08',
    '9': '09',
    'A': '10',
    'B': '11',
    'C': '12',
    'D': '13',
    'E': '14',
    'F': '15',
    'G': '16',
    'H': '17',
    'I': '18',
    'J': '19',
    'K': '20',
    'L': '21',
    'M': '22',
    'N': '23',
    '&': '24',
    'O': '25',
    'P': '26',
    'Q': '27',
    'R': '28',
    'S': '29',
    'T': '30',
    'U': '31',
    'V': '32',
    'W': '33',
    'X': '34',
    'Y': '35',
    'Z': '36',
    ' ': '37',
    'Ñ': '38',
  };

  static const Map<String, String> _homoclaveTable = {
    ' ': '00',
    '0': '00',
    '1': '01',
    '2': '02',
    '3': '03',
    '4': '04',
    '5': '05',
    '6': '06',
    '7': '07',
    '8': '08',
    '9': '09',
    '&': '10',
    'A': '11',
    'B': '12',
    'C': '13',
    'D': '14',
    'E': '15',
    'F': '16',
    'G': '17',
    'H': '18',
    'I': '19',
    'J': '21',
    'K': '22',
    'L': '23',
    'M': '24',
    'N': '25',
    'O': '26',
    'P': '27',
    'Q': '28',
    'R': '29',
    'S': '32',
    'T': '33',
    'U': '34',
    'V': '35',
    'W': '36',
    'X': '37',
    'Y': '38',
    'Z': '39',
    'Ñ': '40',
  };

  static const List<String> _homoclaveAssignTable = [
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z',
  ];

  static const List<String> _cacophonic = [
    'BUEI',
    'BUEY',
    'CACA',
    'CACO',
    'CAGA',
    'CAGO',
    'CAKA',
    'COGE',
    'COJA',
    'COJE',
    'COJI',
    'COJO',
    'CULO',
    'FETO',
    'GUEY',
    'JOTO',
    'KACA',
    'KACO',
    'KAGA',
    'KAGO',
    'KOGE',
    'KOJO',
    'KAKA',
    'KULO',
    'MAME',
    'MAMO',
    'MEAR',
    'MEON',
    'MION',
    'MOCO',
    'MULA',
    'PEDA',
    'PEDO',
    'PENE',
    'PUTA',
    'PUTO',
    'QULO',
    'RATA',
    'RUIN',
  ];

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
    final dateStr = rfc.substring(
      rfc.length == 13 ? 4 : 3,
      rfc.length == 13 ? 10 : 9,
    );
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
      throw RFCException(
        'RFC must be 11 or 12 characters for checksum calculation',
      );
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
  RFCGeneratorFisica({
    required this.nombre,
    required this.apellidoPaterno,
    required this.apellidoMaterno,
    required this.fechaNacimiento,
  });

  final String nombre;
  final String apellidoPaterno;
  final String apellidoMaterno;
  final DateTime fechaNacimiento;

  static const List<String> _excludedWords = [
    'DE',
    'LA',
    'LAS',
    'MC',
    'VON',
    'DEL',
    'LOS',
    'Y',
    'MAC',
    'VAN',
    'MI',
  ];

  static const List<String> _allowedChars = [
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'Ñ',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z',
    '&',
  ];

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
    final nombreParts =
        nombreClean.split(' ').where((p) => p.isNotEmpty).toList();
    if (nombreParts.length > 1) {
      if (nombreParts[0] == 'MARIA' || nombreParts[0] == 'JOSE') {
        nombreIniciales = nombreParts.sublist(1).join(' ');
        if (nombreIniciales.isEmpty) nombreIniciales = nombreParts[0];
      }
    }

    // Get parts of compound surnames
    final paternoParts =
        paternoClean.split(' ').where((p) => p.isNotEmpty).toList();
    final maternoParts =
        maternoClean.split(' ').where((p) => p.isNotEmpty).toList();

    final paternoFirst = paternoParts.isNotEmpty ? paternoParts[0] : '';
    final nombreSafe = nombreIniciales.isNotEmpty ? nombreIniciales : 'X';

    // Check if materno originally had prepositions
    final originalMaternoUpper = apellidoMaterno.toUpperCase().trim();
    final maternoHadPrepositions = originalMaternoUpper.startsWith('DE ') ||
        originalMaternoUpper.startsWith('DEL ') ||
        originalMaternoUpper.startsWith('LA ') ||
        originalMaternoUpper.startsWith('LOS ') ||
        originalMaternoUpper.startsWith('LAS ');

    // Determine effective materno: use second word of paterno if materno was preposition-based or empty
    String effectiveMaternoFirst =
        maternoParts.isNotEmpty ? maternoParts[0] : '';
    if (paternoParts.length >= 2 &&
        (maternoHadPrepositions || effectiveMaternoFirst.isEmpty)) {
      effectiveMaternoFirst = paternoParts.length >= 2 ? paternoParts[1] : '';
    }

    String iniciales = '';

    // Regla 4: Apellido paterno de 1-2 letras
    if (paternoFirst.isNotEmpty &&
        paternoFirst.length <= 2 &&
        effectiveMaternoFirst.isNotEmpty) {
      iniciales = paternoFirst.isNotEmpty ? paternoFirst[0] : 'X';
      iniciales +=
          effectiveMaternoFirst.isNotEmpty ? effectiveMaternoFirst[0] : 'X';
      iniciales += nombreSafe.isNotEmpty ? nombreSafe[0] : 'X';
      iniciales += nombreSafe.length > 1 ? nombreSafe[1] : 'X';
    }
    // Regla 7: Un solo apellido (sin materno)
    else if (effectiveMaternoFirst.isEmpty) {
      final apellido = paternoFirst.isNotEmpty ? paternoFirst : 'X';
      iniciales = apellido.isNotEmpty ? apellido[0] : 'X';
      iniciales += apellido.length > 1 ? apellido[1] : 'X';
      iniciales += nombreSafe.isNotEmpty ? nombreSafe[0] : 'X';
      iniciales += nombreSafe.length > 1 ? nombreSafe[1] : 'X';
    }
    // Regla 1: Formación básica
    else {
      iniciales = paternoFirst.isNotEmpty ? paternoFirst[0] : 'X';
      final vowel = getFirstVowel(paternoFirst, startIndex: 1);
      iniciales += vowel ?? 'X';
      iniciales +=
          effectiveMaternoFirst.isNotEmpty ? effectiveMaternoFirst[0] : 'X';
      iniciales += nombreSafe.isNotEmpty ? nombreSafe[0] : 'X';
    }

    // Check for cacophonic words
    if (RFCValidator._cacophonic.contains(iniciales)) {
      iniciales = iniciales.substring(0, iniciales.length - 1) + 'X';
    }

    return iniciales;
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

/// Number conversion tables
const Map<String, String> _numerosTexto = {
  '0': 'CERO',
  '1': 'UNO',
  '2': 'DOS',
  '3': 'TRES',
  '4': 'CUATRO',
  '5': 'CINCO',
  '6': 'SEIS',
  '7': 'SIETE',
  '8': 'OCHO',
  '9': 'NUEVE',
  '10': 'DIEZ',
  '11': 'ONCE',
  '12': 'DOCE',
  '13': 'TRECE',
  '14': 'CATORCE',
  '15': 'QUINCE',
  '16': 'DIECISEIS',
  '17': 'DIECISIETE',
  '18': 'DIECIOCHO',
  '19': 'DIECINUEVE',
  '20': 'VEINTE',
  '21': 'VEINTIUNO',
  '22': 'VEINTIDOS',
  '23': 'VEINTITRES',
  '24': 'VEINTICUATRO',
  '25': 'VEINTICINCO',
  '26': 'VEINTISEIS',
  '27': 'VEINTISIETE',
  '28': 'VEINTIOCHO',
  '29': 'VEINTINUEVE',
  '30': 'TREINTA',
  '40': 'CUARENTA',
  '50': 'CINCUENTA',
  '60': 'SESENTA',
  '70': 'SETENTA',
  '80': 'OCHENTA',
  '90': 'NOVENTA',
  '100': 'CIEN',
  '200': 'DOSCIENTOS',
  '300': 'TRESCIENTOS',
  '400': 'CUATROCIENTOS',
  '500': 'QUINIENTOS',
  '600': 'SEISCIENTOS',
  '700': 'SETECIENTOS',
  '800': 'OCHOCIENTOS',
  '900': 'NOVECIENTOS',
};

const Map<String, int> _numerosRomanos = {
  'I': 1,
  'II': 2,
  'III': 3,
  'IV': 4,
  'V': 5,
  'VI': 6,
  'VII': 7,
  'VIII': 8,
  'IX': 9,
  'X': 10,
  'XI': 11,
  'XII': 12,
  'XIII': 13,
  'XIV': 14,
  'XV': 15,
  'XVI': 16,
  'XVII': 17,
  'XVIII': 18,
  'XIX': 19,
  'XX': 20,
  'XXI': 21,
  'XXII': 22,
  'XXIII': 23,
  'XXIV': 24,
  'XXV': 25,
  'XXVI': 26,
  'XXVII': 27,
  'XXVIII': 28,
  'XXIX': 29,
  'XXX': 30,
};

const Map<String, String> _specialCharWords = {
  '@': 'ARROBA',
  '%': 'PORCIENTO',
  '#': 'NUMERO',
  '(': 'ABRE',
  '/': 'DIAGONAL',
};

/// Convert Arabic number to text (supports 0-100000)
String _convertArabigoATexto(int num) {
  if (num < 0) return num.toString();
  if (_numerosTexto.containsKey(num.toString())) {
    return _numerosTexto[num.toString()]!;
  }
  if (num == 100000) return 'CIEN MIL';

  final parts = <String>[];

  if (num >= 1000) {
    final thousands = num ~/ 1000;
    if (thousands == 1) {
      parts.add('MIL');
    } else {
      parts.add(_convertArabigoATexto(thousands));
      parts.add('MIL');
    }
    num = num % 1000;
  }

  if (num >= 100) {
    final hundreds = (num ~/ 100) * 100;
    if (_numerosTexto.containsKey(hundreds.toString())) {
      parts.add(_numerosTexto[hundreds.toString()]!);
    }
    num = num % 100;
  }

  if (num > 0) {
    if (_numerosTexto.containsKey(num.toString())) {
      parts.add(_numerosTexto[num.toString()]!);
    } else if (num >= 30) {
      final tens = (num ~/ 10) * 10;
      final units = num % 10;
      if (_numerosTexto.containsKey(tens.toString())) {
        parts.add(_numerosTexto[tens.toString()]!);
      }
      if (units > 0 && _numerosTexto.containsKey(units.toString())) {
        parts.add(_numerosTexto[units.toString()]!);
      }
    }
  }

  return parts.isNotEmpty ? parts.join(' ') : num.toString();
}

/// Convert number (Arabic or Roman) to text
String _convertirNumeroATexto(String numero) {
  final upper = numero.trim().toUpperCase();
  if (_numerosRomanos.containsKey(upper)) {
    return _convertArabigoATexto(_numerosRomanos[upper]!);
  }
  final num = int.tryParse(upper);
  if (num != null && num >= 0) {
    return _convertArabigoATexto(num);
  }
  return numero;
}

/// RFC Generator for Persona Moral (Company)
class RFCGeneratorMoral {
  RFCGeneratorMoral({
    required this.razonSocial,
    required this.fechaConstitucion,
  });

  final String razonSocial;
  final DateTime fechaConstitucion;

  static const List<String> _excludedWords = [
    'EL',
    'LA',
    'DE',
    'LOS',
    'LAS',
    'Y',
    'DEL',
    'MI',
    'COMPAÑIA',
    'COMPAÑÍA',
    'COMPANIA', // without accent
    'CIA',
    'CIA.',
    'SOCIEDAD',
    'SOC',
    'SOC.',
    // Note: COOPERATIVA is NOT excluded according to SAT spec
    'S.A.',
    'SA',
    'S.A',
    'S. A.',
    'S. A',
    'S.A.B.',
    'SAB',
    'S.A.B',
    'S. A. B.',
    'S. A. B',
    'S. DE R.L.',
    'S DE RL',
    'SRL',
    'S.R.L.',
    'S. R. L.',
    'S. EN C.',
    'S EN C',
    'S.C.',
    'SC',
    'S. EN C. POR A.',
    'S EN C POR A',
    'S. EN N.C.',
    'S EN NC',
    'A.C.',
    'AC',
    'A. C.',
    'A. EN P.',
    'A EN P',
    'S.C.L.',
    'SCL',
    'S.N.C.',
    'SNC',
    'C.V.',
    'CV',
    'C. V.',
    'SA DE CV',
    'S.A. DE C.V.',
    'SA DE CV MI',
    'S.A. DE C.V. MI',
    'S.A.B. DE C.V.',
    'SAB DE CV',
    'S.A.B DE C.V',
    'SRL DE CV',
    'S.R.L. DE C.V.',
    'SRL DE CV MI',
    'SRL MI',
    'THE',
    'OF',
    'COMPANY',
    'AND',
    'CO',
    'CO.',
    'MC',
    'VON',
    'MAC',
    'VAN',
    'PARA',
    'POR',
    'AL',
    'E',
    'EN',
    'CON',
    'SUS',
    'A',
  ];

  static const List<String> _allowedChars = [
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'Ñ',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z',
    '&',
  ];

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
    var razon = razonSocial.toUpperCase().trim();

    // Step 0: Handle special characters - different treatment for standalone vs embedded
    for (final entry in _specialCharWords.entries) {
      final char = entry.key;
      final word = entry.value;
      // Replace standalone special chars with their word equivalents
      razon = razon.replaceAllMapped(
        RegExp('(^|\\s)${RegExp.escape(char)}(\\s|\$)'),
        (m) => '${m.group(1)}$word${m.group(2)}',
      );
    }
    // Remove special characters embedded inside words
    for (final char in _specialCharWords.keys) {
      razon = razon.replaceAll(char, '');
    }

    // Step 1: First pass - remove excluded words with punctuation patterns
    final sortedExcluded = List<String>.from(_excludedWords)
      ..sort((a, b) => b.length.compareTo(a.length));
    for (final excluded in sortedExcluded) {
      razon = razon.replaceAll(' $excluded ', ' ');
      razon = razon.replaceAll(' $excluded,', ' ');
      razon = razon.replaceAll(' $excluded.', ' ');
      if (razon.startsWith('$excluded ')) {
        razon = razon.substring(excluded.length + 1);
      }
      if (razon.endsWith(' $excluded')) {
        razon = razon.substring(0, razon.length - excluded.length - 1);
      }
      if (razon.endsWith(',$excluded')) {
        razon = razon.substring(0, razon.length - excluded.length - 1);
      }
    }

    // Step 2: Remove special characters except spaces, letters, numbers, dots, and &
    const allowedForProcessing =
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .ÑÁÉÍÓÚÜñáéíóúü&';
    final sanitized = StringBuffer();
    for (var i = 0; i < razon.length; i++) {
      final char = razon[i];
      if (allowedForProcessing.contains(char)) {
        sanitized.write(char);
      } else {
        sanitized.write(' ');
      }
    }
    razon = sanitized.toString();

    // Step 3: Substitute Ñ with X
    razon = razon.replaceAll('Ñ', 'X').replaceAll('ñ', 'X');

    // Step 4: Handle initials (F.A.Z. → F A Z) and convert numbers
    final wordsTemp = <String>[];
    final isInitial = <bool>[];

    for (final word in razon.split(RegExp(r'\s+'))) {
      final trimmed = word.trim();
      if (trimmed.isEmpty) continue;

      // Detect initials pattern
      if (trimmed.contains('.') && trimmed.length <= 15) {
        final parts =
            trimmed.split('.').where((c) => c.trim().isNotEmpty).toList();
        if (parts.isNotEmpty &&
            parts.every((p) =>
                p.length <= 2 &&
                RegExp(r'^[A-Z]+$', caseSensitive: false).hasMatch(p))) {
          for (final part in parts) {
            wordsTemp.add(part.toUpperCase());
            isInitial.add(true);
          }
          continue;
        }
      }
      // Remove trailing dots from normal words
      final cleanWord = trimmed.replaceAll(RegExp(r'\.+$'), '');
      if (cleanWord.isNotEmpty) {
        wordsTemp.add(cleanWord);
        isInitial.add(false);
      }
    }

    // Step 5: Convert numbers to text (Arabic and Roman)
    final wordsConverted = <String>[];
    final isInitialConverted = <bool>[];

    for (var i = 0; i < wordsTemp.length; i++) {
      final word = wordsTemp[i];
      final isInit = isInitial[i];
      // Check if it's a number
      if (RegExp(r'^\d+$').hasMatch(word) ||
          _numerosRomanos.containsKey(word)) {
        wordsConverted.add(_convertirNumeroATexto(word));
      } else {
        wordsConverted.add(word);
      }
      isInitialConverted.add(isInit);
    }

    // Step 6: Second pass - Remove excluded words (but keep initials)
    final filteredWords = <String>[];
    for (var i = 0; i < wordsConverted.length; i++) {
      final word = wordsConverted[i].trim().toUpperCase();
      if (word.isEmpty) continue;
      if (isInitialConverted[i]) {
        filteredWords.add(word);
      } else if (!_excludedWords.contains(word)) {
        filteredWords.add(word);
      }
    }

    // If ALL words were excluded, keep the original words
    final wordsToUse = filteredWords.isEmpty
        ? wordsConverted.map((w) => w.toUpperCase()).toList()
        : filteredWords;

    // Step 7: Clean remaining special characters and accents
    final result = StringBuffer();
    for (final char in wordsToUse.join(' ').split('')) {
      if (_allowedChars.contains(char)) {
        result.write(char);
      } else if (char == ' ') {
        result.write(' ');
      } else {
        final decoded = removeDiacritics(char);
        if (_allowedChars.contains(decoded.toUpperCase())) {
          result.write(decoded.toUpperCase());
        }
      }
    }
    final resultStr = result.toString().trim().toUpperCase();

    // Step 8: Handle consonant compounds (CH → C, LL → L)
    final wordsFinal = <String>[];
    for (final word in resultStr.split(RegExp(r'\s+'))) {
      var processedWord = word;
      if (word.startsWith('CH')) {
        processedWord = 'C${word.substring(2)}';
      } else if (word.startsWith('LL')) {
        processedWord = 'L${word.substring(2)}';
      }
      wordsFinal.add(processedWord);
    }

    return wordsFinal.join(' ');
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
      clave.write(word.isNotEmpty ? word[0] : 'X');
      clave.write(word.length > 1 ? word[1] : 'X');
      clave.write(word.length > 2 ? word[2] : 'X');
    } else if (words.length == 2) {
      // Two words: First letter of first word + first two letters of second word
      clave.write(words[0][0]);
      final second = words[1];
      clave.write(second.isNotEmpty ? second[0] : 'X');
      clave.write(second.length > 1 ? second[1] : 'X');
    } else {
      // Three or more words: First letter of each of first three words
      clave.write(words[0][0]);
      clave.write(words[1][0]);
      clave.write(words[2][0]);
    }

    var result = clave.toString();

    // Check for cacophonic words
    if (RFCValidator._cacophonic.contains(result)) {
      result = '${result.substring(0, result.length - 1)}X';
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
