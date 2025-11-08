/**
 * SAT Comercio Exterior - País Catalog
 * ISO 3166-1 alpha-3 country codes
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { Pais } from '../../../types';

export class PaisCatalog {
  private static _data: Pais[] | null = null;

  private static getData(): Pais[] {
    if (!this._data) {
      this._data = loadCatalog<Pais>('sat/comercio_exterior/paises.json');
    }
    return this._data;
  }

  static getAll(): Pais[] {
    return this.getData();
  }

  static getPais(code: string): Pais | undefined {
    return this.getData().find(p => p.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some(p => p.code === code.toUpperCase());
  }

  /**
   * Get country name
   */
  static getName(code: string): string | undefined {
    return this.getPais(code)?.name;
  }

  /**
   * Search countries by name
   */
  static searchByName(keyword: string): Pais[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(p =>
      p.name.toUpperCase().includes(search)
    );
  }

  /**
   * Get countries by grouping (if available)
   */
  static getByAgrupacion(agrupacion: string): Pais[] {
    return this.getData().filter(p => p.agrupacion === agrupacion);
  }

  /**
   * Check if country code is Mexico
   */
  static isMexico(code: string): boolean {
    return code.toUpperCase() === 'MEX';
  }

  /**
   * Check if country code is USA
   */
  static isUSA(code: string): boolean {
    return code.toUpperCase() === 'USA';
  }

  /**
   * Check if country code is Canada
   */
  static isCanada(code: string): boolean {
    return code.toUpperCase() === 'CAN';
  }
}
