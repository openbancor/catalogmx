/**
 * Mexican Tax Calculators with step-by-step breakdown
 */

// ISR 2024 Monthly brackets
const ISR_MONTHLY_BRACKETS = [
  { limiteInferior: 0.01, limiteSuperior: 746.04, cuotaFija: 0, tasa: 1.92 },
  { limiteInferior: 746.05, limiteSuperior: 6332.05, cuotaFija: 14.32, tasa: 6.40 },
  { limiteInferior: 6332.06, limiteSuperior: 11128.01, cuotaFija: 371.83, tasa: 10.88 },
  { limiteInferior: 11128.02, limiteSuperior: 12935.82, cuotaFija: 893.63, tasa: 16.00 },
  { limiteInferior: 12935.83, limiteSuperior: 15487.71, cuotaFija: 1182.88, tasa: 17.92 },
  { limiteInferior: 15487.72, limiteSuperior: 31236.49, cuotaFija: 1640.18, tasa: 21.36 },
  { limiteInferior: 31236.50, limiteSuperior: 49233.00, cuotaFija: 5004.12, tasa: 23.52 },
  { limiteInferior: 49233.01, limiteSuperior: 93993.90, cuotaFija: 9236.89, tasa: 30.00 },
  { limiteInferior: 93993.91, limiteSuperior: 125325.20, cuotaFija: 22665.17, tasa: 32.00 },
  { limiteInferior: 125325.21, limiteSuperior: 375975.61, cuotaFija: 32691.18, tasa: 34.00 },
  { limiteInferior: 375975.62, limiteSuperior: Infinity, cuotaFija: 117912.32, tasa: 35.00 }
];

// ISR Subsidy (subsidio al empleo) 2024 monthly
const ISR_SUBSIDY_MONTHLY = [
  { desde: 0.01, hasta: 1768.96, subsidio: 407.02 },
  { desde: 1768.97, hasta: 2653.38, subsidio: 406.83 },
  { desde: 2653.39, hasta: 3472.84, subsidio: 406.62 },
  { desde: 3472.85, hasta: 3537.87, subsidio: 392.77 },
  { desde: 3537.88, hasta: 4446.15, subsidio: 382.46 },
  { desde: 4446.16, hasta: 4717.18, subsidio: 354.23 },
  { desde: 4717.19, hasta: 5335.42, subsidio: 324.87 },
  { desde: 5335.43, hasta: 6224.67, subsidio: 294.63 },
  { desde: 6224.68, hasta: 7113.90, subsidio: 253.54 },
  { desde: 7113.91, hasta: 7382.33, subsidio: 217.61 },
  { desde: 7382.34, hasta: Infinity, subsidio: 0 }
];

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
  periodo: 'mensual' | 'quincenal' | 'semanal' | 'anual' = 'mensual'
): ISRCalculationResult {
  const steps: ISRCalculationStep[] = [];

  // Step 1: Convert to monthly
  let ingresoMensualizado = ingresoGravable;
  let factor = 1;
  switch (periodo) {
    case 'quincenal': factor = 2; break;
    case 'semanal': factor = 4.33; break;
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
  const bracket = ISR_MONTHLY_BRACKETS.find(b =>
    ingresoMensualizado >= b.limiteInferior && ingresoMensualizado <= b.limiteSuperior
  ) || ISR_MONTHLY_BRACKETS[ISR_MONTHLY_BRACKETS.length - 1];

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
  const subsidyBracket = ISR_SUBSIDY_MONTHLY.find(s =>
    ingresoMensualizado >= s.desde && ingresoMensualizado <= s.hasta
  ) || { subsidio: 0 };
  const subsidio = subsidyBracket.subsidio;

  steps.push({
    step: 6,
    description: 'Determinar subsidio al empleo',
    formula: `Rango: $${ingresoMensualizado.toFixed(2)}`,
    result: subsidio,
    details: subsidio > 0 ? 'Aplica subsidio' : 'No aplica subsidio'
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
