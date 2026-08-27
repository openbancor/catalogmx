/** SAT Nómina 1.2 - Tipo de Nómina. */

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
    return this.getTipo(code) !== undefined;
  }

  static isOrdinaria(code: string): boolean {
    return code === 'O' && this.isValid(code);
  }

  static isExtraordinaria(code: string): boolean {
    return code === 'E' && this.isValid(code);
  }
}
