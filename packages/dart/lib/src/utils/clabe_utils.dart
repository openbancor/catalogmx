/// CLABE Utilities - Enhanced CLABE generation, decoding, and validation
///
/// This module provides comprehensive CLABE (Clave Bancaria Estandarizada) utilities
/// including generation with optional parameters, decoding with full bank/plaza info,
/// and example generation.
///
/// Example:
/// ```dart
/// import 'package:catalogmx/catalogmx.dart';
///
/// // Generate a random CLABE for BBVA in CDMX
/// final clabe = generateCLABERandom(bankCode: '012', plazaCode: '180');
///
/// // Decode a CLABE to get full info
/// final info = decodeCLABE('002010077777777771');
/// print(info?.bank?.name); // 'BANAMEX'
/// ```
library;

import 'dart:math';

import 'package:catalogmx/src/validators/clabe_validator.dart';
import 'package:catalogmx/src/catalogs/banxico/banks.dart';
import 'package:catalogmx/src/catalogs/banxico/codigos_plaza.dart';

/// Bank information for decoded CLABE
class BankInfo {
  BankInfo({
    required this.code,
    required this.name,
    this.fullName,
    this.rfc,
    required this.spei,
  });

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

/// Plaza information for decoded CLABE
class PlazaInfo {
  PlazaInfo({
    required this.codigo,
    required this.plaza,
    required this.estado,
    required this.cveEntidad,
  });

  factory PlazaInfo.fromJson(Map<String, dynamic> json) {
    return PlazaInfo(
      codigo: json['codigo'] as String? ?? '',
      plaza: json['plaza'] as String? ?? '',
      estado: json['estado'] as String? ?? '',
      cveEntidad: json['cve_entidad'] as String? ?? '',
    );
  }

  final String codigo;
  final String plaza;
  final String estado;
  final String cveEntidad;

  Map<String, dynamic> toJson() => {
        'codigo': codigo,
        'plaza': plaza,
        'estado': estado,
        'cve_entidad': cveEntidad,
      };
}

/// Full decoded CLABE information
class DecodedCLABE {
  DecodedCLABE({
    required this.clabe,
    required this.isValid,
    required this.bankCode,
    required this.plazaCode,
    required this.accountNumber,
    required this.checkDigit,
    this.bank,
    this.plaza,
    required this.allPlazas,
  });

  final String clabe;
  final bool isValid;
  final String bankCode;
  final String plazaCode;
  final String accountNumber;
  final String checkDigit;
  final BankInfo? bank;
  final PlazaInfo? plaza;
  final List<PlazaInfo> allPlazas;

  Map<String, dynamic> toJson() => {
        'clabe': clabe,
        'is_valid': isValid,
        'bank_code': bankCode,
        'plaza_code': plazaCode,
        'account_number': accountNumber,
        'check_digit': checkDigit,
        if (bank != null) 'bank': bank!.toJson(),
        if (plaza != null) 'plaza': plaza!.toJson(),
        'all_plazas': allPlazas.map((p) => p.toJson()).toList(),
      };
}

/// Decode a CLABE to extract all information including bank and plaza details.
///
/// Args:
///   clabe: 18-digit CLABE number
///
/// Returns:
///   DecodedCLABE with full breakdown or null if format is invalid
///
/// Example:
/// ```dart
/// final info = decodeCLABE('002010077777777771');
/// print(info?.isValid); // true
/// print(info?.bank?.name); // 'BANAMEX'
/// print(info?.bank?.fullName); // 'Banco Nacional de México, S.A.'
///
/// // Get plaza info
/// final info2 = decodeCLABE('012180000000000001');
/// print(info2?.plaza?.plaza); // 'Ciudad de México'
/// ```
DecodedCLABE? decodeCLABE(String clabe) {
  final trimmed = clabe.trim();

  if (trimmed.length != 18 || !RegExp(r'^\d+$').hasMatch(trimmed)) {
    return null;
  }

  final bankCode = trimmed.substring(0, 3);
  final plazaCode = trimmed.substring(3, 6);
  final accountNumber = trimmed.substring(6, 17);
  final checkDigit = trimmed[17];

  // Get bank info
  final bankData = BanxicoBanks.getByCode(bankCode);
  BankInfo? bankInfo;
  if (bankData != null) {
    bankInfo = BankInfo(
      code: bankData['code'] as String? ?? '',
      name: bankData['name'] as String? ?? '',
      fullName: bankData['full_name'] as String?,
      rfc: bankData['rfc'] as String?,
      spei: bankData['spei'] as bool? ?? false,
    );
  }

  // Get plaza info (may have multiple matches)
  final allPlazasRaw = CodigosPlazaCatalog.buscarPorCodigo(plazaCode);
  final allPlazas = allPlazasRaw.map((p) => PlazaInfo.fromJson(p)).toList();
  final plazaInfo = allPlazas.isNotEmpty ? allPlazas.first : null;

  return DecodedCLABE(
    clabe: trimmed,
    isValid: validateCLABE(trimmed),
    bankCode: bankCode,
    plazaCode: plazaCode,
    accountNumber: accountNumber,
    checkDigit: checkDigit,
    bank: bankInfo,
    plaza: plazaInfo,
    allPlazas: allPlazas,
  );
}

/// Generate a valid CLABE with optional parameters.
/// Any parameter not provided will be randomly generated.
///
/// Args:
///   bankCode: 3-digit bank code (optional, e.g., '012' for BBVA)
///   plazaCode: 3-digit plaza code (optional, e.g., '180' for CDMX)
///   accountNumber: 11-digit account number (optional)
///
/// Returns:
///   Valid 18-digit CLABE
///
/// Example:
/// ```dart
/// // Fully random CLABE
/// final clabe = generateCLABERandom();
///
/// // CLABE for BBVA (code 012)
/// final clabe2 = generateCLABERandom(bankCode: '012');
///
/// // CLABE for any bank in CDMX (plaza 180)
/// final clabe3 = generateCLABERandom(plazaCode: '180');
///
/// // Fully specified
/// final clabe4 = generateCLABERandom(
///   bankCode: '012',
///   plazaCode: '180',
///   accountNumber: '12345678901',
/// );
/// ```
String generateCLABERandom({
  String? bankCode,
  String? plazaCode,
  String? accountNumber,
}) {
  final random = Random();

  // Get or generate bank code
  if (bankCode == null) {
    final speiBanks = BanxicoBanks.getSPEIBanks();
    if (speiBanks.isNotEmpty) {
      final randomIndex = random.nextInt(speiBanks.length);
      bankCode = speiBanks[randomIndex]['code'] as String? ?? '002';
    } else {
      bankCode = (random.nextInt(999) + 1).toString().padLeft(3, '0');
    }
  }

  // Get or generate plaza code
  if (plazaCode == null) {
    final allPlazas = CodigosPlazaCatalog.getAll();
    if (allPlazas.isNotEmpty) {
      final randomIndex = random.nextInt(allPlazas.length);
      plazaCode = allPlazas[randomIndex]['codigo'] as String? ?? '010';
    } else {
      plazaCode = (random.nextInt(999) + 1).toString().padLeft(3, '0');
    }
  }

  // Get or generate account number (11 digits)
  // Cannot use nextInt(99999999999) as it exceeds 2^32
  // Generate as string by concatenating random digits
  final account = accountNumber ??
      () {
        var num = '';
        for (var i = 0; i < 11; i++) {
          num += random.nextInt(10).toString();
        }
        return num;
      }();

  return generateCLABE(
    bankCode: bankCode,
    branchCode: plazaCode,
    accountNumber: account,
  );
}

/// Generate example CLABEs with full decoded information.
///
/// Args:
///   count: Number of examples to generate (default 5)
///
/// Returns:
///   List of DecodedCLABE objects
///
/// Example:
/// ```dart
/// final examples = generateCLABEExamples(3);
/// for (final ex in examples) {
///   print('${ex.bank?.name}: ${ex.clabe}');
/// }
/// ```
List<DecodedCLABE> generateCLABEExamples([int count = 5]) {
  final examples = <DecodedCLABE>[];

  for (var i = 0; i < count; i++) {
    final clabe = generateCLABERandom();
    final decoded = decodeCLABE(clabe);
    if (decoded != null) {
      examples.add(decoded);
    }
  }

  return examples;
}

/// Generate a CLABE for a specific bank (by name).
///
/// Args:
///   bankName: Bank name (case-insensitive)
///   plazaName: Optional plaza name (case-insensitive)
///
/// Returns:
///   Valid 18-digit CLABE or null if bank not found
///
/// Example:
/// ```dart
/// final clabe = generateCLABEForBank('BBVA');
/// final info = decodeCLABE(clabe!);
/// print(info?.bank?.name); // 'BBVA'
///
/// final clabe2 = generateCLABEForBank('Santander', plazaName: 'Guadalajara');
/// ```
String? generateCLABEForBank(String bankName, {String? plazaName}) {
  final bank = BanxicoBanks.getByName(bankName);
  if (bank == null) {
    return null;
  }

  final bankCode = bank['code'] as String?;
  String? plazaCode;

  if (plazaName != null) {
    final plazas = CodigosPlazaCatalog.buscarPorPlaza(plazaName);
    if (plazas.isNotEmpty) {
      plazaCode = plazas.first['codigo'] as String?;
    }
  }

  return generateCLABERandom(bankCode: bankCode, plazaCode: plazaCode);
}

/// Get list of common banks used for CLABE generation.
List<Map<String, dynamic>> getCommonBanks() {
  return BanxicoBanks.getSPEIBanks();
}

/// Search plazas by name for autocomplete/suggestions.
List<Map<String, dynamic>> getPlazaSuggestions(String query) {
  return CodigosPlazaCatalog.search(query);
}

/// Format a CLABE with separators for readability.
///
/// Args:
///   clabe: 18-digit CLABE
///   separator: Separator character (default '-')
///
/// Returns:
///   Formatted CLABE: XXX-XXX-XXXXXXXXXXX-X
///
/// Example:
/// ```dart
/// formatCLABE('002010077777777771'); // '002-010-07777777777-1'
/// formatCLABE('002010077777777771', separator: ' '); // '002 010 07777777777 1'
/// ```
String formatCLABE(String clabe, {String separator = '-'}) {
  if (clabe.length != 18) {
    return clabe;
  }
  return '${clabe.substring(0, 3)}$separator${clabe.substring(3, 6)}$separator${clabe.substring(6, 17)}$separator${clabe[17]}';
}

/// Get a human-readable description of a CLABE.
///
/// Args:
///   clabe: 18-digit CLABE
///
/// Returns:
///   Human-readable description
///
/// Example:
/// ```dart
/// print(describeCLABE('002010077777777771'));
/// // CLABE: 002-010-07777777777-1
/// // Estado: Valida
/// // Banco: BANAMEX (Banco Nacional de Mexico, S.A.)
/// // Plaza: Aguascalientes, Aguascalientes
/// // Cuenta: 07777777777
/// ```
String describeCLABE(String clabe) {
  final info = decodeCLABE(clabe);
  if (info == null) {
    return 'CLABE invalida: $clabe';
  }

  final lines = <String>[
    'CLABE: ${formatCLABE(clabe)}',
    'Estado: ${info.isValid ? 'Valida' : 'Invalida'}',
  ];

  if (info.bank != null) {
    var bankLine = 'Banco: ${info.bank!.name}';
    if (info.bank!.fullName != null) {
      bankLine += ' (${info.bank!.fullName})';
    }
    lines.add(bankLine);
  } else {
    lines.add('Banco: Codigo ${info.bankCode} (no encontrado)');
  }

  if (info.plaza != null) {
    lines.add('Plaza: ${info.plaza!.plaza}, ${info.plaza!.estado}');
    if (info.allPlazas.length > 1) {
      lines.add(
        '  (Nota: ${info.allPlazas.length} ubicaciones con este codigo)',
      );
    }
  } else {
    lines.add('Plaza: Codigo ${info.plazaCode} (no encontrado)');
  }

  lines.add('Cuenta: ${info.accountNumber}');

  return lines.join('\n');
}
