/**
 * Calculadora de Impuesto Sobre la Renta (ISR) para México
 *
 * Implementa el cálculo de ISR según las tablas del Art. 96 de la Ley del ISR
 * Incluye subsidio al empleo y tarifas progresivas por año
 */

import * as fs from 'fs';
import * as path from 'path';
import { ISRTabla, SubsidioEmpleo, ISRCalculationResult, ISRTramo } from '../types';

interface ISRData {
  metadata: {
    catalog: string;
    description: string;
    source: string;
    last_updated: string;
    notes: string;
  };
  tablas: ISRTabla[];
  subsidio_empleo: Record<string, SubsidioEmpleo[]>;
}

export class ISRCalculator {
  private static _data: ISRData | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(
      __dirname,
      '../../../shared-data/sat/impuestos/isr_tablas.json'
    );
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._data = JSON.parse(rawData) as ISRData;
  }

  /**
   * Obtiene la tabla de ISR para un año específico
   * @param año - Año fiscal (ej: 2025, 2024)
   * @param periodicidad - Periodicidad del pago (mensual, anual, etc.)
   * @returns Tabla de ISR o undefined si no existe
   */
  static getTabla(
    año: number,
    periodicidad: 'mensual' | 'anual' | 'quincenal' | 'semanal' | 'diario' = 'mensual'
  ): ISRTabla | undefined {
    this.loadData();
    return this._data!.tablas.find(
      t => t.año === año && t.periodicidad === periodicidad
    );
  }

  /**
   * Obtiene la tabla de subsidio al empleo para un año
   * @param año - Año fiscal
   * @returns Array de tramos de subsidio
   */
  static getSubsidioEmpleo(año: number): SubsidioEmpleo[] | undefined {
    this.loadData();
    return this._data!.subsidio_empleo[año.toString()];
  }

  /**
   * Calcula el ISR para un ingreso dado
   * @param ingreso - Ingreso gravable
   * @param año - Año fiscal
   * @param periodicidad - Periodicidad del pago
   * @param aplicarSubsidio - Si se debe aplicar subsidio al empleo (solo personas físicas)
   * @returns Resultado detallado del cálculo
   */
  static calcular(
    ingreso: number,
    año: number = new Date().getFullYear(),
    periodicidad: 'mensual' | 'anual' | 'quincenal' | 'semanal' | 'diario' = 'mensual',
    aplicarSubsidio: boolean = false
  ): ISRCalculationResult {
    const tabla = this.getTabla(año, periodicidad);
    if (!tabla) {
      throw new Error(`No se encontró tabla de ISR para año ${año} y periodicidad ${periodicidad}`);
    }

    // Encontrar el tramo correspondiente
    const tramo = this.findTramo(ingreso, tabla.tramos);
    if (!tramo) {
      throw new Error(`No se encontró tramo para ingreso ${ingreso}`);
    }

    // Calcular excedente del límite inferior
    const excedente = ingreso - tramo.limite_inferior;

    // Calcular impuesto sobre el excedente
    const impuestoMarginal = excedente * (tramo.tasa_excedente / 100);

    // ISR causado = cuota fija + impuesto marginal
    const isrCausado = tramo.cuota_fija + impuestoMarginal;

    // Calcular subsidio al empleo si aplica
    let subsidio = 0;
    if (aplicarSubsidio && periodicidad === 'mensual') {
      const subsidios = this.getSubsidioEmpleo(año);
      if (subsidios) {
        const tramoSubsidio = this.findTramoSubsidio(ingreso, subsidios);
        if (tramoSubsidio) {
          subsidio = tramoSubsidio.subsidio;
        }
      }
    }

    // ISR a retener = ISR causado - subsidio al empleo
    const isrARetener = Math.max(0, isrCausado - subsidio);

    // Tasa efectiva
    const tasaEfectiva = ingreso > 0 ? (isrARetener / ingreso) * 100 : 0;

    return {
      ingreso_gravable: ingreso,
      limite_inferior: tramo.limite_inferior,
      excedente,
      cuota_fija: tramo.cuota_fija,
      impuesto_marginal: impuestoMarginal,
      isr_causado: isrCausado,
      tasa_efectiva: tasaEfectiva,
      subsidio_empleo: subsidio,
      isr_a_retener: isrARetener,
    };
  }

  /**
   * Encuentra el tramo de ISR correspondiente a un ingreso
   * @param ingreso - Ingreso a buscar
   * @param tramos - Tramos de la tabla
   * @returns Tramo correspondiente o undefined
   */
  private static findTramo(ingreso: number, tramos: ISRTramo[]): ISRTramo | undefined {
    return tramos.find(t => {
      const dentroDeLimiteInferior = ingreso >= t.limite_inferior;
      const dentroDeLimiteSuperior = t.limite_superior === null || ingreso <= t.limite_superior;
      return dentroDeLimiteInferior && dentroDeLimiteSuperior;
    });
  }

  /**
   * Encuentra el tramo de subsidio al empleo correspondiente
   * @param ingreso - Ingreso a buscar
   * @param tramos - Tramos de subsidio
   * @returns Tramo de subsidio o undefined
   */
  private static findTramoSubsidio(
    ingreso: number,
    tramos: SubsidioEmpleo[]
  ): SubsidioEmpleo | undefined {
    return tramos.find(t => {
      const dentroDeLimiteInferior = ingreso >= t.limite_inferior;
      const dentroDeLimiteSuperior = t.limite_superior === null || ingreso <= t.limite_superior;
      return dentroDeLimiteInferior && dentroDeLimiteSuperior;
    });
  }

  /**
   * Calcula el salario neto después de ISR
   * @param salarioBruto - Salario bruto
   * @param año - Año fiscal
   * @param periodicidad - Periodicidad
   * @param aplicarSubsidio - Si aplica subsidio
   * @returns Salario neto
   */
  static calcularSalarioNeto(
    salarioBruto: number,
    año: number = new Date().getFullYear(),
    periodicidad: 'mensual' | 'anual' | 'quincenal' | 'semanal' | 'diario' = 'mensual',
    aplicarSubsidio: boolean = true
  ): number {
    const resultado = this.calcular(salarioBruto, año, periodicidad, aplicarSubsidio);
    return salarioBruto - resultado.isr_a_retener;
  }

  /**
   * Calcula ISR anual a partir de ingresos mensuales
   * @param ingresosMensuales - Array de 12 ingresos mensuales
   * @param año - Año fiscal
   * @returns ISR anual total
   */
  static calcularISRAnual(ingresosMensuales: number[], año: number = new Date().getFullYear()): number {
    if (ingresosMensuales.length !== 12) {
      throw new Error('Se requieren exactamente 12 ingresos mensuales');
    }

    let isrAnualTotal = 0;
    for (const ingreso of ingresosMensuales) {
      const resultado = this.calcular(ingreso, año, 'mensual', true);
      isrAnualTotal += resultado.isr_a_retener;
    }

    return isrAnualTotal;
  }

  /**
   * Calcula la tasa marginal efectiva para un ingreso
   * @param ingreso - Ingreso a evaluar
   * @param año - Año fiscal
   * @param periodicidad - Periodicidad
   * @returns Tasa marginal (%)
   */
  static calcularTasaMarginal(
    ingreso: number,
    año: number = new Date().getFullYear(),
    periodicidad: 'mensual' | 'anual' | 'quincenal' | 'semanal' | 'diario' = 'mensual'
  ): number {
    const tabla = this.getTabla(año, periodicidad);
    if (!tabla) {
      throw new Error(`No se encontró tabla de ISR para año ${año}`);
    }

    const tramo = this.findTramo(ingreso, tabla.tramos);
    if (!tramo) {
      throw new Error(`No se encontró tramo para ingreso ${ingreso}`);
    }

    return tramo.tasa_excedente;
  }

  /**
   * Obtiene todas las tablas disponibles
   * @returns Array de tablas ISR
   */
  static getAllTablas(): ISRTabla[] {
    this.loadData();
    return [...this._data!.tablas];
  }

  /**
   * Obtiene los años disponibles
   * @returns Array de años con tablas disponibles
   */
  static getAñosDisponibles(): number[] {
    this.loadData();
    const años = new Set(this._data!.tablas.map(t => t.año));
    return Array.from(años).sort((a, b) => b - a);
  }
}
