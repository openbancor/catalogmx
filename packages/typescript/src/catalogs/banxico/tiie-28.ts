/**
 * TIIE 28 días Catalog
 *
 * Provides access to TIIE 28-day values from Banco de México.
 * TIIE (Tasa de Interés Interbancaria de Equilibrio) is the interbank equilibrium interest rate.
 */

import tiieData from '../../../../shared-data/banxico/tiie_28.json';

export interface TIIE28Record {
  fecha: string;
  tasa: number;
  plazo_dias: number;
  tipo: string;
  año: number;
  mes: number;
  fuente: string;
}

export class TIIE28Catalog {
  private static data: TIIE28Record[] = tiieData as TIIE28Record[];
  private static byFecha: Map<string, TIIE28Record> | null = null;

  private static _loadIndexes(): void {
    if (this.byFecha !== null) return;
    this.byFecha = new Map();
    for (const record of this.data) {
      this.byFecha.set(record.fecha, record);
    }
  }

  static getData(): TIIE28Record[] {
    return [...this.data];
  }

  static getPorFecha(fecha: string): TIIE28Record | null {
    this._loadIndexes();
    return this.byFecha!.get(fecha) ?? null;
  }

  static getActual(): TIIE28Record | null {
    if (this.data.length === 0) return null;
    return this.data.reduce((latest, record) => (record.fecha > latest.fecha ? record : latest));
  }

  static getTasaActual(): number | null {
    return this.getActual()?.tasa ?? null;
  }
}

export function getTIIEActual(): TIIE28Record | null {
  return TIIE28Catalog.getActual();
}
