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
    this.speiCode,
    this.status = 'active',
    this.speiDisaffiliated = false,
  });

  factory Bank.fromJson(Map<String, dynamic> json) {
    return Bank(
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
      fullName: json['full_name'] as String?,
      rfc: json['rfc'] as String?,
      spei: json['spei'] as bool? ?? false,
      speiCode: json['spei_code'] as String?,
      status: json['status'] as String? ?? 'active',
      speiDisaffiliated: json['spei_disaffiliated'] as bool? ?? false,
    );
  }

  final String code;
  final String name;
  final String? fullName;
  final String? rfc;
  final bool spei;

  /// 5-digit SPEI participant code (null if not an active participant)
  final String? speiCode;

  /// `active` or `historical` (disaffiliated from SPEI)
  final String status;

  /// True when the bank was disaffiliated from SPEI
  final bool speiDisaffiliated;

  Map<String, dynamic> toJson() => {
        'code': code,
        'name': name,
        if (fullName != null) 'full_name': fullName,
        if (rfc != null) 'rfc': rfc,
        'spei': spei,
        'spei_code': speiCode,
        'status': status,
        if (speiDisaffiliated) 'spei_disaffiliated': true,
      };
}

/// Banxico Banks Catalog
class BanxicoBanks {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;
  static Map<String, Map<String, dynamic>>? _bySpeiCode;
  static Map<String, Map<String, dynamic>>? _byName;

  /// Loads the banks data
  static void _loadData() {
    if (_data != null) return;

    _data = BaseCatalog.loadJsonDataSync('banxico/banks.json');

    // Build indices
    _byCode = {};
    _byName = {};
    _bySpeiCode = {};

    for (var bank in _data!) {
      final code = bank['code'] as String? ?? '';
      final name = (bank['name'] as String? ?? '').toUpperCase();

      _byCode![code] = bank;
      _byName![name] = bank;
      final speiCode = bank['spei_code'] as String?;
      if (speiCode != null) {
        _bySpeiCode![speiCode] = bank;
      }
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

  /// Gets a bank by its 3-digit CLABE code (alias of [getByCode]).
  ///
  /// Historical (disaffiliated) banks are returned too, with
  /// `status == 'historical'`, so old CLABEs keep resolving.
  static Map<String, dynamic>? getByClabeCode(String code) => getByCode(code);

  /// Gets a bank by its 5-digit SPEI participant code (e.g. `40012`).
  /// BANXICO itself uses the official 4-digit key `2001`.
  static Map<String, dynamic>? getBySpeiCode(String speiCode) {
    _loadData();
    return _bySpeiCode![speiCode];
  }

  /// Gets a Bank object by SPEI participant code
  static Bank? getBankBySpeiCode(String speiCode) {
    final data = getBySpeiCode(speiCode);
    return data != null ? Bank.fromJson(data) : null;
  }

  /// Validates an SPEI participant code and, optionally, that its last 3
  /// digits equal the CLABE bank [code].
  static bool validateSpeiCode(String speiCode, [String? code]) {
    final bank = getBySpeiCode(speiCode);
    if (bank == null) return false;
    if (code == null) return true;
    final padded = code.padLeft(3, '0');
    return bank['code'] == padded &&
        speiCode.substring(speiCode.length - 3) == padded;
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

  /// Gets the SPEI banks; historical (disaffiliated) ones only when
  /// [includeHistorical] is true.
  static List<Map<String, dynamic>> getSPEIBanks({
    bool includeHistorical = false,
  }) {
    _loadData();
    return _data!
        .where((b) =>
            b['status'] == 'historical' ? includeHistorical : b['spei'] == true)
        .toList();
  }

  /// Gets the SPEI banks as Bank objects
  static List<Bank> getAllSPEIBanks({bool includeHistorical = false}) {
    return getSPEIBanks(includeHistorical: includeHistorical)
        .map((b) => Bank.fromJson(b))
        .toList();
  }

  /// Checks if a bank supports SPEI
  static bool supportsSPEI(String code) {
    final bank = getByCode(code);
    return bank?['spei'] == true;
  }
}
