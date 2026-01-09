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

import isrTablesData from '../../../shared-data/isr-tables.json';
import resicoTablesData from '../../../shared-data/resico-tables.json';
import imssTablesData from '../../../shared-data/imss-tables.json';
import imssCatalogsData from '../../../shared-data/imss-catalogs.json';
import ivaData from '../../../shared-data/sat/impuestos/iva_tasas.json';
import iepsData from '../../../shared-data/sat/impuestos/ieps_tasas.json';
import retencionesData from '../../../shared-data/sat/impuestos/retenciones.json';
import impuestosLocalesData from '../../../shared-data/sat/impuestos/impuestos_locales.json';

ISRCalculator.setData(isrTablesData);
RESICOCalculator.setData(resicoTablesData);
IMSSCalculator.setTablesData(imssTablesData);
IMSSCalculator.setCatalogsData(imssCatalogsData);
IVACalculator.setData(ivaData);
IEPSCalculator.setData(iepsData);
RetencionCalculator.setData(retencionesData);
ImpuestosLocalesCalculator.setData(impuestosLocalesData);

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
