/**
 * Catálogo de códigos LADA (plan de numeración telefónica) en México (IFT)
 */

import * as path from 'path';
import * as fs from 'fs';
import { CodigoLADA } from '../../types';

interface CodigosLADAData {
  metadata: {
    catalog: string;
    description: string;
    source: string;
    last_updated: string;
    notes: string;
  };
  codigos: CodigoLADA[];
  tipos_lada: Record<string, string>;
  regiones: string[];
  marcacion_actual: {
    descripcion: string;
    formato: string;
    ejemplo: string;
    prefijos_obsoletos: string[];
    vigencia: string;
  };
  estadisticas: {
    total_codigos: number;
    codigos_metropolitanos: number;
    codigos_fronterizos: number;
    codigos_turisticos: number;
    estados_cubiertos: number;
  };
}

export class CodigosLADA {
  private static _data: CodigoLADA[] | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(__dirname, '../../../../shared-data/ift/codigos_lada.json');
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    const jsonData: CodigosLADAData = JSON.parse(rawData);
    this._data = jsonData.codigos;
  }

  /**
   * Obtener todos los códigos LADA
   */
  static getAll(): CodigoLADA[] {
    this.loadData();
    return this._data!;
  }

  /**
   * Buscar código LADA específico
   */
  static buscarPorLADA(lada: string): CodigoLADA | undefined {
    this.loadData();
    return this._data!.find((c) => c.lada === lada);
  }

  /**
   * Buscar códigos por ciudad
   */
  static buscarPorCiudad(ciudad: string): CodigoLADA[] {
    this.loadData();
    return this._data!.filter((c) => c.ciudad.toLowerCase().includes(ciudad.toLowerCase()));
  }

  /**
   * Obtener códigos por estado
   */
  static getPorEstado(estado: string): CodigoLADA[] {
    this.loadData();
    return this._data!.filter((c) => c.estado.toLowerCase() === estado.toLowerCase());
  }

  /**
   * Obtener códigos por tipo
   */
  static getPorTipo(tipo: 'metropolitana' | 'fronteriza' | 'turistica' | 'normal'): CodigoLADA[] {
    this.loadData();
    return this._data!.filter((c) => c.tipo === tipo);
  }

  /**
   * Obtener códigos por región
   */
  static getPorRegion(region: string): CodigoLADA[] {
    this.loadData();
    return this._data!.filter((c) => c.region.toLowerCase() === region.toLowerCase());
  }

  /**
   * Obtener ciudades metropolitanas
   */
  static getMetropolitanas(): CodigoLADA[] {
    return this.getPorTipo('metropolitana');
  }

  /**
   * Obtener ciudades fronterizas
   */
  static getFronterizas(): CodigoLADA[] {
    return this.getPorTipo('fronteriza');
  }

  /**
   * Obtener destinos turísticos
   */
  static getTuristicas(): CodigoLADA[] {
    return this.getPorTipo('turistica');
  }

  /**
   * Validar formato de número telefónico (10 dígitos)
   */
  static validarNumero(numero: string): {
    valid: boolean;
    lada?: string;
    numero_local?: string;
    ciudad?: string;
    estado?: string;
    error?: string;
  } {
    // Eliminar espacios y guiones
    const numeroLimpio = numero.replace(/[\s-]/g, '');

    // Validar que sean 10 dígitos
    if (!/^\d{10}$/.test(numeroLimpio)) {
      return {
        valid: false,
        error: 'El número debe tener exactamente 10 dígitos',
      };
    }

    // Intentar extraer LADA (primeros 2 o 3 dígitos)
    this.loadData();

    // Intentar con 3 dígitos
    let lada = numeroLimpio.substring(0, 3);
    let codigo = this._data!.find((c) => c.lada === lada);

    // Si no se encuentra, intentar con 2 dígitos
    if (!codigo) {
      lada = numeroLimpio.substring(0, 2);
      codigo = this._data!.find((c) => c.lada === lada);
    }

    if (codigo) {
      const numeroLocal = numeroLimpio.substring(lada.length);
      return {
        valid: true,
        lada: codigo.lada,
        numero_local: numeroLocal,
        ciudad: codigo.ciudad,
        estado: codigo.estado,
      };
    }

    return {
      valid: false,
      lada: lada,
      error: `Código LADA ${lada} no encontrado en el catálogo`,
    };
  }

  /**
   * Formatear número telefónico
   */
  static formatearNumero(numero: string): string {
    const validacion = this.validarNumero(numero);
    if (!validacion.valid || !validacion.lada || !validacion.numero_local) {
      return numero;
    }

    // Formato: LADA XXXX XXXX
    const local = validacion.numero_local;
    if (local.length === 7) {
      return `${validacion.lada} ${local.substring(0, 3)} ${local.substring(3)}`;
    } else if (local.length === 8) {
      return `${validacion.lada} ${local.substring(0, 4)} ${local.substring(4)}`;
    }
    return `${validacion.lada} ${local}`;
  }

  /**
   * Obtener información de un número telefónico
   */
  static getInfoNumero(numero: string): {
    lada: string;
    ciudad: string;
    estado: string;
    tipo: string;
    region: string;
  } | null {
    const validacion = this.validarNumero(numero);
    if (!validacion.valid || !validacion.lada) {
      return null;
    }

    const codigo = this.buscarPorLADA(validacion.lada);
    if (!codigo) {
      return null;
    }

    return {
      lada: codigo.lada,
      ciudad: codigo.ciudad,
      estado: codigo.estado,
      tipo: codigo.tipo,
      region: codigo.region,
    };
  }
}
