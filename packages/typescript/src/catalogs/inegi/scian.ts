/**
 * SCIAN (Sistema de Clasificación Industrial de América del Norte) Catalog
 * Mexican economic sector classification based on INEGI's SCIAN
 */

import { loadCatalogData } from '../../utils/catalog-loader';

export interface SectorSCIAN {
  codigo: string;
  nombre: string;
  descripcion: string;
}

interface SCIANData {
  _meta: {
    description: string;
    source: string;
    updated: string;
  };
  sectores: SectorSCIAN[];
}

/**
 * SCIAN Catalog
 * Provides access to Mexican economic sector classification
 */
export class SCIANCatalog {
  private static _data: SCIANData | null = null;
  private static _byCodigo: Map<string, SectorSCIAN> | null = null;

  private static loadData(): void {
    if (this._data !== null) return;
    this._data = loadCatalogData<SCIANData>('inegi/scian/sectores.json');
    this._byCodigo = new Map(this._data.sectores.map((s) => [s.codigo, s]));
  }

  /**
   * Get all SCIAN sectors
   */
  static getAll(): SectorSCIAN[] {
    this.loadData();
    return [...this._data!.sectores];
  }

  /**
   * Get sector by code
   */
  static getByCodigo(codigo: string): SectorSCIAN | undefined {
    this.loadData();
    return this._byCodigo!.get(codigo);
  }

  /**
   * Validate if a code exists
   */
  static isValid(codigo: string): boolean {
    return this.getByCodigo(codigo) !== undefined;
  }

  /**
   * Search sectors by name or description
   */
  static search(query: string): SectorSCIAN[] {
    this.loadData();
    const queryLower = query.toLowerCase();
    return this._data!.sectores.filter(
      (s) =>
        s.nombre.toLowerCase().includes(queryLower) ||
        s.descripcion.toLowerCase().includes(queryLower)
    );
  }

  /**
   * Get sector for a SCIAN code (hierarchical lookup)
   * A full SCIAN code is 6 digits, first 2 are sector
   */
  static getSectorForCode(fullCode: string): SectorSCIAN | undefined {
    this.loadData();
    // Extract first 2 digits as sector code
    const sectorCode = fullCode.slice(0, 2);
    return this._byCodigo!.get(sectorCode);
  }

  /**
   * Get total count of sectors
   */
  static get count(): number {
    this.loadData();
    return this._data!.sectores.length;
  }
}
