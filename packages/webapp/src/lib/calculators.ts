/**
 * Mexican Tax Calculators with step-by-step breakdown
 * Supports multiple years: 2024, 2025, 2026
 * Uses official tax tables from Anexo 8 RMF
 * Data loaded from centralized JSON (shared across platforms)
 */

import isrTablesData from '../../shared-data/isr-tables.json';

export type ISRYear = 2024 | 2025 | 2026;
export type ISRPeriod = 'diaria' | 'semanal' | 'decenal' | 'quincenal' | 'mensual' | 'anual';

export interface ISRBracket {
  limiteInferior: number;
  limiteSuperior: number;
  cuotaFija: number;
  tasa: number;
}

interface ISRBracketJSON {
  limiteInferior: number;
  limiteSuperior: number | null;
  cuotaFija: number;
  tasa: number;
}

interface ISRSubsidyBracket {
  desde: number;
  hasta: number | null;
  subsidio: number;
}

interface ISRSubsidyFlat {
  amount: number;
  maxIncome: number;
}

// Map JSON period names to ISRPeriod type
const periodMapping: Record<ISRPeriod, string> = {
  'diaria': 'daily',
  'semanal': 'weekly',
  'decenal': 'monthly', // No specific decenal table in JSON, use monthly
  'quincenal': 'biweekly',
  'mensual': 'monthly',
  'anual': 'annual'
};

// Helper to get brackets for a specific year and period
function getISRBrackets(year: ISRYear, period: ISRPeriod): ISRBracket[] {
  const yearStr = year.toString() as '2024' | '2025' | '2026';
  const periodKey = periodMapping[period];

  // Access the brackets data with proper typing
  const yearData = isrTablesData.brackets[yearStr];
  const periodData = yearData[periodKey as 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'annual'] as ISRBracketJSON[];

  // Convert null to Infinity for limiteSuperior
  return periodData.map((b: ISRBracketJSON) => ({
    limiteInferior: b.limiteInferior,
    limiteSuperior: b.limiteSuperior === null ? Infinity : b.limiteSuperior,
    cuotaFija: b.cuotaFija,
    tasa: b.tasa
  }));
}

// Helper to calculate subsidy for a specific year
function calculateSubsidy(income: number, year: ISRYear): number {
  const yearStr = year.toString() as '2024' | '2025' | '2026';
  const subsidyData = isrTablesData.subsidies[yearStr];

  if (subsidyData.type === 'tiered') {
    // 2024: tiered system
    const monthlyData = subsidyData.monthly as unknown as ISRSubsidyBracket[];
    const bracket = monthlyData.find((s: ISRSubsidyBracket) => {
      const hasta = s.hasta === null ? Infinity : s.hasta;
      return income >= s.desde && income <= hasta;
    });
    return bracket?.subsidio || 0;
  } else {
    // 2025/2026: flat system
    const flatData = subsidyData.monthly as unknown as ISRSubsidyFlat;
    return income <= flatData.maxIncome ? flatData.amount : 0;
  }
}

export interface ISRCalculationStep {
  step: number;
  description: string;
  formula: string;
  result: number;
  details?: string;
}

export interface ISRCalculationResult {
  ingresoGravable: number;
  periodo: string;
  year: ISRYear;
  ingresoMensualizado: number;
  bracket: {
    limiteInferior: number;
    limiteSuperior: number;
    cuotaFija: number;
    tasa: number;
  };
  excedente: number;
  impuestoMarginal: number;
  isrAntesSubsidio: number;
  subsidio: number;
  isrFinal: number;
  tasaEfectiva: number;
  steps: ISRCalculationStep[];
}

export function calculateISR(
  ingresoGravable: number,
  periodo: ISRPeriod = 'mensual',
  year: ISRYear = 2026
): ISRCalculationResult {
  const steps: ISRCalculationStep[] = [];

  // For 2026, use period-specific tables directly
  const usePeriodTables = year === 2026 && ['diaria', 'semanal', 'quincenal', 'mensual', 'anual'].includes(periodo);

  if (usePeriodTables) {
    // Use official tables for the period
    const brackets = getISRBrackets(year, periodo);

    // Step 1: Find bracket (no conversion needed)
    const bracket = brackets.find(b =>
      ingresoGravable >= b.limiteInferior && ingresoGravable <= b.limiteSuperior
    ) || brackets[brackets.length - 1];

    steps.push({
      step: 1,
      description: `Identificar rango ISR ${periodo}`,
      formula: `$${bracket.limiteInferior.toFixed(2)} ≤ ingreso ≤ $${bracket.limiteSuperior === Infinity ? '∞' : bracket.limiteSuperior.toFixed(2)}`,
      result: bracket.tasa,
      details: `Tasa marginal: ${bracket.tasa}%, Cuota fija: $${bracket.cuotaFija.toFixed(2)}`
    });

    // Step 2: Calculate excess
    const excedente = ingresoGravable - bracket.limiteInferior;

    steps.push({
      step: 2,
      description: 'Calcular excedente sobre límite inferior',
      formula: `$${ingresoGravable.toFixed(2)} - $${bracket.limiteInferior.toFixed(2)}`,
      result: excedente
    });

    // Step 3: Calculate marginal tax
    const impuestoMarginal = excedente * (bracket.tasa / 100);

    steps.push({
      step: 3,
      description: 'Calcular impuesto marginal',
      formula: `$${excedente.toFixed(2)} × ${bracket.tasa}%`,
      result: impuestoMarginal
    });

    // Step 4: Add fixed fee
    const isrAntesSubsidio = bracket.cuotaFija + impuestoMarginal;

    steps.push({
      step: 4,
      description: 'Sumar cuota fija',
      formula: `$${bracket.cuotaFija.toFixed(2)} + $${impuestoMarginal.toFixed(2)}`,
      result: isrAntesSubsidio
    });

    // Step 5: Calculate subsidy (convert to monthly equivalent)
    const periodFactors: Record<ISRPeriod, number> = {
      'diaria': 30.4,
      'semanal': 4.33,
      'decenal': 3,
      'quincenal': 2,
      'mensual': 1,
      'anual': 1/12
    };
    const ingresoMensualEquivalente = ingresoGravable * periodFactors[periodo];
    const subsidio = calculateSubsidy(ingresoMensualEquivalente, year);
    const subsidioProrrateado = subsidio / periodFactors[periodo];

    const subsidyDetails = subsidio > 0 ? `Cuota mensual: $${subsidio.toFixed(2)} / ${periodFactors[periodo]} = $${subsidioProrrateado.toFixed(2)}` : 'Ingreso excede límite';

    steps.push({
      step: 5,
      description: 'Determinar subsidio al empleo',
      formula: `Ingreso equiv. mensual: $${ingresoMensualEquivalente.toFixed(2)}`,
      result: subsidioProrrateado,
      details: subsidyDetails
    });

    // Step 6: Final ISR
    const isrFinal = Math.max(0, isrAntesSubsidio - subsidioProrrateado);

    steps.push({
      step: 6,
      description: 'ISR final (ISR - Subsidio)',
      formula: `max(0, $${isrAntesSubsidio.toFixed(2)} - $${subsidioProrrateado.toFixed(2)})`,
      result: isrFinal
    });

    const tasaEfectiva = ingresoGravable > 0 ? (isrFinal / ingresoGravable) * 100 : 0;

    return {
      ingresoGravable,
      periodo,
      year,
      ingresoMensualizado: ingresoMensualEquivalente,
      bracket,
      excedente,
      impuestoMarginal,
      isrAntesSubsidio,
      subsidio: subsidioProrrateado,
      isrFinal,
      tasaEfectiva,
      steps
    };
  }

  // For 2024/2025 or decenal period, use factor-based conversion
  const brackets = getISRBrackets(year, 'mensual');

  // Step 1: Convert to monthly
  let ingresoMensualizado = ingresoGravable;
  let factor = 1;
  switch (periodo) {
    case 'quincenal': factor = 2; break;
    case 'semanal': factor = 4.33; break;
    case 'decenal': factor = 3; break;
    case 'diaria': factor = 30.4; break;
    case 'anual': factor = 1/12; break;
  }
  ingresoMensualizado = ingresoGravable * factor;

  steps.push({
    step: 1,
    description: 'Conversión a base mensual',
    formula: periodo === 'mensual'
      ? 'Sin conversión (ya es mensual)'
      : `$${ingresoGravable.toFixed(2)} × ${factor.toFixed(2)}`,
    result: ingresoMensualizado,
    details: `Período: ${periodo}`
  });

  // Step 2: Find bracket
  const bracket = brackets.find(b =>
    ingresoMensualizado >= b.limiteInferior && ingresoMensualizado <= b.limiteSuperior
  ) || brackets[brackets.length - 1];

  steps.push({
    step: 2,
    description: 'Identificar rango de ISR',
    formula: `$${bracket.limiteInferior.toFixed(2)} ≤ ingreso ≤ $${bracket.limiteSuperior === Infinity ? '∞' : bracket.limiteSuperior.toFixed(2)}`,
    result: bracket.tasa,
    details: `Tasa marginal: ${bracket.tasa}%, Cuota fija: $${bracket.cuotaFija.toFixed(2)}`
  });

  // Step 3: Calculate excess over lower limit
  const excedente = ingresoMensualizado - bracket.limiteInferior;

  steps.push({
    step: 3,
    description: 'Calcular excedente sobre límite inferior',
    formula: `$${ingresoMensualizado.toFixed(2)} - $${bracket.limiteInferior.toFixed(2)}`,
    result: excedente
  });

  // Step 4: Calculate marginal tax
  const impuestoMarginal = excedente * (bracket.tasa / 100);

  steps.push({
    step: 4,
    description: 'Calcular impuesto marginal',
    formula: `$${excedente.toFixed(2)} × ${bracket.tasa}%`,
    result: impuestoMarginal
  });

  // Step 5: Add fixed fee
  const isrAntesSubsidio = bracket.cuotaFija + impuestoMarginal;

  steps.push({
    step: 5,
    description: 'Sumar cuota fija',
    formula: `$${bracket.cuotaFija.toFixed(2)} + $${impuestoMarginal.toFixed(2)}`,
    result: isrAntesSubsidio
  });

  // Step 6: Calculate subsidy
  const subsidio = calculateSubsidy(ingresoMensualizado, year);

  const yearStr = year.toString() as '2024' | '2025' | '2026';
  const subsidyData = isrTablesData.subsidies[yearStr];
  const maxIncome = subsidyData.type === 'flat' ? (subsidyData.monthly as unknown as ISRSubsidyFlat).maxIncome : 7382.33;

  const subsidyDetails = year === 2024
    ? (subsidio > 0 ? 'Sistema escalonado: Aplica subsidio' : 'Sistema escalonado: No aplica subsidio')
    : (subsidio > 0 ? `Cuota fija: $${subsidio.toFixed(2)}` : 'Ingreso excede límite');

  steps.push({
    step: 6,
    description: 'Determinar subsidio al empleo',
    formula: year === 2024
      ? `Rango: $${ingresoMensualizado.toFixed(2)}`
      : `Ingreso ≤ $${maxIncome.toFixed(2)}`,
    result: subsidio,
    details: subsidyDetails
  });

  // Step 7: Final ISR
  const isrFinal = Math.max(0, isrAntesSubsidio - subsidio);

  steps.push({
    step: 7,
    description: 'ISR final (ISR - Subsidio)',
    formula: `max(0, $${isrAntesSubsidio.toFixed(2)} - $${subsidio.toFixed(2)})`,
    result: isrFinal
  });

  // Step 8: Convert back to original period
  const isrPeriodo = isrFinal / factor;

  if (periodo !== 'mensual') {
    steps.push({
      step: 8,
      description: `Convertir a período ${periodo}`,
      formula: `$${isrFinal.toFixed(2)} ÷ ${factor.toFixed(2)}`,
      result: isrPeriodo
    });
  }

  const tasaEfectiva = ingresoGravable > 0 ? (isrPeriodo / ingresoGravable) * 100 : 0;

  return {
    ingresoGravable,
    periodo,
    year,
    ingresoMensualizado,
    bracket,
    excedente,
    impuestoMarginal,
    isrAntesSubsidio,
    subsidio,
    isrFinal: isrPeriodo,
    tasaEfectiva,
    steps
  };
}

export interface IVACalculationResult {
  base: number;
  tasa: number;
  iva: number;
  total: number;
  desglose: {
    concepto: string;
    monto: number;
  }[];
}

export function calculateIVA(base: number, tasa: number = 16): IVACalculationResult {
  const iva = base * (tasa / 100);
  const total = base + iva;

  return {
    base,
    tasa,
    iva,
    total,
    desglose: [
      { concepto: 'Subtotal (Base)', monto: base },
      { concepto: `IVA (${tasa}%)`, monto: iva },
      { concepto: 'Total', monto: total }
    ]
  };
}

export interface IEPSRate {
  product: string;
  name: string;
  rate: number;
  description: string;
}

export const IEPS_RATES: IEPSRate[] = [
  { product: 'alcohol_bajo', name: 'Bebidas alcohólicas (<14°)', rate: 26.5, description: 'Cerveza, vino de mesa' },
  { product: 'alcohol_medio', name: 'Bebidas alcohólicas (14-20°)', rate: 30, description: 'Vinos generosos, licores' },
  { product: 'alcohol_alto', name: 'Bebidas alcohólicas (>20°)', rate: 53, description: 'Destilados: tequila, whisky, ron' },
  { product: 'tabaco', name: 'Cigarros', rate: 160, description: 'Cigarros y tabacos labrados' },
  { product: 'gasolina', name: 'Gasolinas', rate: 16.39, description: 'Gasolina y diésel' },
  { product: 'bebidas_azucaradas', name: 'Bebidas azucaradas', rate: 8, description: 'Refrescos, jugos con azúcar añadida' },
  { product: 'comida_chatarra', name: 'Alimentos no básicos', rate: 8, description: 'Alimentos con alta densidad calórica' }
];

export function calculateIEPS(base: number, productType: string): {
  base: number;
  product: IEPSRate;
  ieps: number;
  total: number;
} {
  const product = IEPS_RATES.find(r => r.product === productType) || IEPS_RATES[0];
  const ieps = base * (product.rate / 100);

  return {
    base,
    product,
    ieps,
    total: base + ieps
  };
}
