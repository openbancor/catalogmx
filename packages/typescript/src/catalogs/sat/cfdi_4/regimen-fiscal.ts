/**
 * SAT CFDI 4.0 - Régimen Fiscal Catalog
 * Tax regimes for natural persons and legal entities
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { RegimenFiscal } from '../../../types';

export class RegimenFiscalCatalog {
  private static _data: RegimenFiscal[] | null = null;

  private static getData(): RegimenFiscal[] {
    if (!this._data) {
      this._data = loadCatalog<RegimenFiscal>('sat/cfdi_4.0/regimen_fiscal.json');
    }
    return this._data;
  }

  static getAll(): RegimenFiscal[] {
    return this.getData();
  }

  static getRegimen(code: string): RegimenFiscal | undefined {
    return this.getData().find(reg => reg.code === code);
  }

  static isValidForPersonaFisica(code: string): boolean {
    const regimen = this.getRegimen(code);
    return regimen?.fisica === true || regimen?.persona_fisica === true;
  }

  static isValidForPersonaMoral(code: string): boolean {
    const regimen = this.getRegimen(code);
    return regimen?.moral === true || regimen?.persona_moral === true;
  }

  static getForPersonaFisica(): RegimenFiscal[] {
    return this.getData().filter(reg => reg.fisica || reg.persona_fisica);
  }

  static getForPersonaMoral(): RegimenFiscal[] {
    return this.getData().filter(reg => reg.moral || reg.persona_moral);
  }

  static isValid(code: string): boolean {
    return this.getData().some(reg => reg.code === code);
  }
}
