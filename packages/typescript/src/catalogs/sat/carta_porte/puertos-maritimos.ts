/**
 * SAT Carta Porte 3.0 - Puertos Marítimos
 * Mexican seaports and maritime authorization
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { PuertoMaritimo } from '../../../types';

export class PuertosMaritimos {
  private static _data: PuertoMaritimo[] | null = null;

  private static getData(): PuertoMaritimo[] {
    if (!this._data) {
      this._data = loadCatalogObject<PuertoMaritimo>('sat/carta_porte_3/puertos_maritimos.json');
    }
    return this._data;
  }

  static getAll(): PuertoMaritimo[] {
    return this.getData();
  }

  static getPuerto(code: string): PuertoMaritimo | undefined {
    return this.getData().find(p => p.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(p => p.code === code);
  }

  /**
   * Get ports by coast
   */
  static getByCoast(coast: string): PuertoMaritimo[] {
    return this.getData().filter(p => p.coast.toUpperCase().includes(coast.toUpperCase()));
  }

  /**
   * Get ports by state
   */
  static getByEstado(estado: string): PuertoMaritimo[] {
    const search = estado.toUpperCase();
    return this.getData().filter(p => p.estado.toUpperCase().includes(search));
  }

  /**
   * Search ports by name
   */
  static searchByName(keyword: string): PuertoMaritimo[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(p =>
      p.name.toUpperCase().includes(search)
    );
  }

  /**
   * Get Pacific coast ports
   */
  static getPacificPorts(): PuertoMaritimo[] {
    return this.getData().filter(p =>
      p.coast.toUpperCase().includes('PACIF')
    );
  }

  /**
   * Get Gulf of Mexico ports
   */
  static getGulfPorts(): PuertoMaritimo[] {
    return this.getData().filter(p =>
      p.coast.toUpperCase().includes('GOLFO')
    );
  }
}
