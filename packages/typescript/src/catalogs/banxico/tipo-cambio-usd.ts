/**
 * USD/MXN Exchange Rate FIX Catalog
 *
 * Provides access to USD/MXN exchange rate FIX values from Banco de México.
 * The FIX rate is the official exchange rate determined daily by Banxico.
 */

import tipoCambioData from '../../../../shared-data/banxico/tipo_cambio_usd.json';

export interface TipoCambioRecord {
  fecha: string;
  tipo_cambio: number;
  moneda_origen: string;
  moneda_destino: string;
  tipo: string;
  año: number;
  mes: number;
  fuente: string;
}

export class TipoCambioUSDCatalog {
  private static data: TipoCambioRecord[] = tipoCambioData as TipoCambioRecord[];
  private static byFecha: Map<string, TipoCambioRecord> | null = null;
  private static byAnio: Map<number, TipoCambioRecord[]> | null = null;

  private static _loadIndexes(): void {
    if (this.byFecha !== null) return;

    this.byFecha = new Map();
    this.byAnio = new Map();

    for (const record of this.data) {
      this.byFecha.set(record.fecha, record);

      if (!this.byAnio.has(record.año)) {
        this.byAnio.set(record.año, []);
      }
      this.byAnio.get(record.año)!.push(record);
    }

    // Sort by date within each year
    for (const records of this.byAnio.values()) {
      records.sort((a, b) => a.fecha.localeCompare(b.fecha));
    }
  }

  /**
   * Get all exchange rate data
   */
  static getData(): TipoCambioRecord[] {
    return [...this.data];
  }

  /**
   * Get exchange rate for a specific date
   */
  static getPorFecha(fecha: string): TipoCambioRecord | null {
    this._loadIndexes();
    return this.byFecha!.get(fecha) ?? null;
  }

  /**
   * Get all exchange rates for a specific year
   */
  static getPorAnio(anio: number): TipoCambioRecord[] {
    this._loadIndexes();
    return this.byAnio!.get(anio) ?? [];
  }

  /**
   * Get most recent exchange rate
   */
  static getActual(): TipoCambioRecord | null {
    if (this.data.length === 0) return null;
    return this.data.reduce((latest, record) => (record.fecha > latest.fecha ? record : latest));
  }

  /**
   * Get current exchange rate value
   */
  static getValorActual(): number | null {
    const record = this.getActual();
    return record?.tipo_cambio ?? null;
  }

  /**
   * Convert USD to MXN
   */
  static usdAMxn(usd: number, fecha?: string): number | null {
    const record = fecha ? this.getPorFecha(fecha) : this.getActual();
    if (!record) return null;
    return usd * record.tipo_cambio;
  }

  /**
   * Convert MXN to USD
   */
  static mxnAUsd(mxn: number, fecha?: string): number | null {
    const record = fecha ? this.getPorFecha(fecha) : this.getActual();
    if (!record) return null;
    return mxn / record.tipo_cambio;
  }

  /**
   * Calculate percentage variation between two dates
   */
  static calcularVariacion(fechaInicio: string, fechaFin: string): number | null {
    const recordInicio = this.getPorFecha(fechaInicio);
    const recordFin = this.getPorFecha(fechaFin);

    if (!recordInicio || !recordFin) return null;

    return ((recordFin.tipo_cambio - recordInicio.tipo_cambio) / recordInicio.tipo_cambio) * 100;
  }

  /**
   * Calculate annual average exchange rate
   */
  static getPromedioAnual(anio: number): number | null {
    const records = this.getPorAnio(anio);
    if (records.length === 0) return null;

    const sum = records.reduce((acc, r) => acc + r.tipo_cambio, 0);
    return sum / records.length;
  }
}

// Convenience functions
export function getTipoCambioActual(): TipoCambioRecord | null {
  return TipoCambioUSDCatalog.getActual();
}

export function getTipoCambioPorFecha(fecha: string): TipoCambioRecord | null {
  return TipoCambioUSDCatalog.getPorFecha(fecha);
}

export function usdAMxn(usd: number, fecha?: string): number | null {
  return TipoCambioUSDCatalog.usdAMxn(usd, fecha);
}

export function mxnAUsd(mxn: number, fecha?: string): number | null {
  return TipoCambioUSDCatalog.mxnAUsd(mxn, fecha);
}
