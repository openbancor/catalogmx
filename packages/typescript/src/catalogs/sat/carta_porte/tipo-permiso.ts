/**
 * SAT Carta Porte 3.0 - Tipo de Permiso
 * SCT transport permit types
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { TipoPermiso } from '../../../types';

export class TipoPermisoCatalog {
  private static _data: TipoPermiso[] | null = null;

  private static getData(): TipoPermiso[] {
    if (!this._data) {
      this._data = loadCatalogObject<TipoPermiso>('sat/carta_porte_3/tipo_permiso.json');
    }
    return this._data;
  }

  static getAll(): TipoPermiso[] {
    return this.getData();
  }

  static getPermiso(code: string): TipoPermiso | undefined {
    return this.getData().find(p => p.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some(p => p.code === code.toUpperCase());
  }

  /**
   * Get permits by transport type
   */
  static getByTipoTransporte(tipo: string): TipoPermiso[] {
    const search = tipo.toUpperCase();
    return this.getData().filter(p =>
      p.tipo_transporte.toUpperCase().includes(search)
    );
  }

  /**
   * Check if permit is for cargo transport
   */
  static isCargaPermit(code: string): boolean {
    const permiso = this.getPermiso(code);
    return permiso?.tipo_transporte.toUpperCase().includes('CARGA') ?? false;
  }

  /**
   * Check if permit is for passenger transport
   */
  static isPasajeroPermit(code: string): boolean {
    const permiso = this.getPermiso(code);
    return permiso?.tipo_transporte.toUpperCase().includes('PASAJERO') ?? false;
  }

  /**
   * Search permits by description
   */
  static searchByDescription(keyword: string): TipoPermiso[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(p =>
      p.descripcion.toUpperCase().includes(search)
    );
  }
}
