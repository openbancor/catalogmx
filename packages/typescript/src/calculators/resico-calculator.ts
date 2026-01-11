/**
 * Calculadora de RESICO (Régimen Simplificado de Confianza) para México
 *
 * RESICO es un régimen fiscal simplificado donde:
 * - Se aplica tasa DIRECTA sobre ingreso total
 * - No hay cuota fija ni cálculo de excedente
 * - No se permiten deducciones
 *
 * Implementa cálculos según Artículo 113-E LISR
 * Soporta años: 2024, 2025, 2026
 */

import { loadCatalogData } from '../utils/catalog-loader';

export type RESICOYear = 2024 | 2025 | 2026;
export type RESICOPeriod = 'mensual' | 'anual';

export interface RESICOBracket {
  limiteInferior: number;
  limiteSuperior: number;
  tasa: number;
}

export interface RESICOLimits {
  personaFisica: {
    ingresoAnualMaximo: number;
    ingresoMensualMaximo: number;
    description: string;
  };
  personaMoral: {
    ingresoAnualMaximo: number;
    tasa: number;
    description: string;
  };
}

export interface RESICOCalculationResult {
  ingreso: number;
  periodo: RESICOPeriod;
  year: RESICOYear;
  limiteMaximo: number;
  dentroDeLimite: boolean;
  bracket: RESICOBracket | null;
  resicoCalculado: number;
  tasaEfectiva: number;
}

interface RESICOData {
  metadata: {
    description: string;
    source: string;
    currency: string;
    years: number[];
    note: string;
    calculation: string;
  };
  limits: RESICOLimits;
  brackets: Record<
    string,
    {
      description: string;
      mensual: RESICOBracket[];
      anual: RESICOBracket[];
    }
  >;
}

/**
 * Calculadora de RESICO (Régimen Simplificado de Confianza)
 *
 * @example
 * ```typescript
 * // Calcular RESICO mensual
 * const result = RESICOCalculator.calcular(50000, 2025, 'mensual');
 * console.log(`RESICO: $${result.resicoCalculado}`);
 * console.log(`Tasa efectiva: ${result.tasaEfectiva}%`);
 *
 * // Verificar si está dentro de límites
 * const isEligible = RESICOCalculator.isEligible(3000000, 'anual');
 * ```
 */
export class RESICOCalculator {
  private static _data: RESICOData | null = null;

  static setData(data: RESICOData): void {
    this._data = data;
  }

  private static loadData(): void {
    if (this._data !== null) return;

    this._data = loadCatalogData<RESICOData>('resico-tables.json');
  }

  /**
   * Obtiene los brackets de RESICO para un año y período específico
   * @param year - Año fiscal (2024, 2025, 2026)
   * @param periodo - Período (mensual, anual)
   * @returns Array de brackets RESICO
   */
  static getBrackets(year: RESICOYear, periodo: RESICOPeriod): RESICOBracket[] {
    this.loadData();
    const yearData = this._data!.brackets[year.toString()];
    if (!yearData) {
      throw new Error(`No se encontraron tablas RESICO para el año ${year}`);
    }
    return yearData[periodo];
  }

  /**
   * Obtiene los límites de ingresos para RESICO
   * @returns Límites para persona física y moral
   */
  static getLimits(): RESICOLimits {
    this.loadData();
    return this._data!.limits;
  }

  /**
   * Verifica si un ingreso está dentro de los límites de RESICO
   * @param ingreso - Ingreso a verificar
   * @param periodo - Período (mensual, anual)
   * @returns true si está dentro de los límites
   */
  static isEligible(ingreso: number, periodo: RESICOPeriod): boolean {
    const limits = this.getLimits();
    const limite =
      periodo === 'mensual'
        ? limits.personaFisica.ingresoMensualMaximo
        : limits.personaFisica.ingresoAnualMaximo;
    return ingreso <= limite;
  }

  /**
   * Encuentra el bracket correspondiente a un ingreso
   * @param ingreso - Ingreso a buscar
   * @param brackets - Array de brackets
   * @returns Bracket correspondiente o null
   */
  private static findBracket(ingreso: number, brackets: RESICOBracket[]): RESICOBracket | null {
    return brackets.find((b) => ingreso >= b.limiteInferior && ingreso <= b.limiteSuperior) || null;
  }

  /**
   * Calcula el RESICO para un ingreso dado
   * @param ingreso - Ingreso gravable (total, sin deducciones)
   * @param year - Año fiscal (2024, 2025, 2026)
   * @param periodo - Período (mensual, anual)
   * @returns Resultado detallado del cálculo
   *
   * @example
   * ```typescript
   * const result = RESICOCalculator.calcular(75000, 2025, 'mensual');
   * // result.resicoCalculado = 75000 * 0.015 = 1125
   * ```
   */
  static calcular(
    ingreso: number,
    year: RESICOYear = 2025,
    periodo: RESICOPeriod = 'mensual'
  ): RESICOCalculationResult {
    const brackets = this.getBrackets(year, periodo);
    const limits = this.getLimits();

    const limiteMaximo =
      periodo === 'mensual'
        ? limits.personaFisica.ingresoMensualMaximo
        : limits.personaFisica.ingresoAnualMaximo;

    const dentroDeLimite = ingreso <= limiteMaximo;

    // Si el ingreso es 0 o negativo
    if (ingreso <= 0) {
      return {
        ingreso,
        periodo,
        year,
        limiteMaximo,
        dentroDeLimite: true,
        bracket: null,
        resicoCalculado: 0,
        tasaEfectiva: 0,
      };
    }

    const bracket = this.findBracket(ingreso, brackets);

    // RESICO = Ingreso Total × Tasa del Bracket
    // No hay cuota fija ni cálculo de excedente
    const resicoCalculado = bracket ? ingreso * (bracket.tasa / 100) : 0;

    const tasaEfectiva = ingreso > 0 ? (resicoCalculado / ingreso) * 100 : 0;

    return {
      ingreso,
      periodo,
      year,
      limiteMaximo,
      dentroDeLimite,
      bracket,
      resicoCalculado,
      tasaEfectiva,
    };
  }

  /**
   * Calcula el ingreso neto después de RESICO
   * @param ingreso - Ingreso bruto
   * @param year - Año fiscal
   * @param periodo - Período
   * @returns Ingreso neto
   */
  static calcularIngresoNeto(
    ingreso: number,
    year: RESICOYear = 2025,
    periodo: RESICOPeriod = 'mensual'
  ): number {
    const resultado = this.calcular(ingreso, year, periodo);
    return ingreso - resultado.resicoCalculado;
  }

  /**
   * Calcula RESICO anual a partir de ingresos mensuales
   * @param ingresosMensuales - Array de 12 ingresos mensuales
   * @param year - Año fiscal
   * @returns RESICO anual total
   */
  static calcularRESICOAnual(ingresosMensuales: number[], year: RESICOYear = 2025): number {
    if (ingresosMensuales.length !== 12) {
      throw new Error('Se requieren exactamente 12 ingresos mensuales');
    }

    let resicoAnualTotal = 0;
    for (const ingreso of ingresosMensuales) {
      const resultado = this.calcular(ingreso, year, 'mensual');
      resicoAnualTotal += resultado.resicoCalculado;
    }

    return resicoAnualTotal;
  }

  /**
   * Compara ISR tradicional vs RESICO para determinar el régimen más conveniente
   * @param ingreso - Ingreso mensual
   * @param year - Año fiscal
   * @returns Comparación con recomendación
   */
  static compararConISR(
    ingreso: number,
    year: RESICOYear = 2025
  ): {
    resicoMensual: number;
    tasaRESICO: number;
    recomendacion: string;
    ahorroEstimado: number;
    notaComparativa: string;
  } {
    const resultadoRESICO = this.calcular(ingreso, year, 'mensual');

    // Nota: Para comparación real con ISR, usar ISRCalculator
    // Aquí solo damos una estimación basada en tasas típicas de ISR
    const isrEstimado = ingreso * 0.15; // Estimación conservadora para ingresos medios

    const ahorro = isrEstimado - resultadoRESICO.resicoCalculado;

    let recomendacion: string;
    if (ingreso > 291666.67) {
      recomendacion = 'Ingreso excede límite RESICO. Debe tributar en régimen general.';
    } else if (ahorro > 0) {
      recomendacion = `RESICO es más conveniente. Ahorro estimado: $${ahorro.toFixed(2)} mensuales`;
    } else {
      recomendacion = 'Evaluar deducciones disponibles en régimen general.';
    }

    return {
      resicoMensual: resultadoRESICO.resicoCalculado,
      tasaRESICO: resultadoRESICO.tasaEfectiva,
      recomendacion,
      ahorroEstimado: Math.max(0, ahorro),
      notaComparativa:
        'RESICO no permite deducciones. Comparar con ISR usando ISRCalculator para cálculo exacto.',
    };
  }

  /**
   * Obtiene los años disponibles
   * @returns Array de años con tablas disponibles
   */
  static getAñosDisponibles(): RESICOYear[] {
    this.loadData();
    return this._data!.metadata.years as RESICOYear[];
  }

  /**
   * Obtiene información del régimen
   * @returns Metadata del régimen RESICO
   */
  static getInfo(): RESICOData['metadata'] {
    this.loadData();
    return { ...this._data!.metadata };
  }
}
