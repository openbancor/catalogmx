import { loadCatalogArray } from '../../utils/catalog-loader';
import { UDI } from '../../types';

/**
 * UDI (Unidades de Inversión) Catalog
 * Investment units indexed to inflation, used primarily for mortgages
 * and long-term financial instruments in Mexico
 * Published by Banco de México (Banxico)
 */
export class UDICatalog {
  private static _data: UDI[] | null = null;
  private static _byFecha: Map<string, UDI> | null = null;
  private static _mensual: Map<string, UDI> | null = null;
  private static _anual: Map<number, UDI> | null = null;
  private static _daily: UDI[] | null = null;

  private static loadData(): void {
    if (this._data === null) {
      this._data = loadCatalogArray<UDI>('banxico/udis.json');
    }
    if (this._byFecha !== null) return;

    this._byFecha = new Map();
    this._mensual = new Map();
    this._anual = new Map();
    const daily: UDI[] = [];

    for (const item of this._data!) {
      const existing = this._byFecha.get(item.fecha);
      if (!existing || (item.tipo === 'diario' && existing.tipo !== 'diario')) {
        this._byFecha.set(item.fecha, item);
      }

      if (item.tipo === 'diario') {
        daily.push(item);
      } else if (item.tipo === 'promedio_mensual' && item.mes) {
        this._mensual.set(`${item.año}-${item.mes.toString().padStart(2, '0')}`, item);
      } else if (item.tipo === 'promedio_anual') {
        this._anual.set(item.año, item);
      }
    }

    daily.sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
    this._daily = daily;
  }

  static getData(): UDI[] {
    this.loadData();
    return this._data!;
  }

  private static getByDate(fecha: string): UDI | undefined {
    this.loadData();
    const registro = this._byFecha!.get(fecha);
    if (registro && registro.tipo === 'diario') {
      return registro;
    }

    // Prefer a monthly average if it exists for the same month/year
    if (registro) {
      return registro;
    }

    const [anio, mes, _day] = fecha.split('-').map(Number);
    if (anio && mes) {
      const mensual = this._mensual!.get(`${anio}-${mes.toString().padStart(2, '0')}`);
      if (mensual) {
        return mensual;
      }
    }

    return undefined;
  }

  /**
   * Get UDI value for a specific date
   */
  static getPorFecha(fecha: string): UDI | undefined {
    return this.getByDate(fecha);
  }

  /**
   * Get UDI value for a specific year and month (monthly average)
   */
  static getPorMes(año: number, mes: number): UDI | undefined {
    this.loadData();
    return this._mensual!.get(`${año}-${mes.toString().padStart(2, '0')}`);
  }

  /**
   * Get annual average UDI for a specific year
   */
  static getPromedioAnual(año: number): UDI | undefined {
    this.loadData();
    return this._anual!.get(año);
  }

  /**
   * Get current UDI value (most recent)
   */
  static getActual(): UDI {
    this.loadData();
    if (this._daily && this._daily.length > 0) {
      return this._daily[this._daily.length - 1];
    }

    const sorted = [...this.getData()].sort(
      (a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime()
    );
    return sorted[0];
  }

  /**
   * Get UDI value closest to a given date
   */
  static getValorCercano(fecha: string | Date): UDI | undefined {
    const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
    this.loadData();

    const candidates =
      this._daily && this._daily.length > 0
        ? this._daily
        : this.getData().filter((u) => u.tipo === 'promedio_mensual');

    let closest: UDI | undefined;
    let smallestDiff = Number.POSITIVE_INFINITY;

    for (const item of candidates) {
      const diff = Math.abs(new Date(item.fecha).getTime() - date.getTime());
      if (diff < smallestDiff) {
        smallestDiff = diff;
        closest = item;
      }
    }

    return closest;
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
    this.loadData();

    const source =
      this._daily && this._daily.length > 0
        ? this._daily
        : this.getData().filter((u) => u.tipo === 'promedio_mensual');

    return source
      .filter((u) => {
        const fecha = new Date(u.fecha);
        return fecha >= inicio && fecha <= fin;
      })
      .sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
  }

  /**
   * Get all UDI values for a specific year
   */
  static getPorAño(año: number): UDI[] {
    this.loadData();
    const source =
      this._daily && this._daily.length > 0
        ? this._daily
        : this.getData().filter((u) => u.tipo === 'promedio_mensual');

    return source
      .filter((u) => u.año === año)
      .sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
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
    return this.getData().find((u) => u.tipo === 'valor_inicial');
  }
}
