/**
 * USD/MXN Exchange Rate FIX Catalog - SQLite Backend
 *
 * Uses HTTP VFS for efficient querying without downloading entire database.
 * Works in both Node.js and browser environments.
 */

import { HttpVfsUpdater } from '../../data/http-vfs-updater';

export interface TipoCambioRecord {
  fecha: string;
  tipo_cambio: number;
  moneda_origen: string;
  moneda_destino: string;
  fuente: string;
  año: number;
  mes: number;
}

/**
 * Tipo de Cambio USD Catalog with auto-updating SQLite backend
 */
export class TipoCambioUSDCatalog {
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
   * Convert SQL row to TipoCambio object
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- sql.js row type
  private static rowToTipoCambio(row: any[]): TipoCambioRecord {
    return {
      fecha: row[0] as string,
      tipo_cambio: row[1] as number,
      moneda_origen: row[2] as string,
      moneda_destino: row[3] as string,
      fuente: row[4] as string,
      año: row[5] as number,
      mes: row[6] as number,
    };
  }

  /**
   * Get exchange rate for a specific date
   */
  static async getPorFecha(fecha: string): Promise<TipoCambioRecord | null> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, tipo_cambio, moneda_origen, moneda_destino, fuente, anio, mes
      FROM tipo_cambio
      WHERE fecha = ? AND fuente = 'FIX'
      LIMIT 1
      `,
      [fecha]
    );

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToTipoCambio(result.values[0]);
  }

  /**
   * Get all exchange rates for a specific year
   */
  static async getPorAnio(anio: number): Promise<TipoCambioRecord[]> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, tipo_cambio, moneda_origen, moneda_destino, fuente, anio, mes
      FROM tipo_cambio
      WHERE anio = ? AND fuente = 'FIX'
      ORDER BY fecha
      `,
      [anio]
    );

    return result.values.map((row) => this.rowToTipoCambio(row));
  }

  /**
   * Get most recent exchange rate
   */
  static async getActual(): Promise<TipoCambioRecord | null> {
    const updater = this.getUpdater();

    const result = await updater.query(`
      SELECT fecha, tipo_cambio, moneda_origen, moneda_destino, fuente, anio, mes
      FROM tipo_cambio
      WHERE fuente = 'FIX'
      ORDER BY fecha DESC
      LIMIT 1
    `);

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToTipoCambio(result.values[0]);
  }

  /**
   * Get current exchange rate value
   */
  static async getValorActual(): Promise<number | null> {
    const record = await this.getActual();
    return record?.tipo_cambio ?? null;
  }

  /**
   * Convert USD to MXN
   */
  static async usdAMxn(usd: number, fecha?: string): Promise<number | null> {
    const record = fecha ? await this.getPorFecha(fecha) : await this.getActual();
    if (!record) return null;
    return usd * record.tipo_cambio;
  }

  /**
   * Convert MXN to USD
   */
  static async mxnAUsd(mxn: number, fecha?: string): Promise<number | null> {
    const record = fecha ? await this.getPorFecha(fecha) : await this.getActual();
    if (!record) return null;
    return mxn / record.tipo_cambio;
  }

  /**
   * Calculate percentage variation between two dates
   */
  static async calcularVariacion(fechaInicio: string, fechaFin: string): Promise<number | null> {
    const recordInicio = await this.getPorFecha(fechaInicio);
    const recordFin = await this.getPorFecha(fechaFin);

    if (!recordInicio || !recordFin) return null;

    return ((recordFin.tipo_cambio - recordInicio.tipo_cambio) / recordInicio.tipo_cambio) * 100;
  }

  /**
   * Calculate annual average exchange rate
   */
  static async getPromedioAnual(anio: number): Promise<number | null> {
    const records = await this.getPorAnio(anio);
    if (records.length === 0) return null;

    const sum = records.reduce((acc, r) => acc + r.tipo_cambio, 0);
    return sum / records.length;
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
export async function getTipoCambioActual(): Promise<TipoCambioRecord | null> {
  return TipoCambioUSDCatalog.getActual();
}

export async function getTipoCambioPorFecha(fecha: string): Promise<TipoCambioRecord | null> {
  return TipoCambioUSDCatalog.getPorFecha(fecha);
}

export async function usdAMxn(usd: number, fecha?: string): Promise<number | null> {
  return TipoCambioUSDCatalog.usdAMxn(usd, fecha);
}

export async function mxnAUsd(mxn: number, fecha?: string): Promise<number | null> {
  return TipoCambioUSDCatalog.mxnAUsd(mxn, fecha);
}
