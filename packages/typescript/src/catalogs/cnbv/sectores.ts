/**
 * CNBV Sectores Catalog
 * Financial sectors regulated by CNBV (Comisión Nacional Bancaria y de Valores)
 */

import { loadCatalogData } from '../../utils/catalog-loader';

export interface SectorCNBV {
  id: string;
  nombre: string;
  descripcion: string;
  regulador_principal: string;
  ley_aplicable: string;
  ejemplos: string[];
}

export interface ReguladorFinanciero {
  id: string;
  nombre: string;
  siglas: string;
  descripcion: string;
  sitio_web: string;
}

interface CNBVData {
  _meta: {
    description: string;
    source: string;
    updated: string;
  };
  sectores: SectorCNBV[];
  reguladores: ReguladorFinanciero[];
}

/**
 * CNBV Sectores Catalog
 * Provides access to Mexican financial sectors and their regulators
 */
export class SectoresCNBVCatalog {
  private static _data: CNBVData | null = null;
  private static _byId: Map<string, SectorCNBV> | null = null;
  private static _reguladoresById: Map<string, ReguladorFinanciero> | null = null;

  private static loadData(): void {
    if (this._data !== null) return;
    this._data = loadCatalogData<CNBVData>('cnbv/sectores.json');
    this._byId = new Map(this._data.sectores.map((s) => [s.id, s]));
    this._reguladoresById = new Map(this._data.reguladores.map((r) => [r.id, r]));
  }

  /**
   * Get all financial sectors
   */
  static getAll(): SectorCNBV[] {
    this.loadData();
    return [...this._data!.sectores];
  }

  /**
   * Get all regulators
   */
  static getAllReguladores(): ReguladorFinanciero[] {
    this.loadData();
    return [...this._data!.reguladores];
  }

  /**
   * Get sector by ID
   */
  static getById(id: string): SectorCNBV | undefined {
    this.loadData();
    return this._byId!.get(id);
  }

  /**
   * Get regulator by ID
   */
  static getReguladorById(id: string): ReguladorFinanciero | undefined {
    this.loadData();
    return this._reguladoresById!.get(id);
  }

  /**
   * Validate if a sector ID exists
   */
  static isValid(id: string): boolean {
    return this.getById(id) !== undefined;
  }

  /**
   * Search sectors by name
   */
  static search(query: string): SectorCNBV[] {
    this.loadData();
    const queryLower = query.toLowerCase();
    return this._data!.sectores.filter(
      (s) =>
        s.nombre.toLowerCase().includes(queryLower) ||
        s.descripcion.toLowerCase().includes(queryLower)
    );
  }

  /**
   * Get sectors by regulator
   */
  static getByRegulador(reguladorId: string): SectorCNBV[] {
    this.loadData();
    return this._data!.sectores.filter((s) => s.regulador_principal === reguladorId);
  }

  /**
   * Get total count of sectors
   */
  static get count(): number {
    this.loadData();
    return this._data!.sectores.length;
  }
}
