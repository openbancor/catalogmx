/**
 * SAT Comercio Exterior - Estados USA y Canadá
 * US States and Canadian Provinces (ISO 3166-2)
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { EstadoUSACanada } from '../../../types';

export class EstadoCatalog {
  private static _data: EstadoUSACanada[] | null = null;

  private static getData(): EstadoUSACanada[] {
    if (!this._data) {
      this._data = loadCatalog<EstadoUSACanada>('sat/comercio_exterior/estados_usa_canada.json');
    }
    return this._data;
  }

  static getAll(): EstadoUSACanada[] {
    return this.getData();
  }

  static getEstado(code: string): EstadoUSACanada | undefined {
    return this.getData().find(e => e.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some(e => e.code === code.toUpperCase());
  }

  /**
   * Get US states only
   */
  static getEstadosUSA(): EstadoUSACanada[] {
    return this.getData().filter(e => e.country === 'USA');
  }

  /**
   * Get Canadian provinces only
   */
  static getProvinciasCanada(): EstadoUSACanada[] {
    return this.getData().filter(e => e.country === 'CAN');
  }

  /**
   * Get estado by code (USA specific)
   */
  static getEstadoUsa(code: string): EstadoUSACanada | undefined {
    const estado = this.getEstado(code);
    return estado?.country === 'USA' ? estado : undefined;
  }

  /**
   * Get provincia by code (Canada specific)
   */
  static getProvinciaCanada(code: string): EstadoUSACanada | undefined {
    const estado = this.getEstado(code);
    return estado?.country === 'CAN' ? estado : undefined;
  }

  /**
   * Check if code is valid for USA
   */
  static isValidUSA(code: string): boolean {
    const estado = this.getEstado(code);
    return estado?.country === 'USA';
  }

  /**
   * Check if code is valid for Canada
   */
  static isValidCanada(code: string): boolean {
    const estado = this.getEstado(code);
    return estado?.country === 'CAN';
  }

  /**
   * Validate estado for specific country
   */
  static isValidForCountry(code: string, country: 'USA' | 'CAN'): boolean {
    const estado = this.getEstado(code);
    return estado?.country === country;
  }
}
