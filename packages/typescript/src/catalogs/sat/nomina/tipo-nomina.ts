/**
 * SAT Nómina 1.2 - Tipo de Nómina
 * Payroll types (ordinary and extraordinary)
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { TipoNomina } from '../../../types';

export class TipoNominaCatalog {
  private static _data: TipoNomina[] | null = null;

  private static getData(): TipoNomina[] {
    if (!this._data) {
      this._data = loadCatalogObject<TipoNomina>('sat/nomina_1.2/tipo_nomina.json');
    }
    return this._data;
  }

  static getAll(): TipoNomina[] {
    return this.getData();
  }

  static getTipo(code: string): TipoNomina | undefined {
    return this.getData().find((t) => t.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some((t) => t.code === code);
  }

  /**
   * Check if it's ordinary payroll
   */
  static isOrdinaria(code: string): boolean {
    const tipo = this.getTipo(code);
    return tipo?.descripcion.toUpperCase().includes('ORDINARIA') ?? false;
  }

  /**
   * Check if it's extraordinary payroll
   */
  static isExtraordinaria(code: string): boolean {
    const tipo = this.getTipo(code);
    return tipo?.descripcion.toUpperCase().includes('EXTRAORDINARIA') ?? false;
  }
}
