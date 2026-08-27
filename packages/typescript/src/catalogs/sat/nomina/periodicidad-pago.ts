/**
 * SAT Nómina 1.2 - Periodicidad de Pago
 * Payment frequency
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { PeriodicidadPago } from '../../../types';

export class PeriodicidadPagoCatalog {
  private static _data: PeriodicidadPago[] | null = null;

  private static getData(): PeriodicidadPago[] {
    if (!this._data) {
      this._data = loadCatalogObject<PeriodicidadPago>('sat/nomina_1.2/periodicidad_pago.json');
    }
    return this._data;
  }

  static getAll(): PeriodicidadPago[] {
    return this.getData();
  }

  static getPeriodicidad(code: string): PeriodicidadPago | undefined {
    return this.getData().find((p) => p.code === code);
  }

  static getByCode(code: string): PeriodicidadPago | undefined {
    return this.getPeriodicidad(code);
  }

  static isValid(code: string): boolean {
    return this.getData().some((p) => p.code === code);
  }

  static getDays(code: string): number | undefined {
    return this.getPeriodicidad(code)?.days;
  }

  static getDescription(code: string): string | undefined {
    return this.getPeriodicidad(code)?.descripcion;
  }

  static isQuincenal(code: string): boolean {
    return code === '04';
  }

  static isSemanal(code: string): boolean {
    return code === '02';
  }

  static isMensual(code: string): boolean {
    return code === '05';
  }

  static searchByDescription(keyword: string): PeriodicidadPago[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((p) => p.descripcion.toUpperCase().includes(search));
  }
}
