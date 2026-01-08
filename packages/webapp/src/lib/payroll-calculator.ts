/**
 * Calculadora de Nómina Completa para México
 * Calcula el costo total del empleador y el ingreso neto del trabajador
 * Incluye: IMSS, ISR, INFONAVIT, ISN, provisiones y reservas de liquidación
 */

import imssTablesData from '../../shared-data/imss-tables.json';
import isrTablesData from '../../shared-data/isr-tables.json';

// Types
export type PayrollYear = 2024 | 2025 | 2026;
export type RiskClass = 1 | 2 | 3 | 4 | 5;
export type PayrollPeriod = 'mensual' | 'quincenal' | 'semanal';

// ISN rates by state (2024-2026)
export const ISN_RATES: Record<string, number> = {
  'AGS': 0.025, // Aguascalientes
  'BC': 0.0175, // Baja California
  'BCS': 0.025, // Baja California Sur
  'CAM': 0.02, // Campeche
  'CHIS': 0.02, // Chiapas
  'CHIH': 0.03, // Chihuahua
  'CDMX': 0.03, // Ciudad de México
  'COAH': 0.02, // Coahuila
  'COL': 0.02, // Colima
  'DGO': 0.02, // Durango
  'GTO': 0.02, // Guanajuato
  'GRO': 0.02, // Guerrero
  'HGO': 0.025, // Hidalgo
  'JAL': 0.02, // Jalisco
  'MEX': 0.03, // Estado de México
  'MICH': 0.02, // Michoacán
  'MOR': 0.02, // Morelos
  'NAY': 0.02, // Nayarit
  'NL': 0.03, // Nuevo León
  'OAX': 0.03, // Oaxaca
  'PUE': 0.03, // Puebla
  'QRO': 0.02, // Querétaro
  'QROO': 0.03, // Quintana Roo
  'SLP': 0.025, // San Luis Potosí
  'SIN': 0.024, // Sinaloa
  'SON': 0.02, // Sonora
  'TAB': 0.025, // Tabasco
  'TAM': 0.02, // Tamaulipas
  'TLAX': 0.03, // Tlaxcala
  'VER': 0.03, // Veracruz
  'YUC': 0.025, // Yucatán
  'ZAC': 0.025, // Zacatecas
};

export const STATES = [
  { code: 'AGS', name: 'Aguascalientes' },
  { code: 'BC', name: 'Baja California' },
  { code: 'BCS', name: 'Baja California Sur' },
  { code: 'CAM', name: 'Campeche' },
  { code: 'CHIS', name: 'Chiapas' },
  { code: 'CHIH', name: 'Chihuahua' },
  { code: 'CDMX', name: 'Ciudad de México' },
  { code: 'COAH', name: 'Coahuila' },
  { code: 'COL', name: 'Colima' },
  { code: 'DGO', name: 'Durango' },
  { code: 'GTO', name: 'Guanajuato' },
  { code: 'GRO', name: 'Guerrero' },
  { code: 'HGO', name: 'Hidalgo' },
  { code: 'JAL', name: 'Jalisco' },
  { code: 'MEX', name: 'Estado de México' },
  { code: 'MICH', name: 'Michoacán' },
  { code: 'MOR', name: 'Morelos' },
  { code: 'NAY', name: 'Nayarit' },
  { code: 'NL', name: 'Nuevo León' },
  { code: 'OAX', name: 'Oaxaca' },
  { code: 'PUE', name: 'Puebla' },
  { code: 'QRO', name: 'Querétaro' },
  { code: 'QROO', name: 'Quintana Roo' },
  { code: 'SLP', name: 'San Luis Potosí' },
  { code: 'SIN', name: 'Sinaloa' },
  { code: 'SON', name: 'Sonora' },
  { code: 'TAB', name: 'Tabasco' },
  { code: 'TAM', name: 'Tamaulipas' },
  { code: 'TLAX', name: 'Tlaxcala' },
  { code: 'VER', name: 'Veracruz' },
  { code: 'YUC', name: 'Yucatán' },
  { code: 'ZAC', name: 'Zacatecas' },
];

// Risk class primes
const RISK_PRIMES: Record<RiskClass, number> = {
  1: 0.00543,
  2: 0.01084,
  3: 0.02174,
  4: 0.04350,
  5: 0.07435,
};

// Vacation days by seniority (LFT 2023+)
export function getVacationDays(yearsWorked: number): number {
  if (yearsWorked < 1) return 0;
  if (yearsWorked === 1) return 12;
  if (yearsWorked === 2) return 14;
  if (yearsWorked === 3) return 16;
  if (yearsWorked === 4) return 18;
  if (yearsWorked === 5) return 20;
  // After 5 years, +2 days every 5 years
  const extraPeriods = Math.floor((yearsWorked - 5) / 5);
  return 20 + (extraPeriods * 2);
}

export interface PayrollInput {
  salarioBrutoMensual: number;
  estado: string;
  claseRiesgo: RiskClass;
  diasAguinaldo: number; // Mínimo 15, algunos dan 30, 40, etc.
  antiguedadAnios: number;
  primaVacacional: number; // Porcentaje (mínimo 25%)
  incluirPTU: boolean;
  porcentajePTU?: number; // Como % del salario mensual (aproximado)
  incluirReservaLiquidacion: boolean;
  fondoAhorroPatron?: number; // % aportación patrón
  valesDespensa?: number; // Monto mensual
  year: PayrollYear;
}

export interface IMSSPatronDetail {
  enfermedadMaternidadFija: number;
  enfermedadMaternidadExcedente: number;
  prestacionesDinero: number;
  gastosMedicosPensionados: number;
  invalidezVida: number;
  retiro: number;
  cesantiaVejez: number;
  guarderias: number;
  riesgoTrabajo: number;
  total: number;
}

export interface IMSSTrabajadorDetail {
  enfermedadMaternidadExcedente: number;
  prestacionesDinero: number;
  gastosMedicosPensionados: number;
  invalidezVida: number;
  cesantiaVejez: number;
  total: number;
}

export interface ReservaLiquidacionDetail {
  indemnizacion3Meses: number;
  primaAntiguedad: number;
  veinteDiasPorAnio: number;
  totalAnual: number;
  provisionMensual: number;
}

export interface PayrollResult {
  // Input summary
  salarioBrutoMensual: number;
  salarioDiario: number;
  salarioDiarioIntegrado: number;
  year: PayrollYear;
  uma: number;
  salarioBaseTopeUMA: number; // Tope 25 UMAs

  // Cuotas IMSS Patrón (detalle)
  imssPatron: IMSSPatronDetail;

  // Otros costos patronales
  infonavit: number;
  impuestoSobreNomina: number;
  tasaISN: number;

  // Provisiones
  provisionAguinaldo: number;
  provisionVacaciones: number;
  provisionPrimaVacacional: number;
  provisionPTU: number;

  // Reserva de liquidación
  reservaLiquidacion: ReservaLiquidacionDetail;

  // Fondo de ahorro y vales
  fondoAhorroPatron: number;
  valesDespensa: number;

  // Totales empleador
  costoDirectoMensual: number; // Salario + IMSS + INFONAVIT + ISN
  costoTotalMensual: number; // Incluyendo provisiones
  costoTotalAnual: number;
  porcentajeAdicionalSobreBruto: number;

  // Deducciones trabajador
  imssTrabajador: IMSSTrabajadorDetail;
  isrRetenido: number;
  subsidioEmpleo: number;
  deduccionesTotal: number;

  // Ingreso neto
  ingresoNetoMensual: number;
  ingresoNetoAnual: number;

  // Prestaciones anualizadas netas
  aguinaldoNeto: number;
  primaVacacionalNeta: number;
  ptuNeto: number;

  // Métricas
  tasaEfectivaISR: number;
  relacionCostoIngresoNeto: number; // Cuánto cuesta generar $1 de ingreso neto
}

// Get UMA for year
function getUMA(year: PayrollYear): { diaria: number; mensual: number } {
  const yearStr = year.toString() as '2024' | '2025' | '2026';
  return {
    diaria: imssTablesData.uma[yearStr].diaria,
    mensual: imssTablesData.uma[yearStr].mensual,
  };
}

// Calculate Salario Diario Integrado (SDI)
function calculateSDI(
  salarioDiario: number,
  diasAguinaldo: number,
  antiguedadAnios: number,
  primaVacacional: number
): number {
  // SDI = Salario Diario × Factor de Integración
  // Factor = 1 + (Aguinaldo/365) + (Vacaciones × Prima Vacacional / 365)
  const vacationDays = getVacationDays(antiguedadAnios);
  const factorAguinaldo = diasAguinaldo / 365;
  const factorPrimaVacacional = (vacationDays * (primaVacacional / 100)) / 365;
  const factorIntegracion = 1 + factorAguinaldo + factorPrimaVacacional;
  return salarioDiario * factorIntegracion;
}

// Calculate IMSS Patron contributions
function calculateIMSSPatron(
  sbc: number, // Salario Base de Cotización (diario)
  claseRiesgo: RiskClass,
  year: PayrollYear
): IMSSPatronDetail {
  const uma = getUMA(year);
  const cuotas = imssTablesData.cuotas_imss;

  // Tope de 25 UMAs
  const sbcTopado = Math.min(sbc, uma.diaria * 25);
  const sbcMensual = sbcTopado * 30;

  // Enfermedad y Maternidad - Cuota Fija (20.4% sobre UMA × 3)
  const baseUMAx3 = uma.diaria * 3 * 30; // UMA mensual × 3
  const enfermedadMaternidadFija = baseUMAx3 * cuotas.enfermedad_maternidad.prestaciones_en_especie.patron;

  // Enfermedad y Maternidad - Excedente sobre 3 UMAs
  const excedente3UMA = Math.max(0, sbcMensual - baseUMAx3);
  const enfermedadMaternidadExcedente = excedente3UMA * cuotas.enfermedad_maternidad.prestaciones_en_especie_excedente.patron;

  // Prestaciones en dinero
  const prestacionesDinero = sbcMensual * cuotas.enfermedad_maternidad.prestaciones_en_dinero.patron;

  // Gastos médicos pensionados
  const gastosMedicosPensionados = sbcMensual * cuotas.enfermedad_maternidad.gastos_medicos_pensionados.patron;

  // Invalidez y Vida
  const invalidezVida = sbcMensual * cuotas.invalidez_vida.patron;

  // Retiro
  const retiro = sbcMensual * cuotas.retiro_cesantia_vejez.retiro.patron;

  // Cesantía y Vejez
  const cesantiaVejez = sbcMensual * cuotas.retiro_cesantia_vejez.cesantia_vejez.patron;

  // Guarderías
  const guarderias = sbcMensual * cuotas.guarderias_prestaciones_sociales.patron;

  // Riesgo de Trabajo
  const riesgoTrabajo = sbcMensual * RISK_PRIMES[claseRiesgo];

  const total = enfermedadMaternidadFija + enfermedadMaternidadExcedente + prestacionesDinero +
    gastosMedicosPensionados + invalidezVida + retiro + cesantiaVejez + guarderias + riesgoTrabajo;

  return {
    enfermedadMaternidadFija,
    enfermedadMaternidadExcedente,
    prestacionesDinero,
    gastosMedicosPensionados,
    invalidezVida,
    retiro,
    cesantiaVejez,
    guarderias,
    riesgoTrabajo,
    total,
  };
}

// Calculate IMSS Worker contributions
function calculateIMSSTrabajador(
  sbc: number, // Salario Base de Cotización (diario)
  year: PayrollYear
): IMSSTrabajadorDetail {
  const uma = getUMA(year);
  const cuotas = imssTablesData.cuotas_imss;

  // Tope de 25 UMAs
  const sbcTopado = Math.min(sbc, uma.diaria * 25);
  const sbcMensual = sbcTopado * 30;
  const baseUMAx3 = uma.diaria * 3 * 30;

  // Enfermedad y Maternidad - Excedente sobre 3 UMAs
  const excedente3UMA = Math.max(0, sbcMensual - baseUMAx3);
  const enfermedadMaternidadExcedente = excedente3UMA * cuotas.enfermedad_maternidad.prestaciones_en_especie_excedente.trabajador;

  // Prestaciones en dinero
  const prestacionesDinero = sbcMensual * cuotas.enfermedad_maternidad.prestaciones_en_dinero.trabajador;

  // Gastos médicos pensionados
  const gastosMedicosPensionados = sbcMensual * cuotas.enfermedad_maternidad.gastos_medicos_pensionados.trabajador;

  // Invalidez y Vida
  const invalidezVida = sbcMensual * cuotas.invalidez_vida.trabajador;

  // Cesantía y Vejez
  const cesantiaVejez = sbcMensual * cuotas.retiro_cesantia_vejez.cesantia_vejez.trabajador;

  const total = enfermedadMaternidadExcedente + prestacionesDinero + gastosMedicosPensionados +
    invalidezVida + cesantiaVejez;

  return {
    enfermedadMaternidadExcedente,
    prestacionesDinero,
    gastosMedicosPensionados,
    invalidezVida,
    cesantiaVejez,
    total,
  };
}

// Calculate ISR using monthly tables
interface ISRBracket {
  limiteInferior: number;
  limiteSuperior: number | null;
  cuotaFija: number;
  tasa: number;
}

function calculateISRMensual(baseGravable: number, year: PayrollYear): { isr: number; subsidio: number } {
  const yearStr = year.toString() as '2024' | '2025' | '2026';
  const brackets = isrTablesData.brackets[yearStr].monthly as ISRBracket[];

  // Find applicable bracket
  const bracket = brackets.find(b => {
    const limiteSuperior = b.limiteSuperior === null ? Infinity : b.limiteSuperior;
    return baseGravable >= b.limiteInferior && baseGravable <= limiteSuperior;
  }) || brackets[brackets.length - 1];

  // Calculate ISR
  const excedente = Math.max(0, baseGravable - bracket.limiteInferior);
  const impuestoMarginal = excedente * (bracket.tasa / 100);
  const isrAntesSubsidio = bracket.cuotaFija + impuestoMarginal;

  // Calculate subsidy
  let subsidio = 0;
  const subsidyData = isrTablesData.subsidies[yearStr];

  if (subsidyData.type === 'tiered') {
    // 2024: tiered system
    interface SubsidyBracket {
      desde: number;
      hasta: number | null;
      subsidio: number;
    }
    const monthlySubsidy = subsidyData.monthly as unknown as SubsidyBracket[];
    const subsidyBracket = monthlySubsidy.find((s: SubsidyBracket) => {
      const hasta = s.hasta === null ? Infinity : s.hasta;
      return baseGravable >= s.desde && baseGravable <= hasta;
    });
    subsidio = subsidyBracket?.subsidio || 0;
  } else {
    // 2025/2026: flat system
    interface FlatSubsidy {
      amount: number;
      maxIncome: number;
    }
    const flatSubsidy = subsidyData.monthly as unknown as FlatSubsidy;
    subsidio = baseGravable <= flatSubsidy.maxIncome ? flatSubsidy.amount : 0;
  }

  const isrFinal = Math.max(0, isrAntesSubsidio - subsidio);

  return { isr: isrFinal, subsidio: Math.min(subsidio, isrAntesSubsidio) };
}

// Calculate severance reserve (Reserva de Liquidación)
function calculateReservaLiquidacion(
  salarioDiario: number,
  salarioDiarioIntegrado: number,
  antiguedadAnios: number,
  year: PayrollYear
): ReservaLiquidacionDetail {
  const salarioMinimo = imssTablesData.salario_minimo[year.toString() as '2024' | '2025' | '2026'].general;

  // 3 meses de indemnización (Art. 50 LFT)
  const indemnizacion3Meses = salarioDiarioIntegrado * 90;

  // Prima de antigüedad: 12 días por año trabajado, tope de 2 salarios mínimos
  const diasPrimaAntiguedad = 12 * antiguedadAnios;
  const topePrimaAntiguedad = salarioMinimo * 2;
  const salarioParaPrima = Math.min(salarioDiario, topePrimaAntiguedad);
  const primaAntiguedad = diasPrimaAntiguedad * salarioParaPrima;

  // 20 días por año (Art. 50 Fracción II LFT - despido injustificado)
  const veinteDiasPorAnio = salarioDiarioIntegrado * 20 * antiguedadAnios;

  const totalAnual = indemnizacion3Meses + primaAntiguedad + veinteDiasPorAnio;
  const provisionMensual = totalAnual / 12;

  return {
    indemnizacion3Meses,
    primaAntiguedad,
    veinteDiasPorAnio,
    totalAnual,
    provisionMensual,
  };
}

// Main payroll calculation function
export function calculatePayroll(input: PayrollInput): PayrollResult {
  const uma = getUMA(input.year);
  const salarioDiario = input.salarioBrutoMensual / 30;

  // Calculate SDI
  const sdi = calculateSDI(
    salarioDiario,
    input.diasAguinaldo,
    input.antiguedadAnios,
    input.primaVacacional
  );

  // Apply 25 UMA cap for IMSS calculations
  const sdiTopado = Math.min(sdi, uma.diaria * 25);

  // IMSS Patron
  const imssPatron = calculateIMSSPatron(sdi, input.claseRiesgo, input.year);

  // INFONAVIT (5% sobre SBC topado)
  const infonavit = sdiTopado * 30 * 0.05;

  // ISN (Impuesto Sobre Nómina)
  const tasaISN = ISN_RATES[input.estado] || 0.02;
  const impuestoSobreNomina = input.salarioBrutoMensual * tasaISN;

  // Provisions
  // Aguinaldo: días de aguinaldo / 12 meses
  const provisionAguinaldo = (salarioDiario * input.diasAguinaldo) / 12;

  // Vacaciones: días de vacaciones según antigüedad
  const diasVacaciones = getVacationDays(input.antiguedadAnios);
  const provisionVacaciones = (salarioDiario * diasVacaciones) / 12;

  // Prima Vacacional: % sobre días de vacaciones
  const provisionPrimaVacacional = (salarioDiario * diasVacaciones * (input.primaVacacional / 100)) / 12;

  // PTU (opcional, como aproximación mensual)
  const provisionPTU = input.incluirPTU && input.porcentajePTU
    ? input.salarioBrutoMensual * (input.porcentajePTU / 100)
    : 0;

  // Reserva de liquidación
  const reservaLiquidacion = input.incluirReservaLiquidacion
    ? calculateReservaLiquidacion(salarioDiario, sdi, input.antiguedadAnios, input.year)
    : {
        indemnizacion3Meses: 0,
        primaAntiguedad: 0,
        veinteDiasPorAnio: 0,
        totalAnual: 0,
        provisionMensual: 0,
      };

  // Fondo de ahorro patrón (si aplica)
  const fondoAhorroPatron = input.fondoAhorroPatron
    ? input.salarioBrutoMensual * (input.fondoAhorroPatron / 100)
    : 0;

  // Vales de despensa
  const valesDespensa = input.valesDespensa || 0;

  // --- EMPLOYER COSTS ---
  const costoDirectoMensual = input.salarioBrutoMensual + imssPatron.total + infonavit + impuestoSobreNomina;

  const costoTotalMensual = costoDirectoMensual +
    provisionAguinaldo + provisionVacaciones + provisionPrimaVacacional + provisionPTU +
    reservaLiquidacion.provisionMensual + fondoAhorroPatron + valesDespensa;

  const costoTotalAnual = costoTotalMensual * 12;

  // --- WORKER DEDUCTIONS ---
  const imssTrabajador = calculateIMSSTrabajador(sdi, input.year);

  // ISR base = Salario bruto - IMSS trabajador
  const baseGravableISR = input.salarioBrutoMensual - imssTrabajador.total;
  const { isr: isrRetenido, subsidio: subsidioEmpleo } = calculateISRMensual(baseGravableISR, input.year);

  const deduccionesTotal = imssTrabajador.total + isrRetenido;

  // --- NET INCOME ---
  const ingresoNetoMensual = input.salarioBrutoMensual - deduccionesTotal + valesDespensa;

  // Annual benefits (net estimates)
  // Aguinaldo: First 30 days are exempt from ISR
  const aguinaldoBruto = salarioDiario * input.diasAguinaldo;
  const aguinaldoExento = Math.min(aguinaldoBruto, uma.diaria * 30);
  const aguinaldoGravado = aguinaldoBruto - aguinaldoExento;
  const { isr: isrAguinaldo } = calculateISRMensual(aguinaldoGravado + baseGravableISR, input.year);
  const isrAdicionalAguinaldo = Math.max(0, isrAguinaldo - isrRetenido);
  const aguinaldoNeto = aguinaldoBruto - isrAdicionalAguinaldo;

  // Prima vacacional: First 15 days of salary are exempt
  const primaVacacionalBruto = salarioDiario * diasVacaciones * (input.primaVacacional / 100);
  const primaVacacionalExento = Math.min(primaVacacionalBruto, uma.diaria * 15);
  const primaVacacionalGravado = primaVacacionalBruto - primaVacacionalExento;
  const { isr: isrPrimaVac } = calculateISRMensual(primaVacacionalGravado + baseGravableISR, input.year);
  const isrAdicionalPrimaVac = Math.max(0, isrPrimaVac - isrRetenido);
  const primaVacacionalNeta = primaVacacionalBruto - isrAdicionalPrimaVac;

  // PTU: First 15 days of UMA are exempt
  const ptuBruto = provisionPTU * 12;
  const ptuExento = Math.min(ptuBruto, uma.diaria * 15);
  const ptuGravado = ptuBruto - ptuExento;
  const { isr: isrPTU } = calculateISRMensual((ptuGravado / 12) + baseGravableISR, input.year);
  const isrAdicionalPTU = Math.max(0, (isrPTU - isrRetenido) * 12);
  const ptuNeto = ptuBruto - isrAdicionalPTU;

  const ingresoNetoAnual = (ingresoNetoMensual * 12) + aguinaldoNeto + primaVacacionalNeta + ptuNeto;

  // --- METRICS ---
  const porcentajeAdicionalSobreBruto = ((costoTotalMensual - input.salarioBrutoMensual) / input.salarioBrutoMensual) * 100;
  const tasaEfectivaISR = (isrRetenido / input.salarioBrutoMensual) * 100;
  const relacionCostoIngresoNeto = costoTotalMensual / ingresoNetoMensual;

  return {
    salarioBrutoMensual: input.salarioBrutoMensual,
    salarioDiario,
    salarioDiarioIntegrado: sdi,
    year: input.year,
    uma: uma.diaria,
    salarioBaseTopeUMA: uma.diaria * 25 * 30,

    imssPatron,
    infonavit,
    impuestoSobreNomina,
    tasaISN,

    provisionAguinaldo,
    provisionVacaciones,
    provisionPrimaVacacional,
    provisionPTU,

    reservaLiquidacion,

    fondoAhorroPatron,
    valesDespensa,

    costoDirectoMensual,
    costoTotalMensual,
    costoTotalAnual,
    porcentajeAdicionalSobreBruto,

    imssTrabajador,
    isrRetenido,
    subsidioEmpleo,
    deduccionesTotal,

    ingresoNetoMensual,
    ingresoNetoAnual,

    aguinaldoNeto,
    primaVacacionalNeta,
    ptuNeto,

    tasaEfectivaISR,
    relacionCostoIngresoNeto,
  };
}

// Inverse calculation: Given budget, find gross salary
export function calculateGrossFromBudget(
  presupuestoMensual: number,
  input: Omit<PayrollInput, 'salarioBrutoMensual'>
): { salarioBrutoMensual: number; result: PayrollResult } {
  // Use binary search to find the gross salary that produces the target cost
  let low = 0;
  let high = presupuestoMensual * 2; // Start with a reasonable upper bound
  let bestGuess = presupuestoMensual * 0.6; // Initial guess: ~60% of budget is typically gross

  for (let i = 0; i < 50; i++) { // Max 50 iterations
    const mid = (low + high) / 2;
    const result = calculatePayroll({ ...input, salarioBrutoMensual: mid });

    if (Math.abs(result.costoTotalMensual - presupuestoMensual) < 0.01) {
      return { salarioBrutoMensual: mid, result };
    }

    if (result.costoTotalMensual < presupuestoMensual) {
      low = mid;
      bestGuess = mid;
    } else {
      high = mid;
    }
  }

  const finalResult = calculatePayroll({ ...input, salarioBrutoMensual: bestGuess });
  return { salarioBrutoMensual: bestGuess, result: finalResult };
}
