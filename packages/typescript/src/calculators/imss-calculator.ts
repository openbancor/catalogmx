/**
 * Calculadora de IMSS (Instituto Mexicano del Seguro Social) para México
 *
 * Calcula cuotas obrero-patronales y modalidades voluntarias (10, 40)
 * Fuentes oficiales:
 * - Ley del Seguro Social
 * - Sistema Único de Autodeterminación (SUA)
 */

import * as fs from 'fs';
import * as path from 'path';

export type IMSSYear = 2024 | 2025 | 2026;
export type ZonaSalario = 'general' | 'frontera';
export type ClaseRiesgo = 1 | 2 | 3 | 4 | 5;

export interface UMAInfo {
  diaria: number;
  mensual: number;
  anual: number;
}

export interface CuotasIMSSResult {
  salario_diario: number;
  dias: number;
  salario_base_cotizacion: number;
  year: number;
  cuotas_patron: Record<string, number>;
  cuotas_trabajador: Record<string, number>;
  total_patron: number;
  total_trabajador: number;
  total_imss: number;
}

export interface Modalidad40Result {
  salario_base_cotizacion: number;
  year: number;
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

interface IMSSTablesData {
  _meta: {
    description: string;
    source: string;
    calculation: string;
    updated: string;
  };
  uma: Record<string, UMAInfo>;
  salario_minimo: Record<string, Record<ZonaSalario, number>>;
  cuotas_imss: any;
  modalidad_40: any;
  modalidad_10: any;
  topes_cotizacion: any;
  riesgos_trabajo_clases: any[];
}

interface IMSSCatalogsData {
  _meta: {
    description: string;
    source: string;
    updated: string;
  };
  tipos_movimiento_afiliatorio: any[];
  tipos_trabajador: any[];
  tipos_incapacidad: any[];
  seguros_imss: any[];
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

    const dataPath = path.resolve(__dirname, '../../../shared-data/imss-tables.json');
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._tablesData = JSON.parse(rawData) as IMSSTablesData;
  }

  private static loadCatalogsData(): void {
    if (this._catalogsData !== null) return;

    const dataPath = path.resolve(__dirname, '../../../shared-data/imss-catalogs.json');
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._catalogsData = JSON.parse(rawData) as IMSSCatalogsData;
  }

  /**
   * Obtiene los valores de UMA para un año específico
   * @param year - Año (2024, 2025, o 2026)
   * @returns Valores de UMA (diaria, mensual, anual)
   */
  static getUMA(year: IMSSYear): UMAInfo {
    this.loadTablesData();
    const yearStr = year.toString();
    return this._tablesData!.uma[yearStr];
  }

  /**
   * Obtiene el salario mínimo para un año y zona específicos
   * @param year - Año (2024, 2025, o 2026)
   * @param zona - Zona ("general" o "frontera")
   * @returns Salario mínimo diario
   */
  static getSalarioMinimo(year: IMSSYear, zona: ZonaSalario = 'general'): number {
    this.loadTablesData();
    const yearStr = year.toString();
    return this._tablesData!.salario_minimo[yearStr][zona];
  }

  /**
   * Calcula las cuotas obrero-patronales del IMSS
   * @param salarioDiario - Salario diario del trabajador
   * @param dias - Número de días (default: 30)
   * @param year - Año (default: 2026)
   * @param claseRiesgo - Clase de riesgo de trabajo 1-5 (default: 1 - riesgo mínimo)
   * @returns Desglose completo de cuotas IMSS
   */
  static calcularCuotasObreroPatronales(
    salarioDiario: number,
    dias: number = 30,
    year: IMSSYear = 2026,
    claseRiesgo: ClaseRiesgo = 1
  ): CuotasIMSSResult {
    this.loadTablesData();
    const uma = this.getUMA(year);
    const cuotas = this._tablesData!.cuotas_imss;

    // Calcular salario base de cotización
    const salarioBase = salarioDiario * dias;

    // Límite de 3 UMAs diario para algunas cuotas
    const umaDiaria = uma.diaria;
    const tresUmaMensual = umaDiaria * 3 * 30;

    // Inicializar diccionarios de cuotas
    const cuotasPatron: Record<string, number> = {};
    const cuotasTrabajador: Record<string, number> = {};

    // 1. Enfermedad y Maternidad
    const em = cuotas.enfermedad_maternidad;

    // Cuota fija (sobre 3 UMAs)
    cuotasPatron.enfermedad_mat_cuota_fija =
      umaDiaria * 3 * dias * em.prestaciones_en_especie.patron;

    // Excedente de 3 UMAs
    if (salarioDiario > tresUmaMensual / 30) {
      const excedenteBase = salarioBase - tresUmaMensual;
      cuotasPatron.enfermedad_mat_excedente =
        excedenteBase * em.prestaciones_en_especie_excedente.patron;
      cuotasTrabajador.enfermedad_mat_excedente =
        excedenteBase * em.prestaciones_en_especie_excedente.trabajador;
    } else {
      cuotasPatron.enfermedad_mat_excedente = 0.0;
      cuotasTrabajador.enfermedad_mat_excedente = 0.0;
    }

    // Prestaciones en dinero
    cuotasPatron.enfermedad_mat_dinero = salarioBase * em.prestaciones_en_dinero.patron;
    cuotasTrabajador.enfermedad_mat_dinero = salarioBase * em.prestaciones_en_dinero.trabajador;

    // Gastos médicos pensionados
    cuotasPatron.gastos_medicos_pensionados = salarioBase * em.gastos_medicos_pensionados.patron;
    cuotasTrabajador.gastos_medicos_pensionados =
      salarioBase * em.gastos_medicos_pensionados.trabajador;

    // 2. Invalidez y Vida
    const iv = cuotas.invalidez_vida;
    cuotasPatron.invalidez_vida = salarioBase * iv.patron;
    cuotasTrabajador.invalidez_vida = salarioBase * iv.trabajador;

    // 3. Retiro, Cesantía y Vejez
    const rcv = cuotas.retiro_cesantia_vejez;
    cuotasPatron.retiro = salarioBase * rcv.retiro.patron;
    cuotasPatron.cesantia_vejez = salarioBase * rcv.cesantia_vejez.patron;
    cuotasTrabajador.cesantia_vejez = salarioBase * rcv.cesantia_vejez.trabajador;

    // 4. Guarderías y Prestaciones Sociales
    const gps = cuotas.guarderias_prestaciones_sociales;
    cuotasPatron.guarderias = salarioBase * gps.patron;

    // 5. Riesgos de Trabajo
    const rt = cuotas.riesgo_trabajo;
    const primaRiesgo = rt[`clase_${claseRiesgo}`];
    cuotasPatron.riesgo_trabajo = salarioBase * primaRiesgo;

    // Calcular totales
    const totalPatron = Object.values(cuotasPatron).reduce((sum, val) => sum + val, 0);
    const totalTrabajador = Object.values(cuotasTrabajador).reduce((sum, val) => sum + val, 0);

    return {
      salario_diario: salarioDiario,
      dias,
      salario_base_cotizacion: salarioBase,
      year,
      cuotas_patron: cuotasPatron,
      cuotas_trabajador: cuotasTrabajador,
      total_patron: totalPatron,
      total_trabajador: totalTrabajador,
      total_imss: totalPatron + totalTrabajador,
    };
  }

  /**
   * Calcula la Modalidad 40 del IMSS (Continuación voluntaria en el régimen obligatorio)
   *
   * La Modalidad 40 permite a trabajadores que causaron baja del régimen obligatorio
   * continuar cotizando voluntariamente para incrementar su pensión.
   *
   * @param salarioBaseCotizacion - Salario base mensual (entre 1 y 25 UMAs)
   * @param year - Año (default: 2026)
   * @returns Resultado del cálculo de Modalidad 40
   */
  static calcularModalidad40(
    salarioBaseCotizacion: number,
    year: IMSSYear = 2026
  ): Modalidad40Result {
    this.loadTablesData();
    const uma = this.getUMA(year);
    const mod40 = this._tablesData!.modalidad_40;

    // Validar límites de salario
    const umaMensual = uma.mensual;
    const salarioMinimo = umaMensual * mod40.limites_salario.minimo_uma;
    const salarioMaximo = umaMensual * mod40.limites_salario.maximo_uma;

    if (salarioBaseCotizacion < salarioMinimo) {
      salarioBaseCotizacion = salarioMinimo;
    } else if (salarioBaseCotizacion > salarioMaximo) {
      salarioBaseCotizacion = salarioMaximo;
    }

    // Calcular cuota mensual (10.47% total)
    const porcentajeTotal = mod40.cuota_mensual.porcentaje_total;
    const cuotaMensual = salarioBaseCotizacion * porcentajeTotal;

    // Obtener desglose de componentes
    const componentes: Record<string, number> = {};
    for (const [key, value] of Object.entries(mod40.cuota_mensual.componentes)) {
      componentes[key] = salarioBaseCotizacion * (value as number);
    }

    return {
      salario_base_cotizacion: salarioBaseCotizacion,
      year,
      cuota_mensual: cuotaMensual,
      porcentaje_total: porcentajeTotal,
      componentes,
    };
  }

  /**
   * Calcula la Modalidad 10 del IMSS (Incorporación voluntaria - trabajadores independientes)
   *
   * La Modalidad 10 permite a trabajadores independientes inscribirse en el IMSS
   * y acceder a todos los beneficios de seguridad social.
   *
   * @param salarioBaseCotizacion - Salario base mensual (entre 1 y 25 UMAs)
   * @param year - Año (default: 2026)
   * @returns Resultado del cálculo de Modalidad 10
   */
  static calcularModalidad10(
    salarioBaseCotizacion: number,
    year: IMSSYear = 2026
  ): Modalidad10Result {
    this.loadTablesData();
    const uma = this.getUMA(year);
    const mod10 = this._tablesData!.modalidad_10;

    // Validar límites de salario
    const umaMensual = uma.mensual;
    const salarioMinimo = umaMensual * mod10.limites_salario.minimo_uma;
    const salarioMaximo = umaMensual * mod10.limites_salario.maximo_uma;

    if (salarioBaseCotizacion < salarioMinimo) {
      salarioBaseCotizacion = salarioMinimo;
    } else if (salarioBaseCotizacion > salarioMaximo) {
      salarioBaseCotizacion = salarioMaximo;
    }

    // Cuota fija: 3.3 UMAs para prestaciones en especie
    const cuotaFijaUma = uma.diaria * mod10.cuota_mensual.cuota_fija_uma_factor;

    // Porcentaje variable: 10.47%
    const porcentajeVariable = mod10.cuota_mensual.porcentaje_variable;
    const cuotaVariable = salarioBaseCotizacion * porcentajeVariable;

    // Cuota mensual total
    const cuotaMensual = cuotaFijaUma + cuotaVariable;

    // Obtener desglose de componentes
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

  /**
   * Obtiene todos los catálogos de tipos de trabajador del IMSS
   * @returns Array de tipos de trabajador
   */
  static getTiposTrabajador(): any[] {
    this.loadCatalogsData();
    return [...this._catalogsData!.tipos_trabajador];
  }

  /**
   * Obtiene todos los catálogos de seguros del IMSS
   * @returns Array de seguros IMSS
   */
  static getSegurosIMSS(): any[] {
    this.loadCatalogsData();
    return [...this._catalogsData!.seguros_imss];
  }

  /**
   * Obtiene las clases de riesgo de trabajo disponibles
   * @returns Array de clases de riesgo con sus primas
   */
  static getClasesRiesgoTrabajo(): any[] {
    this.loadTablesData();
    return [...this._tablesData!.riesgos_trabajo_clases];
  }
}
