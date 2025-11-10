/**
 * Calculadoras de impuestos: IVA, IEPS, Retenciones e Impuestos Locales
 *
 * Provee métodos para calcular IVA, IEPS y retenciones según las leyes mexicanas
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  IVATasa,
  IEPSCategoria,
  RetencionISR,
  RetencionIVA,
  ImpuestoEstatal,
  IVACalculationResult,
  IEPSCalculationResult,
  RetencionCalculationResult,
} from '../types';

interface IVAData {
  metadata: object;
  tasas: IVATasa[];
  exenciones: any[];
  tasa_cero_productos: any[];
}

interface RetencionesData {
  metadata: object;
  isr_retenciones: RetencionISR[];
  iva_retenciones: RetencionIVA[];
  retenciones_definitivas: any[];
}

interface ImpuestosLocalesData {
  metadata: object;
  impuesto_nomina: ImpuestoEstatal[];
  impuesto_hospedaje: ImpuestoEstatal[];
  otros_impuestos_estatales: any[];
  predial: object;
}

/**
 * Calculadora de IVA
 */
export class IVACalculator {
  private static _data: IVAData | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(__dirname, '../../../shared-data/sat/impuestos/iva_tasas.json');
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._data = JSON.parse(rawData) as IVAData;
  }

  /**
   * Obtiene la tasa de IVA vigente para una fecha
   * @param fecha - Fecha en formato ISO (YYYY-MM-DD) o Date
   * @param tipoTasa - Tipo de tasa (general, frontera, tasa_cero)
   * @returns Tasa de IVA vigente
   */
  static getTasaVigente(
    fecha: string | Date = new Date(),
    tipoTasa: 'general' | 'frontera' | 'tasa_cero' = 'general'
  ): IVATasa | undefined {
    this.loadData();

    const fechaDate = typeof fecha === 'string' ? new Date(fecha) : fecha;

    const tasasDelTipo = this._data!.tasas.filter((t) => t.tipo === tipoTasa);

    return tasasDelTipo.find((tasa) => {
      const inicioDate = new Date(tasa.vigencia_inicio);
      const finDate = tasa.vigencia_fin ? new Date(tasa.vigencia_fin) : null;

      const despuesInicio = fechaDate >= inicioDate;
      const antesFin = !finDate || fechaDate <= finDate;

      return despuesInicio && antesFin;
    });
  }

  /**
   * Calcula el IVA para una cantidad base
   * @param base - Monto base sin IVA
   * @param tipoTasa - Tipo de tasa (general, frontera, tasa_cero)
   * @param fecha - Fecha para determinar tasa vigente
   * @returns Resultado del cálculo
   */
  static calcular(
    base: number,
    tipoTasa: 'general' | 'frontera' | 'tasa_cero' = 'general',
    fecha: string | Date = new Date()
  ): IVACalculationResult {
    const tasaObj = this.getTasaVigente(fecha, tipoTasa);

    if (!tasaObj) {
      throw new Error(`No se encontró tasa de IVA vigente para tipo ${tipoTasa} y fecha ${fecha}`);
    }

    const tasa = tasaObj.tasa;
    const iva = base * (tasa / 100);
    const totalConIva = base + iva;

    return {
      base,
      tasa,
      iva,
      total_con_iva: totalConIva,
      tipo_tasa: tipoTasa,
    };
  }

  /**
   * Calcula el IVA ya incluido en un total
   * (Desglose de IVA cuando el precio incluye IVA)
   * @param totalConIva - Monto total que incluye IVA
   * @param tipoTasa - Tipo de tasa
   * @param fecha - Fecha para determinar tasa vigente
   * @returns Resultado del cálculo
   */
  static calcularIncluido(
    totalConIva: number,
    tipoTasa: 'general' | 'frontera' | 'tasa_cero' = 'general',
    fecha: string | Date = new Date()
  ): IVACalculationResult {
    const tasaObj = this.getTasaVigente(fecha, tipoTasa);

    if (!tasaObj) {
      throw new Error(`No se encontró tasa de IVA vigente`);
    }

    const tasa = tasaObj.tasa;
    const base = totalConIva / (1 + tasa / 100);
    const iva = totalConIva - base;

    return {
      base,
      tasa,
      iva,
      total_con_iva: totalConIva,
      tipo_tasa: tipoTasa,
    };
  }

  /**
   * Obtiene todas las tasas históricas
   * @returns Array de tasas IVA
   */
  static getAllTasas(): IVATasa[] {
    this.loadData();
    return [...this._data!.tasas];
  }
}

/**
 * Calculadora de IEPS
 */
export class IEPSCalculator {
  private static _data: IEPSCategoria[] | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(__dirname, '../../../shared-data/sat/impuestos/ieps_tasas.json');
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._data = JSON.parse(rawData) as IEPSCategoria[];
  }

  /**
   * Obtiene una categoría de IEPS
   * @param categoria - Nombre de la categoría
   * @returns Categoría de IEPS o undefined
   */
  static getCategoria(categoria: string): IEPSCategoria | undefined {
    this.loadData();
    return this._data!.find((c) => c.categoria === categoria);
  }

  /**
   * Calcula IEPS ad-valorem (porcentaje sobre el valor)
   * @param base - Valor base
   * @param tasa - Tasa de IEPS en porcentaje
   * @returns Resultado del cálculo
   */
  static calcularAdValorem(base: number, tasa: number): IEPSCalculationResult {
    const ieps = base * (tasa / 100);

    return {
      base,
      tasa,
      ieps,
      tipo_calculo: 'ad_valorem',
    };
  }

  /**
   * Calcula IEPS por cuota fija (cantidad * tasa)
   * @param cantidad - Cantidad de unidades
   * @param cuotaPorUnidad - Cuota fija por unidad
   * @param unidad - Unidad de medida
   * @returns Resultado del cálculo
   */
  static calcularCuotaFija(
    cantidad: number,
    cuotaPorUnidad: number,
    unidad: string = 'litro'
  ): IEPSCalculationResult {
    const ieps = cantidad * cuotaPorUnidad;

    return {
      base: cantidad,
      tasa: cuotaPorUnidad,
      ieps,
      tipo_calculo: 'cuota_fija',
      unidad,
      cantidad,
    };
  }

  /**
   * Calcula IEPS para bebidas alcohólicas
   * @param valor - Valor del producto
   * @param gradosAlcohol - Grados de alcohol
   * @returns Resultado del cálculo
   */
  static calcularBebidasAlcoholicas(valor: number, gradosAlcohol: number): IEPSCalculationResult {
    let tasa = 0;

    if (gradosAlcohol <= 14) {
      tasa = 26.5; // Cerveza y bebidas hasta 14°
    } else if (gradosAlcohol <= 20) {
      tasa = 30.0; // Bebidas de 14° a 20°
    } else {
      tasa = 53.0; // Bebidas mayores a 20°
    }

    return this.calcularAdValorem(valor, tasa);
  }

  /**
   * Calcula IEPS para cigarros
   * @param valor - Valor de venta
   * @param numeroCigarros - Número de cigarros
   * @returns Resultado del cálculo
   */
  static calcularCigarros(valor: number, numeroCigarros: number): IEPSCalculationResult {
    // IEPS = 160% del valor + $0.5080 por cigarro
    const iepsAdValorem = valor * (160 / 100);
    const iepsCuotaFija = numeroCigarros * 0.508;
    const iepsTotal = iepsAdValorem + iepsCuotaFija;

    return {
      base: valor,
      tasa: 160,
      ieps: iepsTotal,
      tipo_calculo: 'ad_valorem',
      cantidad: numeroCigarros,
    };
  }

  /**
   * Obtiene todas las categorías de IEPS
   * @returns Array de categorías
   */
  static getAllCategorias(): IEPSCategoria[] {
    this.loadData();
    return [...this._data!];
  }
}

/**
 * Calculadora de Retenciones
 */
export class RetencionCalculator {
  private static _data: RetencionesData | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(__dirname, '../../../shared-data/sat/impuestos/retenciones.json');
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._data = JSON.parse(rawData) as RetencionesData;
  }

  /**
   * Obtiene información de retención ISR por concepto
   * @param concepto - Concepto de retención
   * @returns Retención ISR o undefined
   */
  static getRetencionISR(concepto: string): RetencionISR | undefined {
    this.loadData();
    return this._data!.isr_retenciones.find((r) => r.concepto === concepto);
  }

  /**
   * Obtiene información de retención IVA por concepto
   * @param concepto - Concepto de retención
   * @returns Retención IVA o undefined
   */
  static getRetencionIVA(concepto: string): RetencionIVA | undefined {
    this.loadData();
    return this._data!.iva_retenciones.find((r) => r.concepto === concepto);
  }

  /**
   * Calcula retención de ISR
   * @param base - Base para la retención
   * @param concepto - Concepto de retención
   * @returns Resultado del cálculo
   */
  static calcularRetencionISR(base: number, concepto: string): RetencionCalculationResult {
    const retencion = this.getRetencionISR(concepto);

    if (!retencion) {
      throw new Error(`No se encontró retención ISR para concepto: ${concepto}`);
    }

    if (typeof retencion.tasa === 'string') {
      throw new Error(`La tasa de ${concepto} es variable. Use método específico.`);
    }

    const montoRetencion = base * (retencion.tasa / 100);

    return {
      concepto: retencion.concepto,
      base,
      tasa: retencion.tasa,
      retencion: montoRetencion,
    };
  }

  /**
   * Calcula retención de IVA (2/3 partes)
   * @param ivaTrasladado - IVA trasladado
   * @param concepto - Concepto de retención
   * @returns Resultado del cálculo
   */
  static calcularRetencionIVA(ivaTrasladado: number, concepto: string): RetencionCalculationResult {
    const retencion = this.getRetencionIVA(concepto);

    if (!retencion) {
      throw new Error(`No se encontró retención IVA para concepto: ${concepto}`);
    }

    const montoRetencion = ivaTrasladado * (retencion.tasa / 100);

    return {
      concepto: retencion.concepto,
      base: ivaTrasladado,
      tasa: retencion.tasa,
      retencion: montoRetencion,
      impuesto_base: ivaTrasladado,
    };
  }

  /**
   * Calcula retención de honorarios (10% ISR)
   * @param montoSinIVA - Monto de honorarios sin IVA
   * @returns Resultado del cálculo
   */
  static calcularHonorarios(montoSinIVA: number): RetencionCalculationResult {
    return this.calcularRetencionISR(montoSinIVA, 'honorarios');
  }

  /**
   * Calcula retención de arrendamiento (10% ISR)
   * @param montoSinIVA - Monto de arrendamiento sin IVA
   * @returns Resultado del cálculo
   */
  static calcularArrendamiento(montoSinIVA: number): RetencionCalculationResult {
    return this.calcularRetencionISR(montoSinIVA, 'arrendamiento');
  }

  /**
   * Calcula retención de fletes (4% ISR)
   * @param montoSinIVA - Monto de flete sin IVA
   * @returns Resultado del cálculo
   */
  static calcularFletes(montoSinIVA: number): RetencionCalculationResult {
    return this.calcularRetencionISR(montoSinIVA, 'fletes');
  }

  /**
   * Obtiene todas las retenciones ISR
   * @returns Array de retenciones ISR
   */
  static getAllRetencionesISR(): RetencionISR[] {
    this.loadData();
    return [...this._data!.isr_retenciones];
  }

  /**
   * Obtiene todas las retenciones IVA
   * @returns Array de retenciones IVA
   */
  static getAllRetencionesIVA(): RetencionIVA[] {
    this.loadData();
    return [...this._data!.iva_retenciones];
  }
}

/**
 * Calculadora de Impuestos Locales (Estatales y Municipales)
 */
export class ImpuestosLocalesCalculator {
  private static _data: ImpuestosLocalesData | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(
      __dirname,
      '../../../shared-data/sat/impuestos/impuestos_locales.json'
    );
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._data = JSON.parse(rawData) as ImpuestosLocalesData;
  }

  /**
   * Obtiene la tasa de impuesto sobre nómina para un estado
   * @param cveEstado - Clave del estado (01-32)
   * @returns Impuesto estatal o undefined
   */
  static getImpuestoNomina(cveEstado: string): ImpuestoEstatal | undefined {
    this.loadData();
    return this._data!.impuesto_nomina.find((i) => i.cve_estado === cveEstado.padStart(2, '0'));
  }

  /**
   * Calcula impuesto sobre nómina
   * @param totalPercepciones - Total de percepciones del período
   * @param cveEstado - Clave del estado
   * @returns Monto del impuesto
   */
  static calcularImpuestoNomina(totalPercepciones: number, cveEstado: string): number {
    const impuesto = this.getImpuestoNomina(cveEstado);

    if (!impuesto) {
      throw new Error(`No se encontró tasa de impuesto sobre nómina para estado: ${cveEstado}`);
    }

    return totalPercepciones * (impuesto.tasa / 100);
  }

  /**
   * Obtiene la tasa de impuesto sobre hospedaje para un estado
   * @param cveEstado - Clave del estado
   * @returns Impuesto estatal o undefined
   */
  static getImpuestoHospedaje(cveEstado: string): ImpuestoEstatal | undefined {
    this.loadData();
    return this._data!.impuesto_hospedaje.find((i) => i.cve_estado === cveEstado.padStart(2, '0'));
  }

  /**
   * Calcula impuesto sobre hospedaje
   * @param montoHospedaje - Monto del servicio de hospedaje
   * @param cveEstado - Clave del estado
   * @returns Monto del impuesto
   */
  static calcularImpuestoHospedaje(montoHospedaje: number, cveEstado: string): number {
    const impuesto = this.getImpuestoHospedaje(cveEstado);

    if (!impuesto) {
      throw new Error(`No se encontró tasa de impuesto sobre hospedaje para estado: ${cveEstado}`);
    }

    return montoHospedaje * (impuesto.tasa / 100);
  }

  /**
   * Obtiene todas las tasas de impuesto sobre nómina
   * @returns Array de impuestos estatales
   */
  static getAllImpuestosNomina(): ImpuestoEstatal[] {
    this.loadData();
    return [...this._data!.impuesto_nomina];
  }

  /**
   * Obtiene todas las tasas de impuesto sobre hospedaje
   * @returns Array de impuestos estatales
   */
  static getAllImpuestosHospedaje(): ImpuestoEstatal[] {
    this.loadData();
    return [...this._data!.impuesto_hospedaje];
  }
}
