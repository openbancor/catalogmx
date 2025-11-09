/**
 * SAT Carta Porte 3.0 - Configuración de Autotransporte
 * Vehicle configurations for road transport
 */

import { loadCatalog } from '../../../utils/catalog-loader';
import type { ConfigAutotransporte } from '../../../types';

export class ConfigAutotransporteCatalog {
  private static _data: ConfigAutotransporte[] | null = null;

  private static getData(): ConfigAutotransporte[] {
    if (!this._data) {
      this._data = loadCatalog<ConfigAutotransporte>('sat/carta_porte_3/config_autotransporte.json');
    }
    return this._data;
  }

  static getAll(): ConfigAutotransporte[] {
    return this.getData();
  }

  static getConfig(code: string): ConfigAutotransporte | undefined {
    return this.getData().find(c => c.code === code.toUpperCase());
  }

  static isValid(code: string): boolean {
    return this.getData().some(c => c.code === code.toUpperCase());
  }

  /**
   * Check if configuration requires trailer
   */
  static requiresRemolque(code: string): boolean {
    const config = this.getConfig(code);
    return config?.remolque === true;
  }

  /**
   * Get configurations with trailer
   */
  static getWithRemolque(): ConfigAutotransporte[] {
    return this.getData().filter(c => c.remolque);
  }

  /**
   * Get configurations without trailer
   */
  static getWithoutRemolque(): ConfigAutotransporte[] {
    return this.getData().filter(c => !c.remolque);
  }

  /**
   * Get number of axles for configuration
   */
  static getNumEjes(code: string): number | undefined {
    return this.getConfig(code)?.num_ejes;
  }

  /**
   * Search configurations by description
   */
  static searchByDescription(keyword: string): ConfigAutotransporte[] {
    const search = keyword.toUpperCase();
    return this.getData().filter(c =>
      c.descripcion.toUpperCase().includes(search)
    );
  }
}
