/**
 * UDI (Unidades de Inversión) Catalog - SQLite Backend
 *
 * Uses HTTP VFS for efficient querying without downloading entire database.
 * Works in both Node.js and browser environments.
 */

import { HttpVfsUpdater, IncrementalDataQuery } from '../../data/http-vfs-updater';

export interface UDI {
  fecha: string;
  valor: number;
  año: number;
  mes: number;
  tipo: 'diario' | 'oficial_banxico' | 'promedio_mensual' | 'promedio_anual';
  moneda: string;
  notas?: string | null;
}

/**
 * UDI Catalog with auto-updating SQLite backend
 */
export class UDICatalog {
  private static updater: HttpVfsUpdater | null = null;
  private static incrementalQuery: IncrementalDataQuery | null = null;

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
   * Get incremental query instance
   */
  private static getIncrementalQuery(): IncrementalDataQuery {
    if (!this.incrementalQuery) {
      this.incrementalQuery = new IncrementalDataQuery();
    }
    return this.incrementalQuery;
  }

  /**
   * Convert SQL row to UDI object
   */
  private static rowToUDI(row: any[]): UDI {
    return {
      fecha: row[0] as string,
      valor: row[1] as number,
      año: row[2] as number,
      mes: row[3] as number,
      tipo: row[4] as any,
      moneda: row[5] as string,
      notas: row[6] as string | null,
    };
  }

  /**
   * Get UDI value for a specific date
   */
  static async getPorFecha(fecha: string): Promise<UDI | null> {
    const updater = this.getUpdater();

    // Try exact match first
    const result = await updater.query(
      `
      SELECT fecha, valor, anio, mes, tipo, moneda, notas
      FROM udis
      WHERE fecha = ? AND tipo IN ('diario', 'oficial_banxico')
      LIMIT 1
      `,
      [fecha]
    );

    if (result.values.length > 0) {
      return this.rowToUDI(result.values[0]);
    }

    // Try monthly average as fallback
    const [anio, mes] = fecha.split('-').map((v) => parseInt(v, 10));
    const monthlyResult = await updater.query(
      `
      SELECT fecha, valor, anio, mes, tipo, moneda, notas
      FROM udis
      WHERE anio = ? AND mes = ? AND tipo = 'promedio_mensual'
      LIMIT 1
      `,
      [anio, mes]
    );

    if (monthlyResult.values.length > 0) {
      return this.rowToUDI(monthlyResult.values[0]);
    }

    return null;
  }

  /**
   * Get most recent UDI value
   */
  static async getActual(): Promise<UDI | null> {
    const updater = this.getUpdater();

    const result = await updater.query(`
      SELECT fecha, valor, anio, mes, tipo, moneda, notas
      FROM udis
      WHERE tipo IN ('diario', 'oficial_banxico')
      ORDER BY fecha DESC
      LIMIT 1
    `);

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToUDI(result.values[0]);
  }

  /**
   * Get monthly average UDI
   */
  static async getPorMes(anio: number, mes: number): Promise<UDI | null> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, valor, anio, mes, tipo, moneda, notas
      FROM udis
      WHERE anio = ? AND mes = ? AND tipo = 'promedio_mensual'
      LIMIT 1
      `,
      [anio, mes]
    );

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToUDI(result.values[0]);
  }

  /**
   * Get annual average UDI
   */
  static async getPromedioAnual(anio: number): Promise<UDI | null> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, valor, anio, mes, tipo, moneda, notas
      FROM udis
      WHERE anio = ? AND tipo = 'promedio_anual'
      LIMIT 1
      `,
      [anio]
    );

    if (result.values.length === 0) {
      return null;
    }

    return this.rowToUDI(result.values[0]);
  }

  /**
   * Get all UDIs for a year
   */
  static async getPorAnio(anio: number): Promise<UDI[]> {
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, valor, anio, mes, tipo, moneda, notas
      FROM udis
      WHERE anio = ? AND tipo IN ('diario', 'oficial_banxico')
      ORDER BY fecha
      `,
      [anio]
    );

    return result.values.map((row) => this.rowToUDI(row));
  }

  /**
   * Get recent updates only (efficient)
   *
   * This method fetches only UDIs updated since last sync,
   * perfect for keeping local cache up to date.
   */
  static async getRecentUpdates(sinceDate?: string): Promise<UDI[]> {
    const since = sinceDate || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
    const updater = this.getUpdater();

    const result = await updater.query(
      `
      SELECT fecha, valor, anio, mes, tipo, moneda, notas
      FROM udis
      WHERE updated_at >= ?
      ORDER BY fecha DESC
      `,
      [since]
    );

    return result.values.map((row) => this.rowToUDI(row));
  }

  /**
   * Convert pesos to UDIs
   */
  static async pesosAUdis(pesos: number, fecha: string): Promise<number | null> {
    const udi = await this.getPorFecha(fecha);
    if (!udi) return null;
    return pesos / udi.valor;
  }

  /**
   * Convert UDIs to pesos
   */
  static async udisAPesos(udis: number, fecha: string): Promise<number | null> {
    const udi = await this.getPorFecha(fecha);
    if (!udi) return null;
    return udis * udi.valor;
  }

  /**
   * Calculate percentage variation between two dates
   */
  static async calcularVariacion(fechaInicio: string, fechaFin: string): Promise<number | null> {
    const udiInicio = await this.getPorFecha(fechaInicio);
    const udiFin = await this.getPorFecha(fechaFin);

    if (!udiInicio || !udiFin) return null;

    return ((udiFin.valor - udiInicio.valor) / udiInicio.valor) * 100;
  }

  /**
   * Sync local cache with remote updates
   *
   * Use this method to efficiently update local cache
   * without re-downloading everything.
   */
  static async syncWithRemote(localData: UDI[]): Promise<UDI[]> {
    const incrementalQuery = this.getIncrementalQuery();
    return incrementalQuery.syncTable('udis', localData);
  }

  /**
   * Close database connection (cleanup)
   */
  static close() {
    if (this.updater) {
      this.updater.close();
      this.updater = null;
    }
    if (this.incrementalQuery) {
      this.incrementalQuery.close();
      this.incrementalQuery = null;
    }
  }
}

// Convenience functions
export async function getUdiActual(): Promise<UDI | null> {
  return UDICatalog.getActual();
}

export async function getUdiPorFecha(fecha: string): Promise<UDI | null> {
  return UDICatalog.getPorFecha(fecha);
}

export async function pesosAUdis(pesos: number, fecha: string): Promise<number | null> {
  return UDICatalog.pesosAUdis(pesos, fecha);
}

export async function udisAPesos(udis: number, fecha: string): Promise<number | null> {
  return UDICatalog.udisAPesos(udis, fecha);
}

/**
 * Example usage:
 *
 * // Get current UDI
 * const udi = await getUdiActual();
 * console.log(`UDI actual: ${udi.valor}`);
 *
 * // Get UDI for specific date
 * const udiHoy = await getUdiPorFecha('2025-12-04');
 *
 * // Convert 100,000 pesos to UDIs
 * const udis = await pesosAUdis(100000, '2025-12-04');
 *
 * // Get only recent updates (last 7 days)
 * const updates = await UDICatalog.getRecentUpdates();
 * console.log(`${updates.length} UDIs updated in last 7 days`);
 */
