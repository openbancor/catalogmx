/**
 * SAT Nómina 1.2 - Tipo de Jornada
 * Work shift types
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { TipoJornada } from '../../../types';

export class TipoJornadaCatalog {
  private static _data: TipoJornada[] | null = null;

  private static getData(): TipoJornada[] {
    if (!this._data) {
      this._data = loadCatalog<TipoJornada>('sat/nomina_1.2/tipo_jornada.json');
    }
    return this._data;
  }

  static getAll(): TipoJornada[] {
    return this.getData();
  }

  static getJornada(code: string): TipoJornada | undefined {
    return this.getData().find(j => j.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(j => j.code === code);
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): TipoJornada[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(j =>
      j.descripcion.toUpperCase().includes(search)
    );
  }

  /**
   * Check if it's day shift
   */
  static isDiurna(code: string): boolean {
    const jornada = this.getJornada(code);
    return jornada?.descripcion.toUpperCase().includes('DIURNA') ?? false;
  }

  /**
   * Check if it's night shift
   */
  static isNocturna(code: string): boolean {
    const jornada = this.getJornada(code);
    return jornada?.descripcion.toUpperCase().includes('NOCTURNA') ?? false;
  }

  /**
   * Check if it's mixed shift
   */
  static isMixta(code: string): boolean {
    const jornada = this.getJornada(code);
    return jornada?.descripcion.toUpperCase().includes('MIXTA') ?? false;
  }
}
