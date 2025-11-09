/**
 * SAT Nómina 1.2 - Periodicidad de Pago
 * Payment frequency
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { PeriodicidadPago } from '../../../types';

export class PeriodicidadPagoCatalog {
  private static _data: PeriodicidadPago[] | null = null;

  private static getData(): PeriodicidadPago[] {
    if (!this._data) {
      this._data = loadCatalog<PeriodicidadPago>('sat/nomina_1.2/periodicidad_pago.json');
    }
    return this._data;
  }

  static getAll(): PeriodicidadPago[] {
    return this.getData();
  }

  static getPeriodicidad(code: string): PeriodicidadPago | undefined {
    return this.getData().find(p => p.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(p => p.code === code);
  }

  /**
   * Get number of days for payment period
   */
  static getDays(code: string): number | undefined {
    return this.getPeriodicidad(code)?.days;
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getPeriodicidad(code)?.descripcion;
  }

  /**
   * Check if it's biweekly (quincenal)
   */
  static isQuincenal(code: string): boolean {
    return code === '04';
  }

  /**
   * Check if it's weekly
   */
  static isSemanal(code: string): boolean {
    return code === '02';
  }

  /**
   * Check if it's monthly
   */
  static isMensual(code: string): boolean {
    return code === '05';
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): PeriodicidadPago[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(p =>
      p.descripcion.toUpperCase().includes(search)
    );
  }
}
