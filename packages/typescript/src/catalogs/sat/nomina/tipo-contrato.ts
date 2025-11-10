/**
 * SAT Nómina 1.2 - Tipo de Contrato
 * Labor contract types
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { TipoContrato } from '../../../types';

export class TipoContratoCatalog {
  private static _data: TipoContrato[] | null = null;

  private static getData(): TipoContrato[] {
    if (!this._data) {
      this._data = loadCatalogObject<TipoContrato>('sat/nomina_1.2/tipo_contrato.json');
    }
    return this._data;
  }

  static getAll(): TipoContrato[] {
    return this.getData();
  }

  static getContrato(code: string): TipoContrato | undefined {
    return this.getData().find(c => c.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(c => c.code === code);
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): TipoContrato[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(c =>
      c.descripcion.toUpperCase().includes(search)
    );
  }

  /**
   * Check if contract is indefinite term
   */
  static isIndefinido(code: string): boolean {
    const contrato = this.getContrato(code);
    return contrato?.descripcion.toUpperCase().includes('INDETERMINADO') ?? false;
  }

  /**
   * Check if contract is fixed term
   */
  static isDeterminado(code: string): boolean {
    const contrato = this.getContrato(code);
    return contrato?.descripcion.toUpperCase().includes('DETERMINADO') ?? false;
  }
}
