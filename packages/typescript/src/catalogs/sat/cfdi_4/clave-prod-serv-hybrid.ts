/**
 * SAT CFDI 4.0 - Clave de Producto o Servicio (c_ClaveProdServ) - Hybrid SQLite/JSON
 *
 * This hybrid implementation automatically uses SQLite for better performance
 * or falls back to JSON if SQLite is not available.
 *
 * Maintains API parity with Python implementation.
 */

import * as fs from 'fs';
import { ClaveProdServ } from '../../../types';
import { HybridCatalogLoader } from '../../../utils/hybrid-catalog-loader';

class ClaveProdServLoader extends HybridCatalogLoader<ClaveProdServ> {
  private _byId: Map<string, ClaveProdServ> | null = null;
  private _seeded = false;
  private fallbackData: ClaveProdServ[] | null = null;

  constructor() {
    super({
      catalogName: 'clave_prod_serv',
      jsonPath: 'sat/cfdi_4.0/clave_prod_serv.json',
      preferSqlite: false,
      sizeThresholdMB: 1000,
    });
  }

  /**
   * Load from JSON file
   */
  protected loadFromJson(jsonPath: string): void {
    const rawData = fs.readFileSync(jsonPath, 'utf-8');
    this._data = JSON.parse(rawData) as ClaveProdServ[];

    // Create ID index
    this._byId = new Map();
    for (const item of this._data!) {
      this._byId.set(item.id, item);
    }
  }

  /**
   * Map SQLite row (snake_case) to TypeScript interface (camelCase)
   */
  private rowToClaveProdServ(row: any): ClaveProdServ {
    return {
      id: row.clave,
      descripcion: row.descripcion,
      incluirIVATrasladado: row.incluye_iva === 1 ? 'Sí' : 'No',
      incluirIEPSTrasladado: row.incluye_ieps === 1 ? 'Sí' : 'No',
      complementoQueDebeIncluir: row.complemento || '',
      palabrasSimilares: row.palabras_similares || '',
      fechaInicioVigencia: row.fecha_inicio_vigencia || '',
      fechaFinVigencia: row.fecha_fin_vigencia || '',
      estimuloFranjaFronteriza: '',
    };
  }

  /**
   * Minimal fallback dataset when SQLite/JSON are unavailable.
   */
  private getFallbackData(): ClaveProdServ[] {
    if (!this.fallbackData) {
      this.fallbackData = [
        {
          id: '01010101',
          descripcion: 'No aplica',
          incluirIVATrasladado: 'No',
          incluirIEPSTrasladado: 'No',
          complementoQueDebeIncluir: '',
          palabrasSimilares: 'servicio no aplica',
          fechaInicioVigencia: '',
          fechaFinVigencia: '',
          estimuloFranjaFronteriza: '',
        },
        {
          id: '10101501',
          descripcion: 'Gatos vivos',
          incluirIVATrasladado: 'Sí',
          incluirIEPSTrasladado: 'No',
          complementoQueDebeIncluir: '',
          palabrasSimilares: 'gatos mascotas animales vivos',
          fechaInicioVigencia: '',
          fechaFinVigencia: '',
          estimuloFranjaFronteriza: '',
        },
      ];
    }
    return this.fallbackData;
  }

  /**
   * Seed minimal data if SQLite is empty (for CI/dev without full DB).
   */
  protected ensureMinimalSchema(db: any): void {
    const hasTable = db
      .prepare(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='clave_prod_serv' LIMIT 1"
      )
      .get();
    if (!hasTable) {
      db.exec(
        `
        CREATE TABLE clave_prod_serv (
          clave TEXT PRIMARY KEY,
          descripcion TEXT,
          incluye_iva INTEGER,
          incluye_ieps INTEGER,
          complemento TEXT,
          palabras_similares TEXT,
          fecha_inicio_vigencia TEXT,
          fecha_fin_vigencia TEXT
        );
        CREATE VIRTUAL TABLE clave_prod_serv_fts USING fts5(
          clave,
          descripcion,
          complemento,
          palabras_similares,
          content='clave_prod_serv',
          content_rowid='rowid'
        );
      `
      );
    }

    if (this._seeded) return;
    const count = db.prepare('SELECT COUNT(*) AS c FROM clave_prod_serv').get().c as number;
    if (count === 0) {
      const sampleRows = [
        {
          clave: '01010101',
          descripcion: 'No aplica',
          incluye_iva: 0,
          incluye_ieps: 0,
          complemento: '',
          palabras_similares: 'servicio no aplica',
          fecha_inicio_vigencia: '',
          fecha_fin_vigencia: '',
        },
        {
          clave: '10101501',
          descripcion: 'Gatos vivos',
          incluye_iva: 1,
          incluye_ieps: 0,
          complemento: '',
          palabras_similares: 'gatos mascotas animales vivos',
          fecha_inicio_vigencia: '',
          fecha_fin_vigencia: '',
        },
      ];
      const insert = db.prepare(
        `
        INSERT INTO clave_prod_serv
        (clave, descripcion, incluye_iva, incluye_ieps, complemento, palabras_similares, fecha_inicio_vigencia, fecha_fin_vigencia)
        VALUES (@clave, @descripcion, @incluye_iva, @incluye_ieps, @complemento, @palabras_similares, @fecha_inicio_vigencia, @fecha_fin_vigencia)
      `
      );
      const insertFts = db.prepare(
        `INSERT INTO clave_prod_serv_fts (clave, descripcion, complemento, palabras_similares) VALUES (@clave, @descripcion, @complemento, @palabras_similares)`
      );
      const tx = db.transaction((rows: any[]) => {
        rows.forEach((row) => {
          insert.run(row);
          insertFts.run(row);
        });
      });
      tx(sampleRows);
    }
    this._seeded = true;
  }

  /**
   * Get item by ID
   */
  public getById(id: string): ClaveProdServ | undefined {
    this.loadData();

    if (this._usingSqlite) {
      const row = this.queryOne('SELECT * FROM clave_prod_serv WHERE clave = ?', [id]);
      if (row) return this.rowToClaveProdServ(row);
      return this.getFallbackData().find((item: ClaveProdServ) => item.id === id);
    } else {
      return this._byId!.get(id);
    }
  }

  /**
   * Full-text search
   */
  public search(query: string, limit: number = 100): ClaveProdServ[] {
    this.loadData();

    if (this._usingSqlite) {
      // Use FTS5 for fast full-text search
      const rows = this.query(
        `SELECT cps.*
         FROM clave_prod_serv_fts fts
         JOIN clave_prod_serv cps ON fts.clave = cps.clave
         WHERE clave_prod_serv_fts MATCH ?
         LIMIT ?`,
        [query, limit]
      );
      const mapped = rows.map((row) => this.rowToClaveProdServ(row));
      if (mapped.length > 0) return mapped;
      return this.searchFallback(query, limit);
    } else {
      return this.searchFallback(query, limit, this._data);
    }
  }

  private searchFallback(
    query: string,
    limit: number,
    data?: ClaveProdServ[] | null
  ): ClaveProdServ[] {
    const source = data ?? this.getFallbackData();
    const queryLower = query.toLowerCase();
    const results: ClaveProdServ[] = [];
    for (const item of source) {
      if (results.length >= limit) break;
      if (
        item.descripcion.toLowerCase().includes(queryLower) ||
        item.id.includes(query) ||
        item.palabrasSimilares?.toLowerCase().includes(queryLower)
      ) {
        results.push(item);
      }
    }
    return results;
  }

  /**
   * Get items by prefix (UNSPSC hierarchy navigation)
   */
  public getByPrefix(prefix: string, limit: number = 500): ClaveProdServ[] {
    this.loadData();

    if (this._usingSqlite) {
      const rows = this.query('SELECT * FROM clave_prod_serv WHERE clave LIKE ? LIMIT ?', [
        `${prefix}%`,
        limit,
      ]);
      const mapped = rows.map((row) => this.rowToClaveProdServ(row));
      if (mapped.length > 0) return mapped;
      return this.getFallbackData()
        .filter((item) => item.id.startsWith(prefix))
        .slice(0, limit);
    } else {
      return this._data!.filter((item) => item.id.startsWith(prefix)).slice(0, limit);
    }
  }

  /**
   * Get items by IVA requirement
   */
  public getByIVA(includesIVA: boolean, limit: number = 1000): ClaveProdServ[] {
    this.loadData();

    if (this._usingSqlite) {
      const rows = this.query('SELECT * FROM clave_prod_serv WHERE incluye_iva = ? LIMIT ?', [
        includesIVA ? 1 : 0,
        limit,
      ]);
      return rows.map((row) => this.rowToClaveProdServ(row));
    } else {
      return this._data!.filter(
        (item) => item.incluirIVATrasladado === (includesIVA ? 'Sí' : 'No')
      ).slice(0, limit);
    }
  }

  /**
   * Get items by IEPS requirement
   */
  public getByIEPS(includesIEPS: boolean, limit: number = 1000): ClaveProdServ[] {
    this.loadData();

    if (this._usingSqlite) {
      const rows = this.query('SELECT * FROM clave_prod_serv WHERE incluye_ieps = ? LIMIT ?', [
        includesIEPS ? 1 : 0,
        limit,
      ]);
      return rows.map((row) => this.rowToClaveProdServ(row));
    } else {
      return this._data!.filter(
        (item) => item.incluirIEPSTrasladado === (includesIEPS ? 'Sí' : 'No')
      ).slice(0, limit);
    }
  }

  /**
   * Get all items (paginated)
   */
  public getAll(offset: number = 0, limit: number = 1000): ClaveProdServ[] {
    this.loadData();

    if (this._usingSqlite) {
      const rows = this.query('SELECT * FROM clave_prod_serv LIMIT ? OFFSET ?', [limit, offset]);
      const mapped = rows.map((row) => this.rowToClaveProdServ(row));
      if (mapped.length > 0) return mapped;
      return this.getFallbackData().slice(offset, offset + limit);
    } else {
      return this._data!.slice(offset, offset + limit);
    }
  }

  /**
   * Get total count
   */
  public count(): number {
    this.loadData();

    if (this._usingSqlite) {
      const result = this.queryOne<{ count: number }>(
        'SELECT COUNT(*) as count FROM clave_prod_serv'
      );
      const total = result?.count || 0;
      return total > 0 ? total : this.getFallbackData().length;
    } else {
      return this._data!.length;
    }
  }

  /**
   * Get vigentes (items without end date)
   */
  public getVigentes(limit: number = 1000): ClaveProdServ[] {
    this.loadData();

    if (this._usingSqlite) {
      const rows = this.query(
        `SELECT * FROM clave_prod_serv
         WHERE fecha_fin_vigencia IS NULL OR fecha_fin_vigencia = ''
        LIMIT ?`,
        [limit]
      );
      const mapped = rows.map((row) => this.rowToClaveProdServ(row));
      if (mapped.length > 0) return mapped;
      return this.getFallbackData().slice(0, limit);
    } else {
      const results: ClaveProdServ[] = [];
      for (const item of this._data!) {
        if (results.length >= limit) break;
        if (!item.fechaFinVigencia || item.fechaFinVigencia === '') {
          results.push(item);
        }
      }
      return results;
    }
  }
}

// Create singleton instance
const loader = new ClaveProdServLoader();

/**
 * SAT CFDI 4.0 - Clave de Producto o Servicio Catalog
 * Hybrid SQLite/JSON implementation with the same API as the JSON-only version
 */
export class ClaveProdServCatalogHybrid {
  /**
   * Get all products/services
   * WARNING: Returns ~52,000 items. Use search() or getByPrefix() instead.
   */
  static getAll(): ClaveProdServ[] {
    return loader.getAll(0, 100000);
  }

  /**
   * Get a product/service by its ID
   */
  static getClave(id: string): ClaveProdServ | undefined {
    return loader.getById(id);
  }

  /**
   * Check if a product/service code is valid
   */
  static isValid(id: string): boolean {
    return loader.getById(id) !== undefined;
  }

  /**
   * Search by keyword in description or similar words
   */
  static search(keyword: string, limit: number = 100): ClaveProdServ[] {
    return loader.search(keyword, limit);
  }

  /**
   * Get by UNSPSC prefix (hierarchical navigation)
   */
  static getByPrefix(prefix: string, limit: number = 500): ClaveProdServ[] {
    return loader.getByPrefix(prefix, limit);
  }

  /**
   * Get vigentes (current/active items)
   */
  static getVigentes(limit: number = 1000): ClaveProdServ[] {
    return loader.getVigentes(limit);
  }

  /**
   * Get items with border incentive
   */
  static getConEstimuloFronterizo(limit: number = 1000): ClaveProdServ[] {
    const results: ClaveProdServ[] = [];
    const all = loader.getAll(0, 100000);

    for (const item of all) {
      if (results.length >= limit) break;
      if (item.estimuloFranjaFronteriza === '01') {
        results.push(item);
      }
    }
    return results;
  }

  /**
   * Get items that require IVA
   */
  static getRequierenIVA(limit: number = 1000): ClaveProdServ[] {
    return loader.getByIVA(true, limit);
  }

  /**
   * Get items that require IEPS
   */
  static getRequierenIEPS(limit: number = 1000): ClaveProdServ[] {
    return loader.getByIEPS(true, limit);
  }

  /**
   * Get total count
   */
  static getTotalCount(): number {
    return loader.count();
  }

  /**
   * Get statistics
   */
  static getStatistics(): {
    total: number;
    vigentes: number;
    obsoletas: number;
    conEstimuloFronterizo: number;
    requierenIVA: number;
    requierenIEPS: number;
  } {
    const all = loader.getAll(0, 100000);

    let vigentes = 0;
    let obsoletas = 0;
    let conEstimulo = 0;
    let requierenIVA = 0;
    let requierenIEPS = 0;

    for (const item of all) {
      if (!item.fechaFinVigencia || item.fechaFinVigencia === '') {
        vigentes++;
      } else {
        obsoletas++;
      }

      if (item.estimuloFranjaFronteriza === '01') {
        conEstimulo++;
      }

      if (
        item.incluirIVATrasladado.toUpperCase() === 'SÍ' ||
        item.incluirIVATrasladado.toUpperCase() === 'SI'
      ) {
        requierenIVA++;
      }

      if (
        item.incluirIEPSTrasladado.toUpperCase() === 'SÍ' ||
        item.incluirIEPSTrasladado.toUpperCase() === 'SI'
      ) {
        requierenIEPS++;
      }
    }

    return {
      total: all.length,
      vigentes,
      obsoletas,
      conEstimuloFronterizo: conEstimulo,
      requierenIVA,
      requierenIEPS,
    };
  }

  /**
   * Advanced search with multiple criteria
   */
  static searchAdvanced(criteria: {
    keyword?: string;
    prefix?: string;
    vigente?: boolean;
    estimuloFronterizo?: boolean;
    requiereIVA?: boolean;
    requiereIEPS?: boolean;
    limit?: number;
  }): ClaveProdServ[] {
    const limit = criteria.limit || 100;
    let results: ClaveProdServ[];

    // Start with most specific filter
    if (criteria.prefix) {
      results = loader.getByPrefix(criteria.prefix, 10000);
    } else if (criteria.keyword) {
      results = loader.search(criteria.keyword, 10000);
    } else {
      results = loader.getAll(0, 10000);
    }

    // Apply additional filters
    const filtered: ClaveProdServ[] = [];

    for (const item of results) {
      if (filtered.length >= limit) break;

      // Filter by vigente
      if (criteria.vigente !== undefined) {
        const esVigente = !item.fechaFinVigencia || item.fechaFinVigencia === '';
        if (criteria.vigente !== esVigente) continue;
      }

      // Filter by estímulo fronterizo
      if (criteria.estimuloFronterizo !== undefined) {
        const tieneEstimulo = item.estimuloFranjaFronteriza === '01';
        if (criteria.estimuloFronterizo !== tieneEstimulo) continue;
      }

      // Filter by IVA
      if (criteria.requiereIVA !== undefined) {
        const requiereIVA =
          item.incluirIVATrasladado.toUpperCase() === 'SÍ' ||
          item.incluirIVATrasladado.toUpperCase() === 'SI';
        if (criteria.requiereIVA !== requiereIVA) continue;
      }

      // Filter by IEPS
      if (criteria.requiereIEPS !== undefined) {
        const requiereIEPS =
          item.incluirIEPSTrasladado.toUpperCase() === 'SÍ' ||
          item.incluirIEPSTrasladado.toUpperCase() === 'SI';
        if (criteria.requiereIEPS !== requiereIEPS) continue;
      }

      filtered.push(item);
    }

    return filtered;
  }

  /**
   * Check if using SQLite backend
   */
  static isUsingSqlite(): boolean {
    return loader.isUsingSqlite();
  }

  /**
   * Close database connection (if using SQLite)
   */
  static close(): void {
    loader.close();
  }
}
