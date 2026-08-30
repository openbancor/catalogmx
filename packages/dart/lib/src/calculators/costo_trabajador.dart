/// Costo Total del Trabajador Calculator for Mexico
/// Calculates the true cost of hiring an employee in Mexico including all contributions and reserves
///
/// Official sources:
/// - Ley Federal del Trabajo (LFT)
/// - IMSS contribution tables
/// - Infonavit contributions
/// - State payroll tax laws
library;

import 'imss.dart';
import 'impuestos.dart';

/// Total worker cost calculation result
class CostoTotalResult {
  const CostoTotalResult({
    required this.salarioBrutoMensual,
    required this.cuotasImssPatronales,
    required this.infonavit,
    required this.impuestoNomina,
    required this.reservaAguinaldo,
    required this.reservaPrimaVacacional,
    required this.reservaVacaciones,
    required this.ptuEstimado,
    required this.costoTotalMensual,
    required this.costoTotalAnual,
    required this.factorCosto,
  });

  final double salarioBrutoMensual;
  final double cuotasImssPatronales;
  final double infonavit;
  final double impuestoNomina;
  final double reservaAguinaldo;
  final double reservaPrimaVacacional;
  final double reservaVacaciones;
  final double ptuEstimado;
  final double costoTotalMensual;
  final double costoTotalAnual;
  final double factorCosto;

  Map<String, dynamic> toJson() => {
        'salario_bruto_mensual': salarioBrutoMensual,
        'cuotas_imss_patronales': cuotasImssPatronales,
        'infonavit': infonavit,
        'impuesto_nomina': impuestoNomina,
        'reserva_aguinaldo': reservaAguinaldo,
        'reserva_prima_vacacional': reservaPrimaVacacional,
        'reserva_vacaciones': reservaVacaciones,
        'ptu_estimado': ptuEstimado,
        'costo_total_mensual': costoTotalMensual,
        'costo_total_anual': costoTotalAnual,
        'factor_costo': factorCosto,
      };
}

/// Vacation days according to LFT 2023 (Article 76)
const Map<int, int> _diasVacacionesPorAntiguedad = {
  1: 12,
  2: 14,
  3: 16,
  4: 18,
  5: 20,
  6: 22,
  7: 22,
  8: 22,
  9: 22,
  10: 22,
  11: 24,
  12: 24,
  13: 24,
  14: 24,
  15: 24,
  16: 26,
  17: 26,
  18: 26,
  19: 26,
  20: 26,
  21: 28,
  22: 28,
  23: 28,
  24: 28,
  25: 28,
  26: 30,
  27: 30,
  28: 30,
  29: 30,
  30: 30,
  31: 32,
  32: 32,
  33: 32,
  34: 32,
  35: 32,
};

/// Get vacation days based on seniority according to LFT 2023
///
/// Args:
///   antiguedadAnos: Years of seniority (1-35+)
///
/// Returns:
///   Number of vacation days
///
/// Examples:
/// ```dart
/// obtenerDiasVacaciones(1); // 12
/// obtenerDiasVacaciones(5); // 20
/// obtenerDiasVacaciones(40); // 32
/// ```
int obtenerDiasVacaciones(int antiguedadAnos) {
  if (antiguedadAnos <= 0) {
    return 12;
  } else if (antiguedadAnos <= 35) {
    return _diasVacacionesPorAntiguedad[antiguedadAnos] ?? 32;
  } else {
    return 32;
  }
}

/// Calculate the total cost of employing a worker in Mexico
///
/// This calculator helps employers understand the true cost of hiring someone
/// by including all mandatory contributions, taxes, and labor law reserves.
///
/// Args:
///   salarioMensualBruto: Monthly gross salary (base pay)
///   cveEstado: State code for payroll tax calculation (default: "09" CDMX)
///   antiguedadAnos: Years of seniority (affects vacation days, default: 1)
///   diasAguinaldo: Aguinaldo days (minimum 15, default: 15)
///   incluirPtu: Include PTU (profit sharing) reserve (default: false)
///   porcentajePtu: PTU percentage if included (default: 10.0%)
///   year: Year for IMSS calculations (default: IMSSYear.year2026)
///
/// Returns:
///   Complete breakdown of employer costs including:
///   - IMSS employer contributions
///   - Infonavit (5% of SBC)
///   - Payroll tax (varies by state)
///   - Aguinaldo reserve
///   - Vacation bonus reserve
///   - Vacation pay reserve
///   - Optional PTU reserve
///
/// Examples:
/// ```dart
/// // Calculate cost for $15,000/month employee in CDMX
/// final result = calcularCostoTotal(salarioMensualBruto: 15000);
/// print('Total monthly cost: \$${result.costoTotalMensual.toStringAsFixed(2)}');
///
/// // Calculate with PTU included
/// final result2 = calcularCostoTotal(
///   salarioMensualBruto: 20000,
///   cveEstado: '09',
///   antiguedadAnos: 3,
///   incluirPtu: true,
/// );
/// print('Factor: ${result2.factorCosto.toStringAsFixed(2)}x');
/// ```
CostoTotalResult calcularCostoTotal({
  required double salarioMensualBruto,
  String cveEstado = '09',
  int antiguedadAnos = 1,
  int diasAguinaldo = 15,
  bool incluirPtu = false,
  double porcentajePtu = 10.0,
  IMSSYear year = IMSSYear.year2026,
}) {
  if (antiguedadAnos < 0) {
    throw ArgumentError('antiguedadAnos debe ser un entero no negativo');
  }
  if (diasAguinaldo < 15) {
    throw ArgumentError('diasAguinaldo debe ser un entero mayor o igual a 15');
  }
  if (!porcentajePtu.isFinite || porcentajePtu < 0 || porcentajePtu > 100) {
    throw ArgumentError(
      'porcentajePtu debe ser un número finito entre 0 y 100',
    );
  }

  // 1. Calculate daily wage (assuming 30-day month for calculation purposes)
  final salarioDiario = salarioMensualBruto / 30.0;

  // 2. Calculate IMSS employer contributions
  final cuotasImss = IMSSCalculator.calcularCuotasObreroPatronales(
    salarioDiario,
    dias: 30,
    year: year,
  );
  final cuotasImssPatronales = cuotasImss.totalPatron;

  // 3. Calculate Infonavit (5% of SBC)
  final salarioBaseCotizacion = cuotasImss.salarioBaseCotizacion;
  final infonavit = salarioBaseCotizacion * 0.05;

  // 4. Calculate payroll tax (varies by state, typically 2-3%)
  final impuestoNomina = ImpuestosLocalesCalculator.calcularImpuestoNomina(
    salarioMensualBruto,
    cveEstado,
  );

  // 5. Calculate monthly reserves

  // Aguinaldo: diasAguinaldo / 12 months
  final reservaAguinaldo = (salarioDiario * diasAguinaldo) / 12.0;

  // Vacation days based on seniority (LFT 2023)
  final diasVacaciones = obtenerDiasVacaciones(antiguedadAnos);

  // Vacation reserve: vacation days / 12 months
  final reservaVacaciones = (salarioDiario * diasVacaciones) / 12.0;

  // Vacation bonus (prima vacacional): 25% of vacation days value
  final reservaPrimaVacacional = reservaVacaciones * 0.25;

  // 6. Optional PTU reserve
  var ptuEstimado = 0.0;
  if (incluirPtu) {
    // PTU is typically calculated on annual salary
    // We estimate monthly reserve as (annual_salary * ptu_percentage) / 12
    ptuEstimado = (salarioMensualBruto * 12 * (porcentajePtu / 100)) / 12.0;
  }

  // 7. Calculate totals
  final costoTotalMensual = salarioMensualBruto +
      cuotasImssPatronales +
      infonavit +
      impuestoNomina +
      reservaAguinaldo +
      reservaPrimaVacacional +
      reservaVacaciones +
      ptuEstimado;

  final costoTotalAnual = costoTotalMensual * 12;

  // Factor: how much the real cost is compared to base salary
  final factorCosto = costoTotalMensual / salarioMensualBruto;

  return CostoTotalResult(
    salarioBrutoMensual: salarioMensualBruto,
    cuotasImssPatronales: cuotasImssPatronales,
    infonavit: infonavit,
    impuestoNomina: impuestoNomina,
    reservaAguinaldo: reservaAguinaldo,
    reservaPrimaVacacional: reservaPrimaVacacional,
    reservaVacaciones: reservaVacaciones,
    ptuEstimado: ptuEstimado,
    costoTotalMensual: costoTotalMensual,
    costoTotalAnual: costoTotalAnual,
    factorCosto: factorCosto,
  );
}

/// Worker Cost Calculator
class WorkerCostCalculator {
  /// Get vacation days based on seniority according to LFT 2023
  static int obtenerDiasVacaciones(int antiguedadAnos) =>
      obtenerDiasVacaciones(antiguedadAnos);

  /// Calculate the total cost of employing a worker in Mexico
  static CostoTotalResult calcularCostoTotal({
    required double salarioMensualBruto,
    String cveEstado = '09',
    int antiguedadAnos = 1,
    int diasAguinaldo = 15,
    bool incluirPtu = false,
    double porcentajePtu = 10.0,
    IMSSYear year = IMSSYear.year2026,
  }) =>
      calcularCostoTotal(
        salarioMensualBruto: salarioMensualBruto,
        cveEstado: cveEstado,
        antiguedadAnos: antiguedadAnos,
        diasAguinaldo: diasAguinaldo,
        incluirPtu: incluirPtu,
        porcentajePtu: porcentajePtu,
        year: year,
      );
}
