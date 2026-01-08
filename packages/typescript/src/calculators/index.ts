/**
 * Tax and Payroll Calculators for Mexico
 * ISR, RESICO, IMSS, IVA, IEPS, Retenciones, Impuestos Locales, Worker Cost
 */

export { ISRCalculator } from './isr-calculator';
export {
  RESICOCalculator,
  type RESICOYear,
  type RESICOPeriod,
  type RESICOBracket,
  type RESICOLimits,
  type RESICOCalculationResult,
} from './resico-calculator';
export {
  IMSSCalculator,
  type IMSSYear,
  type ZonaSalario,
  type ClaseRiesgo,
  type UMAInfo,
  type CuotasIMSSResult,
  type Modalidad40Result,
  type Modalidad10Result,
} from './imss-calculator';
export {
  IVACalculator,
  IEPSCalculator,
  RetencionCalculator,
  ImpuestosLocalesCalculator,
} from './tax-calculator';
export {
  WorkerCostCalculator,
  calcularCostoTotal,
  obtenerDiasVacaciones,
  type CostoTotalResult,
  type CalcularCostoTotalOptions,
} from './worker-cost-calculator';
