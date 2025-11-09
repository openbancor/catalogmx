/**
 * SAT CFDI 4.0 - Tipo de Relación Catalog
 * CFDI relationship types
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { TipoRelacion } from '../../../types';

export class TipoRelacionCatalog {
  private static _data: TipoRelacion[] | null = null;

  private static getData(): TipoRelacion[] {
    if (!this._data) {
      this._data = loadCatalog<TipoRelacion>('sat/cfdi_4.0/tipo_relacion.json');
    }
    return this._data;
  }

  static getAll(): TipoRelacion[] {
    return this.getData();
  }

  static getRelacion(code: string): TipoRelacion | undefined {
    return this.getData().find(r => r.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(r => r.code === code);
  }

  /**
   * Check if it's a substitute note
   */
  static isNotaDeDebito(code: string): boolean {
    return code === '01';
  }

  /**
   * Check if it's a credit note
   */
  static isNotaDeCredito(code: string): boolean {
    return code === '02';
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getRelacion(code)?.description;
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): TipoRelacion[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(r =>
      r.description.toUpperCase().includes(search)
    );
  }
}
