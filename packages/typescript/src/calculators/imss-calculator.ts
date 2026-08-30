/**
 * Calculadora histórica de IMSS (Instituto Mexicano del Seguro Social) para México.
 *
 * Las cuotas que cambian por ejercicio (principalmente CEAV y Modalidad 40)
 * se seleccionan por año. La UMA se selecciona por vigencia cuando el llamador
 * proporciona una fecha, porque cambia el 1 de febrero y no el 1 de enero.
 */

import { loadCatalogData } from '../utils/catalog-loader';

export type IMSSYear = 2024 | 2025 | 2026;
export type ZonaSalario = 'general' | 'frontera';
export type ClaseRiesgo = 1 | 2 | 3 | 4 | 5;

export interface UMAInfo {
  diaria: number;
  mensual: number;
  anual: number;
  vigencia_desde?: string;
  vigencia_hasta?: string;
  source_id?: string;
}

export interface CuotasIMSSResult {
  salario_diario: number;
  dias: number;
  salario_base_cotizacion: number;
  year: number;
  uma_diaria: number;
  ceav_patron_rate: number;
  cuotas_patron: Record<string, number>;
  cuotas_trabajador: Record<string, number>;
  total_patron: number;
  total_trabajador: number;
  total_imss: number;
}

export interface Modalidad40Result {
  salario_base_cotizacion: number;
  ultimo_sbc_mensual: number;
  year: number;
  uma_mensual: number;
  cuota_mensual: number;
  porcentaje_total: number;
  componentes: Record<string, number>;
}

export interface Modalidad10Result {
  salario_base_cotizacion: number;
  year: number;
  cuota_mensual: number;
  cuota_fija_uma: number;
  cuota_variable: number;
  porcentaje_variable: number;
  componentes: Record<string, number>;
}

type CuotaBase = {
  descripcion: string;
  patron: number;
  trabajador: number;
  base: string;
  umbral_uma?: number;
};

type CuotaEnfermedadMaternidad = {
  prestaciones_en_especie: CuotaBase;
  prestaciones_en_especie_excedente: CuotaBase;
  prestaciones_en_dinero: CuotaBase;
  gastos_medicos_pensionados: CuotaBase;
};

type CEAVPatronRate = {
  rango: string;
  tasa: number;
};

type CuotaRiesgoTrabajo = Record<`clase_${ClaseRiesgo}`, number> & {
  minima?: number;
  maxima?: number;
};

type CuotasIMSS = {
  enfermedad_maternidad: CuotaEnfermedadMaternidad;
  invalidez_vida: {
    patron: number;
    trabajador: number;
  };
  retiro_cesantia_vejez: {
    retiro: { patron: number };
    cesantia_vejez: {
      trabajador: number;
      patron_por_ejercicio: Record<string, CEAVPatronRate[]>;
    };
  };
  guarderias_prestaciones_sociales: {
    patron: number;
  };
  riesgo_trabajo: CuotaRiesgoTrabajo;
};

type Modalidad40LimitesSalario = {
  maximo_uma: number;
  minimo_regla?: string;
};

type Modalidad10LimitesSalario = {
  minimo_uma: number;
  maximo_uma: number;
};

type Modalidad40Data = {
  descripcion: string;
  verification?: string;
  requisitos: Record<string, number | string | boolean>;
  calculo: {
    componentes_constantes: Record<string, number>;
    ceav_patronal: { source_path: string; selection: string };
  };
  referencia_por_ejercicio: Record<
    string,
    {
      vigencia_desde: string;
      vigencia_hasta: string;
      tasa_total_banda_4_01_uma_en_adelante: number;
    }
  >;
  limites_salario: Modalidad40LimitesSalario;
};

type Modalidad10Data = {
  descripcion: string;
  verification?: string;
  requisitos: Record<string, number | string | boolean>;
  cuota_mensual: {
    formula: string;
    porcentaje_variable: number;
    cuota_fija_uma_factor: number;
    componentes: Record<string, number | string>;
  };
  limites_salario: Modalidad10LimitesSalario;
  beneficios: string[];
};

type SalarioMinimoData = {
  general: number;
  frontera: number;
  vigencia_desde?: string;
  vigencia_hasta?: string;
  source_id?: string;
};

type RiesgoTrabajoClase = {
  clase: ClaseRiesgo;
  prima: number;
  descripcion: string;
  ejemplos: string[];
};

interface IMSSTablesData {
  _meta: {
    schema_version?: number;
    description: string;
    calculation: string;
    updated: string;
    verification?: Record<string, string>;
    sources?: Record<string, Record<string, string>>;
  };
  uma: Record<string, UMAInfo>;
  salario_minimo: Record<string, SalarioMinimoData>;
  cuotas_imss: CuotasIMSS;
  modalidad_40: Modalidad40Data;
  modalidad_10: Modalidad10Data;
  topes_cotizacion: Record<string, unknown>;
  riesgos_trabajo_clases: RiesgoTrabajoClase[];
}

interface IMSSCatalogsData {
  _meta: {
    description: string;
    source: string;
    updated: string;
  };
  tipos_movimiento_afiliatorio: Array<Record<string, unknown>>;
  tipos_trabajador: Array<Record<string, unknown>>;
  tipos_incapacidad: Array<Record<string, unknown>>;
  seguros_imss: Array<Record<string, unknown>>;
}

export class IMSSCalculator {
  private static _tablesData: IMSSTablesData | null = null;
  private static _catalogsData: IMSSCatalogsData | null = null;

  static setTablesData(data: IMSSTablesData): void {
    this._tablesData = data;
  }

  static setCatalogsData(data: IMSSCatalogsData): void {
    this._catalogsData = data;
  }

  private static loadTablesData(): void {
    if (this._tablesData !== null) return;
    this._tablesData = loadCatalogData<IMSSTablesData>('imss-tables.json');
  }

  private static loadCatalogsData(): void {
    if (this._catalogsData !== null) return;
    this._catalogsData = loadCatalogData<IMSSCatalogsData>('imss-catalogs.json');
  }

  /**
   * UMA publicada para un ejercicio. Para cálculos de enero, donde todavía
   * puede seguir vigente la UMA del ejercicio previo, usar getUMAForDate().
   */
  static getUMA(year: IMSSYear): UMAInfo {
    this.loadTablesData();
    const uma = this._tablesData!.uma[year.toString()];
    if (!uma) {
      throw new Error(`No se encontró UMA para ${year}`);
    }
    return { ...uma };
  }

  /**
   * UMA aplicable en una fecha concreta, respetando la vigencia 1-feb / 31-ene.
   */
  static getUMAForDate(fecha: string | Date): UMAInfo {
    this.loadTablesData();
    const iso = this.toIsoDate(fecha);
    const uma = Object.values(this._tablesData!.uma).find(
      (item) =>
        item.vigencia_desde !== undefined &&
        item.vigencia_hasta !== undefined &&
        iso >= item.vigencia_desde &&
        iso <= item.vigencia_hasta
    );
    if (!uma) {
      throw new Error(`No se encontró UMA vigente para ${iso}`);
    }
    return { ...uma };
  }

  static getSalarioMinimo(year: IMSSYear, zona: ZonaSalario = 'general'): number {
    this.loadTablesData();
    const row = this._tablesData!.salario_minimo[year.toString()];
    if (!row) {
      throw new Error(`No se encontró salario mínimo para ${year}`);
    }
    return row[zona];
  }

  /**
   * Tasa patronal CEAV aplicable al SBC diario.
   *
   * La fila "1 SM" se trata como caso especial. Para los demás salarios,
   * la reforma de pensiones clasifica el SBC en veces UMA.
   */
  static getCEAVPatronRate(salarioDiario: number, year: IMSSYear, fecha?: string | Date): number {
    this.loadTablesData();
    const rates =
      this._tablesData!.cuotas_imss.retiro_cesantia_vejez.cesantia_vejez.patron_por_ejercicio[
        year.toString()
      ];
    if (!rates || rates.length !== 8) {
      throw new Error(`No se encontró tarifa CEAV patronal para ${year}`);
    }

    const minimum = this._tablesData!.salario_minimo[year.toString()];
    if (!minimum) {
      throw new Error(`No se encontró salario mínimo para ${year}`);
    }
    const isMinimumWage =
      this.almostEqual(salarioDiario, minimum.general) ||
      this.almostEqual(salarioDiario, minimum.frontera);
    if (isMinimumWage) return rates[0].tasa;

    const uma = fecha === undefined ? this.getUMA(year) : this.getUMAForDate(fecha);
    const ratio = salarioDiario / uma.diaria;
    if (ratio <= 1.5) return rates[1].tasa;
    if (ratio <= 2.0) return rates[2].tasa;
    if (ratio <= 2.5) return rates[3].tasa;
    if (ratio <= 3.0) return rates[4].tasa;
    if (ratio <= 3.5) return rates[5].tasa;
    if (ratio <= 4.0) return rates[6].tasa;
    return rates[7].tasa;
  }

  /**
   * Calcula cuotas obrero-patronales.
   *
   * `fecha` es opcional para compatibilidad. Cuando se proporciona permite
   * resolver correctamente la UMA vigente en enero/febrero del mismo ejercicio.
   */
  static calcularCuotasObreroPatronales(
    salarioDiario: number,
    dias: number = 30,
    year: IMSSYear = 2026,
    claseRiesgo: ClaseRiesgo = 1,
    fecha?: string | Date
  ): CuotasIMSSResult {
    this.loadTablesData();
    const uma = fecha === undefined ? this.getUMA(year) : this.getUMAForDate(fecha);
    const cuotas = this._tablesData!.cuotas_imss;
    const salarioBase = salarioDiario * dias;
    const umaDiaria = uma.diaria;

    const cuotasPatron: Record<string, number> = {};
    const cuotasTrabajador: Record<string, number> = {};

    const em = cuotas.enfermedad_maternidad;
    cuotasPatron.enfermedad_mat_cuota_fija = umaDiaria * dias * em.prestaciones_en_especie.patron;

    const threshold = (em.prestaciones_en_especie_excedente.umbral_uma ?? 3) * umaDiaria;
    const excedenteBase = Math.max(0, salarioDiario - threshold) * dias;
    cuotasPatron.enfermedad_mat_excedente =
      excedenteBase * em.prestaciones_en_especie_excedente.patron;
    cuotasTrabajador.enfermedad_mat_excedente =
      excedenteBase * em.prestaciones_en_especie_excedente.trabajador;

    cuotasPatron.enfermedad_mat_dinero = salarioBase * em.prestaciones_en_dinero.patron;
    cuotasTrabajador.enfermedad_mat_dinero = salarioBase * em.prestaciones_en_dinero.trabajador;

    cuotasPatron.gastos_medicos_pensionados = salarioBase * em.gastos_medicos_pensionados.patron;
    cuotasTrabajador.gastos_medicos_pensionados =
      salarioBase * em.gastos_medicos_pensionados.trabajador;

    const iv = cuotas.invalidez_vida;
    cuotasPatron.invalidez_vida = salarioBase * iv.patron;
    cuotasTrabajador.invalidez_vida = salarioBase * iv.trabajador;

    const rcv = cuotas.retiro_cesantia_vejez;
    cuotasPatron.retiro = salarioBase * rcv.retiro.patron;
    const ceavPatronRate = this.getCEAVPatronRate(salarioDiario, year, fecha);
    cuotasPatron.cesantia_vejez = salarioBase * ceavPatronRate;
    cuotasTrabajador.cesantia_vejez = salarioBase * rcv.cesantia_vejez.trabajador;

    const gps = cuotas.guarderias_prestaciones_sociales;
    cuotasPatron.guarderias = salarioBase * gps.patron;

    const rt = cuotas.riesgo_trabajo;
    const primaRiesgo = rt[`clase_${claseRiesgo}`];
    cuotasPatron.riesgo_trabajo = salarioBase * primaRiesgo;

    const totalPatron = Object.values(cuotasPatron).reduce((sum, val) => sum + val, 0);
    const totalTrabajador = Object.values(cuotasTrabajador).reduce((sum, val) => sum + val, 0);

    return {
      salario_diario: salarioDiario,
      dias,
      salario_base_cotizacion: salarioBase,
      year,
      uma_diaria: umaDiaria,
      ceav_patron_rate: ceavPatronRate,
      cuotas_patron: cuotasPatron,
      cuotas_trabajador: cuotasTrabajador,
      total_patron: totalPatron,
      total_trabajador: totalTrabajador,
      total_imss: totalPatron + totalTrabajador,
    };
  }

  /**
   * Calcula la cuota mensual de Modalidad 40 usando montos mensuales.
   *
   * La continuación voluntaria sólo permite un SBC igual o mayor al último
   * SBC registrado. Por ello `ultimoSbcMensual` es obligatorio: omitir ese dato
   * convertiría una proyección en una validación de elegibilidad falsa.
   */
  static calcularModalidad40(
    salarioBaseCotizacionMensual: number,
    ultimoSbcMensual: number,
    year: IMSSYear,
    fecha?: string | Date
  ): Modalidad40Result {
    this.loadTablesData();
    const uma = fecha === undefined ? this.getUMA(year) : this.getUMAForDate(fecha);
    const mod40 = this._tablesData!.modalidad_40;
    const yearReference = mod40.referencia_por_ejercicio[year.toString()];
    if (!yearReference) {
      throw new Error(`No se encontró tarifa de Modalidad 40 para ${year}`);
    }

    const umaMensual = uma.mensual;
    const salarioMaximo = umaMensual * mod40.limites_salario.maximo_uma;
    if (!Number.isFinite(salarioBaseCotizacionMensual) || salarioBaseCotizacionMensual <= 0) {
      throw new RangeError('El SBC mensual de Modalidad 40 debe ser mayor que cero');
    }
    if (!Number.isFinite(ultimoSbcMensual) || ultimoSbcMensual <= 0) {
      throw new RangeError('El último SBC mensual debe ser mayor que cero');
    }
    if (ultimoSbcMensual > salarioMaximo) {
      throw new RangeError('El último SBC mensual excede el tope de 25 UMA');
    }
    if (salarioBaseCotizacionMensual < ultimoSbcMensual) {
      throw new RangeError('El SBC de Modalidad 40 no puede ser menor al último SBC registrado');
    }
    if (salarioBaseCotizacionMensual > salarioMaximo) {
      salarioBaseCotizacionMensual = salarioMaximo;
    }

    const diasUmaMensual = umaMensual / uma.diaria;
    const salarioDiarioEquivalente = salarioBaseCotizacionMensual / diasUmaMensual;
    const ceavPatronRate = this.getCEAVPatronRate(salarioDiarioEquivalente, year, fecha);

    const componentes: Record<string, number> = {};
    let porcentajeTotal = ceavPatronRate;
    componentes.cesantia_vejez_patron = salarioBaseCotizacionMensual * ceavPatronRate;
    for (const [key, value] of Object.entries(mod40.calculo.componentes_constantes)) {
      porcentajeTotal += value;
      componentes[key] = salarioBaseCotizacionMensual * value;
    }
    const cuotaMensual = salarioBaseCotizacionMensual * porcentajeTotal;

    return {
      salario_base_cotizacion: salarioBaseCotizacionMensual,
      ultimo_sbc_mensual: ultimoSbcMensual,
      year,
      uma_mensual: umaMensual,
      cuota_mensual: cuotaMensual,
      porcentaje_total: porcentajeTotal,
      componentes,
    };
  }

  /**
   * Modalidad 10 mantiene por ahora el modelo histórico existente.
   * El dataset la marca como legacy_pending_review para no presentarla como
   * parámetro fiscal verificado hasta completar su auditoría específica.
   */
  static calcularModalidad10(
    salarioBaseCotizacion: number,
    year: IMSSYear = 2026,
    fecha?: string | Date
  ): Modalidad10Result {
    this.loadTablesData();
    const uma = fecha === undefined ? this.getUMA(year) : this.getUMAForDate(fecha);
    const mod10 = this._tablesData!.modalidad_10;

    const umaMensual = uma.mensual;
    const salarioMinimo = umaMensual * mod10.limites_salario.minimo_uma;
    const salarioMaximo = umaMensual * mod10.limites_salario.maximo_uma;

    if (salarioBaseCotizacion < salarioMinimo) {
      salarioBaseCotizacion = salarioMinimo;
    } else if (salarioBaseCotizacion > salarioMaximo) {
      salarioBaseCotizacion = salarioMaximo;
    }

    const cuotaFijaUma = uma.diaria * mod10.cuota_mensual.cuota_fija_uma_factor;
    const porcentajeVariable = mod10.cuota_mensual.porcentaje_variable;
    const cuotaVariable = salarioBaseCotizacion * porcentajeVariable;
    const cuotaMensual = cuotaFijaUma + cuotaVariable;

    const componentes: Record<string, number> = {
      prestaciones_en_especie_fija: cuotaFijaUma,
    };
    for (const [key, value] of Object.entries(mod10.cuota_mensual.componentes)) {
      if (typeof value === 'number') {
        componentes[key] = salarioBaseCotizacion * value;
      }
    }

    return {
      salario_base_cotizacion: salarioBaseCotizacion,
      year,
      cuota_mensual: cuotaMensual,
      cuota_fija_uma: cuotaFijaUma,
      cuota_variable: cuotaVariable,
      porcentaje_variable: porcentajeVariable,
      componentes,
    };
  }

  static getTiposTrabajador(): Array<Record<string, unknown>> {
    this.loadCatalogsData();
    return [...this._catalogsData!.tipos_trabajador];
  }

  static getSegurosIMSS(): Array<Record<string, unknown>> {
    this.loadCatalogsData();
    return [...this._catalogsData!.seguros_imss];
  }

  static getClasesRiesgoTrabajo(): RiesgoTrabajoClase[] {
    this.loadTablesData();
    return [...this._tablesData!.riesgos_trabajo_clases];
  }

  private static toIsoDate(fecha: string | Date): string {
    if (typeof fecha === 'string') {
      const match = /^\d{4}-\d{2}-\d{2}/.exec(fecha);
      if (!match) {
        throw new Error(`Fecha inválida: ${fecha}`);
      }
      return match[0];
    }
    if (Number.isNaN(fecha.getTime())) {
      throw new Error('Fecha inválida');
    }
    return fecha.toISOString().slice(0, 10);
  }

  private static almostEqual(left: number, right: number): boolean {
    return Math.abs(left - right) < 0.005;
  }
}
