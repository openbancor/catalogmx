/// INEGI States Catalog
///
/// Provides access to Mexican states (entidades federativas) data from INEGI.
library;

import 'dart:convert';
import '../../../catalogmx.dart';

/// INEGI States Catalog
class InegStates {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;
  static Map<String, Map<String, dynamic>>? _byClaveInegi;

  /// Loads the states data from embedded JSON
  static void _loadData() {
    if (_data != null) return;

    // Embedded states data for Flutter compatibility
    // In a real implementation, this would load from assets or shared-data
    const jsonData = '''
[
  {"code": "AS", "name": "AGUASCALIENTES", "abbreviation": "AGS", "clave_inegi": "01"},
  {"code": "BC", "name": "BAJA CALIFORNIA", "abbreviation": "BC", "clave_inegi": "02"},
  {"code": "BS", "name": "BAJA CALIFORNIA SUR", "abbreviation": "BCS", "clave_inegi": "03"},
  {"code": "CC", "name": "CAMPECHE", "abbreviation": "CAMP", "clave_inegi": "04"},
  {"code": "CL", "name": "COAHUILA", "abbreviation": "COAH", "clave_inegi": "05"},
  {"code": "CM", "name": "COLIMA", "abbreviation": "COL", "clave_inegi": "06"},
  {"code": "CS", "name": "CHIAPAS", "abbreviation": "CHIS", "clave_inegi": "07"},
  {"code": "CH", "name": "CHIHUAHUA", "abbreviation": "CHIH", "clave_inegi": "08"},
  {"code": "DF", "name": "CIUDAD DE MEXICO", "abbreviation": "CDMX", "clave_inegi": "09"},
  {"code": "DG", "name": "DURANGO", "abbreviation": "DGO", "clave_inegi": "10"},
  {"code": "GT", "name": "GUANAJUATO", "abbreviation": "GTO", "clave_inegi": "11"},
  {"code": "GR", "name": "GUERRERO", "abbreviation": "GRO", "clave_inegi": "12"},
  {"code": "HG", "name": "HIDALGO", "abbreviation": "HGO", "clave_inegi": "13"},
  {"code": "JC", "name": "JALISCO", "abbreviation": "JAL", "clave_inegi": "14"},
  {"code": "MC", "name": "ESTADO DE MEXICO", "abbreviation": "MEX", "clave_inegi": "15"},
  {"code": "MN", "name": "MICHOACAN", "abbreviation": "MICH", "clave_inegi": "16"},
  {"code": "MS", "name": "MORELOS", "abbreviation": "MOR", "clave_inegi": "17"},
  {"code": "NT", "name": "NAYARIT", "abbreviation": "NAY", "clave_inegi": "18"},
  {"code": "NL", "name": "NUEVO LEON", "abbreviation": "NL", "clave_inegi": "19"},
  {"code": "OC", "name": "OAXACA", "abbreviation": "OAX", "clave_inegi": "20"},
  {"code": "PL", "name": "PUEBLA", "abbreviation": "PUE", "clave_inegi": "21"},
  {"code": "QT", "name": "QUERETARO", "abbreviation": "QRO", "clave_inegi": "22"},
  {"code": "QR", "name": "QUINTANA ROO", "abbreviation": "QROO", "clave_inegi": "23"},
  {"code": "SP", "name": "SAN LUIS POTOSI", "abbreviation": "SLP", "clave_inegi": "24"},
  {"code": "SL", "name": "SINALOA", "abbreviation": "SIN", "clave_inegi": "25"},
  {"code": "SR", "name": "SONORA", "abbreviation": "SON", "clave_inegi": "26"},
  {"code": "TC", "name": "TABASCO", "abbreviation": "TAB", "clave_inegi": "27"},
  {"code": "TS", "name": "TAMAULIPAS", "abbreviation": "TAMPS", "clave_inegi": "28"},
  {"code": "TL", "name": "TLAXCALA", "abbreviation": "TLAX", "clave_inegi": "29"},
  {"code": "VZ", "name": "VERACRUZ", "abbreviation": "VER", "clave_inegi": "30"},
  {"code": "YN", "name": "YUCATAN", "abbreviation": "YUC", "clave_inegi": "31"},
  {"code": "ZS", "name": "ZACATECAS", "abbreviation": "ZAC", "clave_inegi": "32"},
  {"code": "NE", "name": "NACIDO EN EL EXTRANJERO", "abbreviation": "EXT", "clave_inegi": "99"}
]
''';

    final decoded = json.decode(jsonData) as List;
    _data = decoded.map((item) => item as Map<String, dynamic>).toList();

    // Build lookup maps
    _byCode = {};
    _byClaveInegi = {};

    for (final state in _data!) {
      _byCode![state['code'] as String] = state;
      _byClaveInegi![state['clave_inegi'] as String] = state;
    }
  }

  /// Gets all states
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets a state by CURP/RFC code (2 letters)
  static Map<String, dynamic>? getByCode(String code) {
    _loadData();
    return _byCode![code.toUpperCase()];
  }

  /// Gets a state by INEGI clave (2 digits)
  static Map<String, dynamic>? getByClaveInegi(String clave) {
    _loadData();
    return _byClaveInegi![clave];
  }

  /// Gets a state by name (case insensitive)
  static Map<String, dynamic>? getByName(String name) {
    _loadData();
    final normalized = normalizeText(name);
    for (final state in _data!) {
      if (normalizeText(state['name'] as String) == normalized) {
        return state;
      }
    }
    return null;
  }

  /// Validates if a code exists
  static bool isValid(String code) {
    return getByCode(code) != null;
  }

  /// Searches states by partial name match
  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final normalized = normalizeText(query);
    return _data!.where((state) {
      return normalizeText(state['name'] as String).contains(normalized);
    }).toList();
  }
}
