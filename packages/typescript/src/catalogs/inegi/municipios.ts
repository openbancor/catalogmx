/**
 * INEGI - Mexican Municipalities Catalog
 * Catalog of Mexican municipalities with INEGI codes
 */

import { loadCatalog } from '../../utils/catalog-loader';
import type { Municipality } from '../../types';

export class MunicipiosCatalog {
  private static _data: Municipality[] | null = null;

  /**
   * Load municipalities data (lazy loading with caching)
   */
  private static getData(): Municipality[] {
    if (!this._data) {
      this._data = loadCatalog<Municipality>('inegi/municipios.json');
    }
    return this._data;
  }

  /**
   * Get all municipalities
   */
  static getAll(): Municipality[] {
    return this.getData();
  }

  /**
   * Get municipality by complete code (cve_completa)
   */
  static getMunicipio(cveCompleta: string): Municipality | undefined {
    return this.getData().find(mun => mun.cve_completa === cveCompleta);
  }

  /**
   * Get municipalities by state (cve_entidad)
   */
  static getByEntidad(cveEntidad: string): Municipality[] {
    return this.getData().filter(mun => mun.cve_entidad === cveEntidad);
  }

  /**
   * Search municipalities by name
   */
  static searchByName(name: string): Municipality[] {
    const searchTerm = name.toUpperCase();
    return this.getData().filter(mun =>
      mun.nom_municipio.toUpperCase().includes(searchTerm)
    );
  }

  /**
   * Get municipalities by state name
   */
  static getByStateName(stateName: string): Municipality[] {
    const searchTerm = stateName.toUpperCase();
    return this.getData().filter(mun =>
      mun.nom_entidad.toUpperCase() === searchTerm
    );
  }

  /**
   * Validate municipality code
   */
  static isValid(cveCompleta: string): boolean {
    return this.getData().some(mun => mun.cve_completa === cveCompleta);
  }
}
