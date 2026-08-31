import { loadCatalogObject } from '../../../utils/catalog-loader';

export interface NominaClaveProdServ {
  code: string;
  description: string;
  valid_from: string;
  valid_to: string;
}

/** Bounded CFDI fields fixed by SAT's Nómina filling guide. */
export class NominaCfdiCatalog {
  private static _data: NominaClaveProdServ[] | null = null;

  private static getData(): NominaClaveProdServ[] {
    if (this._data === null) {
      this._data = loadCatalogObject<NominaClaveProdServ>(
        'sat/cfdi_4.0/nomina_clave_prod_serv.json'
      );
    }
    return this._data;
  }

  static getClaveProdServ(code: string): NominaClaveProdServ | undefined {
    return this.getData().find((item) => item.code === code);
  }

  static isValidClaveProdServ(code: string): boolean {
    return this.getClaveProdServ(code) !== undefined;
  }

  static getAllClaveProdServ(): NominaClaveProdServ[] {
    return [...this.getData()];
  }
}
