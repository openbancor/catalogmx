/**
 * SAT CFDI 4.0 - Régimen Fiscal Catalog
 * Tax regimes for natural persons and legal entities
 */

import { loadCatalogArray } from '../../../utils/catalog-loader';
import type { RegimenFiscal } from '../../../types';

export class RegimenFiscalCatalog {
  private static _data: RegimenFiscal[] | null = null;

  private static getData(): RegimenFiscal[] {
    if (this._data === null) {
      const rawData = loadCatalogArray<RegimenFiscal>('sat/cfdi_4.0/regimen_fiscal.json');
      this._data = rawData.map(regimen => ({
        ...regimen,
        persona_fisica: regimen.persona_fisica ?? regimen.fisica,
        persona_moral: regimen.persona_moral ?? regimen.moral
      }));
    }
    return this._data;
  }

  static getRegimen(code: string): RegimenFiscal | undefined {
    return this.getData().find(reg => reg.code === code);
  }

  static isValid(code: string): boolean {
    return this.getData().some(reg => reg.code === code);
  }

  static isValidForPersonaFisica(code: string): boolean {
    const regimen = this.getRegimen(code);
    return !!(regimen && (regimen.persona_fisica ?? regimen.fisica));
  }

  static isValidForPersonaMoral(code: string): boolean {
    const regimen = this.getRegimen(code);
    return !!(regimen && (regimen.persona_moral ?? regimen.moral));
  }
}
