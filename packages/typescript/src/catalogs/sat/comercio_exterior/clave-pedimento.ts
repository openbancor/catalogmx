/**
 * SAT Comercio Exterior - Clave de Pedimento Catalog
 * Customs document classification keys
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { ClavePedimento } from '../../../types';

export class ClavePedimentoCatalog {
  private static _data: ClavePedimento[] | null = null;

  private static getData(): ClavePedimento[] {
    if (!this._data) {
      this._data = loadCatalogObject<ClavePedimento>('sat/comercio_exterior/claves_pedimento.json');
    }
    return this._data;
  }

  static getAll(): ClavePedimento[] {
    return this.getData();
  }

  static getClave(clave: string): ClavePedimento | undefined {
    return this.getData().find((cp) => cp.clave === clave.toUpperCase());
  }

  static isValid(clave: string): boolean {
    return this.getData().some((cp) => cp.clave === clave.toUpperCase());
  }

  /**
   * Check if clave is for importation
   */
  static isImport(clave: string): boolean {
    const pedimento = this.getClave(clave);
    return pedimento?.tipo === 'importacion';
  }

  /**
   * Check if clave is for exportation
   */
  static isExport(clave: string): boolean {
    const pedimento = this.getClave(clave);
    return pedimento?.tipo === 'exportacion';
  }

  /**
   * Check if clave is for transit
   */
  static isTransit(clave: string): boolean {
    const pedimento = this.getClave(clave);
    return pedimento?.tipo === 'transito';
  }

  /**
   * Get all import claves
   */
  static getImportClaves(): ClavePedimento[] {
    return this.getData().filter((cp) => cp.tipo === 'importacion');
  }

  /**
   * Get all export claves
   */
  static getExportClaves(): ClavePedimento[] {
    return this.getData().filter((cp) => cp.tipo === 'exportacion');
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): ClavePedimento[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((cp) => cp.descripcion.toUpperCase().includes(search));
  }
}
