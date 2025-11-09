/**
 * SEPOMEX - Complete Mexican Postal Codes Catalog
 * All ~150,000 postal codes
 *
 * WARNING: This catalog is very large and should be used with caution.
 * Consider using pagination or filters when displaying results.
 */

import { loadCatalog } from '../../utils/catalog-loader';
import type { PostalCode } from '../../types';

export class CodigosPostalesCompleto {
  private static _data: PostalCode[] | null = null;

  /**
   * Load complete postal codes data (lazy loading with caching)
   * WARNING: This loads ~150,000 postal codes into memory (~15-20 MB)
   */
  private static getData(): PostalCode[] {
    if (!this._data) {
      this._data = loadCatalog<PostalCode>('sepomex/codigos_postales_completo.json');
    }
    return this._data;
  }

  /**
   * Get all postal codes (~150,000 records)
   * WARNING: This returns a very large array
   */
  static getAll(): PostalCode[] {
    return this.getData();
  }

  /**
   * Get postal code information
   */
  static getByCp(cp: string): PostalCode[] {
    return this.getData().filter(postal => postal.cp === cp || postal.codigo_postal === cp);
  }

  /**
   * Get state name from postal code
   */
  static getEstado(cp: string): string | undefined {
    const postal = this.getData().find(p => p.cp === cp || p.codigo_postal === cp);
    return postal?.estado;
  }

  /**
   * Get municipality from postal code
   */
  static getMunicipio(cp: string): string | undefined {
    const postal = this.getData().find(p => p.cp === cp || p.codigo_postal === cp);
    return postal?.municipio;
  }

  /**
   * Search by municipality (returns paginated results)
   */
  static getByMunicipio(municipio: string, limit: number = 100): PostalCode[] {
    const searchTerm = municipio.toUpperCase();
    const results = this.getData().filter(postal =>
      postal.municipio.toUpperCase().includes(searchTerm)
    );
    return results.slice(0, limit);
  }

  /**
   * Search by state (returns paginated results)
   */
  static getByEstado(estado: string, limit: number = 1000): PostalCode[] {
    const searchTerm = estado.toUpperCase();
    const results = this.getData().filter(postal =>
      postal.estado.toUpperCase() === searchTerm
    );
    return results.slice(0, limit);
  }

  /**
   * Search by settlement (asentamiento) with pagination
   */
  static searchByAsentamiento(asentamiento: string, limit: number = 100): PostalCode[] {
    const searchTerm = asentamiento.toUpperCase();
    const results = this.getData().filter(postal =>
      postal.asentamiento.toUpperCase().includes(searchTerm)
    );
    return results.slice(0, limit);
  }

  /**
   * Validate postal code exists
   */
  static isValid(cp: string): boolean {
    return this.getData().some(postal => postal.cp === cp || postal.codigo_postal === cp);
  }

  /**
   * Get total count of postal codes
   */
  static getTotalCount(): number {
    return this.getData().length;
  }

  /**
   * Get all unique postal codes
   */
  static getUniqueCPs(): string[] {
    const cpsSet = new Set(this.getData().map(p => p.cp || p.codigo_postal!));
    return Array.from(cpsSet).sort();
  }

  /**
   * Get count of postal codes by state
   */
  static getCountByEstado(estado: string): number {
    const searchTerm = estado.toUpperCase();
    return this.getData().filter(postal =>
      postal.estado.toUpperCase() === searchTerm
    ).length;
  }

  /**
   * Get all settlements (asentamientos) for a postal code
   */
  static getAsentamientos(cp: string): string[] {
    return this.getData()
      .filter(postal => postal.codigo_postal === cp)
      .map(postal => postal.asentamiento);
  }

  /**
   * Search with multiple criteria (with pagination)
   */
  static search(criteria: {
    cp?: string;
    estado?: string;
    municipio?: string;
    asentamiento?: string;
    limit?: number;
  }): PostalCode[] {
    const limit = criteria.limit ?? 100;
    let results = this.getData();

    if (criteria.cp) {
      results = results.filter(p => p.codigo_postal === criteria.cp);
    }
    if (criteria.estado) {
      const estado = criteria.estado.toUpperCase();
      results = results.filter(p => p.estado.toUpperCase() === estado);
    }
    if (criteria.municipio) {
      const municipio = criteria.municipio.toUpperCase();
      results = results.filter(p => p.municipio.toUpperCase().includes(municipio));
    }
    if (criteria.asentamiento) {
      const asentamiento = criteria.asentamiento.toUpperCase();
      results = results.filter(p => p.asentamiento.toUpperCase().includes(asentamiento));
    }

    return results.slice(0, limit);
  }

  /**
   * Get statistics about the catalog
   */
  static getStatistics(): {
    totalPostalCodes: number;
    uniquePostalCodes: number;
    states: number;
    municipalities: number;
  } {
    const data = this.getData();
    const uniqueCPs = new Set(data.map(p => p.codigo_postal));
    const uniqueStates = new Set(data.map(p => p.estado));
    const uniqueMunicipalities = new Set(data.map(p => `${p.estado}:${p.municipio}`));

    return {
      totalPostalCodes: data.length,
      uniquePostalCodes: uniqueCPs.size,
      states: uniqueStates.size,
      municipalities: uniqueMunicipalities.size
    };
  }
}
