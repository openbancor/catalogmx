/**
 * INEGI - Mexican States Catalog
 * Official catalog of Mexican states with INEGI and CURP codes
 */

import { loadCatalogArray } from '../../utils/catalog-loader';
import type { State } from '../../types';

export class StateCatalog {
  private static _data: State[] | null = null;

  /**
   * Load states data (lazy loading with caching)
   */
  private static getData(): State[] {
    if (!this._data) {
      this._data = loadCatalogArray<State>('inegi/states.json');
    }
    return this._data;
  }

  /**
   * Get all states
   */
  static getAll(): State[] {
    return this.getData();
  }

  /**
   * Get state by CURP code
   */
  static getStateByCode(code: string): State | undefined {
    return this.getData().find(state => state.code === code.toUpperCase());
  }

  /**
   * Get state by INEGI code
   */
  static getStateByInegi(claveInegi: string): State | undefined {
    return this.getData().find(state => state.clave_inegi === claveInegi);
  }

  /**
   * Get state by name (case-insensitive)
   */
  static getStateByName(name: string): State | undefined {
    const searchName = name.toUpperCase();
    return this.getData().find(state =>
      state.name.toUpperCase() === searchName
    );
  }

  /**
   * Search states by keyword
   */
  static searchStates(keyword: string): State[] {
    const searchTerm = keyword.toUpperCase();
    return this.getData().filter(state =>
      state.name.toUpperCase().includes(searchTerm) ||
      state.abreviatura.toUpperCase().includes(searchTerm)
    );
  }

  /**
   * Get state name by CURP code
   */
  static getStateName(code: string): string | undefined {
    return this.getStateByCode(code)?.name;
  }

  /**
   * Get CURP code by state name
   */
  static getCurpCode(stateName: string): string | undefined {
    return this.getStateByName(stateName)?.code;
  }

  /**
   * Validate state code
   */
  static isValidCode(code: string): boolean {
    return this.getData().some(state => state.code === code.toUpperCase());
  }
}
