/**
 * SAT Nómina 1.2 - Tipo de Régimen
 * Regime types for payroll
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { TipoRegimen } from '../../../types';

export class TipoRegimenCatalog {
  private static _data: TipoRegimen[] | null = null;

  private static getData(): TipoRegimen[] {
    if (!this._data) {
      this._data = loadCatalog<TipoRegimen>('sat/nomina_1.2/tipo_regimen.json');
    }
    return this._data;
  }

  static getAll(): TipoRegimen[] {
    return this.getData();
  }

  static getRegimen(code: string): TipoRegimen | undefined {
    return this.getData().find(r => r.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(r => r.code === code);
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getRegimen(code)?.descripcion;
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): TipoRegimen[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(r =>
      r.descripcion.toUpperCase().includes(search)
    );
  }
}
