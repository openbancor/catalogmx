/**
 * Catálogo de monedas y divisas internacionales (Banxico)
 */

import * as path from 'path';
import * as fs from 'fs';
import { MonedaDivisa } from '../../types';

interface MonedasDivisasData {
  metadata: {
    catalog: string;
    description: string;
    source: string;
    last_updated: string;
    notes: string;
  };
  monedas: MonedaDivisa[];
  tipo_cambio_fix: {
    descripcion: string;
    formula: string;
    publicacion: string;
    horario: string;
    uso: string;
  };
  regiones: Array<{
    region: string;
    monedas: string[];
  }>;
  estadisticas: {
    total_monedas: number;
    monedas_con_tipo_cambio_banxico: number;
    monedas_sin_decimales: number;
    regiones_cubiertas: number;
  };
}

export class MonedasDivisas {
  private static _data: MonedaDivisa[] | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(
      __dirname,
      '../../../../shared-data/banxico/monedas_divisas.json'
    );
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    const jsonData: MonedasDivisasData = JSON.parse(rawData);
    this._data = jsonData.monedas;
  }

  /**
   * Obtener todas las monedas
   */
  static getAll(): MonedaDivisa[] {
    this.loadData();
    return this._data!;
  }

  /**
   * Buscar moneda por código ISO
   */
  static getPorCodigo(codigoISO: string): MonedaDivisa | undefined {
    this.loadData();
    return this._data!.find((m) => m.codigo_iso.toUpperCase() === codigoISO.toUpperCase());
  }

  /**
   * Buscar monedas por país
   */
  static getPorPais(pais: string): MonedaDivisa[] {
    this.loadData();
    return this._data!.filter((m) => m.pais.toLowerCase().includes(pais.toLowerCase()));
  }

  /**
   * Obtener monedas con tipo de cambio publicado por Banxico
   */
  static getConTipoCambioBanxico(): MonedaDivisa[] {
    this.loadData();
    return this._data!.filter((m) => m.tipo_cambio_banxico);
  }

  /**
   * Obtener monedas con tipo de cambio FIX
   */
  static getConTipoCambioFIX(): MonedaDivisa[] {
    this.loadData();
    return this._data!.filter((m) => m.tipo_cambio_fix === true);
  }

  /**
   * Obtener monedas de una región específica
   */
  static getPorRegion(region: string): MonedaDivisa[] {
    this.loadData();
    const regiones: Record<string, string[]> = {
      'America del Norte': ['USD', 'CAD', 'MXN'],
      'America Latina': ['ARS', 'BRL', 'CLP', 'COP', 'PEN', 'GTQ', 'CRC', 'UYU', 'VES'],
      Europa: ['EUR', 'GBP', 'CHF', 'SEK', 'NOK', 'DKK', 'RUB'],
      'Asia-Pacifico': ['JPY', 'CNY', 'AUD', 'NZD', 'SGD', 'HKD', 'INR', 'KRW'],
      Africa: ['ZAR'],
    };

    const codigos = regiones[region] || [];
    return this._data!.filter((m) => codigos.includes(m.codigo_iso));
  }

  /**
   * Obtener monedas principales para operaciones en México
   */
  static getPrincipales(): MonedaDivisa[] {
    this.loadData();
    const principales = ['MXN', 'USD', 'EUR', 'CAD', 'GBP', 'JPY', 'CHF'];
    return this._data!.filter((m) => principales.includes(m.codigo_iso));
  }

  /**
   * Obtener monedas latinoamericanas
   */
  static getLatam(): MonedaDivisa[] {
    this.loadData();
    const latam = ['MXN', 'ARS', 'BRL', 'CLP', 'COP', 'PEN', 'GTQ', 'CRC', 'UYU', 'VES'];
    return this._data!.filter((m) => latam.includes(m.codigo_iso));
  }

  /**
   * Validar código ISO de moneda
   */
  static validarCodigoISO(codigo: string): boolean {
    this.loadData();
    return this._data!.some((m) => m.codigo_iso.toUpperCase() === codigo.toUpperCase());
  }

  /**
   * Obtener información de formato de moneda
   */
  static getFormatoMoneda(codigoISO: string): {
    simbolo: string;
    decimales: number;
    formato_ejemplo: string;
  } | null {
    const moneda = this.getPorCodigo(codigoISO);
    if (!moneda) return null;

    const ejemploMonto = 1234.56;
    const montoFormateado =
      moneda.decimales === 0
        ? Math.round(ejemploMonto).toString()
        : ejemploMonto.toFixed(moneda.decimales);

    return {
      simbolo: moneda.simbolo,
      decimales: moneda.decimales,
      formato_ejemplo: `${moneda.simbolo} ${montoFormateado}`,
    };
  }

  /**
   * Formatear monto en una moneda específica
   */
  static formatearMonto(monto: number, codigoISO: string): string {
    const moneda = this.getPorCodigo(codigoISO);
    if (!moneda) return monto.toString();

    const montoFormateado =
      moneda.decimales === 0
        ? Math.round(monto).toLocaleString('es-MX')
        : monto.toLocaleString('es-MX', {
            minimumFractionDigits: moneda.decimales,
            maximumFractionDigits: moneda.decimales,
          });

    return `${moneda.simbolo} ${montoFormateado}`;
  }

  /**
   * Obtener peso mexicano (MXN)
   */
  static getMXN(): MonedaDivisa | undefined {
    return this.getPorCodigo('MXN');
  }

  /**
   * Obtener dólar estadounidense (USD)
   */
  static getUSD(): MonedaDivisa | undefined {
    return this.getPorCodigo('USD');
  }

  /**
   * Obtener euro (EUR)
   */
  static getEUR(): MonedaDivisa | undefined {
    return this.getPorCodigo('EUR');
  }

  /**
   * Buscar monedas por nombre
   */
  static buscarPorNombre(nombre: string): MonedaDivisa[] {
    this.loadData();
    return this._data!.filter((m) => m.moneda.toLowerCase().includes(nombre.toLowerCase()));
  }

  /**
   * Obtener monedas activas
   */
  static getActivas(): MonedaDivisa[] {
    this.loadData();
    return this._data!.filter((m) => m.activa);
  }

  /**
   * Información del tipo de cambio FIX
   */
  static getInfoTipoCambioFIX(): {
    descripcion: string;
    horario: string;
    uso: string;
  } {
    return {
      descripcion:
        'Tipo de cambio FIX determinado por Banco de México - Promedio ponderado de cotizaciones del mercado de cambios al mayoreo',
      horario: '12:00 hrs (mediodía) tiempo de la Ciudad de México',
      uso: 'Referencia oficial para liquidación de obligaciones denominadas en dólares',
    };
  }
}
