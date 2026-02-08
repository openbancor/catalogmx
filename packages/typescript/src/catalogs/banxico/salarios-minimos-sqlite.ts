/**
 * Salarios Mínimos Catalog - SQLite Backend
 *
 * Uses HTTP VFS for efficient querying without downloading entire database.
 * Provides access to minimum wage data from Banco de México.
 */

import { HttpVfsUpdater } from '../../data/http-vfs-updater';

export interface SalarioMinimoRecord {
  fecha: string;
  salario_minimo: number;
  tipo: string;
  zona: string;
  periodo: string;
  serie: string;
  año: number;
  mes: number;
}

/**
 * Salarios Mínimos Catalog with auto-updating SQLite backend
 */
export class SalariosMinimosCatalog {
  private static updater: HttpVfsUpdater | null = null;

  /**
   * Get updater instance
   */
  private static getUpdater(): HttpVfsUpdater {
    if (!this.updater) {
      this.updater = new HttpVfsUpdater();
    }
    return this.updater;
  }

  /**
   * Convert SQL row to SalarioMinimo object
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- sql.js row type
  private static rowToSalario(row: any[]): SalarioMinimoRecord {
    return {
      fecha: row[0] as string,
      salario_minimo: row[1] as number,
      tipo: row[2] as string,
      zona: row[3] as string,
      periodo: row[4] as string,
      serie: row[5] as string,
      año: row[6] as number,
      mes: row[7] as number,
    };
  }

  /**
   * Get minimum wage for a specific date and zone
   */
  static async getPorFechaZona(
    fecha: string,
    zona: string = 'general'
  ): Promise<SalarioMinimoRecord | null> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT
        fecha,
        salario_diario AS salario_minimo,
        'diario' AS tipo,
        zona,
        'mensual' AS periodo,
        'banxico_salarios_minimos' AS serie,
        anio,
        mes
      FROM salarios_minimos
      WHERE fecha = ? AND zona = ?
      LIMIT 1
      `,
      [fecha, zona]
    );

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToSalario(result.values[0]);
  }

  /**
   * Get most recent minimum wage for a zone
   */
  static async getActualZona(zona: string = 'general'): Promise<SalarioMinimoRecord | null> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT
        fecha,
        salario_diario AS salario_minimo,
        'diario' AS tipo,
        zona,
        'mensual' AS periodo,
        'banxico_salarios_minimos' AS serie,
        anio,
        mes
      FROM salarios_minimos
      WHERE zona = ?
      ORDER BY fecha DESC
      LIMIT 1
      `,
      [zona]
    );

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToSalario(result.values[0]);
  }

  /**
   * Get most recent general minimum wage
   */
  static async getActualGeneral(): Promise<SalarioMinimoRecord | null> {
    return this.getActualZona('general');
  }

  /**
   * Get most recent border zone minimum wage
   */
  static async getActualFrontera(): Promise<SalarioMinimoRecord | null> {
    return this.getActualZona('frontera_norte');
  }

  /**
   * Get current minimum wage value for a zone
   */
  static async getSalarioActualZona(zona: string = 'general'): Promise<number | null> {
    const record = await this.getActualZona(zona);
    return record?.salario_minimo ?? null;
  }

  /**
   * Get all minimum wages for a specific year and zone
   */
  static async getPorAnioZona(
    anio: number,
    zona: string = 'general'
  ): Promise<SalarioMinimoRecord[]> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT
        fecha,
        salario_diario AS salario_minimo,
        'diario' AS tipo,
        zona,
        'mensual' AS periodo,
        'banxico_salarios_minimos' AS serie,
        anio,
        mes
      FROM salarios_minimos
      WHERE anio = ? AND zona = ?
      ORDER BY fecha
      `,
      [anio, zona]
    );

    return result.values.map((row) => this.rowToSalario(row));
  }

  /**
   * Close database connection (cleanup)
   */
  static close() {
    if (this.updater) {
      this.updater.close();
      this.updater = null;
    }
  }
}

// Convenience functions
export async function getSalarioMinimoActualGeneral(): Promise<SalarioMinimoRecord | null> {
  return SalariosMinimosCatalog.getActualGeneral();
}

export async function getSalarioMinimoActualFrontera(): Promise<SalarioMinimoRecord | null> {
  return SalariosMinimosCatalog.getActualFrontera();
}
