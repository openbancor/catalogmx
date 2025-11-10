/**
 * SAT Carta Porte 3.0 - Aeropuertos
 * Mexican airports with IATA and ICAO codes
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { Aeropuerto } from '../../../types';

export class AeropuertosCatalog {
  private static _data: Aeropuerto[] | null = null;

  private static getData(): Aeropuerto[] {
    if (!this._data) {
      this._data = loadCatalogObject<Aeropuerto>('sat/carta_porte_3/aeropuertos.json');
    }
    return this._data;
  }

  static getAll(): Aeropuerto[] {
    return this.getData();
  }

  static getByCode(code: string): Aeropuerto | undefined {
    return this.getData().find((a) => a.code === code.toUpperCase());
  }

  static getByIATA(iata: string): Aeropuerto | undefined {
    return this.getData().find((a) => a.iata === iata.toUpperCase());
  }

  static getByICAO(icao: string): Aeropuerto | undefined {
    return this.getData().find((a) => a.icao === icao.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some((a) => a.code === code.toUpperCase());
  }

  static isValidIATA(iata: string): boolean {
    return this.getData().some((a) => a.iata === iata.toUpperCase());
  }

  static isValidICAO(icao: string): boolean {
    return this.getData().some((a) => a.icao === icao.toUpperCase());
  }

  /**
   * Get airports by state
   */
  static getByEstado(estado: string): Aeropuerto[] {
    const search = estado.toUpperCase();
    return this.getData().filter((a) => a.estado.toUpperCase().includes(search));
  }

  /**
   * Get airports by city
   */
  static getByCiudad(ciudad: string): Aeropuerto[] {
    const search = ciudad.toUpperCase();
    return this.getData().filter((a) => a.ciudad.toUpperCase().includes(search));
  }

  /**
   * Search airports by name
   */
  static searchByName(keyword: string): Aeropuerto[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(
      (a) => a.name.toUpperCase().includes(search) || a.ciudad.toUpperCase().includes(search)
    );
  }
}
