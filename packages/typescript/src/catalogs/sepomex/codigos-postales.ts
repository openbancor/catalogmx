/**
 * SEPOMEX - Mexican Postal Codes Catalog
 * Official catalog of Mexican postal codes
 */

import { loadCatalog } from '../../utils/catalog-loader';
import type { PostalCode } from '../../types';

export class CodigosPostales {
  private static _data: PostalCode[] | null = null;

  /**
   * Load postal codes data (lazy loading with caching)
   */
  private static getData(): PostalCode[] {
    if (!this._data) {
      this._data = loadCatalog<PostalCode>('sepomex/codigos_postales.json');
    }
    return this._data;
  }

  /**
   * Get all postal codes
   */
  static getAll(): PostalCode[] {
    return this.getData();
  }

  /**
   * Get postal code information
   */
  static getByCp(cp: string): PostalCode[] {
    return this.getData().filter(postal => postal.codigo_postal === cp);
  }

  /**
   * Get state name from postal code
   */
  static getEstado(cp: string): string | undefined {
    const postal = this.getData().find(p => p.codigo_postal === cp);
    return postal?.estado;
  }

  /**
   * Get municipality from postal code
   */
  static getMunicipio(cp: string): string | undefined {
    const postal = this.getData().find(p => p.codigo_postal === cp);
    return postal?.municipio;
  }

  /**
   * Search by municipality
   */
  static getByMunicipio(municipio: string): PostalCode[] {
    const searchTerm = municipio.toUpperCase();
    return this.getData().filter(postal =>
      postal.municipio.toUpperCase().includes(searchTerm)
    );
  }

  /**
   * Search by state
   */
  static getByEstado(estado: string): PostalCode[] {
    const searchTerm = estado.toUpperCase();
    return this.getData().filter(postal =>
      postal.estado.toUpperCase() === searchTerm
    );
  }

  /**
   * Search by settlement (asentamiento)
   */
  static searchByAsentamiento(asentamiento: string): PostalCode[] {
    const searchTerm = asentamiento.toUpperCase();
    return this.getData().filter(postal =>
      postal.asentamiento.toUpperCase().includes(searchTerm)
    );
  }

  /**
   * Validate postal code exists
   */
  static isValid(cp: string): boolean {
    return this.getData().some(postal => postal.codigo_postal === cp);
  }
}
