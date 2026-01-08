/**
 * Costo Total del Trabajador Calculator for Mexico
 * Calculates the true cost of hiring an employee in Mexico including all contributions and reserves
 *
 * Official sources:
 * - Ley Federal del Trabajo (LFT)
 * - IMSS contribution tables
 * - Infonavit contributions
 * - State payroll tax laws
 */

import { IMSSCalculator, type IMSSYear } from './imss-calculator';
import { ImpuestosLocalesCalculator } from './tax-calculator';

export interface CostoTotalResult {
  salario_bruto_mensual: number;
  cuotas_imss_patronales: number;
  infonavit: number;
  impuesto_nomina: number;
  reserva_aguinaldo: number;
  reserva_prima_vacacional: number;
  reserva_vacaciones: number;
  ptu_estimado: number;
  costo_total_mensual: number;
  costo_total_anual: number;
  factor_costo: number;
}

// Vacation days according to LFT 2023 (Article 76)
const DIAS_VACACIONES_POR_ANTIGUEDAD: Record<number, number> = {
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

/**
 * Get vacation days based on seniority according to LFT 2023
 *
 * @param antiguedad_anos - Years of seniority (1-35+)
 * @returns Number of vacation days
 *
 * @example
 * ```typescript
 * obtenerDiasVacaciones(1); // 12
 * obtenerDiasVacaciones(5); // 20
 * obtenerDiasVacaciones(40); // 32
 * ```
 */
export function obtenerDiasVacaciones(antiguedad_anos: number): number {
  if (antiguedad_anos <= 0) {
    return 12;
  } else if (antiguedad_anos <= 35) {
    return DIAS_VACACIONES_POR_ANTIGUEDAD[antiguedad_anos] ?? 32;
  } else {
    return 32;
  }
}

export interface CalcularCostoTotalOptions {
  salario_mensual_bruto: number;
  cve_estado?: string;
  antiguedad_anos?: number;
  dias_aguinaldo?: number;
  incluir_ptu?: boolean;
  porcentaje_ptu?: number;
  year?: IMSSYear;
}

/**
 * Calculate the total cost of employing a worker in Mexico
 *
 * This calculator helps employers understand the true cost of hiring someone
 * by including all mandatory contributions, taxes, and labor law reserves.
 *
 * @param options - Calculation options
 * @param options.salario_mensual_bruto - Monthly gross salary (base pay)
 * @param options.cve_estado - State code for payroll tax calculation (default: "09" CDMX)
 * @param options.antiguedad_anos - Years of seniority (affects vacation days, default: 1)
 * @param options.dias_aguinaldo - Aguinaldo days (minimum 15, default: 15)
 * @param options.incluir_ptu - Include PTU (profit sharing) reserve (default: false)
 * @param options.porcentaje_ptu - PTU percentage if included (default: 10.0%)
 * @param options.year - Year for IMSS calculations (default: 2026)
 * @returns Complete breakdown of employer costs
 *
 * @example
 * ```typescript
 * // Calculate cost for $15,000/month employee in CDMX
 * const result = calcularCostoTotal({ salario_mensual_bruto: 15000 });
 * console.log(`Total monthly cost: $${result.costo_total_mensual.toFixed(2)}`);
 *
 * // Calculate with PTU included
 * const result2 = calcularCostoTotal({
 *   salario_mensual_bruto: 20000,
 *   cve_estado: "09",
 *   antiguedad_anos: 3,
 *   incluir_ptu: true
 * });
 * console.log(`Factor: ${result2.factor_costo.toFixed(2)}x`);
 * ```
 */
export function calcularCostoTotal(options: CalcularCostoTotalOptions): CostoTotalResult {
  const {
    salario_mensual_bruto,
    cve_estado = '09',
    antiguedad_anos = 1,
    dias_aguinaldo = 15,
    incluir_ptu = false,
    porcentaje_ptu = 10.0,
    year = 2026,
  } = options;

  // 1. Calculate daily wage (assuming 30-day month for calculation purposes)
  const salario_diario = salario_mensual_bruto / 30.0;

  // 2. Calculate IMSS employer contributions
  const cuotas_imss = IMSSCalculator.calcularCuotasObreroPatronales(salario_diario, 30, year);
  const cuotas_imss_patronales = cuotas_imss.total_patron;

  // 3. Calculate Infonavit (5% of SBC)
  const salario_base_cotizacion = cuotas_imss.salario_base_cotizacion;
  const infonavit = salario_base_cotizacion * 0.05;

  // 4. Calculate payroll tax (varies by state, typically 2-3%)
  const impuesto_nomina = ImpuestosLocalesCalculator.calcularImpuestoNomina(
    salario_mensual_bruto,
    cve_estado
  );

  // 5. Calculate monthly reserves

  // Aguinaldo: dias_aguinaldo / 12 months
  const reserva_aguinaldo = (salario_diario * dias_aguinaldo) / 12.0;

  // Vacation days based on seniority (LFT 2023)
  const dias_vacaciones = obtenerDiasVacaciones(antiguedad_anos);

  // Vacation reserve: vacation days / 12 months
  const reserva_vacaciones = (salario_diario * dias_vacaciones) / 12.0;

  // Vacation bonus (prima vacacional): 25% of vacation days value
  const reserva_prima_vacacional = reserva_vacaciones * 0.25;

  // 6. Optional PTU reserve
  let ptu_estimado = 0.0;
  if (incluir_ptu) {
    // PTU is typically calculated on annual salary
    // We estimate monthly reserve as (annual_salary * ptu_percentage) / 12
    ptu_estimado = (salario_mensual_bruto * 12 * (porcentaje_ptu / 100)) / 12.0;
  }

  // 7. Calculate totals
  const costo_total_mensual =
    salario_mensual_bruto +
    cuotas_imss_patronales +
    infonavit +
    impuesto_nomina +
    reserva_aguinaldo +
    reserva_prima_vacacional +
    reserva_vacaciones +
    ptu_estimado;

  const costo_total_anual = costo_total_mensual * 12;

  // Factor: how much the real cost is compared to base salary
  const factor_costo = costo_total_mensual / salario_mensual_bruto;

  return {
    salario_bruto_mensual: salario_mensual_bruto,
    cuotas_imss_patronales,
    infonavit,
    impuesto_nomina,
    reserva_aguinaldo,
    reserva_prima_vacacional,
    reserva_vacaciones,
    ptu_estimado,
    costo_total_mensual,
    costo_total_anual,
    factor_costo,
  };
}

export class WorkerCostCalculator {
  /**
   * Get vacation days based on seniority according to LFT 2023
   */
  static obtenerDiasVacaciones(antiguedad_anos: number): number {
    return obtenerDiasVacaciones(antiguedad_anos);
  }

  /**
   * Calculate the total cost of employing a worker in Mexico
   */
  static calcularCostoTotal(options: CalcularCostoTotalOptions): CostoTotalResult {
    return calcularCostoTotal(options);
  }
}
