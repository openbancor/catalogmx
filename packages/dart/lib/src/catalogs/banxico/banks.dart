/// Banxico Banks Catalog
///
/// Catalog of Mexican banks from Banco de México
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Bank information
class Bank {
  Bank({
    required this.code,
    required this.name,
    this.fullName,
    this.rfc,
    this.spei = false,
  });

  factory Bank.fromJson(Map<String, dynamic> json) {
    return Bank(
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
      fullName: json['full_name'] as String?,
      rfc: json['rfc'] as String?,
      spei: json['spei'] as bool? ?? false,
    );
  }

  final String code;
  final String name;
  final String? fullName;
  final String? rfc;
  final bool spei;

  Map<String, dynamic> toJson() => {
        'code': code,
        'name': name,
        if (fullName != null) 'full_name': fullName,
        if (rfc != null) 'rfc': rfc,
        'spei': spei,
      };
}

/// Banxico Banks Catalog
class BanxicoBanks {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;
  static Map<String, Map<String, dynamic>>? _byName;

  /// Loads the banks data
  static void _loadData() {
    if (_data != null) return;

    _data = BaseCatalog.loadJsonDataSync('banxico/banks.json');

    // Build indices
    _byCode = {};
    _byName = {};

    for (var bank in _data!) {
      final code = bank['code'] as String? ?? '';
      final name = (bank['name'] as String? ?? '').toUpperCase();

      _byCode![code] = bank;
      _byName![name] = bank;
    }
  }

  /// Gets all banks
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Gets all banks as Bank objects
  static List<Bank> getAllBanks() {
    _loadData();
    return _data!.map((b) => Bank.fromJson(b)).toList();
  }

  /// Gets a bank by code (CLABE bank code)
  static Map<String, dynamic>? getByCode(String code) {
    _loadData();
    final paddedCode = code.padLeft(3, '0');
    return _byCode![paddedCode];
  }

  /// Gets a Bank object by code
  static Bank? getBankByCode(String code) {
    final data = getByCode(code);
    return data != null ? Bank.fromJson(data) : null;
  }

  /// Gets a bank by name (case-insensitive)
  static Map<String, dynamic>? getByName(String name) {
    _loadData();
    final normalized = name.toUpperCase();
    return _byName![normalized];
  }

  /// Gets a Bank object by name
  static Bank? getBankByName(String name) {
    final data = getByName(name);
    return data != null ? Bank.fromJson(data) : null;
  }

  /// Searches banks by keyword (name or code)
  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final q = query.toUpperCase();
    return _data!.where((b) {
      final name = (b['name'] as String? ?? '').toUpperCase();
      final fullName = (b['full_name'] as String? ?? '').toUpperCase();
      final code = b['code'] as String? ?? '';
      return name.contains(q) || fullName.contains(q) || code.contains(q);
    }).toList();
  }

  /// Validates if a bank code exists
  static bool isValid(String code) {
    return getByCode(code) != null;
  }

  /// Gets all SPEI banks
  static List<Map<String, dynamic>> getSPEIBanks() {
    _loadData();
    return _data!.where((b) => b['spei'] == true).toList();
  }

  /// Gets all SPEI banks as Bank objects
  static List<Bank> getAllSPEIBanks() {
    return getSPEIBanks().map((b) => Bank.fromJson(b)).toList();
  }

  /// Checks if a bank supports SPEI
  static bool supportsSPEI(String code) {
    final bank = getByCode(code);
    return bank?['spei'] == true;
  }
}
