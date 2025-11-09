import { loadCatalogObject } from '../../../utils/catalog-loader';

export class TasaOCuota {
  private static _data: any[] | null = null;

  private static getData(): any[] {
    if (this._data === null) {
        this._data = loadCatalogObject<any>('sat/cfdi_4.0/c_TasaOCuota.json');
    }
    return this._data;
  }

  static getAll(): any[] {
    return this.getData();
  }
}
