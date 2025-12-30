/**
 * TIIE 28 días Catalog - SQLite Backend
 *
 * Uses HTTP VFS for efficient querying without downloading entire database.
 * TIIE (Tasa de Interés Interbancaria de Equilibrio) is the interbank equilibrium interest rate.
 */

import { HttpVfsUpdater } from '../../data/http-vfs-updater';

export interface TIIE28Record {
  fecha: string;
  tasa: number;
  plazo: number;
  tipo: string;
  año: number;
  mes: number;
}

/**
 * TIIE 28 Catalog with auto-updating SQLite backend
 */
export class TIIE28Catalog {
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
   * Convert SQL row to TIIE object
   */
  private static rowToTIIE(row: any[]): TIIE28Record {
    return {
      fecha: row[0] as string,
      tasa: row[1] as number,
      plazo: row[2] as number,
      tipo: row[3] as string,
      año: row[4] as number,
      mes: row[5] as number,
    };
  }

  /**
   * Get TIIE value for a specific date
   */
  static async getPorFecha(fecha: string): Promise<TIIE28Record | null> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, tasa, plazo, tipo, anio, mes
      FROM tiie
      WHERE fecha = ? AND plazo = 28
      LIMIT 1
      `,
      [fecha]
    );

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToTIIE(result.values[0]);
  }

  /**
   * Get most recent TIIE value
   */
  static async getActual(): Promise<TIIE28Record | null> {
    const updater = this.getUpdater();

    const result = await updater.query(`
      SELECT fecha, tasa, plazo, tipo, anio, mes
      FROM tiie
      WHERE plazo = 28
      ORDER BY fecha DESC
      LIMIT 1
    `);

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToTIIE(result.values[0]);
  }

  /**
   * Get current TIIE rate value
   */
  static async getTasaActual(): Promise<number | null> {
    const record = await this.getActual();
    return record?.tasa ?? null;
  }

  /**
   * Get all TIIE values for a specific year
   */
  static async getPorAnio(anio: number): Promise<TIIE28Record[]> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, tasa, plazo, tipo, anio, mes
      FROM tiie
      WHERE anio = ? AND plazo = 28
      ORDER BY fecha
      `,
      [anio]
    );

    return result.values.map((row) => this.rowToTIIE(row));
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
export async function getTIIEActual(): Promise<TIIE28Record | null> {
  return TIIE28Catalog.getActual();
}

export async function getTIIEPorFecha(fecha: string): Promise<TIIE28Record | null> {
  return TIIE28Catalog.getPorFecha(fecha);
}
