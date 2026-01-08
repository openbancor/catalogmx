/**
 * Giros Mercantiles Catalog
 * Common business types in Mexico for commercial licenses and registrations
 */

import { loadCatalogData } from '../../utils/catalog-loader';

export interface CategoriaGiro {
  id: string;
  nombre: string;
  descripcion: string;
}

export interface GiroMercantil {
  id: string;
  nombre: string;
  categoria: string;
  requiere_licencia_alcohol: boolean;
}

interface GirosMercantilesData {
  _meta: {
    description: string;
    source: string;
    updated: string;
    uso: string;
  };
  categorias: CategoriaGiro[];
  giros: GiroMercantil[];
}

/**
 * Giros Mercantiles Catalog
 * Provides access to common business types for licensing
 */
export class GirosMercantilesCatalog {
  private static _data: GirosMercantilesData | null = null;
  private static _byId: Map<string, GiroMercantil> | null = null;
  private static _categoriasById: Map<string, CategoriaGiro> | null = null;

  private static loadData(): void {
    if (this._data !== null) return;
    this._data = loadCatalogData<GirosMercantilesData>('mexico/giros_mercantiles.json');
    this._byId = new Map(this._data.giros.map((g) => [g.id, g]));
    this._categoriasById = new Map(this._data.categorias.map((c) => [c.id, c]));
  }

  /**
   * Get all business types
   */
  static getAll(): GiroMercantil[] {
    this.loadData();
    return [...this._data!.giros];
  }

  /**
   * Get all categories
   */
  static getAllCategorias(): CategoriaGiro[] {
    this.loadData();
    return [...this._data!.categorias];
  }

  /**
   * Get business type by ID
   */
  static getById(id: string): GiroMercantil | undefined {
    this.loadData();
    return this._byId!.get(id);
  }

  /**
   * Get category by ID
   */
  static getCategoriaById(id: string): CategoriaGiro | undefined {
    this.loadData();
    return this._categoriasById!.get(id);
  }

  /**
   * Validate if a business type ID exists
   */
  static isValid(id: string): boolean {
    return this.getById(id) !== undefined;
  }

  /**
   * Search business types by name
   */
  static search(query: string): GiroMercantil[] {
    this.loadData();
    const queryLower = query.toLowerCase();
    return this._data!.giros.filter((g) => g.nombre.toLowerCase().includes(queryLower));
  }

  /**
   * Get business types by category
   */
  static getByCategoria(categoriaId: string): GiroMercantil[] {
    this.loadData();
    return this._data!.giros.filter((g) => g.categoria === categoriaId);
  }

  /**
   * Get business types that require alcohol license
   */
  static getRequierenLicenciaAlcohol(): GiroMercantil[] {
    this.loadData();
    return this._data!.giros.filter((g) => g.requiere_licencia_alcohol);
  }

  /**
   * Get total count of business types
   */
  static get count(): number {
    this.loadData();
    return this._data!.giros.length;
  }

  /**
   * Get total count of categories
   */
  static get categoriasCount(): number {
    this.loadData();
    return this._data!.categorias.length;
  }
}
