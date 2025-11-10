/**
 * SAT CFDI 4.0 - Método de Pago Catalog
 * Payment methods (PUE, PPD)
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { MetodoPago } from '../../../types';

export class MetodoPagoCatalog {
  private static _data: MetodoPago[] | null = null;

  private static getData(): MetodoPago[] {
    if (!this._data) {
      this._data = loadCatalogObject<MetodoPago>('sat/cfdi_4.0/metodo_pago.json');
    }
    return this._data;
  }

  static getAll(): MetodoPago[] {
    return this.getData();
  }

  static getMetodo(code: string): MetodoPago | undefined {
    return this.getData().find(m => m.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some(m => m.code === code.toUpperCase());
  }

  /**
   * Check if payment is in one exhibition (Pago en Una Sola Exhibición)
   */
  static isPUE(code: string): boolean {
    return code.toUpperCase() === 'PUE';
  }

  /**
   * Check if payment is in installments (Pago en Parcialidades o Diferido)
   */
  static isPPD(code: string): boolean {
    return code.toUpperCase() === 'PPD';
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getMetodo(code)?.description;
  }
}
