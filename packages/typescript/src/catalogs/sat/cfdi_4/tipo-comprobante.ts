/**
 * SAT CFDI 4.0 - Tipo de Comprobante Catalog
 * Receipt types (I, E, T, N, P)
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { TipoComprobante } from '../../../types';

export class TipoComprobanteCatalog {
  private static _data: TipoComprobante[] | null = null;

  private static getData(): TipoComprobante[] {
    if (!this._data) {
      this._data = loadCatalog<TipoComprobante>('sat/cfdi_4.0/tipo_comprobante.json');
    }
    return this._data;
  }

  static getAll(): TipoComprobante[] {
    return this.getData();
  }

  static getTipo(code: string): TipoComprobante | undefined {
    return this.getData().find(t => t.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some(t => t.code === code.toUpperCase());
  }

  /**
   * Check if it's an Income receipt (Ingreso)
   */
  static isIngreso(code: string): boolean {
    return code.toUpperCase() === 'I';
  }

  /**
   * Check if it's an Expense receipt (Egreso)
   */
  static isEgreso(code: string): boolean {
    return code.toUpperCase() === 'E';
  }

  /**
   * Check if it's a Transfer receipt (Traslado)
   */
  static isTraslado(code: string): boolean {
    return code.toUpperCase() === 'T';
  }

  /**
   * Check if it's a Payroll receipt (Nómina)
   */
  static isNomina(code: string): boolean {
    return code.toUpperCase() === 'N';
  }

  /**
   * Check if it's a Payment receipt (Pago)
   */
  static isPago(code: string): boolean {
    return code.toUpperCase() === 'P';
  }

  /**
   * Get max value for receipt type
   */
  static getValorMax(code: string): number | undefined {
    return this.getTipo(code)?.valor_max;
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getTipo(code)?.description;
  }
}
