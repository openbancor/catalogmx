/**
 * SAT Carta Porte 3.0 - Tipo de Embalaje
 * UN packaging types
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { TipoEmbalaje } from '../../../types';

export class TipoEmbalajeCatalog {
  private static _data: TipoEmbalaje[] | null = null;

  private static getData(): TipoEmbalaje[] {
    if (!this._data) {
      this._data = loadCatalogObject<TipoEmbalaje>('sat/carta_porte_3/tipo_embalaje.json');
    }
    return this._data;
  }

  static getAll(): TipoEmbalaje[] {
    return this.getData();
  }

  static getEmbalaje(code: string): TipoEmbalaje | undefined {
    return this.getData().find((e) => e.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some((e) => e.code === code.toUpperCase());
  }

  /**
   * Get packaging description
   */
  static getDescription(code: string): string | undefined {
    return this.getEmbalaje(code)?.descripcion;
  }

  /**
   * Get UN category
   */
  static getCategoriaONU(code: string): string | undefined {
    return this.getEmbalaje(code)?.categoria_onu;
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): TipoEmbalaje[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((e) => e.descripcion.toUpperCase().includes(search));
  }

  /**
   * Get packaging types by UN category
   */
  static getByCategoriaONU(categoria: string): TipoEmbalaje[] {
    return this.getData().filter((e) =>
      e.categoria_onu.toUpperCase().includes(categoria.toUpperCase())
    );
  }

  /**
   * Check if packaging is for drums
   */
  static isDrum(code: string): boolean {
    const embalaje = this.getEmbalaje(code);
    return embalaje?.descripcion.toUpperCase().includes('TAMBOR') ?? false;
  }

  /**
   * Check if packaging is for boxes
   */
  static isBox(code: string): boolean {
    const embalaje = this.getEmbalaje(code);
    const desc = embalaje?.descripcion.toUpperCase() ?? '';
    return desc.includes('CAJA') || desc.includes('BOX');
  }

  /**
   * Check if packaging is for bags
   */
  static isBag(code: string): boolean {
    const embalaje = this.getEmbalaje(code);
    const desc = embalaje?.descripcion.toUpperCase() ?? '';
    return desc.includes('SACO') || desc.includes('BOLSA');
  }

  /**
   * Check if packaging is rigid
   */
  static isRigid(code: string): boolean {
    const embalaje = this.getEmbalaje(code);
    const desc = embalaje?.descripcion.toUpperCase() ?? '';
    return desc.includes('RIGID') || desc.includes('TAMBOR') || desc.includes('BIDON');
  }

  /**
   * Check if packaging is flexible
   */
  static isFlexible(code: string): boolean {
    const embalaje = this.getEmbalaje(code);
    const desc = embalaje?.descripcion.toUpperCase() ?? '';
    return desc.includes('FLEX') || desc.includes('SACO') || desc.includes('BOLSA');
  }
}
