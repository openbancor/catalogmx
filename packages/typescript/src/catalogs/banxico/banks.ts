/**
 * Banxico - Mexican Banks Catalog
 * Official catalog of Mexican banks with SPEI participation status
 */

import { loadCatalog } from '../../utils/catalog-loader';
import type { Bank } from '../../types';

export class BankCatalog {
  private static _data: Bank[] | null = null;

  /**
   * Load banks data (lazy loading with caching)
   */
  private static getData(): Bank[] {
    if (!this._data) {
      this._data = loadCatalog<Bank>('banxico/banks.json');
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
    return this.getData().find(bank => bank.code === code);
  }

  /**
   * Get bank by name (case-insensitive search)
   */
  static getBankByName(name: string): Bank | undefined {
    const searchName = name.toUpperCase();
    return this.getData().find(bank =>
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
    return this.getData().filter(bank =>
      bank.name.toUpperCase().includes(searchTerm) ||
      bank.short_name?.toUpperCase().includes(searchTerm) ||
      bank.full_name?.toUpperCase().includes(searchTerm) ||
      bank.code.includes(searchTerm)
    );
  }

  /**
   * Get all banks with SPEI support
   */
  static getSPEIBanks(): Bank[] {
    return this.getData().filter(bank => bank.spei === true);
  }

  /**
   * Check if a bank code is valid
   */
  static isValidCode(code: string): boolean {
    return this.getData().some(bank => bank.code === code);
  }

  /**
   * Check if a bank supports SPEI
   */
  static supportsSPEI(code: string): boolean {
    const bank = this.getBankByCode(code);
    return bank?.spei === true;
  }
}
