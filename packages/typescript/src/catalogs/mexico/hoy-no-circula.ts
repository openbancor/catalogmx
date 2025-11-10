import path from 'path';
import fs from 'fs';
import { HoyNoCirculaPrograma } from '../../types';

/**
 * Hoy No Circula CDMX Catalog
 * Traffic restriction program for Mexico City and Metropolitan Area
 * Includes daily restrictions, hologram exemptions, and contingency rules
 */
export class HoyNoCirculaCDMX {
  private static _data: HoyNoCirculaPrograma | null = null;

  private static loadData(): void {
    if (this._data !== null) return;
    // From dist/catalogs/mexico, go up 4 levels to packages dir and then to shared-data
    const dataPath = path.resolve(
      __dirname,
      '../../../../shared-data/mexico/hoy_no_circula_cdmx.json'
    );
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._data = JSON.parse(rawData) as HoyNoCirculaPrograma;
  }

  static getData(): HoyNoCirculaPrograma {
    this.loadData();
    return this._data!;
  }

  /**
   * Check if a vehicle can circulate on a specific day
   */
  static puedeCircular(
    terminacionPlaca: string,
    dia: string,
    holograma: '00' | '0' | '1' | '2' | 'sin_verificacion' = '1'
  ): boolean {
    this.loadData();

    // Vehículos sin verificación no pueden circular
    if (holograma === 'sin_verificacion') return false;

    // Check hologram exemptions
    const exencion = this._data!.exenciones_por_holograma.find((h) => h.holograma === holograma);
    if (exencion?.exento) return true;

    // Check daily restrictions
    const restriccion = this._data!.restricciones_por_dia.find(
      (r) => r.dia.toLowerCase() === dia.toLowerCase()
    );
    if (!restriccion) return true;

    const ultimoDigito = terminacionPlaca.slice(-1);
    return !restriccion.terminacion_placa.includes(ultimoDigito);
  }

  /**
   * Get restriction for a specific day
   */
  static getRestriccionPorDia(dia: string) {
    this.loadData();
    return this._data!.restricciones_por_dia.find((r) => r.dia.toLowerCase() === dia.toLowerCase());
  }

  /**
   * Get exemption info for a specific hologram
   */
  static getExencionPorHolograma(holograma: '00' | '0' | '1' | '2') {
    this.loadData();
    return this._data!.exenciones_por_holograma.find((h) => h.holograma === holograma);
  }

  /**
   * Check if a plate number can circulate on Saturdays (hologram 2)
   */
  static puedeCircularSabado(terminacionPlaca: string, semana: number): boolean {
    this.loadData();
    const ultimoDigito = terminacionPlaca.slice(-1);

    const restriccion = this._data!.calendario_sabados_holograma_2.find((s) => s.semana === semana);
    if (!restriccion) return true;

    return !restriccion.terminaciones.includes(ultimoDigito);
  }

  /**
   * Get Saturday restriction schedule for hologram 2
   */
  static getCalendarioSabados() {
    this.loadData();
    return this._data!.calendario_sabados_holograma_2;
  }

  /**
   * Check which day of the week a vehicle cannot circulate
   */
  static getDiaRestriccion(terminacionPlaca: string): string | undefined {
    this.loadData();
    const ultimoDigito = terminacionPlaca.slice(-1);

    const restriccion = this._data!.restricciones_por_dia.find((r) =>
      r.terminacion_placa.includes(ultimoDigito)
    );

    return restriccion?.dia;
  }

  /**
   * Get sticker color (engomado) for a plate number
   */
  static getEngomado(terminacionPlaca: string): string | undefined {
    this.loadData();
    const ultimoDigito = terminacionPlaca.slice(-1);

    const restriccion = this._data!.restricciones_por_dia.find((r) =>
      r.terminacion_placa.includes(ultimoDigito)
    );

    return restriccion?.engomado[0];
  }

  /**
   * Get contingency info
   */
  static getContingencias() {
    this.loadData();
    return this._data!.contingencias_ambientales;
  }

  /**
   * Get exempt vehicle types
   */
  static getVehiculosExentos() {
    this.loadData();
    return this._data!.tipos_vehiculos_exentos;
  }

  /**
   * Get application zones
   */
  static getZonasAplicacion() {
    this.loadData();
    return this._data!.zonas_aplicacion;
  }

  /**
   * Get Estado de México municipalities where program applies
   */
  static getMunicipiosEdomex() {
    this.loadData();
    return this._data!.municipios_edomex;
  }

  /**
   * Get verification schedule
   */
  static getCalendarioVerificacion() {
    this.loadData();
    return this._data!.verificacion_vehicular;
  }

  /**
   * Get verification period for a plate number
   */
  static getPeriodoVerificacion(terminacionPlaca: string): string | undefined {
    this.loadData();
    const ultimoDigito = terminacionPlaca.slice(-1);

    const periodo = this._data!.verificacion_vehicular.periodos.find((p) =>
      p.terminacion_placa.includes(ultimoDigito)
    );

    return periodo?.periodo;
  }
}
