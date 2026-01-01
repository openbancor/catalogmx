/**
 * SEPOMEX - Mexican Postal Codes Catalog
 * Official catalog of Mexican postal codes
 */

import { loadCatalogArray } from '../../utils/catalog-loader';
import { normalizeText } from '../../utils/text';
import type { PostalCode } from '../../types';

export class CodigosPostales {
  private static _data: PostalCode[] | null = null;

  /**
   * Load postal codes data (lazy loading with caching)
   */
  private static getData(): PostalCode[] {
    if (!this._data) {
      this._data = loadCatalogArray<PostalCode>('sepomex/codigos_postales.json');
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
    return this.getData().filter((postal) => postal.cp === cp || postal.codigo_postal === cp);
  }

  /**
   * Get state name from postal code
   */
  static getEstado(cp: string): string | undefined {
    const postal = this.getData().find((p) => p.cp === cp || p.codigo_postal === cp);
    return postal?.estado;
  }

  /**
   * Get municipality from postal code
   */
  static getMunicipio(cp: string): string | undefined {
    const postal = this.getData().find((p) => p.cp === cp || p.codigo_postal === cp);
    return postal?.municipio;
  }

  /**
   * Search by municipality (accent-insensitive)
   */
  static getByMunicipio(municipio: string): PostalCode[] {
    const searchTerm = normalizeText(municipio);
    return this.getData().filter((postal) => normalizeText(postal.municipio).includes(searchTerm));
  }

  /**
   * Search by state (accent-insensitive)
   */
  static getByEstado(estado: string): PostalCode[] {
    const searchTerm = normalizeText(estado);
    return this.getData().filter((postal) => normalizeText(postal.estado) === searchTerm);
  }

  /**
   * Search by settlement (asentamiento) - accent-insensitive
   *
   * Example: searchByAsentamiento("Aguilas") will find "Las Águilas"
   */
  static searchByAsentamiento(asentamiento: string): PostalCode[] {
    const searchTerm = normalizeText(asentamiento);
    return this.getData().filter((postal) =>
      normalizeText(postal.asentamiento).includes(searchTerm)
    );
  }

  /**
   * Validate postal code exists
   */
  static isValid(cp: string): boolean {
    return this.getData().some((postal) => postal.cp === cp || postal.codigo_postal === cp);
  }
}
