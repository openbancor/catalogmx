import {
  ISRCalculator,
  RESICOCalculator,
  IMSSCalculator,
  IVACalculator,
  IEPSCalculator,
  RetencionCalculator,
  ImpuestosLocalesCalculator,
  WorkerCostCalculator,
  calcularCostoTotal,
  obtenerDiasVacaciones,
} from 'catalogmx/calculators';
import {
  RFCValidator,
  CURPValidator,
  CLABEValidator,
  NSSValidator,
  validateRfc,
  validateCurp,
  validateClabe,
  validateNss,
  generateRfcPersonaFisica,
  generateRfcPersonaMoral,
  generateCurp,
  generateClabe,
  generateNss,
  calculateClabeCheckDigit,
} from 'catalogmx/validators';
import { getDatabase } from './db';

export async function initCatalogmxSqlite(): Promise<void> {
  await getDatabase();
}

export {
  ISRCalculator,
  RESICOCalculator,
  IMSSCalculator,
  IVACalculator,
  IEPSCalculator,
  RetencionCalculator,
  ImpuestosLocalesCalculator,
  WorkerCostCalculator,
  calcularCostoTotal,
  obtenerDiasVacaciones,
  RFCValidator,
  CURPValidator,
  CLABEValidator,
  NSSValidator,
  validateRfc,
  validateCurp,
  validateClabe,
  validateNss,
  generateRfcPersonaFisica,
  generateRfcPersonaMoral,
  generateCurp,
  generateClabe,
  generateNss,
  calculateClabeCheckDigit,
};
