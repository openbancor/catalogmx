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
import { base } from '$app/paths';
import { setCatalogJsonData } from 'catalogmx/utils';
import { getDatabase } from './db';

export async function initCatalogmxSqlite(): Promise<void> {
  await Promise.all([getDatabase(), preloadCatalogJson()]);
}

async function preloadCatalogJson(): Promise<void> {
  const files: Array<{ key: string; path: string }> = [
    { key: 'isr-tables.json', path: 'isr-tables.json' },
    { key: 'resico-tables.json', path: 'resico-tables.json' },
    { key: 'imss-tables.json', path: 'imss-tables.json' },
    { key: 'imss-catalogs.json', path: 'imss/imss-catalogs.json' },
    { key: 'sat/impuestos/iva_tasas.json', path: 'sat/impuestos/iva_tasas.json' },
    { key: 'sat/impuestos/ieps_tasas.json', path: 'sat/impuestos/ieps_tasas.json' },
    { key: 'sat/impuestos/retenciones.json', path: 'sat/impuestos/retenciones.json' },
    { key: 'sat/impuestos/impuestos_locales.json', path: 'sat/impuestos/impuestos_locales.json' },
  ];

  const prefix = base ? `${base}/` : '/';
  const buildUrl = (path: string) => `${prefix}data/${path}`.replace(/\/{2,}/g, '/');

  const results = await Promise.allSettled(
    files.map(async ({ key, path }) => {
      const url = buildUrl(path);
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to preload ${path}: ${response.status} ${response.statusText}`);
      }
      const payload = (await response.json()) as unknown;
      setCatalogJsonData(key, payload);
    })
  );

  for (const result of results) {
    if (result.status === 'rejected') {
      console.warn('catalogmx preload failed:', result.reason);
    }
  }
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
