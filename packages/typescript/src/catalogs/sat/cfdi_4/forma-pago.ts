/**
 * SAT CFDI 4.0 - Forma de Pago Catalog
 * Payment methods
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { FormaPago } from '../../../types';

export class FormaPagoCatalog {
  private static _data: FormaPago[] | null = null;

  private static getData(): FormaPago[] {
    if (!this._data) {
      this._data = loadCatalogObject<FormaPago>('sat/cfdi_4.0/forma_pago.json');
    }
    return this._data;
  }

  static getAll(): FormaPago[] {
    return this.getData();
  }

  static getForma(code: string): FormaPago | undefined {
    return this.getData().find((forma) => forma.code === code);
  }

  static isBancarizado(code: string): boolean {
    const forma = this.getForma(code);
    return forma?.bancarizado === true;
  }

  static isValid(code: string): boolean {
    return this.getData().some((forma) => forma.code === code);
  }

  static searchByDescription(keyword: string): FormaPago[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((forma) => forma.description.toUpperCase().includes(search));
  }
}
