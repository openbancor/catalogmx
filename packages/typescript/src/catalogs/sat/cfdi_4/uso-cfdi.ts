/**
 * SAT CFDI 4.0 - Uso CFDI Catalog
 * CFDI usage codes
 */

import { loadCatalogArray } from '../../../utils/catalog-loader';
import type { UsoCfdi } from '../../../types';

export class UsoCFDICatalog {
  private static _data: UsoCfdi[] | null = null;

  private static getData(): UsoCfdi[] {
    if (this._data === null) {
      const rawData = loadCatalogArray<UsoCfdi>('sat/cfdi_4.0/uso_cfdi.json');
      this._data = rawData.map((uso) => ({
        ...uso,
        persona_fisica: uso.persona_fisica ?? uso.fisica,
        persona_moral: uso.persona_moral ?? uso.moral,
      }));
    }
    return this._data;
  }

  static getUso(code: string): UsoCfdi | undefined {
    const normalized = code.toUpperCase();
    return this.getData().find((uso) => uso.code === normalized);
  }

  static isValid(code: string): boolean {
    return this.getUso(code) !== undefined;
  }

  static searchByDescription(keyword: string): UsoCfdi[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((uso) => uso.description.toUpperCase().includes(search));
  }
}
