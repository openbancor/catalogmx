/**
 * CETES 28 días Catalog - SQLite Backend
 *
 * Uses HTTP VFS for efficient querying without downloading entire database.
 * Works in both Node.js and browser environments.
 */

import { HttpVfsUpdater } from '../../data/http-vfs-updater';

export interface CETES28Record {
  fecha: string;
  tasa: number;
  plazo: number;
  instrumento: string;
  tipo: string;
  año: number;
  mes: number;
}

/**
 * CETES 28 Catalog with auto-updating SQLite backend
 */
export class CETES28Catalog {
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
   * Convert SQL row to CETES object
   */
  private static rowToCETES(row: any[]): CETES28Record {
    return {
      fecha: row[0] as string,
      tasa: row[1] as number,
      plazo: row[2] as number,
      instrumento: row[3] as string,
      tipo: row[4] as string,
      año: row[5] as number,
      mes: row[6] as number,
    };
  }

  /**
   * Get CETES value for a specific date
   */
  static async getPorFecha(fecha: string): Promise<CETES28Record | null> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, tasa, plazo, instrumento, tipo, anio, mes
      FROM cetes
      WHERE fecha = ? AND plazo = 28
      LIMIT 1
      `,
      [fecha]
    );

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToCETES(result.values[0]);
  }

  /**
   * Get most recent CETES value
   */
  static async getActual(): Promise<CETES28Record | null> {
    const updater = this.getUpdater();

    const result = await updater.query(`
      SELECT fecha, tasa, plazo, instrumento, tipo, anio, mes
      FROM cetes
      WHERE plazo = 28
      ORDER BY fecha DESC
      LIMIT 1
    `);

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToCETES(result.values[0]);
  }

  /**
   * Get current CETES rate value
   */
  static async getTasaActual(): Promise<number | null> {
    const record = await this.getActual();
    return record?.tasa ?? null;
  }

  /**
   * Get all CETES values for a specific year
   */
  static async getPorAnio(anio: number): Promise<CETES28Record[]> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, tasa, plazo, instrumento, tipo, anio, mes
      FROM cetes
      WHERE anio = ? AND plazo = 28
      ORDER BY fecha
      `,
      [anio]
    );

    return result.values.map((row) => this.rowToCETES(row));
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
export async function getCETESActual(): Promise<CETES28Record | null> {
  return CETES28Catalog.getActual();
}

export async function getCETESPorFecha(fecha: string): Promise<CETES28Record | null> {
  return CETES28Catalog.getPorFecha(fecha);
}
