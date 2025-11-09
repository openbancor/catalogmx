import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { CatalogItem } from '../../../types';

export class Meses {
  private static _data: CatalogItem[] | null = null;

  private static getData(): CatalogItem[] {
    if (this._data === null) {
      this._data = loadCatalogObject<any>('sat/cfdi_4.0/c_Meses.json').map(
        (item: any) => ({
          id: item.valor,
          name: item.descripcion || item.valor,
          ...item,
        })
      );
    }
    return this._data;
  }

  static getById(id: string): CatalogItem | undefined {
    return this.getData().find(item => item.id === id);
  }

  static isValid(id: string): boolean {
    return !!this.getById(id);
  }
}
