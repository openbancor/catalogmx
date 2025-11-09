/**
 * Catálogo de operadores de telefonía móvil en México (IFT)
 */

import * as path from 'path';
import * as fs from 'fs';
import { OperadorMovil } from '../../types';

interface OperadoresMovilesData {
  metadata: {
    catalog: string;
    description: string;
    source: string;
    last_updated: string;
    notes: string;
  };
  operadores: OperadorMovil[];
  tipos_operador: Record<string, string>;
  estadisticas: {
    total_operadores: number;
    operadores_activos: number;
    omr_activos: number;
    omv_activos: number;
    lineas_totales_mercado: number;
    fecha_estadisticas: string;
  };
}

export class OperadoresMoviles {
  private static _data: OperadorMovil[] | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(
      __dirname,
      '../../../../shared-data/ift/operadores_moviles.json'
    );
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    const jsonData: OperadoresMovilesData = JSON.parse(rawData);
    this._data = jsonData.operadores;
  }

  /**
   * Obtener todos los operadores móviles
   */
  static getAll(): OperadorMovil[] {
    this.loadData();
    return this._data!;
  }

  /**
   * Obtener operadores activos
   */
  static getActivos(): OperadorMovil[] {
    this.loadData();
    return this._data!.filter((op) => op.activo);
  }

  /**
   * Buscar operador por nombre comercial
   */
  static buscarPorNombre(nombre: string): OperadorMovil | undefined {
    this.loadData();
    return this._data!.find((op) =>
      op.nombre_comercial.toLowerCase().includes(nombre.toLowerCase())
    );
  }

  /**
   * Filtrar por tipo de operador (OMR o OMV)
   */
  static getPorTipo(tipo: 'OMR' | 'OMV'): OperadorMovil[] {
    this.loadData();
    return this._data!.filter((op) => op.tipo === tipo && op.activo);
  }

  /**
   * Obtener operadores por grupo empresarial
   */
  static getPorGrupo(grupo: string): OperadorMovil[] {
    this.loadData();
    return this._data!.filter(
      (op) =>
        op.grupo_empresarial &&
        op.grupo_empresarial.toLowerCase().includes(grupo.toLowerCase())
    );
  }

  /**
   * Obtener OMVs que operan en una red específica
   */
  static getOMVsPorRed(redAnfitriona: string): OperadorMovil[] {
    this.loadData();
    return this._data!.filter(
      (op) =>
        op.tipo === 'OMV' &&
        op.red_anfitriona &&
        op.red_anfitriona.toLowerCase().includes(redAnfitriona.toLowerCase())
    );
  }

  /**
   * Obtener operadores con cobertura 5G
   */
  static getCon5G(): OperadorMovil[] {
    this.loadData();
    return this._data!.filter(
      (op) => op.activo && op.tecnologias.includes('5G')
    );
  }

  /**
   * Validar si un operador existe
   */
  static validar(nombreComercial: string): boolean {
    this.loadData();
    return this._data!.some(
      (op) =>
        op.nombre_comercial.toLowerCase() === nombreComercial.toLowerCase() &&
        op.activo
    );
  }

  /**
   * Obtener market share total por tipo
   */
  static getMarketSharePorTipo(): { OMR: number; OMV: number } {
    this.loadData();
    const omr = this._data!
      .filter((op) => op.tipo === 'OMR' && op.activo)
      .reduce((sum, op) => sum + op.market_share_aprox, 0);
    const omv = this._data!
      .filter((op) => op.tipo === 'OMV' && op.activo)
      .reduce((sum, op) => sum + op.market_share_aprox, 0);
    return { OMR: omr, OMV: omv };
  }
}
