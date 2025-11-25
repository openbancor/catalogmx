/**
 * CETES 28 días Catalog
 *
 * Provides access to CETES 28-day values from Banco de México.
 */

import cetesData from '../../../../shared-data/banxico/cetes_28.json';

export interface CETES28Record {
  fecha: string;
  tasa: number;
  plazo_dias: number;
  instrumento: string;
  tipo: string;
  año: number;
  mes: number;
  fuente: string;
}

export class CETES28Catalog {
  private static data: CETES28Record[] = cetesData as CETES28Record[];
  private static byFecha: Map<string, CETES28Record> | null = null;

  private static _loadIndexes(): void {
    if (this.byFecha !== null) return;
    this.byFecha = new Map();
    for (const record of this.data) {
      this.byFecha.set(record.fecha, record);
    }
  }

  static getData(): CETES28Record[] {
    return [...this.data];
  }

  static getPorFecha(fecha: string): CETES28Record | null {
    this._loadIndexes();
    return this.byFecha!.get(fecha) ?? null;
  }

  static getActual(): CETES28Record | null {
    if (this.data.length === 0) return null;
    return this.data.reduce((latest, record) => (record.fecha > latest.fecha ? record : latest));
  }

  static getTasaActual(): number | null {
    return this.getActual()?.tasa ?? null;
  }
}

export function getCETESActual(): CETES28Record | null {
  return CETES28Catalog.getActual();
}
