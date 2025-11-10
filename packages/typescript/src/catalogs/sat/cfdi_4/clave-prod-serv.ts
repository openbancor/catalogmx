/**
 * SAT CFDI 4.0 - Clave de Producto o Servicio (c_ClaveProdServ)
 * Catalog of product and service codes for CFDI invoicing
 *
 * Contains ~52,000 official product/service codes from SAT
 * Based on UNSPSC (United Nations Standard Products and Services Code)
 *
 * WARNING: This is a large catalog. Use search and pagination methods.
 */

import * as fs from 'fs';
import * as path from 'path';
import { ClaveProdServ } from '../../../types';

export class ClaveProdServCatalog {
  private static _data: ClaveProdServ[] | null = null;
  private static _byId: Map<string, ClaveProdServ> | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(
      __dirname,
      '../../../../../shared-data/sat/cfdi_4.0/clave_prod_serv.json'
    );
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._data = JSON.parse(rawData) as ClaveProdServ[];

    // Crear índice por ID
    this._byId = new Map();
    for (const item of this._data!) {
      this._byId.set(item.id, item);
    }
  }

  /**
   * Obtiene todas las claves
   * WARNING: Retorna ~52,000 productos/servicios (~18 MB en memoria).
   * Evite usar este método. Use search() o getByPrefix() en su lugar.
   * @returns Lista completa de productos/servicios
   */
  static getAll(): ClaveProdServ[] {
    this.loadData();
    return [...this._data!];
  }

  /**
   * Obtiene una clave por su ID
   * @param id - Clave de 8 dígitos (ej: "10101500", "01010101")
   * @returns Producto/servicio o undefined si no existe
   */
  static getClave(id: string): ClaveProdServ | undefined {
    this.loadData();
    return this._byId!.get(id);
  }

  /**
   * Verifica si una clave de producto/servicio existe
   * @param id - Clave de 8 dígitos
   * @returns true si existe, false en caso contrario
   */
  static isValid(id: string): boolean {
    return this.getClave(id) !== undefined;
  }

  /**
   * Busca productos/servicios por descripción (búsqueda parcial, case-insensitive)
   * @param keyword - Palabra clave a buscar en la descripción
   * @param limit - Máximo número de resultados (default: 100)
   * @returns Lista de productos/servicios que coinciden
   */
  static search(keyword: string, limit: number = 100): ClaveProdServ[] {
    this.loadData();
    const keywordLower = keyword.toLowerCase();
    const results: ClaveProdServ[] = [];

    for (const item of this._data!) {
      if (results.length >= limit) break;

      if (
        item.descripcion.toLowerCase().includes(keywordLower) ||
        item.palabrasSimilares.toLowerCase().includes(keywordLower)
      ) {
        results.push(item);
      }
    }

    return results;
  }

  /**
   * Obtiene productos/servicios por prefijo de clave
   * Útil para navegación jerárquica del catálogo UNSPSC
   * @param prefix - Prefijo de la clave (2, 4, 6 u 8 dígitos)
   * @param limit - Máximo número de resultados (default: 500)
   * @returns Lista de productos/servicios con ese prefijo
   *
   * Ejemplos:
   * - "10" → Todos los productos en el segmento 10 (Animales vivos)
   * - "1010" → Familia 1010 (Animales vivos de granja)
   * - "101015" → Clase 101015 (Animales domésticos)
   */
  static getByPrefix(prefix: string, limit: number = 500): ClaveProdServ[] {
    this.loadData();
    const results: ClaveProdServ[] = [];

    for (const item of this._data!) {
      if (results.length >= limit) break;

      if (item.id.startsWith(prefix)) {
        results.push(item);
      }
    }

    return results;
  }

  /**
   * Obtiene claves vigentes (sin fecha de fin de vigencia)
   * @param limit - Máximo número de resultados (default: 1000)
   * @returns Lista de claves vigentes
   */
  static getVigentes(limit: number = 1000): ClaveProdServ[] {
    this.loadData();
    const results: ClaveProdServ[] = [];

    for (const item of this._data!) {
      if (results.length >= limit) break;

      if (!item.fechaFinVigencia || item.fechaFinVigencia === '') {
        results.push(item);
      }
    }

    return results;
  }

  /**
   * Obtiene claves con estímulo de franja fronteriza
   * @param limit - Máximo número de resultados (default: 1000)
   * @returns Lista de claves con estímulo fronterizo
   */
  static getConEstimuloFronterizo(limit: number = 1000): ClaveProdServ[] {
    this.loadData();
    const results: ClaveProdServ[] = [];

    for (const item of this._data!) {
      if (results.length >= limit) break;

      if (item.estimuloFranjaFronteriza === '01') {
        results.push(item);
      }
    }

    return results;
  }

  /**
   * Obtiene claves que requieren IVA trasladado
   * @param limit - Máximo número de resultados (default: 1000)
   * @returns Lista de claves que requieren IVA
   */
  static getRequierenIVA(limit: number = 1000): ClaveProdServ[] {
    this.loadData();
    const results: ClaveProdServ[] = [];

    for (const item of this._data!) {
      if (results.length >= limit) break;

      if (
        item.incluirIVATrasladado.toUpperCase() === 'SÍ' ||
        item.incluirIVATrasladado.toUpperCase() === 'SI'
      ) {
        results.push(item);
      }
    }

    return results;
  }

  /**
   * Obtiene claves que requieren IEPS trasladado
   * @param limit - Máximo número de resultados (default: 1000)
   * @returns Lista de claves que requieren IEPS
   */
  static getRequierenIEPS(limit: number = 1000): ClaveProdServ[] {
    this.loadData();
    const results: ClaveProdServ[] = [];

    for (const item of this._data!) {
      if (results.length >= limit) break;

      if (
        item.incluirIEPSTrasladado.toUpperCase() === 'SÍ' ||
        item.incluirIEPSTrasladado.toUpperCase() === 'SI'
      ) {
        results.push(item);
      }
    }

    return results;
  }

  /**
   * Obtiene el total de productos/servicios en el catálogo
   * @returns Número total (52,514)
   */
  static getTotalCount(): number {
    this.loadData();
    return this._data!.length;
  }

  /**
   * Obtiene estadísticas del catálogo
   * @returns Estadísticas del catálogo
   */
  static getStatistics(): {
    total: number;
    vigentes: number;
    obsoletas: number;
    conEstimuloFronterizo: number;
    requierenIVA: number;
    requierenIEPS: number;
  } {
    this.loadData();

    let vigentes = 0;
    let obsoletas = 0;
    let conEstimulo = 0;
    let requierenIVA = 0;
    let requierenIEPS = 0;

    for (const item of this._data!) {
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
      total: this._data!.length,
      vigentes,
      obsoletas,
      conEstimuloFronterizo: conEstimulo,
      requierenIVA,
      requierenIEPS,
    };
  }

  /**
   * Búsqueda avanzada con múltiples criterios
   * @param criteria - Criterios de búsqueda
   * @returns Lista de productos/servicios que coinciden
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
    this.loadData();
    const limit = criteria.limit || 100;
    const results: ClaveProdServ[] = [];

    const keywordLower = criteria.keyword?.toLowerCase();

    for (const item of this._data!) {
      if (results.length >= limit) break;

      // Filtrar por keyword
      if (keywordLower) {
        const matchKeyword =
          item.descripcion.toLowerCase().includes(keywordLower) ||
          item.palabrasSimilares.toLowerCase().includes(keywordLower);
        if (!matchKeyword) continue;
      }

      // Filtrar por prefijo
      if (criteria.prefix && !item.id.startsWith(criteria.prefix)) {
        continue;
      }

      // Filtrar por vigencia
      if (criteria.vigente !== undefined) {
        const esVigente = !item.fechaFinVigencia || item.fechaFinVigencia === '';
        if (criteria.vigente !== esVigente) continue;
      }

      // Filtrar por estímulo fronterizo
      if (criteria.estimuloFronterizo !== undefined) {
        const tieneEstimulo = item.estimuloFranjaFronteriza === '01';
        if (criteria.estimuloFronterizo !== tieneEstimulo) continue;
      }

      // Filtrar por IVA
      if (criteria.requiereIVA !== undefined) {
        const requiereIVA =
          item.incluirIVATrasladado.toUpperCase() === 'SÍ' ||
          item.incluirIVATrasladado.toUpperCase() === 'SI';
        if (criteria.requiereIVA !== requiereIVA) continue;
      }

      // Filtrar por IEPS
      if (criteria.requiereIEPS !== undefined) {
        const requiereIEPS =
          item.incluirIEPSTrasladado.toUpperCase() === 'SÍ' ||
          item.incluirIEPSTrasladado.toUpperCase() === 'SI';
        if (criteria.requiereIEPS !== requiereIEPS) continue;
      }

      results.push(item);
    }

    return results;
  }
}
