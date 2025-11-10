/**
 * SAT CFDI 4.0 - Objeto de Impuesto Catalog
 * Tax object codes (updated Dec 2024)
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { ObjetoImp } from '../../../types';

export class ObjetoImpCatalog {
  private static _data: ObjetoImp[] | null = null;

  private static getData(): ObjetoImp[] {
    if (!this._data) {
      this._data = loadCatalogObject<ObjetoImp>('sat/cfdi_4.0/objeto_imp.json');
    }
    return this._data;
  }

  static getAll(): ObjetoImp[] {
    return this.getData();
  }

  static getObjeto(code: string): ObjetoImp | undefined {
    return this.getData().find((o) => o.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some((o) => o.code === code);
  }

  /**
   * Check if it's not subject to tax
   */
  static isNoObjetoImpuesto(code: string): boolean {
    return code === '01';
  }

  /**
   * Check if it's subject to tax
   */
  static isSiObjetoImpuesto(code: string): boolean {
    return code === '02';
  }

  /**
   * Check if it's exempt from tax
   */
  static isExento(code: string): boolean {
    return code === '03' || code === '04';
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getObjeto(code)?.description;
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): ObjetoImp[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((o) => o.description.toUpperCase().includes(search));
  }
}
