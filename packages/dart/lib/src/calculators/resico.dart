/// RESICO (Régimen Simplificado de Confianza) Calculator for Mexico
/// Supports years: 2024, 2025, 2026
///
/// RESICO uses a DIRECT TAX RATE system (simpler than ISR):
/// - No deductions allowed
/// - No fixed fee (cuota fija)
/// - Tax = Total Income × Bracket Rate
///
/// Official source: Artículo 113-E LISR (Ley del Impuesto Sobre la Renta)
library;

import 'dart:convert';
import 'dart:io';

/// Supported tax years
enum RESICOYear {
  year2024(2024),
  year2025(2025),
  year2026(2026);

  const RESICOYear(this.value);
  final int value;
}

/// Supported periods
enum RESICOPeriod {
  mensual('mensual'),
  anual('anual');

  const RESICOPeriod(this.value);
  final String value;
}

/// RESICO tax bracket structure (simplified - no cuota fija)
class RESICOBracket {
  final double limiteInferior;
  final double limiteSuperior;
  final double tasa;

  const RESICOBracket({
    required this.limiteInferior,
    required this.limiteSuperior,
    required this.tasa,
  });

  factory RESICOBracket.fromJson(Map<String, dynamic> json) {
    return RESICOBracket(
      limiteInferior: (json['limiteInferior'] as num).toDouble(),
      limiteSuperior: (json['limiteSuperior'] as num).toDouble(),
      tasa: (json['tasa'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
    'limiteInferior': limiteInferior,
    'limiteSuperior': limiteSuperior,
    'tasa': tasa,
  };
}

/// Complete RESICO calculation result
class RESICOCalculationResult {
  final double ingreso;
  final String periodo;
  final int year;
  final double limiteMaximo;
  final bool dentroDeLimite;
  final RESICOBracket bracket;
  final double resicoCalculado;
  final double tasaEfectiva;

  const RESICOCalculationResult({
    required this.ingreso,
    required this.periodo,
    required this.year,
    required this.limiteMaximo,
    required this.dentroDeLimite,
    required this.bracket,
    required this.resicoCalculado,
    required this.tasaEfectiva,
  });

  Map<String, dynamic> toJson() => {
    'ingreso': ingreso,
    'periodo': periodo,
    'year': year,
    'limiteMaximo': limiteMaximo,
    'dentroDeLimite': dentroDeLimite,
    'bracket': bracket.toJson(),
    'resicoCalculado': resicoCalculado,
    'tasaEfectiva': tasaEfectiva,
  };
}

/// RESICO Calculator class
class RESICOCalculator {
  static Map<String, dynamic>? _resicoTables;

  /// Load RESICO tables from centralized JSON file
  static Map<String, dynamic> _loadRESICOTables() {
    if (_resicoTables != null) return _resicoTables!;

    // Path to shared JSON file (relative to Dart package root)
    final jsonPath = '../../shared-data/resico-tables.json';
    final file = File(jsonPath);

    if (!file.existsSync()) {
      // Try alternative path when running from lib/src/calculators
      final altPath = '../../../shared-data/resico-tables.json';
      final altFile = File(altPath);
      if (!altFile.existsSync()) {
        throw Exception('RESICO tables JSON file not found');
      }
      final jsonString = altFile.readAsStringSync();
      _resicoTables = jsonDecode(jsonString) as Map<String, dynamic>;
      return _resicoTables!;
    }

    final jsonString = file.readAsStringSync();
    _resicoTables = jsonDecode(jsonString) as Map<String, dynamic>;
    return _resicoTables!;
  }

  /// Get RESICO tax brackets for a specific year and period
  static List<RESICOBracket> getRESICOBrackets(
    RESICOYear year,
    RESICOPeriod period,
  ) {
    final tables = _loadRESICOTables();
    final yearStr = year.value.toString();
    final periodKey = period.value;

    final brackets = tables['brackets']![yearStr]![periodKey] as List;
    return brackets.map((b) => RESICOBracket.fromJson(b)).toList();
  }

  /// Calculate RESICO (Régimen Simplificado de Confianza) tax
  ///
  /// RESICO uses a DIRECT TAX RATE system (not marginal like regular ISR):
  /// - No deductions allowed
  /// - No fixed fee (cuota fija)
  /// - Tax = Total Income × Bracket Rate
  ///
  /// Parameters:
  /// - [ingreso]: Taxable income for the period
  /// - [periodo]: Period (default: mensual)
  /// - [year]: Tax year (default: 2026)
  ///
  /// Returns: Complete RESICO calculation result
  ///
  /// Examples:
  /// ```dart
  /// // Monthly income $50,000 → bracket 1.1% → ISR = $50,000 × 1.1% = $550
  /// final result = RESICOCalculator.calculateRESICO(50000);
  /// print('RESICO: \$${result.resicoCalculado.toStringAsFixed(2)}'); // $550.00
  ///
  /// // Annual income $500,000 → bracket 1.1% → ISR = $500,000 × 1.1% = $5,500
  /// final resultAnual = RESICOCalculator.calculateRESICO(
  ///   500000,
  ///   periodo: RESICOPeriod.anual,
  /// );
  /// print('RESICO anual: \$${resultAnual.resicoCalculado.toStringAsFixed(2)}');
  /// ```
  static RESICOCalculationResult calculateRESICO(
    double ingreso, {
    RESICOPeriod periodo = RESICOPeriod.mensual,
    RESICOYear year = RESICOYear.year2026,
  }) {
    final tables = _loadRESICOTables();

    // Get income limits
    final limits = tables['limits']!['personaFisica']! as Map<String, dynamic>;
    final limiteMaximo = periodo == RESICOPeriod.mensual
        ? (limits['ingresoMensualMaximo'] as num).toDouble()
        : (limits['ingresoAnualMaximo'] as num).toDouble();
    final dentroDeLimite = ingreso <= limiteMaximo;

    // Get brackets for year and period
    final brackets = getRESICOBrackets(year, periodo);

    // Find applicable bracket
    final bracket = brackets.firstWhere(
      (b) => ingreso >= b.limiteInferior && ingreso <= b.limiteSuperior,
      orElse: () => brackets.last,
    );

    // RESICO calculation: Direct rate on total income (NO cuota fija, NO excedente)
    final resicoCalculado = ingreso * (bracket.tasa / 100);

    // Effective rate (should equal bracket rate for RESICO)
    final tasaEfectiva = ingreso > 0 ? (resicoCalculado / ingreso * 100) : 0.0;

    return RESICOCalculationResult(
      ingreso: ingreso,
      periodo: periodo.value,
      year: year.value,
      limiteMaximo: limiteMaximo,
      dentroDeLimite: dentroDeLimite,
      bracket: bracket,
      resicoCalculado: resicoCalculado,
      tasaEfectiva: tasaEfectiva,
    );
  }
}
