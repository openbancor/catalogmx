/**
 * Catálogo de tipos de instituciones financieras en México (Banxico)
 */

import * as path from 'path';
import * as fs from 'fs';
import { TipoInstitucionFinanciera } from '../../types';

interface InstitucionesFinancierasData {
  metadata: {
    catalog: string;
    description: string;
    source: string;
    last_updated: string;
    notes: string;
  };
  tipos_institucion: TipoInstitucionFinanciera[];
  reguladores: Record<string, string>;
  estadisticas: {
    total_tipos: number;
    entidades_reguladas_cnbv: number;
    entidades_reguladas_cnsf: number;
    entidades_reguladas_consar: number;
    fecha_actualizacion: string;
  };
}

export class InstitucionesFinancieras {
  private static _data: TipoInstitucionFinanciera[] | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(
      __dirname,
      '../../../../shared-data/banxico/instituciones_financieras.json'
    );
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    const jsonData: InstitucionesFinancierasData = JSON.parse(rawData);
    this._data = jsonData.tipos_institucion;
  }

  /**
   * Obtener todos los tipos de instituciones financieras
   */
  static getAll(): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!;
  }

  /**
   * Buscar tipo de institución por código
   */
  static getPorCodigo(codigo: string): TipoInstitucionFinanciera | undefined {
    this.loadData();
    return this._data!.find((inst) => inst.codigo === codigo);
  }

  /**
   * Buscar por tipo de institución
   */
  static buscarPorTipo(tipo: string): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!.filter((inst) =>
      inst.tipo.toLowerCase().includes(tipo.toLowerCase())
    );
  }

  /**
   * Obtener instituciones por regulador
   */
  static getPorRegulador(regulador: string): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!.filter((inst) =>
      inst.regulador.toLowerCase().includes(regulador.toLowerCase())
    );
  }

  /**
   * Obtener bancos (múltiples y de desarrollo)
   */
  static getBancos(): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!.filter((inst) =>
      inst.tipo.toLowerCase().includes('banco')
    );
  }

  /**
   * Obtener SOFOMes (ENR y ER)
   */
  static getSOFOMes(): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!.filter((inst) => inst.tipo.includes('SOFOM'));
  }

  /**
   * Obtener instituciones de ahorro y crédito popular
   */
  static getSectorPopular(): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!.filter(
      (inst) =>
        inst.tipo.includes('Cooperativa') ||
        inst.tipo.includes('Financiera Popular') ||
        inst.tipo.includes('Ahorro y Crédito')
    );
  }

  /**
   * Obtener instituciones de seguros y fianzas
   */
  static getSegurosYFianzas(): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!.filter(
      (inst) => inst.tipo.includes('Seguros') || inst.tipo.includes('Fianzas')
    );
  }

  /**
   * Obtener instituciones del mercado de valores
   */
  static getMercadoValores(): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!.filter(
      (inst) =>
        inst.tipo.includes('Bolsa') ||
        inst.tipo.includes('Casa de Bolsa') ||
        inst.tipo.includes('Valores') ||
        inst.tipo.includes('Inversión')
    );
  }

  /**
   * Obtener instituciones de tecnología financiera (Fintech)
   */
  static getFintech(): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!.filter((inst) =>
      inst.tipo.includes('Tecnología Financiera')
    );
  }

  /**
   * Obtener AFORES y SIEFORES
   */
  static getRetiro(): TipoInstitucionFinanciera[] {
    this.loadData();
    return this._data!.filter(
      (inst) => inst.tipo.includes('AFORE') || inst.tipo.includes('SIEFORE')
    );
  }

  /**
   * Validar código de institución
   */
  static validarCodigo(codigo: string): boolean {
    this.loadData();
    return this._data!.some((inst) => inst.codigo === codigo);
  }

  /**
   * Obtener descripción de regulador
   */
  static getDescripcionRegulador(siglas: string): string | undefined {
    this.loadData();
    const reguladores: Record<string, string> = {
      CNBV: 'Comisión Nacional Bancaria y de Valores',
      CNSF: 'Comisión Nacional de Seguros y Fianzas',
      CONSAR: 'Comisión Nacional del Sistema de Ahorro para el Retiro',
      CONDUSEF:
        'Comisión Nacional para la Protección y Defensa de los Usuarios de Servicios Financieros',
      SHCP: 'Secretaría de Hacienda y Crédito Público',
    };
    return reguladores[siglas.toUpperCase()];
  }
}
