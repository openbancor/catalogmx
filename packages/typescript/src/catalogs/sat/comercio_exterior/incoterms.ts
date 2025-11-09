/**
 * SAT Comercio Exterior - INCOTERMS 2020 Catalog
 * International Commercial Terms for foreign trade
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { Incoterm } from '../../../types';

export class IncotermsValidator {
  private static _data: Incoterm[] | null = null;

  private static getData(): Incoterm[] {
    if (!this._data) {
      this._data = loadCatalog<Incoterm>('sat/comercio_exterior/incoterms.json');
    }
    return this._data;
  }

  static getAll(): Incoterm[] {
    return this.getData();
  }

  static getIncoterm(code: string): Incoterm | undefined {
    return this.getData().find(inc => inc.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some(inc => inc.code === code.toUpperCase());
  }

  /**
   * Check if seller pays insurance for this INCOTERM
   */
  static sellerPaysInsurance(code: string): boolean {
    const incoterm = this.getIncoterm(code);
    return incoterm?.seller_pays_insurance === true || incoterm?.insurance_paid_by === 'seller';
  }

  /**
   * Check if buyer pays insurance for this INCOTERM
   */
  static buyerPaysInsurance(code: string): boolean {
    const incoterm = this.getIncoterm(code);
    return incoterm?.seller_pays_insurance === false || incoterm?.insurance_paid_by === 'buyer';
  }

  /**
   * Get INCOTERMs for specific transport mode
   */
  static getByTransportMode(mode: 'any' | 'maritime' | 'multimodal'): Incoterm[] {
    return this.getData().filter(inc => inc.transport_mode === mode);
  }

  /**
   * Get INCOTERMs valid for any transport mode
   */
  static getForAnyTransport(): Incoterm[] {
    return this.getByTransportMode('any');
  }

  /**
   * Get INCOTERMs for maritime transport only
   */
  static getForMaritimeTransport(): Incoterm[] {
    return this.getByTransportMode('maritime');
  }

  /**
   * Validate INCOTERM is appropriate for transport mode
   */
  static isValidForTransportMode(code: string, mode: 'any' | 'maritime' | 'multimodal'): boolean {
    const incoterm = this.getIncoterm(code);
    if (!incoterm) return false;
    return incoterm.transport_mode === 'any' || incoterm.transport_mode === mode;
  }
}
