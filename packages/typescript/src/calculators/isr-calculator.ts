/**
 * Calculadora de Impuesto Sobre la Renta (ISR) para México
 *
 * Implementa el cálculo de ISR según las tablas del Art. 96 de la Ley del ISR
 * Incluye subsidio al empleo y tarifas progresivas por año
 */

import { ISRCalculationResult } from '../types';
import { loadCatalogData } from '../utils/catalog-loader';

interface ISRBracket {
  limiteInferior: number;
  limiteSuperior: number | null;
  cuotaFija: number;
  tasa: number;
}

interface ISRYearTables {
  inflationFactor?: number;
  description?: string;
  daily?: ISRBracket[];
  weekly?: ISRBracket[];
  biweekly?: ISRBracket[];
  monthly?: ISRBracket[];
  annual?: ISRBracket[];
}

interface SubsidyTier {
  desde: number;
  hasta: number | null;
  subsidio: number;
}

interface ISRSubsidy {
  type: 'tiered' | 'flat';
  monthly: SubsidyTier[] | { amount: number; maxIncome: number };
}

interface ISRData {
  metadata: {
    catalog: string;
    description: string;
    source: string;
    last_updated: string;
    notes: string;
  };
  subsidies: Record<string, ISRSubsidy>;
  brackets: Record<string, ISRYearTables>;
}

type ISRBracketKey = 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'annual';

const PERIOD_MAPPING: Record<string, ISRBracketKey> = {
  diaria: 'daily',
  diario: 'daily',
  semanal: 'weekly',
  quincenal: 'biweekly',
  mensual: 'monthly',
  anual: 'annual',
  decenal: 'monthly',
};

const PERIOD_FACTORS: Record<string, number> = {
  diaria: 30.4,
  diario: 30.4,
  semanal: 4.33,
  decenal: 3.0,
  quincenal: 2.0,
  mensual: 1.0,
  anual: 1 / 12,
};

export class ISRCalculator {
  private static _data: ISRData | null = null;

  static setData(data: ISRData): void {
    this._data = data;
  }

  private static loadData(): void {
    if (this._data !== null) return;

    this._data = loadCatalogData<ISRData>('isr-tables.json');
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
  ): ISRBracket[] | undefined {
    this.loadData();
    const yearTables = this._data!.brackets[año.toString()];
    if (!yearTables) return undefined;
    const key = PERIOD_MAPPING[periodicidad];
    return yearTables[key];
  }

  /**
   * Obtiene la tabla de subsidio al empleo para un año
   * @param año - Año fiscal
   * @returns Array de tramos de subsidio
   */
  static getSubsidioEmpleo(año: number): ISRSubsidy | undefined {
    this.loadData();
    return this._data!.subsidies[año.toString()];
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
    this.loadData();
    const yearStr = año.toString();
    const usePeriodTables =
      año === 2026 &&
      ['diaria', 'diario', 'semanal', 'quincenal', 'mensual', 'anual'].includes(periodicidad);

    const periodKey = PERIOD_MAPPING[periodicidad];
    const factor = PERIOD_FACTORS[periodicidad];

    const yearTables = this._data!.brackets[yearStr];
    if (!yearTables) {
      throw new Error(`No se encontró tabla de ISR para año ${año}`);
    }

    const subsidyData = this._data!.subsidies[yearStr];
    if (!subsidyData) {
      throw new Error(`No se encontró subsidio para año ${año}`);
    }

    const getBrackets = (key: ISRBracketKey): ISRBracket[] => {
      const data = yearTables[key];
      if (!data) {
        throw new Error(
          `No se encontró tabla de ISR para año ${año} y periodicidad ${periodicidad}`
        );
      }
      return data;
    };

    const calculateSubsidy = (monthlyIncome: number): number => {
      if (!aplicarSubsidio) return 0;
      if (subsidyData.type === 'flat') {
        const flat = subsidyData.monthly as { amount: number; maxIncome: number };
        return monthlyIncome <= flat.maxIncome ? flat.amount : 0;
      }

      const tiers = subsidyData.monthly as SubsidyTier[];
      for (const tier of tiers) {
        const hasta = tier.hasta ?? Number.POSITIVE_INFINITY;
        if (monthlyIncome >= tier.desde && monthlyIncome <= hasta) {
          return tier.subsidio;
        }
      }
      return 0;
    };

    const selectBracket = (brackets: ISRBracket[], income: number): ISRBracket => {
      return (
        brackets.find((b) => {
          const limiteSuperior = b.limiteSuperior ?? Number.POSITIVE_INFINITY;
          return income >= b.limiteInferior && income <= limiteSuperior;
        }) ?? brackets[brackets.length - 1]
      );
    };

    if (usePeriodTables) {
      const brackets = getBrackets(periodKey);
      const bracket = selectBracket(brackets, ingreso);
      const excedente = ingreso - bracket.limiteInferior;
      const impuestoMarginal = excedente * (bracket.tasa / 100);
      const isrAntesSubsidio = bracket.cuotaFija + impuestoMarginal;

      const ingresoMensual = ingreso * factor;
      const subsidioMensual = calculateSubsidy(ingresoMensual);
      const subsidioProrrateado = subsidioMensual / factor;

      const isrFinal = Math.max(0, isrAntesSubsidio - subsidioProrrateado);
      const tasaEfectiva = ingreso > 0 ? (isrFinal / ingreso) * 100 : 0;

      return {
        ingreso_gravable: ingreso,
        limite_inferior: bracket.limiteInferior,
        excedente,
        cuota_fija: bracket.cuotaFija,
        impuesto_marginal: impuestoMarginal,
        isr_causado: isrAntesSubsidio,
        tasa_efectiva: tasaEfectiva,
        subsidio_empleo: subsidioProrrateado,
        isr_a_retener: isrFinal,
      };
    }

    const monthlyBrackets = getBrackets('monthly');
    const ingresoMensualizado = ingreso * factor;
    const bracket = selectBracket(monthlyBrackets, ingresoMensualizado);
    const excedente = ingresoMensualizado - bracket.limiteInferior;
    const impuestoMarginal = excedente * (bracket.tasa / 100);
    const isrAntesSubsidio = bracket.cuotaFija + impuestoMarginal;
    const subsidioMensual = calculateSubsidy(ingresoMensualizado);
    const isrFinalMensual = Math.max(0, isrAntesSubsidio - subsidioMensual);
    const isrFinal = isrFinalMensual / factor;
    const tasaEfectiva = ingreso > 0 ? (isrFinal / ingreso) * 100 : 0;

    return {
      ingreso_gravable: ingreso,
      limite_inferior: bracket.limiteInferior,
      excedente,
      cuota_fija: bracket.cuotaFija,
      impuesto_marginal: impuestoMarginal,
      isr_causado: isrAntesSubsidio,
      tasa_efectiva: tasaEfectiva,
      subsidio_empleo: subsidioMensual,
      isr_a_retener: isrFinal,
    };
  }

  /**
   * Encuentra el tramo de ISR correspondiente a un ingreso
   * @param ingreso - Ingreso a buscar
   * @param tramos - Tramos de la tabla
   * @returns Tramo correspondiente o undefined
   */
  private static findTramo(ingreso: number, tramos: ISRBracket[]): ISRBracket | undefined {
    return tramos.find((t) => {
      const limiteSuperior = t.limiteSuperior ?? Number.POSITIVE_INFINITY;
      return ingreso >= t.limiteInferior && ingreso <= limiteSuperior;
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
  static calcularISRAnual(
    ingresosMensuales: number[],
    año: number = new Date().getFullYear()
  ): number {
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

    const tramo = this.findTramo(ingreso, tabla);
    if (!tramo) {
      throw new Error(`No se encontró tramo para ingreso ${ingreso}`);
    }

    return tramo.tasa;
  }

  /**
   * Obtiene todas las tablas disponibles
   * @returns Array de tablas ISR
   */
  static getAllTablas(): Array<{ year: number; periodicidad: string; tramos: ISRBracket[] }> {
    this.loadData();
    const tablas: Array<{ year: number; periodicidad: string; tramos: ISRBracket[] }> = [];
    for (const [year, tables] of Object.entries(this._data!.brackets)) {
      for (const key of Object.keys(PERIOD_MAPPING)) {
        const periodKey = PERIOD_MAPPING[key];
        const tramos = tables[periodKey];
        if (tramos) {
          tablas.push({ year: Number(year), periodicidad: key, tramos });
        }
      }
    }
    return tablas;
  }

  /**
   * Obtiene los años disponibles
   * @returns Array de años con tablas disponibles
   */
  static getAñosDisponibles(): number[] {
    this.loadData();
    return Object.keys(this._data!.brackets)
      .map((year) => Number(year))
      .sort((a, b) => b - a);
  }
}
