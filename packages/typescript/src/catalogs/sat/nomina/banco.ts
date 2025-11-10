/**
 * SAT Nómina 1.2 - Banco
 * Banks for payroll deposits
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { BancoNomina } from '../../../types';

export class BancoNominaCatalog {
  private static _data: BancoNomina[] | null = null;

  private static getData(): BancoNomina[] {
    if (!this._data) {
      this._data = loadCatalogObject<BancoNomina>('sat/nomina_1.2/banco.json');
    }
    return this._data;
  }

  static getAll(): BancoNomina[] {
    return this.getData();
  }

  static getBanco(code: string): BancoNomina | undefined {
    return this.getData().find((b) => b.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some((b) => b.code === code);
  }

  /**
   * Get bank name
   */
  static getName(code: string): string | undefined {
    return this.getBanco(code)?.name;
  }

  /**
   * Get bank legal name (razón social)
   */
  static getRazonSocial(code: string): string | undefined {
    return this.getBanco(code)?.razon_social;
  }

  /**
   * Search banks by name
   */
  static searchByName(keyword: string): BancoNomina[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(
      (b) => b.name.toUpperCase().includes(search) || b.razon_social.toUpperCase().includes(search)
    );
  }
}
