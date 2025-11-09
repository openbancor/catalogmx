/**
 * SAT CFDI 4.0 - Clave de Unidad (c_ClaveUnidad)
 * Catalog of measurement units for products and services
 *
 * Contains ~2,400 official measurement units from SAT
 * Based on UN/ECE Recommendation 20 and 21
 */

import * as fs from 'fs';
import * as path from 'path';
import { ClaveUnidad } from '../../../types';

export class ClaveUnidadCatalog {
  private static _data: ClaveUnidad[] | null = null;
  private static _byId: Map<string, ClaveUnidad> | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(
      __dirname,
      '../../../../../shared-data/sat/cfdi_4.0/clave_unidad.json'
    );
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._data = JSON.parse(rawData) as ClaveUnidad[];

    // Crear índice por ID
    this._byId = new Map();
    for (const item of this._data!) {
      this._byId.set(item.id, item);
    }
  }

  /**
   * Obtiene todas las unidades
   * WARNING: Retorna ~2,400 unidades. Considere usar búsqueda o paginación.
   * @returns Lista completa de unidades
   */
  static getAll(): ClaveUnidad[] {
    this.loadData();
    return [...this._data!];
  }

  /**
   * Obtiene una unidad por su ID/clave
   * @param id - Clave de la unidad (ej: "MTR", "KGM", "H87")
   * @returns Unidad o undefined si no existe
   */
  static getUnidad(id: string): ClaveUnidad | undefined {
    this.loadData();
    return this._byId!.get(id);
  }

  /**
   * Verifica si una clave de unidad existe
   * @param id - Clave de la unidad
   * @returns true si existe, false en caso contrario
   */
  static isValid(id: string): boolean {
    return this.getUnidad(id) !== undefined;
  }

  /**
   * Busca unidades por nombre (búsqueda parcial, case-insensitive)
   * @param keyword - Palabra clave a buscar en el nombre
   * @returns Lista de unidades que coinciden
   */
  static searchByName(keyword: string): ClaveUnidad[] {
    this.loadData();
    const keywordLower = keyword.toLowerCase();
    return this._data!.filter(u =>
      u.nombre.toLowerCase().includes(keywordLower)
    );
  }

  /**
   * Busca unidades por símbolo (ej: "kg", "m", "l")
   * @param simbolo - Símbolo a buscar
   * @returns Lista de unidades con ese símbolo
   */
  static searchBySymbol(simbolo: string): ClaveUnidad[] {
    this.loadData();
    const simboloLower = simbolo.toLowerCase();
    return this._data!.filter(u =>
      u.simbolo.toLowerCase() === simboloLower
    );
  }

  /**
   * Obtiene unidades vigentes (sin fecha de fin de vigencia)
   * @returns Lista de unidades vigentes
   */
  static getVigentes(): ClaveUnidad[] {
    this.loadData();
    return this._data!.filter(u => !u.fechaDeFinDeVigencia || u.fechaDeFinDeVigencia === '');
  }

  /**
   * Obtiene unidades obsoletas (con fecha de fin de vigencia)
   * @returns Lista de unidades obsoletas
   */
  static getObsoletas(): ClaveUnidad[] {
    this.loadData();
    return this._data!.filter(u => u.fechaDeFinDeVigencia && u.fechaDeFinDeVigencia !== '');
  }

  /**
   * Busca unidades por categoría (en el nombre)
   * Ejemplos: "peso", "longitud", "volumen", "tiempo", "pieza"
   * @param categoria - Categoría a buscar
   * @returns Lista de unidades en esa categoría
   */
  static searchByCategory(categoria: string): ClaveUnidad[] {
    this.loadData();
    const catLower = categoria.toLowerCase();

    const keywords: Record<string, string[]> = {
      'peso': ['kilogramo', 'gramo', 'tonelada', 'libra', 'onza'],
      'longitud': ['metro', 'centímetro', 'milímetro', 'kilómetro', 'pulgada', 'pie', 'yarda'],
      'volumen': ['litro', 'mililitro', 'metro cúbico', 'galón', 'barril'],
      'tiempo': ['hora', 'minuto', 'segundo', 'día', 'semana', 'mes', 'año'],
      'pieza': ['pieza', 'unidad', 'paquete', 'caja', 'docena']
    };

    const searchWords = keywords[catLower] || [catLower];

    return this._data!.filter(u => {
      const nombreLower = u.nombre.toLowerCase();
      return searchWords.some(word => nombreLower.includes(word));
    });
  }

  /**
   * Obtiene el total de unidades en el catálogo
   * @returns Número total de unidades
   */
  static getTotalCount(): number {
    this.loadData();
    return this._data!.length;
  }

  /**
   * Obtiene estadísticas del catálogo
   * @returns Estadísticas de unidades
   */
  static getStatistics(): {
    total: number;
    vigentes: number;
    obsoletas: number;
    conSimbolo: number;
    sinSimbolo: number;
  } {
    this.loadData();

    return {
      total: this._data!.length,
      vigentes: this.getVigentes().length,
      obsoletas: this.getObsoletas().length,
      conSimbolo: this._data!.filter(u => u.simbolo && u.simbolo !== '').length,
      sinSimbolo: this._data!.filter(u => !u.simbolo || u.simbolo === '').length,
    };
  }
}
