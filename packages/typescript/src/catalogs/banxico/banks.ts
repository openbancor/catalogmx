/**
 * Banxico - Mexican Banks Catalog
 * Official catalog of Mexican banks with SPEI participation status
 */

import { loadCatalogArray } from '../../utils/catalog-loader';
import type { Bank } from '../../types';

export class BankCatalog {
  private static _data: Bank[] | null = null;

  /**
   * Load banks data (lazy loading with caching)
   */
  private static getData(): Bank[] {
    if (this._data === null) {
      this._data = loadCatalogArray<Bank>('banxico/banks.json');
    }
    return this._data;
  }

  /**
   * Get all banks
   */
  static getAll(): Bank[] {
    return this.getData();
  }

  /**
   * Get bank by code
   */
  static getBankByCode(code: string): Bank | undefined {
    return this.getData().find((bank) => bank.code === code);
  }

  /**
   * Get bank by its 3-digit CLABE code (alias of getBankByCode).
   * Historical (disaffiliated) banks are returned too, with status 'historical'.
   */
  static getBankByClabeCode(code: string): Bank | undefined {
    return this.getBankByCode(code);
  }

  /**
   * Get bank by its 5-digit SPEI participant code (e.g. '40012').
   * BANXICO itself uses the official 4-digit key '2001'.
   */
  static getBankBySpeiCode(speiCode: string): Bank | undefined {
    return this.getData().find((bank) => bank.spei_code === speiCode);
  }

  /**
   * Validate an SPEI participant code and, optionally, that its last 3 digits
   * equal the CLABE bank code.
   */
  static validateSpeiCode(speiCode: string, code?: string): boolean {
    const bank = this.getBankBySpeiCode(speiCode);
    if (bank === undefined) return false;
    if (code === undefined) return true;
    const padded = code.padStart(3, '0');
    return bank.code === padded && speiCode.slice(-3) === padded;
  }

  /**
   * Get bank by name (case-insensitive search)
   */
  static getBankByName(name: string): Bank | undefined {
    const searchName = name.toUpperCase();
    return this.getData().find(
      (bank) =>
        bank.name.toUpperCase().includes(searchName) ||
        bank.short_name?.toUpperCase().includes(searchName) ||
        bank.full_name?.toUpperCase().includes(searchName)
    );
  }

  /**
   * Search banks by keyword
   */
  static searchBanks(keyword: string): Bank[] {
    const searchTerm = keyword.toUpperCase();
    return this.getData().filter(
      (bank) =>
        bank.name.toUpperCase().includes(searchTerm) ||
        bank.short_name?.toUpperCase().includes(searchTerm) ||
        bank.full_name?.toUpperCase().includes(searchTerm) ||
        bank.code.includes(searchTerm)
    );
  }

  /**
   * Get banks with SPEI support. Historical (disaffiliated) rows are never
   * listed by default, whatever their spei flag; they are only included when
   * includeHistorical is true.
   */
  static getSPEIBanks(includeHistorical = false): Bank[] {
    return this.getData().filter((bank) =>
      bank.status === 'historical' ? includeHistorical : bank.spei === true
    );
  }

  /**
   * Check if a bank code is valid
   */
  static isValidCode(code: string): boolean {
    return this.getData().some((bank) => bank.code === code);
  }

  /**
   * Check if a bank supports SPEI
   */
  static supportsSPEI(code: string): boolean {
    const bank = this.getBankByCode(code);
    return bank?.spei === true;
  }
}
