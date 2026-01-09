/// ISR (Impuesto Sobre la Renta) Calculator for Mexico
/// Supports multi-year calculations: 2024, 2025, 2026
/// Uses centralized JSON tables from shared-data
///
/// Official source: Anexo 8 RMF (Resolución Miscelánea Fiscal)
library;

import 'dart:convert';
import 'dart:io';

/// Supported tax years
enum ISRYear {
  year2024(2024),
  year2025(2025),
  year2026(2026);

  const ISRYear(this.value);
  final int value;
}

/// Supported payment periods
enum ISRPeriod {
  diaria('diaria', 'daily', 30.4),
  semanal('semanal', 'weekly', 4.33),
  decenal('decenal', 'monthly', 3.0),
  quincenal('quincenal', 'biweekly', 2.0),
  mensual('mensual', 'monthly', 1.0),
  anual('anual', 'annual', 1 / 12);

  const ISRPeriod(this.value, this.jsonKey, this.factor);
  final String value;
  final String jsonKey;
  final double factor;
}

/// Tax bracket structure
class ISRBracket {
  final double limiteInferior;
  final double limiteSuperior;
  final double cuotaFija;
  final double tasa;

  const ISRBracket({
    required this.limiteInferior,
    required this.limiteSuperior,
    required this.cuotaFija,
    required this.tasa,
  });

  factory ISRBracket.fromJson(Map<String, dynamic> json) {
    return ISRBracket(
      limiteInferior: (json['limiteInferior'] as num).toDouble(),
      limiteSuperior: json['limiteSuperior'] == null
          ? double.infinity
          : (json['limiteSuperior'] as num).toDouble(),
      cuotaFija: (json['cuotaFija'] as num).toDouble(),
      tasa: (json['tasa'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'limiteInferior': limiteInferior,
        'limiteSuperior':
            limiteSuperior == double.infinity ? null : limiteSuperior,
        'cuotaFija': cuotaFija,
        'tasa': tasa,
      };
}

/// Complete ISR calculation result
class ISRCalculationResult {
  final double ingresoGravable;
  final String periodo;
  final int year;
  final double ingresoMensualizado;
  final ISRBracket bracket;
  final double excedente;
  final double impuestoMarginal;
  final double isrAntesSubsidio;
  final double subsidio;
  final double isrFinal;
  final double tasaEfectiva;

  const ISRCalculationResult({
    required this.ingresoGravable,
    required this.periodo,
    required this.year,
    required this.ingresoMensualizado,
    required this.bracket,
    required this.excedente,
    required this.impuestoMarginal,
    required this.isrAntesSubsidio,
    required this.subsidio,
    required this.isrFinal,
    required this.tasaEfectiva,
  });

  Map<String, dynamic> toJson() => {
        'ingresoGravable': ingresoGravable,
        'periodo': periodo,
        'year': year,
        'ingresoMensualizado': ingresoMensualizado,
        'bracket': bracket.toJson(),
        'excedente': excedente,
        'impuestoMarginal': impuestoMarginal,
        'isrAntesSubsidio': isrAntesSubsidio,
        'subsidio': subsidio,
        'isrFinal': isrFinal,
        'tasaEfectiva': tasaEfectiva,
      };
}

/// ISR Calculator class
class ISRCalculator {
  static Map<String, dynamic>? _isrTables;

  /// Load ISR tables from centralized JSON file
  static Map<String, dynamic> _loadISRTables() {
    if (_isrTables != null) return _isrTables!;

    final candidates = [
      '../shared-data/isr-tables.json',
      '../../shared-data/isr-tables.json',
      '../../../shared-data/isr-tables.json',
      'packages/shared-data/isr-tables.json',
    ];

    for (final path in candidates) {
      final file = File(path);
      if (!file.existsSync()) {
        continue;
      }
      final jsonString = file.readAsStringSync();
      _isrTables = jsonDecode(jsonString) as Map<String, dynamic>;
      return _isrTables!;
    }

    throw Exception('ISR tables JSON file not found');
  }

  /// Get ISR tax brackets for a specific year and period
  static List<ISRBracket> getISRBrackets(ISRYear year, ISRPeriod period) {
    final tables = _loadISRTables();
    final yearStr = year.value.toString();
    final periodKey = period.jsonKey;

    final brackets = tables['brackets']![yearStr]![periodKey] as List;
    return brackets.map((b) => ISRBracket.fromJson(b)).toList();
  }

  /// Calculate employment subsidy (subsidio al empleo)
  static double calculateSubsidy(double income, ISRYear year) {
    final tables = _loadISRTables();
    final yearStr = year.value.toString();
    final subsidyData = tables['subsidies']![yearStr]!;

    if (subsidyData['type'] == 'tiered') {
      // 2024: tiered system
      final monthly = subsidyData['monthly'] as List;
      for (final s in monthly) {
        final desde = (s['desde'] as num).toDouble();
        final hasta = s['hasta'] == null
            ? double.infinity
            : (s['hasta'] as num).toDouble();
        if (income >= desde && income <= hasta) {
          return (s['subsidio'] as num).toDouble();
        }
      }
      return 0.0;
    } else {
      // 2025/2026: flat system
      final monthly = subsidyData['monthly'] as Map<String, dynamic>;
      final maxIncome = (monthly['maxIncome'] as num).toDouble();
      final amount = (monthly['amount'] as num).toDouble();
      return income <= maxIncome ? amount : 0.0;
    }
  }

  /// Calculate ISR (Income Tax) for Mexico
  ///
  /// Parameters:
  /// - [ingresoGravable]: Taxable income for the period
  /// - [periodo]: Payment period (default: mensual)
  /// - [year]: Tax year (default: 2026)
  ///
  /// Returns: Complete calculation result with breakdown
  ///
  /// Examples:
  /// ```dart
  /// final result = ISRCalculator.calculateISR(15000, ISRPeriod.mensual, ISRYear.year2026);
  /// print('ISR: \$${result.isrFinal.toStringAsFixed(2)}');
  /// ```
  static ISRCalculationResult calculateISR(
    double ingresoGravable, {
    ISRPeriod periodo = ISRPeriod.mensual,
    ISRYear year = ISRYear.year2026,
  }) {
    // For 2026, use period-specific tables directly
    final usePeriodTables = year == ISRYear.year2026 &&
        [
          ISRPeriod.diaria,
          ISRPeriod.semanal,
          ISRPeriod.quincenal,
          ISRPeriod.mensual,
          ISRPeriod.anual,
        ].contains(periodo);

    if (usePeriodTables) {
      // Use official tables for the period (no conversion needed)
      final brackets = getISRBrackets(year, periodo);

      // Find applicable bracket
      final bracket = brackets.firstWhere(
        (b) =>
            ingresoGravable >= b.limiteInferior &&
            ingresoGravable <= b.limiteSuperior,
        orElse: () => brackets.last,
      );

      // Calculate excess over lower limit
      final excedente = ingresoGravable - bracket.limiteInferior;

      // Calculate marginal tax
      final impuestoMarginal = excedente * (bracket.tasa / 100);

      // Add fixed fee
      final isrAntesSubsidio = bracket.cuotaFija + impuestoMarginal;

      // Calculate subsidy (convert to monthly equivalent)
      final factor = periodo.factor;
      final ingresoMensualEquivalente = ingresoGravable * factor;
      final subsidioMensual = calculateSubsidy(ingresoMensualEquivalente, year);
      final subsidioProrrateado = subsidioMensual / factor;

      // Final ISR
      final isrFinal = isrAntesSubsidio - subsidioProrrateado < 0
          ? 0.0
          : isrAntesSubsidio - subsidioProrrateado;

      final tasaEfectiva =
          ingresoGravable > 0 ? (isrFinal / ingresoGravable * 100) : 0.0;

      return ISRCalculationResult(
        ingresoGravable: ingresoGravable,
        periodo: periodo.value,
        year: year.value,
        ingresoMensualizado: ingresoMensualEquivalente,
        bracket: bracket,
        excedente: excedente,
        impuestoMarginal: impuestoMarginal,
        isrAntesSubsidio: isrAntesSubsidio,
        subsidio: subsidioProrrateado,
        isrFinal: isrFinal,
        tasaEfectiva: tasaEfectiva,
      );
    }

    // For 2024/2025 or decenal period, use factor-based conversion
    final brackets = getISRBrackets(year, ISRPeriod.mensual);

    // Convert to monthly
    final factor = periodo.factor;
    final ingresoMensualizado = ingresoGravable * factor;

    // Find applicable bracket
    final bracket = brackets.firstWhere(
      (b) =>
          ingresoMensualizado >= b.limiteInferior &&
          ingresoMensualizado <= b.limiteSuperior,
      orElse: () => brackets.last,
    );

    // Calculate excess over lower limit
    final excedente = ingresoMensualizado - bracket.limiteInferior;

    // Calculate marginal tax
    final impuestoMarginal = excedente * (bracket.tasa / 100);

    // Add fixed fee
    final isrAntesSubsidio = bracket.cuotaFija + impuestoMarginal;

    // Calculate subsidy
    final subsidio = calculateSubsidy(ingresoMensualizado, year);

    // Final ISR (monthly)
    final isrFinalMensual =
        isrAntesSubsidio - subsidio < 0 ? 0.0 : isrAntesSubsidio - subsidio;

    // Convert back to original period
    final isrPeriodo = isrFinalMensual / factor;

    final tasaEfectiva =
        ingresoGravable > 0 ? (isrPeriodo / ingresoGravable * 100) : 0.0;

    return ISRCalculationResult(
      ingresoGravable: ingresoGravable,
      periodo: periodo.value,
      year: year.value,
      ingresoMensualizado: ingresoMensualizado,
      bracket: bracket,
      excedente: excedente,
      impuestoMarginal: impuestoMarginal,
      isrAntesSubsidio: isrAntesSubsidio,
      subsidio: subsidio,
      isrFinal: isrPeriodo,
      tasaEfectiva: tasaEfectiva,
    );
  }
}
