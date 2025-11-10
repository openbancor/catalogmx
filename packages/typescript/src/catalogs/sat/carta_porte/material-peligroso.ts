/**
 * SAT Carta Porte 3.0 - Material Peligroso
 * UN hazardous materials (HAZMAT) catalog
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { MaterialPeligroso } from '../../../types';

export class MaterialPeligrosoCatalog {
  private static _data: MaterialPeligroso[] | null = null;

  private static getData(): MaterialPeligroso[] {
    if (!this._data) {
      this._data = loadCatalogObject<MaterialPeligroso>(
        'sat/carta_porte_3/material_peligroso.json'
      );
    }
    return this._data;
  }

  static getAll(): MaterialPeligroso[] {
    return this.getData();
  }

  static getMaterial(code: string): MaterialPeligroso | undefined {
    return this.getData().find((m) => m.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some((m) => m.code === code.toUpperCase());
  }

  /**
   * Get material description
   */
  static getDescription(code: string): string | undefined {
    return this.getMaterial(code)?.descripcion;
  }

  /**
   * Get UN risk class
   */
  static getClaseRiesgo(code: string): string | undefined {
    return this.getMaterial(code)?.clase_riesgo;
  }

  /**
   * Get risk division
   */
  static getClaseDivision(code: string): string | undefined {
    return this.getMaterial(code)?.clase_division;
  }

  /**
   * Get packing group
   */
  static getGrupoEmbalaje(code: string): string | undefined {
    return this.getMaterial(code)?.grupo_embalaje;
  }

  /**
   * Search materials by description
   */
  static searchByDescription(keyword: string): MaterialPeligroso[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((m) => m.descripcion.toUpperCase().includes(search));
  }

  /**
   * Get materials by risk class
   */
  static getByClaseRiesgo(clase: string): MaterialPeligroso[] {
    return this.getData().filter((m) => m.clase_riesgo === clase);
  }

  /**
   * Check if material is explosive (Class 1)
   */
  static isExplosive(code: string): boolean {
    const material = this.getMaterial(code);
    return material?.clase_riesgo === '1';
  }

  /**
   * Check if material is flammable (Class 2 or 3)
   */
  static isFlammable(code: string): boolean {
    const material = this.getMaterial(code);
    return material?.clase_riesgo === '2' || material?.clase_riesgo === '3';
  }

  /**
   * Check if material is toxic (Class 6)
   */
  static isToxic(code: string): boolean {
    const material = this.getMaterial(code);
    return material?.clase_riesgo === '6';
  }

  /**
   * Check if material is corrosive (Class 8)
   */
  static isCorrosive(code: string): boolean {
    const material = this.getMaterial(code);
    return material?.clase_riesgo === '8';
  }

  /**
   * Get materials by packing group
   */
  static getByGrupoEmbalaje(grupo: string): MaterialPeligroso[] {
    return this.getData().filter((m) => m.grupo_embalaje === grupo);
  }

  /**
   * Check if material requires high-level packing (Group I)
   */
  static requiresGroupI(code: string): boolean {
    const material = this.getMaterial(code);
    return material?.grupo_embalaje === 'I';
  }
}
