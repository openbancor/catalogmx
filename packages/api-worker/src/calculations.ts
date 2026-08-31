import {
  IMSSCalculator,
  type CuotasIMSSResult,
  type IMSSYear,
  ISRCalculator,
} from '../../typescript/src/calculators';
import type { ISRCalculationResult } from '../../typescript/src/types';
import * as fiscal from '../../typescript/src/fiscal';
import { ApiError } from './errors';
import { preloadSmallData } from './data';

export type IsrPeriod = 'diario' | 'semanal' | 'quincenal' | 'mensual' | 'anual';

const ISR_PERIODS: readonly IsrPeriod[] = ['diario', 'semanal', 'quincenal', 'mensual', 'anual'];

const ISR_PERIOD_FACTORS: Record<IsrPeriod, number> = {
  diario: 30.4,
  semanal: 4.33,
  quincenal: 2,
  mensual: 1,
  anual: 1 / 12,
};

const MAX_AMOUNT = 1_000_000_000;
const MAX_DAYS = 366;
const IMSS_YEARS: readonly IMSSYear[] = [2024, 2025, 2026];

export interface IsrCalculationResponse {
  retencion_mensual: number;
  periodo: IsrPeriod;
  ejercicio: number;
  resultado: ISRCalculationResult;
  tabla_aplicada: {
    ejercicio: number;
    periodicidad: IsrPeriod;
    ingreso_tabla: number;
    limite_inferior: number;
    limite_superior: number | null;
    cuota_fija: number;
    tasa_marginal: number;
    subsidio: number;
  };
  regla_aplicada: {
    ejercicio: number;
    periodicidad: IsrPeriod;
    formulas: {
      excedente: string;
      impuesto_marginal: string;
      isr_a_retener: string;
    };
    fuente: string;
  };
  auditoria: {
    redondeo_decimales: 2;
    interno: ISRCalculationResult;
  };
}

export interface ImssCalculationResponse {
  cuotas_obrera: number;
  cuotas_patronal: number;
  resultado: CuotasIMSSResult;
  desglose: {
    cuotas_obrera: Record<string, number>;
    cuotas_patronal: Record<string, number>;
  };
  regla_aplicada: {
    ejercicio: number;
    uma: { diaria: number; mensual: number; anual: number };
    clase_riesgo: 1;
    fuente_uma: string;
    formula_identificadores: string[];
  };
  auditoria: {
    redondeo_decimales: 2;
    interno: CuotasIMSSResult;
  };
}

export function calculateIsr(body: Record<string, unknown>): IsrCalculationResponse {
  assertExactKeys(body, ['base_gravable', 'periodo', 'ejercicio']);
  const baseGravable = requireNumber(body.base_gravable, 'base_gravable', MAX_AMOUNT);
  const periodo = requireIsrPeriod(body.periodo);
  const ejercicio = requireYear(body.ejercicio);

  try {
    fiscal.assertFiscalDataVerified('isr_payroll', ejercicio);
  } catch {
    throw new ApiError(
      422,
      'unsupported_fiscal_data',
      `ISR fiscal data for ${ejercicio} is not verified`
    );
  }

  preloadSmallData();
  const tabla = ISRCalculator.getTabla(ejercicio, periodo);
  if (!tabla) {
    throw new ApiError(422, 'unsupported_fiscal_data', 'ISR table is not available');
  }

  const interno = ISRCalculator.calcular(baseGravable, ejercicio, periodo, false);
  const ingresoTabla =
    ejercicio === 2026 ? baseGravable : baseGravable * ISR_PERIOD_FACTORS[periodo];
  const tramo =
    tabla.find((candidate) => {
      const upper = candidate.limiteSuperior ?? Number.POSITIVE_INFINITY;
      return ingresoTabla >= candidate.limiteInferior && ingresoTabla <= upper;
    }) ?? tabla[tabla.length - 1];

  const resultado = roundIsrResult(interno);
  return {
    retencion_mensual: round(interno.isr_a_retener),
    periodo,
    ejercicio,
    resultado,
    tabla_aplicada: {
      ejercicio,
      periodicidad: periodo,
      ingreso_tabla: round(ingresoTabla),
      limite_inferior: round(tramo.limiteInferior),
      limite_superior: tramo.limiteSuperior === null ? null : round(tramo.limiteSuperior),
      cuota_fija: round(tramo.cuotaFija),
      tasa_marginal: round(tramo.tasa),
      subsidio: round(interno.subsidio_empleo ?? 0),
    },
    regla_aplicada: {
      ejercicio,
      periodicidad: periodo,
      formulas: {
        excedente: 'ingreso_tabla - limite_inferior',
        impuesto_marginal: 'excedente * tasa_marginal',
        isr_a_retener: 'max(0, isr_causado - subsidio)',
      },
      fuente: 'ISRCalculator.calcular',
    },
    auditoria: { redondeo_decimales: 2, interno },
  };
}

export function calculateImss(body: Record<string, unknown>): ImssCalculationResponse {
  assertExactKeys(body, ['sdi', 'dias_cotizados', 'ejercicio']);
  const sdi = requireNumber(body.sdi, 'sdi', MAX_AMOUNT);
  const diasCotizados = requireInteger(body.dias_cotizados, 'dias_cotizados', MAX_DAYS);
  if (diasCotizados < 1) {
    throw new ApiError(400, 'invalid_request', 'dias_cotizados must be positive');
  }
  const ejercicio = requireYear(body.ejercicio);
  const year = requireImssYear(ejercicio);

  preloadSmallData();
  const uma = IMSSCalculator.getUMA(year);
  const salarioMinimo = IMSSCalculator.getSalarioMinimo(year);
  if (sdi < salarioMinimo) {
    throw new ApiError(
      400,
      'invalid_request',
      'sdi cannot be lower than the applicable general minimum wage'
    );
  }

  const interno = IMSSCalculator.calcularCuotasObreroPatronales(sdi, diasCotizados, year, 1);
  return {
    cuotas_obrera: round(interno.total_trabajador),
    cuotas_patronal: round(interno.total_patron),
    resultado: roundImssResult(interno),
    desglose: {
      cuotas_obrera: roundMap(interno.cuotas_trabajador),
      cuotas_patronal: roundMap(interno.cuotas_patron),
    },
    regla_aplicada: {
      ejercicio,
      uma: { diaria: round(uma.diaria), mensual: round(uma.mensual), anual: round(uma.anual) },
      clase_riesgo: 1,
      fuente_uma: 'IMSSCalculator.getUMA',
      formula_identificadores: [
        'cuotas_imss',
        'riesgo_trabajo',
        'total_patron',
        'total_trabajador',
      ],
    },
    auditoria: { redondeo_decimales: 2, interno },
  };
}

function assertExactKeys(body: Record<string, unknown>, allowed: readonly string[]): void {
  const allowedSet = new Set(allowed);
  const unexpected = Object.keys(body).find((key) => !allowedSet.has(key));
  if (unexpected) {
    throw new ApiError(400, 'invalid_request', `Unexpected field: ${unexpected}`);
  }
}

function requireNumber(value: unknown, field: string, maximum: number): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new ApiError(400, 'invalid_request', `${field} must be a finite number`);
  }
  if (value < 0 || value > maximum) {
    throw new ApiError(400, 'invalid_request', `${field} is outside the supported range`);
  }
  return value;
}

function requireInteger(value: unknown, field: string, maximum: number): number {
  const number = requireNumber(value, field, maximum);
  if (!Number.isInteger(number)) {
    throw new ApiError(400, 'invalid_request', `${field} must be an integer`);
  }
  return number;
}

function requireYear(value: unknown): number {
  const year = requireInteger(value, 'ejercicio', 2100);
  if (year < 1900) {
    throw new ApiError(400, 'invalid_request', 'ejercicio is outside the supported range');
  }
  return year;
}

function requireImssYear(year: number): IMSSYear {
  if (!IMSS_YEARS.includes(year as IMSSYear)) {
    throw new ApiError(422, 'unsupported_fiscal_data', 'IMSS table is not available');
  }
  return year as IMSSYear;
}

function requireIsrPeriod(value: unknown): IsrPeriod {
  if (typeof value !== 'string') {
    throw new ApiError(400, 'invalid_request', 'periodo must be a supported string');
  }
  if (!ISR_PERIODS.includes(value as IsrPeriod)) {
    throw new ApiError(422, 'unsupported_fiscal_data', 'ISR period is not available');
  }
  return value as IsrPeriod;
}

function round(value: number): number {
  return Number(value.toFixed(2));
}

function roundIsrResult(result: ISRCalculationResult): ISRCalculationResult {
  return {
    ingreso_gravable: round(result.ingreso_gravable),
    limite_inferior: round(result.limite_inferior),
    excedente: round(result.excedente),
    cuota_fija: round(result.cuota_fija),
    impuesto_marginal: round(result.impuesto_marginal),
    isr_causado: round(result.isr_causado),
    tasa_efectiva: round(result.tasa_efectiva),
    subsidio_empleo: round(result.subsidio_empleo ?? 0),
    isr_a_retener: round(result.isr_a_retener),
  };
}

function roundImssResult(result: CuotasIMSSResult): CuotasIMSSResult {
  return {
    salario_diario: round(result.salario_diario),
    dias: round(result.dias),
    salario_base_cotizacion: round(result.salario_base_cotizacion),
    year: result.year,
    uma_diaria: round(result.uma_diaria),
    ceav_patron_rate: result.ceav_patron_rate,
    cuotas_patron: roundMap(result.cuotas_patron),
    cuotas_trabajador: roundMap(result.cuotas_trabajador),
    total_patron: round(result.total_patron),
    total_trabajador: round(result.total_trabajador),
    total_imss: round(result.total_imss),
  };
}

function roundMap(values: Record<string, number>): Record<string, number> {
  return Object.fromEntries(Object.entries(values).map(([key, value]) => [key, round(value)]));
}
