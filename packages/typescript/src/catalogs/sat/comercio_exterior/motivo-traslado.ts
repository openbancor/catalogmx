/**
 * SAT Comercio Exterior - Motivos de Traslado
 * Transfer motives for CFDI type T
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { MotivoTraslado } from '../../../types';

export class MotivoTrasladoCatalog {
  private static _data: MotivoTraslado[] | null = null;

  private static getData(): MotivoTraslado[] {
    if (!this._data) {
      this._data = loadCatalog<MotivoTraslado>('sat/comercio_exterior/motivos_traslado.json');
    }
    return this._data;
  }

  static getAll(): MotivoTraslado[] {
    return this.getData();
  }

  static getMotivo(code: string): MotivoTraslado | undefined {
    return this.getData().find(m => m.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(m => m.code === code);
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getMotivo(code)?.descripcion;
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): MotivoTraslado[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(m =>
      m.descripcion.toUpperCase().includes(search)
    );
  }

  /**
   * Check if motive is for export
   */
  static isExportMotivo(code: string): boolean {
    const motivo = this.getMotivo(code);
    return motivo?.descripcion.toUpperCase().includes('EXPORTA') ?? false;
  }

  /**
   * Check if motive is for import
   */
  static isImportMotivo(code: string): boolean {
    const motivo = this.getMotivo(code);
    return motivo?.descripcion.toUpperCase().includes('IMPORTA') ?? false;
  }
}
