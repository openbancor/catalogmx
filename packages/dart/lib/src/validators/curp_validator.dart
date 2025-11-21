/// CURP (Clave Única de Registro de Población) Validator and Generator
///
/// CURP is Mexico's unique population registry code, issued by RENAPO.
///
/// Structure (18 characters):
/// - 4 letters from name (like RFC)
/// - 6 digits for birth date (YYMMDD)
/// - 1 letter for gender (H=Male, M=Female)
/// - 2 letters for birth state code
/// - 3 consonants from paterno, materno, nombre
/// - 1 alphanumeric differentiator (assigned by RENAPO)
/// - 1 numeric check digit
///
/// Example: OEAF771012HMCRGR09
library;

import 'package:diacritic/diacritic.dart';
import 'package:catalogmx/src/utils/date_utils.dart';
import 'package:catalogmx/src/utils/text_utils.dart';

/// Exception for CURP validation errors
class CURPException implements Exception {
  final String message;
  CURPException(this.message);

  @override
  String toString() => 'CURPException: $message';
}

/// CURP Validator
class CURPValidator {
  final String curp;

  static final RegExp _generalRegex = RegExp(
    r'^[A-Z][AEIOUX][A-Z]{2}[0-9]{2}[0-1][0-9][0-3][0-9][MH][A-Z]{2}[BCDFGHJKLMNPQRSTVWXYZ]{3}[0-9A-Z]{2}$',
  );

  static const int length = 18;

  static const Map<String, String> _stateCodes = {
    'AGUASCALIENTES': 'AS',
    'BAJA CALIFORNIA': 'BC',
    'BAJA CALIFORNIA SUR': 'BS',
    'CAMPECHE': 'CC',
    'COAHUILA': 'CL',
    'COLIMA': 'CM',
    'CHIAPAS': 'CS',
    'CHIHUAHUA': 'CH',
    'CIUDAD DE MEXICO': 'DF',
    'DISTRITO FEDERAL': 'DF',
    'CDMX': 'DF',
    'DURANGO': 'DG',
    'GUANAJUATO': 'GT',
    'GUERRERO': 'GR',
    'HIDALGO': 'HG',
    'JALISCO': 'JC',
    'ESTADO DE MEXICO': 'MC',
    'MEXICO': 'MC',
    'MICHOACAN': 'MN',
    'MORELOS': 'MS',
    'NAYARIT': 'NT',
    'NUEVO LEON': 'NL',
    'OAXACA': 'OC',
    'PUEBLA': 'PL',
    'QUERETARO': 'QT',
    'QUINTANA ROO': 'QR',
    'SAN LUIS POTOSI': 'SP',
    'SINALOA': 'SL',
    'SONORA': 'SR',
    'TABASCO': 'TC',
    'TAMAULIPAS': 'TS',
    'TLAXCALA': 'TL',
    'VERACRUZ': 'VZ',
    'YUCATAN': 'YN',
    'ZACATECAS': 'ZS',
    'NACIDO EN EL EXTRANJERO': 'NE',
    'EXTRANJERO': 'NE',
  };

  static const List<String> _cacophonic = [
    'BACA', 'BAKA', 'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO',
    'CAKA', 'KAKO', 'COGE', 'COGI', 'COJA', 'COJE', 'COJI', 'COJO',
    'COLA', 'CULO', 'FALO', 'FETO', 'GETA', 'GUEI', 'GUEY', 'JETA',
    'JOTO', 'KACA', 'KACO', 'KAGA', 'KAGO', 'KOGE', 'KOGI', 'KOJA',
    'KOJE', 'KOJI', 'KOJO', 'KOLA', 'KULO', 'LILO', 'LOCA', 'LOCO',
    'LOKA', 'LOKO', 'MAME', 'MAMO', 'MEAR', 'MEAS', 'MEON', 'MIAR',
    'MION', 'MOCO', 'MOKO', 'MULA', 'MULO', 'NACA', 'NACO', 'PEDA',
    'PEDO', 'PENE', 'PIPI', 'PITO', 'POPO', 'PUTA', 'PUTO', 'QULO',
    'RATA', 'ROBA', 'ROBE', 'ROBO', 'RUIN', 'SENO', 'TETA', 'VACA',
    'VAGA', 'VAGO', 'VAKA', 'VUEI', 'VUEY', 'WUEI', 'WUEY',
  ];

  CURPValidator(String curp) : curp = curp.toUpperCase().trim();

  /// Validates if the CURP is structurally valid
  bool validate() {
    if (curp.length != length) {
      throw CURPException('CURP length must be $length');
    }
    if (!_generalRegex.hasMatch(curp)) {
      throw CURPException('Invalid CURP structure');
    }
    return true;
  }

  /// Alias for validate() that doesn't throw exceptions
  bool isValid() {
    try {
      return validate();
    } catch (e) {
      return false;
    }
  }

  /// Validates the check digit
  bool validateCheckDigit() {
    if (curp.length != 18) return false;

    final curp17 = curp.substring(0, 17);
    final expectedDigit = CURPGenerator.calculateCheckDigit(curp17);
    final actualDigit = curp[17];

    return expectedDigit == actualDigit;
  }

  /// Extracts birth date from CURP
  DateTime? getBirthDate() {
    if (!isValid()) return null;
    return parseDateYYMMDD(curp.substring(4, 10));
  }

  /// Extracts gender from CURP
  String? getGender() {
    if (!isValid()) return null;
    final code = curp[10];
    return code == 'H' ? 'Hombre' : 'Mujer';
  }

  /// Extracts state code from CURP
  String? getStateCode() {
    if (!isValid()) return null;
    return curp.substring(11, 13);
  }
}

/// CURP Generator
class CURPGenerator {
  final String nombre;
  final String apellidoPaterno;
  final String? apellidoMaterno;
  final DateTime fechaNacimiento;
  final String sexo;
  final String? estado;

  static const String _vowels = 'AEIOU';
  static const String _consonants = 'BCDFGHJKLMNPQRSTVWXYZ';

  static const List<String> _excludedWords = [
    'DE', 'LA', 'LAS', 'MC', 'VON', 'DEL', 'LOS', 'Y', 'MAC', 'VAN', 'MI',
    'DA', 'DAS', 'DE', 'DEL', 'DER', 'DI', 'DIE', 'DD', 'EL', 'LA', 'LOS',
    'LAS', 'LE', 'LES', 'MAC', 'MC', 'VAN', 'VON', 'Y',
  ];

  static const List<String> _allowedChars = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
  ];

  CURPGenerator({
    required this.nombre,
    required this.apellidoPaterno,
    this.apellidoMaterno,
    required this.fechaNacimiento,
    required this.sexo,
    this.estado,
  }) {
    if (apellidoPaterno.trim().isEmpty) {
      throw CURPException('Apellido paterno is required');
    }
    if (nombre.trim().isEmpty) {
      throw CURPException('Nombre is required');
    }
    if (sexo.toUpperCase() != 'H' && sexo.toUpperCase() != 'M') {
      throw CURPException('sexo must be "H" (Hombre) or "M" (Mujer)');
    }
  }

  /// Generates the CURP
  String generate() {
    final letters = _generateLetters();
    final date = _generateDate();
    final gender = sexo.toUpperCase();
    final stateCode = _getStateCode(estado);
    final consonants = _generateConsonants();
    final homoclave = _generateHomoclave();

    return letters + date + gender + stateCode + consonants + homoclave;
  }

  String _cleanName(String name) {
    if (name.isEmpty) return '';
    return cleanName(name, _excludedWords, _allowedChars);
  }

  String get _paternoCalculo => _cleanName(apellidoPaterno);
  String get _maternoCalculo => apellidoMaterno != null ? _cleanName(apellidoMaterno!) : '';
  String get _nombreCalculo => _cleanName(nombre);

  String get _nombreIniciales {
    if (_nombreCalculo.isEmpty) return _nombreCalculo;

    final words = _nombreCalculo.split(' ');
    if (words.length > 1) {
      if (['MARIA', 'JOSE', 'MA', 'MA.', 'J', 'J.'].contains(words[0])) {
        return words.sublist(1).join(' ');
      }
    }
    return _nombreCalculo;
  }

  String _generateLetters() {
    final clave = StringBuffer();
    final paterno = _paternoCalculo;

    if (paterno.isEmpty) {
      throw CURPException('Apellido paterno cannot be empty');
    }

    // First letter of paterno
    clave.write(paterno[0]);

    // First vowel of paterno (after first letter)
    bool vowelFound = false;
    for (var i = 1; i < paterno.length; i++) {
      if (_vowels.contains(paterno[i])) {
        clave.write(paterno[i]);
        vowelFound = true;
        break;
      }
    }
    if (!vowelFound) {
      clave.write('X');
    }

    // First letter of materno (or X if none)
    final materno = _maternoCalculo;
    if (materno.isNotEmpty) {
      clave.write(materno[0]);
    } else {
      clave.write('X');
    }

    // First letter of nombre
    final nombreInit = _nombreIniciales;
    if (nombreInit.isEmpty) {
      throw CURPException('Nombre cannot be empty');
    }
    clave.write(nombreInit[0]);

    String result = clave.toString();

    // Check for cacophonic words - replace second character with 'X'
    if (CURPValidator._cacophonic.contains(result)) {
      result = result[0] + 'X' + result.substring(2);
    }

    return result;
  }

  String _generateDate() {
    return dateToYYMMDD(fechaNacimiento);
  }

  String _getStateCode(String? state) {
    if (state == null || state.isEmpty) return 'NE';

    final stateUpper = state.toUpperCase().trim();

    // Try exact match
    if (CURPValidator._stateCodes.containsKey(stateUpper)) {
      return CURPValidator._stateCodes[stateUpper]!;
    }

    // Try partial match
    for (final entry in CURPValidator._stateCodes.entries) {
      if (entry.key.contains(stateUpper) || stateUpper.contains(entry.key)) {
        return entry.value;
      }
    }

    // If it's already a 2-letter code, return it
    if (stateUpper.length == 2) {
      return stateUpper;
    }

    return 'NE'; // Default to born abroad
  }

  String? _getFirstInternalConsonant(String word) {
    if (word.length <= 1) return 'X';

    for (var i = 1; i < word.length; i++) {
      if (_consonants.contains(word[i])) {
        return word[i];
      }
    }
    return 'X';
  }

  String _generateConsonants() {
    final consonants = StringBuffer();

    // First internal consonant of paterno
    consonants.write(_getFirstInternalConsonant(_paternoCalculo) ?? 'X');

    // First internal consonant of materno
    final materno = _maternoCalculo;
    if (materno.isNotEmpty) {
      consonants.write(_getFirstInternalConsonant(materno) ?? 'X');
    } else {
      consonants.write('X');
    }

    // First internal consonant of nombre
    consonants.write(_getFirstInternalConsonant(_nombreIniciales) ?? 'X');

    return consonants.toString();
  }

  String _generateHomoclave() {
    // Position 17: Differentiator (assigned by RENAPO, we use default)
    final differentiator = fechaNacimiento.year < 2000 ? '0' : 'A';

    // Position 18: Check digit (calculable)
    final tempCurp = _generateLetters() +
        _generateDate() +
        sexo.toUpperCase() +
        _getStateCode(estado) +
        _generateConsonants() +
        differentiator;

    final checkDigit = calculateCheckDigit(tempCurp);

    return differentiator + checkDigit;
  }

  /// Calculates the check digit for a 17-character CURP
  static String calculateCheckDigit(String curp17) {
    if (curp17.length != 17) {
      throw CURPException('CURP must have exactly 17 characters for check digit calculation');
    }

    const dictionary = '0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ';

    int suma = 0;
    for (var i = 0; i < curp17.length; i++) {
      final char = curp17[i];
      int charValue;

      try {
        charValue = dictionary.indexOf(char);
        if (charValue == -1) charValue = 0;
      } catch (e) {
        charValue = 0;
      }

      suma += charValue * (18 - i);
    }

    int digito = 10 - (suma % 10);

    if (digito == 10) {
      digito = 0;
    }

    return digito.toString();
  }
}

// Helper functions

/// Validates a CURP
bool validateCURP(String curp) {
  try {
    final validator = CURPValidator(curp);
    return validator.validate();
  } catch (e) {
    return false;
  }
}

/// Generates a CURP
String generateCURP({
  required String nombre,
  required String apellidoPaterno,
  String? apellidoMaterno,
  required DateTime fechaNacimiento,
  required String sexo,
  String? estado,
}) {
  final generator = CURPGenerator(
    nombre: nombre,
    apellidoPaterno: apellidoPaterno,
    apellidoMaterno: apellidoMaterno,
    fechaNacimiento: fechaNacimiento,
    sexo: sexo,
    estado: estado,
  );
  return generator.generate();
}
