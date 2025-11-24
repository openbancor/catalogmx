import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { CatalogItem } from '../../../types';

export class TipoFactor {
  private static _data: CatalogItem[] | null = null;

  private static getData(): CatalogItem[] {
    if (this._data === null) {
      const raw = loadCatalogObject<Record<string, unknown>>('sat/cfdi_4.0/c_TipoFactor.json');
      this._data = raw.map((item) => ({
        id: String(item.valor ?? ''),
        name: String(item.descripcion ?? item.valor ?? ''),
        ...item,
      }));
    }
    return this._data ?? [];
  }

  static getById(id: string): CatalogItem | undefined {
    return this.getData().find((item) => item.id === id);
  }

  static isValid(id: string): boolean {
    return !!this.getById(id);
  }
}
