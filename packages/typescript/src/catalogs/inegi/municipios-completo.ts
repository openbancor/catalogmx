/**
 * INEGI - Complete Mexican Municipalities Catalog
 * All 2,469 municipalities (2,462 municipios + 7 alcaldías CDMX)
 */

import { loadCatalog } from '../../utils/catalog-loader';
import type { Municipality } from '../../types';

export class MunicipiosCompletoCatalog {
  private static _data: Municipality[] | null = null;

  /**
   * Load complete municipalities data (lazy loading with caching)
   * WARNING: This loads all 2,469 municipalities into memory
   */
  private static getData(): Municipality[] {
    if (!this._data) {
      this._data = loadCatalog<Municipality>('inegi/municipios_completo.json');
    }
    return this._data;
  }

  /**
   * Get all municipalities (2,469 total)
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
   * Search municipalities by name (case-insensitive)
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
   * Get count of municipalities by state
   */
  static getCountByEntidad(cveEntidad: string): number {
    return this.getByEntidad(cveEntidad).length;
  }

  /**
   * Validate municipality code
   */
  static isValid(cveCompleta: string): boolean {
    return this.getData().some(mun => mun.cve_completa === cveCompleta);
  }

  /**
   * Get total count of municipalities
   */
  static getTotalCount(): number {
    return this.getData().length;
  }

  /**
   * Get all unique states
   */
  static getUniqueStates(): Array<{ cve_entidad: string; nom_entidad: string }> {
    const statesMap = new Map<string, string>();
    this.getData().forEach(mun => {
      if (!statesMap.has(mun.cve_entidad)) {
        statesMap.set(mun.cve_entidad, mun.nom_entidad);
      }
    });

    return Array.from(statesMap.entries()).map(([cve_entidad, nom_entidad]) => ({
      cve_entidad,
      nom_entidad
    }));
  }

  /**
   * Search municipalities across all fields
   */
  static searchAll(keyword: string): Municipality[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(mun =>
      mun.nom_municipio.toUpperCase().includes(search) ||
      mun.nom_entidad.toUpperCase().includes(search) ||
      mun.cve_completa.includes(search) ||
      mun.cve_municipio.includes(search)
    );
  }
}
