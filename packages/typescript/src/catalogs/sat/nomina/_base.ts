/** Shared support for SAT Nómina 1.2 compatibility views. */

import { loadCatalogObject } from '../../../utils/catalog-loader';

export interface NominaCatalogItem {
  code: string;
  clave?: string;
  description: string;
  descripcion: string;
  valid_from?: string | null;
  valid_to?: string | null;
}

export abstract class NominaSimpleCatalog {
  protected static filename: string;
  private static readonly cache = new Map<string, NominaCatalogItem[]>();

  protected static getData(): NominaCatalogItem[] {
    const filename = this.filename;
    const cached = this.cache.get(filename);
    if (cached) return cached;

    const rows = loadCatalogObject<NominaCatalogItem>(`sat/nomina_1.2/${filename}`);
    const normalized = rows.map((row) => ({
      ...row,
      code: String(row.code ?? row.clave),
      clave: String(row.clave ?? row.code),
      description: row.description ?? row.descripcion,
      descripcion: row.descripcion ?? row.description,
    }));
    this.cache.set(filename, normalized);
    return normalized;
  }

  static reload(): void {
    this.cache.delete(this.filename);
  }

  static getAll(): NominaCatalogItem[] {
    return this.getData();
  }

  static getByCode(code: string): NominaCatalogItem | undefined {
    return this.getData().find((item) => item.code === code);
  }

  static isValid(code: string): boolean {
    return this.getByCode(code) !== undefined;
  }

  static searchByDescription(keyword: string): NominaCatalogItem[] {
    const search = keyword.toUpperCase();
    return this.getData().filter((item) => item.descripcion.toUpperCase().includes(search));
  }
}
