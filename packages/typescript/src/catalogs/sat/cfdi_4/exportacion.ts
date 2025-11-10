/**
 * SAT CFDI 4.0 - Exportación Catalog
 * Export keys
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { Exportacion } from '../../../types';

export class ExportacionCatalog {
  private static _data: Exportacion[] | null = null;

  private static getData(): Exportacion[] {
    if (!this._data) {
      this._data = loadCatalogObject<Exportacion>('sat/cfdi_4.0/exportacion.json');
    }
    return this._data;
  }

  static getAll(): Exportacion[] {
    return this.getData();
  }

  static getExportacion(code: string): Exportacion | undefined {
    return this.getData().find(e => e.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(e => e.code === code);
  }

  /**
   * Check if it's not for export
   */
  static isNoAplicaExportacion(code: string): boolean {
    return code === '01';
  }

  /**
   * Check if it's definitive export
   */
  static isExportacionDefinitiva(code: string): boolean {
    return code === '02';
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getExportacion(code)?.description;
  }
}
