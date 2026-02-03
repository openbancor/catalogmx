/**
 * SAT CFDI 4.0 - Código Postal Catalog (c_CodigoPostal)
 *
 * Mexican postal codes used in:
 * - Comprobante.LugarExpedicion (issuer fiscal domicile postal code)
 * - Receptor.DomicilioFiscalReceptor (receiver fiscal domicile postal code)
 * - ACuentaTerceros.DomicilioFiscalACuentaTerceros
 *
 * Uses SEPOMEX SQLite database (~32,000 unique postal codes, 157K+ settlements).
 * For browser environments, use setCatalogJsonData() to pre-load data.
 */

import { loadCatalogRows } from '../../../utils/catalog-loader';

export interface CodigoPostalInfo {
  cp: string;
  asentamiento: string;
  tipo_asentamiento: string;
  municipio: string;
  estado: string;
  ciudad: string;
  codigo_estado: string;
  codigo_municipio: string;
  zona?: string;
}

const CP_PATTERN = /^\d{5}$/;

export class CodigoPostalCatalog {
  private static _data: CodigoPostalInfo[] | null = null;
  private static _byCP: Map<string, CodigoPostalInfo[]> | null = null;

  private static getData(): CodigoPostalInfo[] {
    if (!this._data) {
      // Try loading from shared data; in browser, this requires pre-loaded data
      try {
        this._data = loadCatalogRows<CodigoPostalInfo>('sepomex/codigos_postales_completo.json');
      } catch {
        // Fallback to summary file
        this._data = loadCatalogRows<CodigoPostalInfo>('sepomex/codigos_postales.json');
      }
    }
    return this._data;
  }

  private static getIndex(): Map<string, CodigoPostalInfo[]> {
    if (!this._byCP) {
      const data = this.getData();
      this._byCP = new Map();
      for (const item of data) {
        const existing = this._byCP.get(item.cp);
        if (existing) {
          existing.push(item);
        } else {
          this._byCP.set(item.cp, [item]);
        }
      }
    }
    return this._byCP;
  }

  /**
   * Validate postal code format (5 digits)
   */
  static isValidFormat(cp: string): boolean {
    return CP_PATTERN.test(cp);
  }

  /**
   * Validate that a postal code exists in the catalog
   */
  static isValid(cp: string): boolean {
    if (!this.isValidFormat(cp)) return false;
    return this.getIndex().has(cp);
  }

  /**
   * Get postal code information
   */
  static getCodigoPostal(cp: string): CodigoPostalInfo | undefined {
    if (!this.isValidFormat(cp)) return undefined;
    const entries = this.getIndex().get(cp);
    return entries?.[0];
  }

  /**
   * Get all settlements for a postal code
   */
  static getAsentamientos(cp: string): CodigoPostalInfo[] {
    if (!this.isValidFormat(cp)) return [];
    return this.getIndex().get(cp) ?? [];
  }

  /**
   * Get estado (state) name for a postal code
   */
  static getEstado(cp: string): string | undefined {
    return this.getCodigoPostal(cp)?.estado;
  }

  /**
   * Get municipio name for a postal code
   */
  static getMunicipio(cp: string): string | undefined {
    return this.getCodigoPostal(cp)?.municipio;
  }

  /**
   * Get estado code (2 digits) for a postal code
   */
  static getCodigoEstado(cp: string): string | undefined {
    return this.getCodigoPostal(cp)?.codigo_estado;
  }

  /**
   * Search postal codes by settlement, municipality, or city name
   */
  static search(query: string, limit: number = 20): CodigoPostalInfo[] {
    const q = query.toLowerCase();
    const results: CodigoPostalInfo[] = [];
    for (const item of this.getData()) {
      if (
        item.asentamiento?.toLowerCase().includes(q) ||
        item.municipio?.toLowerCase().includes(q) ||
        item.ciudad?.toLowerCase().includes(q)
      ) {
        results.push(item);
        if (results.length >= limit) break;
      }
    }
    return results;
  }

  /**
   * Get unique postal code count
   */
  static getUniqueCount(): number {
    return this.getIndex().size;
  }
}
