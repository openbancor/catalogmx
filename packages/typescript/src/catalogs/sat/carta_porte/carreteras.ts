/**
 * SAT Carta Porte 3.0 - Carreteras Federales
 * SCT federal highways
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { Carretera } from '../../../types';

export class CarreterasCatalog {
  private static _data: Carretera[] | null = null;

  private static getData(): Carretera[] {
    if (!this._data) {
      this._data = loadCatalogObject<Carretera>('sat/carta_porte_3/carreteras.json');
    }
    return this._data;
  }

  static getAll(): Carretera[] {
    return this.getData();
  }

  static getCarretera(code: string): Carretera | undefined {
    return this.getData().find((c) => c.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some((c) => c.code === code.toUpperCase());
  }

  /**
   * Get highway name
   */
  static getNombre(code: string): string | undefined {
    return this.getCarretera(code)?.nombre;
  }

  /**
   * Get origin point
   */
  static getOrigen(code: string): string | undefined {
    return this.getCarretera(code)?.origen;
  }

  /**
   * Get destination point
   */
  static getDestino(code: string): string | undefined {
    return this.getCarretera(code)?.destino;
  }

  /**
   * Get highway type
   */
  static getTipo(code: string): string | undefined {
    return this.getCarretera(code)?.tipo;
  }

  /**
   * Search highways by name
   */
  static searchByName(keyword: string): Carretera[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((c) => c.nombre.toUpperCase().includes(search));
  }

  /**
   * Search by origin or destination
   */
  static searchByRoute(keyword: string): Carretera[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(
      (c) => c.origen.toUpperCase().includes(search) || c.destino.toUpperCase().includes(search)
    );
  }

  /**
   * Get highways by type
   */
  static getByTipo(tipo: string): Carretera[] {
    const search = tipo.toUpperCase();
    return this.getData().filter((c) => c.tipo.toUpperCase().includes(search));
  }
}
