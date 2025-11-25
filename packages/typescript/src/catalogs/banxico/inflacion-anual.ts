/**
 * Inflación Anual Catalog
 *
 * Provides access to annual inflation data (INPC) from Banco de México.
 */

import inflacionData from '../../../../shared-data/banxico/inflacion_anual.json';

export interface InflacionAnualRecord {
  fecha: string;
  inflacion_anual: number;
  indice: string;
  tipo: string;
  año: number;
  mes: number;
  fuente: string;
}

export class InflacionAnualCatalog {
  private static data: InflacionAnualRecord[] = inflacionData as InflacionAnualRecord[];
  private static byFecha: Map<string, InflacionAnualRecord> | null = null;

  private static _loadIndexes(): void {
    if (this.byFecha !== null) return;
    this.byFecha = new Map();
    for (const record of this.data) {
      this.byFecha.set(record.fecha, record);
    }
  }

  static getData(): InflacionAnualRecord[] {
    return [...this.data];
  }

  static getPorFecha(fecha: string): InflacionAnualRecord | null {
    this._loadIndexes();
    return this.byFecha!.get(fecha) ?? null;
  }

  static getActual(): InflacionAnualRecord | null {
    if (this.data.length === 0) return null;
    return this.data.reduce((latest, record) => (record.fecha > latest.fecha ? record : latest));
  }

  static getTasaActual(): number | null {
    return this.getActual()?.inflacion_anual ?? null;
  }

  static ajustarPorInflacion(
    monto: number,
    fechaOriginal: string,
    fechaActual: string
  ): number | null {
    const recordOriginal = this.getPorFecha(fechaOriginal);
    const recordActual = this.getPorFecha(fechaActual);

    if (!recordOriginal || !recordActual) return null;

    const inflacionOriginal = recordOriginal.inflacion_anual / 100;
    const inflacionActual = recordActual.inflacion_anual / 100;

    const adjustmentFactor = (1 + inflacionActual) / (1 + inflacionOriginal);
    return monto * adjustmentFactor;
  }
}

export function getInflacionActual(): InflacionAnualRecord | null {
  return InflacionAnualCatalog.getActual();
}
