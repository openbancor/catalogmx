/**
 * SAT Nómina 1.2 - Riesgo de Puesto
 * IMSS risk levels with premium ranges
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { RiesgoPuesto } from '../../../types';

export class RiesgoPuestoCatalog {
  private static _data: RiesgoPuesto[] | null = null;

  private static getData(): RiesgoPuesto[] {
    if (!this._data) {
      this._data = loadCatalogObject<RiesgoPuesto>('sat/nomina_1.2/riesgo_puesto.json');
    }
    return this._data;
  }

  static getAll(): RiesgoPuesto[] {
    return this.getData();
  }

  static getRiesgo(code: string): RiesgoPuesto | undefined {
    return this.getData().find(r => r.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(r => r.code === code);
  }

  /**
   * Get premium range for risk level
   */
  static getPrimaRange(code: string): { minima: number; media: number; maxima: number } | undefined {
    const riesgo = this.getRiesgo(code);
    if (!riesgo) return undefined;
    return {
      minima: riesgo.prima_minima,
      media: riesgo.prima_media,
      maxima: riesgo.prima_maxima
    };
  }

  /**
   * Get average premium for risk level
   */
  static getPrimaMedia(code: string): number | undefined {
    return this.getRiesgo(code)?.prima_media;
  }

  /**
   * Validate if a premium is within valid range for risk level
   */
  static validatePrima(code: string, prima: number): boolean {
    const riesgo = this.getRiesgo(code);
    if (!riesgo) return false;
    return prima >= riesgo.prima_minima && prima <= riesgo.prima_maxima;
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getRiesgo(code)?.descripcion;
  }
}
