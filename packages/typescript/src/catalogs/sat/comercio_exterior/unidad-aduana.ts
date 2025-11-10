/**
 * SAT Comercio Exterior - Unidades de Aduana
 * Customs measurement units
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { UnidadAduana } from '../../../types';

export class UnidadAduanaCatalog {
  private static _data: UnidadAduana[] | null = null;

  private static getData(): UnidadAduana[] {
    if (!this._data) {
      this._data = loadCatalogObject<UnidadAduana>('sat/comercio_exterior/unidades_aduana.json');
    }
    return this._data;
  }

  static getAll(): UnidadAduana[] {
    return this.getData();
  }

  static getUnidad(code: string): UnidadAduana | undefined {
    return this.getData().find(u => u.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some(u => u.code === code.toUpperCase());
  }

  /**
   * Get unit name
   */
  static getName(code: string): string | undefined {
    return this.getUnidad(code)?.name;
  }

  /**
   * Get unit description
   */
  static getDescription(code: string): string | undefined {
    return this.getUnidad(code)?.descripcion;
  }

  /**
   * Search units by name or description
   */
  static searchByName(keyword: string): UnidadAduana[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(u =>
      u.name.toUpperCase().includes(search) ||
      u.descripcion.toUpperCase().includes(search)
    );
  }

  /**
   * Check if unit is for weight
   */
  static isWeightUnit(code: string): boolean {
    const unidad = this.getUnidad(code);
    if (!unidad) return false;
    const desc = unidad.descripcion.toUpperCase();
    return desc.includes('KILO') || desc.includes('GRAM') || desc.includes('TON') || desc.includes('LIBRA');
  }

  /**
   * Check if unit is for volume
   */
  static isVolumeUnit(code: string): boolean {
    const unidad = this.getUnidad(code);
    if (!unidad) return false;
    const desc = unidad.descripcion.toUpperCase();
    return desc.includes('LITR') || desc.includes('METR') || desc.includes('GALON');
  }

  /**
   * Check if unit is for length
   */
  static isLengthUnit(code: string): boolean {
    const unidad = this.getUnidad(code);
    if (!unidad) return false;
    const desc = unidad.descripcion.toUpperCase();
    return desc.includes('METR') && !desc.includes('CUBIC') && !desc.includes('CUADRAD');
  }

  /**
   * Check if unit is for pieces/units
   */
  static isPieceUnit(code: string): boolean {
    const unidad = this.getUnidad(code);
    if (!unidad) return false;
    const desc = unidad.descripcion.toUpperCase();
    return desc.includes('PIEZA') || desc.includes('UNIDAD') || desc.includes('PAR');
  }
}
