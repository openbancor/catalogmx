/**
 * SAT Comercio Exterior - Registro de Identificación Tributaria
 * Foreign tax ID types with regex validation patterns
 */

import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { RegistroIdentTrib } from '../../../types';

export class RegistroIdentTribCatalog {
  private static _data: RegistroIdentTrib[] | null = null;

  private static getData(): RegistroIdentTrib[] {
    if (!this._data) {
      this._data = loadCatalogObject<RegistroIdentTrib>(
        'sat/comercio_exterior/registro_ident_trib.json'
      );
    }
    return this._data;
  }

  static getAll(): RegistroIdentTrib[] {
    return this.getData();
  }

  static getRegistro(code: string): RegistroIdentTrib | undefined {
    return this.getData().find((r) => r.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some((r) => r.code === code);
  }

  /**
   * Get registro by country code
   */
  static getByPais(paisCode: string): RegistroIdentTrib[] {
    return this.getData().filter((r) => r.pais === paisCode.toUpperCase());
  }

  /**
   * Validate foreign tax ID format using regex pattern
   */
  static validateTaxId(registroCode: string, taxId: string): boolean {
    const registro = this.getRegistro(registroCode);
    if (!registro || !registro.regex_pattern) return true; // No pattern = no validation

    try {
      const regex = new RegExp(registro.regex_pattern);
      return regex.test(taxId);
    } catch {
      return false;
    }
  }

  /**
   * Get description
   */
  static getDescription(code: string): string | undefined {
    return this.getRegistro(code)?.descripcion;
  }

  /**
   * Get format/pattern description
   */
  static getFormato(code: string): string | undefined {
    return this.getRegistro(code)?.formato;
  }

  /**
   * Search by description
   */
  static searchByDescription(keyword: string): RegistroIdentTrib[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(
      (r) => r.descripcion.toUpperCase().includes(search) || r.pais.includes(search)
    );
  }

  /**
   * Check if registro is for USA
   */
  static isUSATaxId(code: string): boolean {
    const registro = this.getRegistro(code);
    return registro?.pais === 'USA';
  }

  /**
   * Check if registro is for European Union
   */
  static isEUTaxId(code: string): boolean {
    const registro = this.getRegistro(code);
    return registro?.descripcion.toUpperCase().includes('UNION EUROPEA') ?? false;
  }
}
