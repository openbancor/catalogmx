/**
 * SAT Nómina 1.2 - Tipo de Jornada
 * Work shift types
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { TipoJornada } from '../../../types';

export class TipoJornadaCatalog {
  private static _data: TipoJornada[] | null = null;

  private static getData(): TipoJornada[] {
    if (!this._data) {
      this._data = loadCatalogObject<TipoJornada>('sat/nomina_1.2/tipo_jornada.json');
    }
    return this._data;
  }

  static getAll(): TipoJornada[] {
    return this.getData();
  }

  static getJornada(code: string): TipoJornada | undefined {
    return this.getData().find((j) => j.code === code);
  }

  static getByCode(code: string): TipoJornada | undefined {
    return this.getJornada(code);
  }

  static isValid(code: string): boolean {
    return this.getData().some((j) => j.code === code);
  }

  static searchByDescription(keyword: string): TipoJornada[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((j) => j.descripcion.toUpperCase().includes(search));
  }

  static isDiurna(code: string): boolean {
    const jornada = this.getJornada(code);
    return jornada?.descripcion.toUpperCase().includes('DIURNA') ?? false;
  }

  static isNocturna(code: string): boolean {
    const jornada = this.getJornada(code);
    return jornada?.descripcion.toUpperCase().includes('NOCTURNA') ?? false;
  }

  static isMixta(code: string): boolean {
    const jornada = this.getJornada(code);
    return jornada?.descripcion.toUpperCase().includes('MIXTA') ?? false;
  }
}
