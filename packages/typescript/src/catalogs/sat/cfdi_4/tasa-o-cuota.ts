import { loadCatalogObject } from '../../../utils/catalog-loader';
import type { CatalogItem } from '../../../types';

export class TasaOCuota {
  private static _data: CatalogItem[] | null = null;

  private static getData(): CatalogItem[] {
    if (this._data === null) {
      this._data = loadCatalogObject<Record<string, unknown>>('sat/cfdi_4.0/c_TasaOCuota.json').map(
        (item) => ({
          id: String(
            item.valor ??
              item.tasa ??
              (item as { 'catálogo_de_tasas_o_cuotas_de_impuestos.'?: unknown })[
                'catálogo_de_tasas_o_cuotas_de_impuestos.'
              ] ??
              ''
          ),
          name: String(item.descripcion ?? item.valor ?? item.tasa ?? ''),
          ...item,
        })
      );
    }
    return this._data ?? [];
  }

  static getAll(): CatalogItem[] {
    return this.getData();
  }
}
