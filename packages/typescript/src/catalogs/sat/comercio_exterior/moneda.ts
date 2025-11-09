/**
 * SAT Comercio Exterior - Moneda Catalog
 * ISO 4217 currency codes
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { Moneda } from '../../../types';

export class MonedaCatalog {
  private static _data: Moneda[] | null = null;

  private static getData(): Moneda[] {
    if (!this._data) {
      this._data = loadCatalog<Moneda>('sat/comercio_exterior/monedas.json');
    }
    return this._data;
  }

  static getAll(): Moneda[] {
    return this.getData();
  }

  static getMoneda(code: string): Moneda | undefined {
    return this.getData().find(m => (m.codigo || m.code) === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some(m => (m.codigo || m.code) === code.toUpperCase());
  }

  /**
   * Get currency name
   */
  static getName(code: string): string | undefined {
    const moneda = this.getMoneda(code);
    return moneda?.nombre || moneda?.name;
  }

  /**
   * Get decimal precision for currency
   */
  static getDecimals(code: string): number | undefined {
    const moneda = this.getMoneda(code);
    return moneda?.decimales || moneda?.decimals;
  }

  /**
   * Validate currency conversion to USD
   */
  static validateConversionUsd(data: {
    moneda: string;
    total: number;
    tipo_cambio_usd: number;
    total_usd: number;
  }): { valid: boolean; error?: string; calculated_total?: number } {
    const moneda = this.getMoneda(data.moneda);

    if (!moneda) {
      return { valid: false, error: `Invalid currency code: ${data.moneda}` };
    }

    // If already in USD, tipo_cambio should be 1.0
    if (data.moneda === 'USD') {
      if (Math.abs(data.tipo_cambio_usd - 1.0) > 0.0001) {
        return { valid: false, error: 'Exchange rate for USD must be 1.0' };
      }
      if (Math.abs(data.total - data.total_usd) > 0.01) {
        return { valid: false, error: 'Total and total_usd must be equal for USD' };
      }
      return { valid: true };
    }

    // Calculate expected USD total
    const calculatedTotalUsd = data.total * data.tipo_cambio_usd;
    const decimals = moneda.decimales || moneda.decimals || 2;
    const tolerance = Math.pow(10, -(decimals + 1));

    if (Math.abs(calculatedTotalUsd - data.total_usd) > tolerance) {
      return {
        valid: false,
        error: `Conversion mismatch: expected ${calculatedTotalUsd.toFixed(decimals)}, got ${data.total_usd}`,
        calculated_total: calculatedTotalUsd
      };
    }

    return { valid: true, calculated_total: calculatedTotalUsd };
  }

  /**
   * Search currencies by name
   */
  static searchByName(keyword: string): Moneda[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(m =>
      (m.nombre || m.name || '').toUpperCase().includes(search) ||
      (m.codigo || m.code || '').includes(search)
    );
  }
}
