/**
 * SAT CFDI 4.0 - Impuesto Catalog
 * Tax types (ISR, IVA, IEPS)
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { Impuesto } from '../../../types';

export class ImpuestoCatalog {
  private static _data: Impuesto[] | null = null;

  private static getData(): Impuesto[] {
    if (!this._data) {
      this._data = loadCatalogObject<Impuesto>('sat/cfdi_4.0/impuesto.json');
    }
    return this._data;
  }

  static getAll(): Impuesto[] {
    return this.getData();
  }

  static getImpuesto(code: string): Impuesto | undefined {
    return this.getData().find((i) => i.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some((i) => i.code === code);
  }

  /**
   * Check if tax supports retention (retención)
   */
  static supportsRetencion(code: string): boolean {
    const impuesto = this.getImpuesto(code);
    return impuesto?.retencion === true;
  }

  /**
   * Check if tax supports transfer (traslado)
   */
  static supportsTraslado(code: string): boolean {
    const impuesto = this.getImpuesto(code);
    return impuesto?.traslado === true;
  }

  /**
   * Get taxes that support retention
   */
  static getRetencionTaxes(): Impuesto[] {
    return this.getData().filter((i) => i.retencion);
  }

  /**
   * Get taxes that support transfer
   */
  static getTrasladoTaxes(): Impuesto[] {
    return this.getData().filter((i) => i.traslado);
  }

  /**
   * Check if it's ISR
   */
  static isISR(code: string): boolean {
    return code === '001';
  }

  /**
   * Check if it's IVA
   */
  static isIVA(code: string): boolean {
    return code === '002';
  }

  /**
   * Check if it's IEPS
   */
  static isIEPS(code: string): boolean {
    return code === '003';
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getImpuesto(code)?.description;
  }
}
