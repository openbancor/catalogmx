import { loadCatalog } from '../../utils/catalog-loader';
import { UDI } from '../../types';

/**
 * UDI (Unidades de Inversión) Catalog
 * Investment units indexed to inflation, used primarily for mortgages
 * and long-term financial instruments in Mexico
 * Published by Banco de México (Banxico)
 */
export class UDICatalog {
  private static _data: UDI[] | null = null;

  private static loadData(): void {
    if (this._data !== null) return;
    this._data = loadCatalog<UDI>('banxico/udis.json');
  }

  static getData(): UDI[] {
    this.loadData();
    return this._data!;
  }

  /**
   * Get UDI value for a specific date
   */
  static getPorFecha(fecha: string): UDI | undefined {
    return this.getData().find(u => u.fecha === fecha);
  }

  /**
   * Get UDI value for a specific year and month (monthly average)
   */
  static getPorMes(año: number, mes: number): UDI | undefined {
    return this.getData().find(u =>
      u.año === año && u.mes === mes && u.tipo === 'promedio_mensual'
    );
  }

  /**
   * Get annual average UDI for a specific year
   */
  static getPromedioAnual(año: number): UDI | undefined {
    return this.getData().find(u =>
      u.año === año && u.tipo === 'promedio_anual'
    );
  }

  /**
   * Get current UDI value (most recent)
   */
  static getActual(): UDI {
    const sorted = [...this.getData()].sort((a, b) =>
      new Date(b.fecha).getTime() - new Date(a.fecha).getTime()
    );
    return sorted[0];
  }

  /**
   * Get UDI value closest to a given date
   */
  static getValorCercano(fecha: string | Date): UDI | undefined {
    const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
    const sorted = [...this.getData()]
      .filter(u => u.tipo === 'promedio_mensual' || u.tipo === 'diario')
      .sort((a, b) => {
        const diffA = Math.abs(new Date(a.fecha).getTime() - date.getTime());
        const diffB = Math.abs(new Date(b.fecha).getTime() - date.getTime());
        return diffA - diffB;
      });

    return sorted[0];
  }

  /**
   * Convert pesos to UDIs for a specific date
   */
  static pesosAUdis(monto: number, fecha: string): number | undefined {
    const udi = this.getPorFecha(fecha) || this.getValorCercano(fecha);
    return udi ? monto / udi.valor : undefined;
  }

  /**
   * Convert UDIs to pesos for a specific date
   */
  static udisAPesos(udis: number, fecha: string): number | undefined {
    const udi = this.getPorFecha(fecha) || this.getValorCercano(fecha);
    return udi ? udis * udi.valor : undefined;
  }

  /**
   * Get historical UDI values for a date range
   */
  static getHistorico(fechaInicio: string, fechaFin: string): UDI[] {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);

    return this.getData()
      .filter(u => {
        const fecha = new Date(u.fecha);
        return fecha >= inicio && fecha <= fin;
      })
      .sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
  }

  /**
   * Get all UDI values for a specific year
   */
  static getPorAño(año: number): UDI[] {
    return this.getData()
      .filter(u => u.año === año)
      .sort((a, b) => (a.mes || 0) - (b.mes || 0));
  }

  /**
   * Calculate UDI variation between two dates (percentage)
   */
  static calcularVariacion(fechaInicial: string, fechaFinal: string): number | undefined {
    const udiInicial = this.getPorFecha(fechaInicial) || this.getValorCercano(fechaInicial);
    const udiFinal = this.getPorFecha(fechaFinal) || this.getValorCercano(fechaFinal);

    if (!udiInicial || !udiFinal) return undefined;
    return ((udiFinal.valor - udiInicial.valor) / udiInicial.valor) * 100;
  }

  /**
   * Get initial UDI value (April 4, 1995)
   */
  static getValorInicial(): UDI | undefined {
    return this.getData().find(u => u.tipo === 'valor_inicial');
  }
}
