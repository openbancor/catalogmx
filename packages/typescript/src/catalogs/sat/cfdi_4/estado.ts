import { loadCatalogObject } from '../../../utils/catalog-loader';

export interface EstadoCfdi {
  code: string;
}

/** SAT c_Estado identifiers used by CFDI and Nómina 1.2. */
export class EstadoCfdiCatalog {
  private static _data: EstadoCfdi[] | null = null;

  private static getData(): EstadoCfdi[] {
    if (this._data === null) {
      this._data = loadCatalogObject<EstadoCfdi>('sat/cfdi_4.0/estado.json');
    }
    return this._data;
  }

  static getEstado(code: string): EstadoCfdi | undefined {
    return this.getData().find((estado) => estado.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getEstado(code) !== undefined;
  }

  static getAll(): EstadoCfdi[] {
    return [...this.getData()];
  }
}
