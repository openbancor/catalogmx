/** SAT Nómina 1.2 - Riesgo de Puesto. */

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
    return this.getData().find((r) => r.code === code);
  }

  static isValid(code: string): boolean {
    return this.getRiesgo(code) !== undefined;
  }

  static getPrimaRange(
    code: string
  ): { minima: number; media: number; maxima: number } | undefined {
    const riesgo = this.getRiesgo(code);
    if (
      !riesgo ||
      riesgo.prima_minima == null ||
      riesgo.prima_media == null ||
      riesgo.prima_maxima == null
    ) {
      return undefined;
    }
    return {
      minima: riesgo.prima_minima,
      media: riesgo.prima_media,
      maxima: riesgo.prima_maxima,
    };
  }

  static getPrimaMedia(code: string): number | undefined {
    return this.getPrimaRange(code)?.media;
  }

  static validatePrima(code: string, prima: number): boolean {
    const range = this.getPrimaRange(code);
    return range ? prima >= range.minima && prima <= range.maxima : false;
  }

  static getDescription(code: string): string | undefined {
    return this.getRiesgo(code)?.descripcion;
  }
}
