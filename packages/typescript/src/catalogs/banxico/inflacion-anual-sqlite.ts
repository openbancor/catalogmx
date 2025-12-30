/**
 * Inflación Anual Catalog - SQLite Backend
 *
 * Uses HTTP VFS for efficient querying without downloading entire database.
 * Provides access to annual inflation data (INPC) from Banco de México.
 */

import { HttpVfsUpdater } from '../../data/http-vfs-updater';

export interface InflacionAnualRecord {
  fecha: string;
  inflacion_anual: number;
  indice: string;
  tipo: string;
  año: number;
  mes: number;
}

/**
 * Inflación Anual Catalog with auto-updating SQLite backend
 */
export class InflacionAnualCatalog {
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
   * Convert SQL row to Inflacion object
   */
  private static rowToInflacion(row: any[]): InflacionAnualRecord {
    return {
      fecha: row[0] as string,
      inflacion_anual: row[1] as number,
      indice: row[2] as string,
      tipo: row[3] as string,
      año: row[4] as number,
      mes: row[5] as number,
    };
  }

  /**
   * Get inflation value for a specific date
   */
  static async getPorFecha(fecha: string): Promise<InflacionAnualRecord | null> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, inflacion_anual, indice, tipo, anio, mes
      FROM inflacion
      WHERE fecha = ?
      LIMIT 1
      `,
      [fecha]
    );

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToInflacion(result.values[0]);
  }

  /**
   * Get most recent inflation value
   */
  static async getActual(): Promise<InflacionAnualRecord | null> {
    const updater = this.getUpdater();

    const result = await updater.query(`
      SELECT fecha, inflacion_anual, indice, tipo, anio, mes
      FROM inflacion
      ORDER BY fecha DESC
      LIMIT 1
    `);

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToInflacion(result.values[0]);
  }

  /**
   * Get current inflation rate value
   */
  static async getTasaActual(): Promise<number | null> {
    const record = await this.getActual();
    return record?.inflacion_anual ?? null;
  }

  /**
   * Get all inflation values for a specific year
   */
  static async getPorAnio(anio: number): Promise<InflacionAnualRecord[]> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, inflacion_anual, indice, tipo, anio, mes
      FROM inflacion
      WHERE anio = ?
      ORDER BY fecha
      `,
      [anio]
    );

    return result.values.map((row) => this.rowToInflacion(row));
  }

  /**
   * Adjust amount for inflation between two dates
   */
  static async ajustarPorInflacion(
    monto: number,
    fechaOriginal: string,
    fechaActual: string
  ): Promise<number | null> {
    const recordOriginal = await this.getPorFecha(fechaOriginal);
    const recordActual = await this.getPorFecha(fechaActual);

    if (!recordOriginal || !recordActual) return null;

    const inflacionOriginal = recordOriginal.inflacion_anual / 100;
    const inflacionActual = recordActual.inflacion_anual / 100;

    const adjustmentFactor = (1 + inflacionActual) / (1 + inflacionOriginal);
    return monto * adjustmentFactor;
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
export async function getInflacionActual(): Promise<InflacionAnualRecord | null> {
  return InflacionAnualCatalog.getActual();
}

export async function getInflacionPorFecha(fecha: string): Promise<InflacionAnualRecord | null> {
  return InflacionAnualCatalog.getPorFecha(fecha);
}
