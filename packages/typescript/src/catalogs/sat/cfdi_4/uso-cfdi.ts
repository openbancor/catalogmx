/**
 * SAT CFDI 4.0 - Uso CFDI Catalog
 * CFDI usage codes
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { UsoCfdi } from '../../../types';

export class UsoCFDICatalog {
  private static _data: UsoCfdi[] | null = null;

  private static getData(): UsoCfdi[] {
    if (!this._data) {
      this._data = loadCatalog<UsoCfdi>('sat/cfdi_4.0/uso_cfdi.json');
    }
    return this._data;
  }

  static getAll(): UsoCfdi[] {
    return this.getData();
  }

  static getUso(code: string): UsoCfdi | undefined {
    return this.getData().find(uso => uso.code === code);
  }

  static isValidForPersonaFisica(code: string): boolean {
    const uso = this.getUso(code);
    return uso?.persona_fisica === true;
  }

  static isValidForPersonaMoral(code: string): boolean {
    const uso = this.getUso(code);
    return uso?.persona_moral === true;
  }

  static getForPersonaFisica(): UsoCfdi[] {
    return this.getData().filter(uso => uso.persona_fisica);
  }

  static getForPersonaMoral(): UsoCfdi[] {
    return this.getData().filter(uso => uso.persona_moral);
  }

  static isValid(code: string): boolean {
    return this.getData().some(uso => uso.code === code);
  }

  static searchByDescription(keyword: string): UsoCfdi[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(uso =>
      uso.description.toUpperCase().includes(search)
    );
  }
}
