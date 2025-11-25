/**
 * Salarios Mínimos Catalog
 *
 * Provides access to minimum wage data from Banco de México.
 */

import salariosData from '../../../../shared-data/banxico/salarios_minimos.json';

export interface SalarioMinimoRecord {
  fecha: string;
  salario_minimo: number;
  tipo: string;
  zona: string;
  periodo: string;
  serie: string;
  año: number;
  mes: number;
  fuente: string;
  base_year?: number;
}

export class SalariosMinimosCatalog {
  private static data: SalarioMinimoRecord[] = salariosData as SalarioMinimoRecord[];

  static getData(): SalarioMinimoRecord[] {
    return [...this.data];
  }

  static getPorFechaZona(fecha: string, zona: string = 'general'): SalarioMinimoRecord | null {
    return this.data.find((r) => r.fecha === fecha && r.zona === zona) ?? null;
  }

  static getActualZona(zona: string = 'general'): SalarioMinimoRecord | null {
    const zoneRecords = this.data.filter((r) => r.zona === zona);
    if (zoneRecords.length === 0) return null;

    return zoneRecords.reduce((latest, record) => (record.fecha > latest.fecha ? record : latest));
  }

  static getActualGeneral(): SalarioMinimoRecord | null {
    return this.getActualZona('general');
  }

  static getActualFrontera(): SalarioMinimoRecord | null {
    return this.getActualZona('frontera_norte');
  }

  static getSalarioActualZona(zona: string = 'general'): number | null {
    return this.getActualZona(zona)?.salario_minimo ?? null;
  }
}

export function getSalarioMinimoActualGeneral(): SalarioMinimoRecord | null {
  return SalariosMinimosCatalog.getActualGeneral();
}

export function getSalarioMinimoActualFrontera(): SalarioMinimoRecord | null {
  return SalariosMinimosCatalog.getActualFrontera();
}
