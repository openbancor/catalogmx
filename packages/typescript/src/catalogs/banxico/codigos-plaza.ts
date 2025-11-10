/**
 * Banxico - CLABE Plaza Codes Catalog
 * Códigos de plaza para el sistema CLABE (Clave Bancaria Estandarizada)
 *
 * Plaza codes are 3-digit identifiers for banking locations in Mexico.
 * Source: Banco de México (BANXICO) / Sistema de Pagos Electrónicos Interbancarios (SPEI)
 */

import { loadCatalogData } from '../../utils/catalog-loader';

export interface CodigoPlaza {
  codigo: string;        // 3-digit code
  plaza: string;         // City/plaza name
  estado: string;        // State name
  cve_entidad: string;   // INEGI state code
}

interface PlazaCatalogData {
  metadata: {
    catalog: string;
    description: string;
    source: string;
    last_updated: string;
    total_codes: number;
    total_plazas: number;
    notes: string;
  };
  plazas: CodigoPlaza[];
}

export class CodigosPlazaCatalog {
  private static _data: CodigoPlaza[] | null = null;
  private static _byCodigo: Map<string, CodigoPlaza[]> | null = null;
  private static _byEstado: Map<string, CodigoPlaza[]> | null = null;
  private static _byPlazaNormalized: Map<string, CodigoPlaza[]> | null = null;

  /**
   * Normalize text by removing accents and converting to uppercase
   * This makes searches accent-insensitive
   */
  private static normalizeText(text: string): string {
    return text
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toUpperCase();
  }

  /**
   * Load plaza codes data (lazy loading with caching)
   */
  private static getData(): CodigoPlaza[] {
    if (this._data === null) {
      const catalogData = loadCatalogData<PlazaCatalogData>('banxico/codigos_plaza.json');
      this._data = catalogData.plazas;

      // Build indices
      this._byCodigo = new Map();
      this._byEstado = new Map();
      this._byPlazaNormalized = new Map();

      for (const plaza of this._data) {
        // Index by codigo
        if (!this._byCodigo.has(plaza.codigo)) {
          this._byCodigo.set(plaza.codigo, []);
        }
        this._byCodigo.get(plaza.codigo)!.push(plaza);

        // Index by estado
        if (!this._byEstado.has(plaza.estado)) {
          this._byEstado.set(plaza.estado, []);
        }
        this._byEstado.get(plaza.estado)!.push(plaza);

        // Index by normalized plaza name (accent-insensitive)
        const normalized = this.normalizeText(plaza.plaza);
        if (!this._byPlazaNormalized.has(normalized)) {
          this._byPlazaNormalized.set(normalized, []);
        }
        this._byPlazaNormalized.get(normalized)!.push(plaza);
      }
    }
    return this._data;
  }

  /**
   * Get all plaza codes
   */
  static getAll(): CodigoPlaza[] {
    return this.getData();
  }

  /**
   * Find plazas by code
   * @param codigo - 3-digit plaza code
   * @returns Array of plazas with that code (can be multiple)
   *
   * @example
   * const plazas = CodigosPlazaCatalog.buscarPorCodigo('320');
   * plazas.forEach(p => console.log(`${p.plaza}, ${p.estado}`));
   * // Output: Guadalajara, Jalisco
   * //         Tonala, Jalisco
   * //         ...
   */
  static buscarPorCodigo(codigo: string): CodigoPlaza[] {
    this.getData(); // Ensure data is loaded
    const codigoPadded = codigo.padStart(3, '0');
    return this._byCodigo!.get(codigoPadded) || [];
  }

  /**
   * Find plazas by name (accent-insensitive)
   * @param nombrePlaza - Plaza/city name
   * @returns Array of plazas matching the name
   *
   * @example
   * // Search with or without accents - both work!
   * const tuxpam1 = CodigosPlazaCatalog.buscarPorPlaza('Túxpam');
   * const tuxpam2 = CodigosPlazaCatalog.buscarPorPlaza('Tuxpam'); // Same result
   *
   * // Tonalá appears in two different states
   * const tonala = CodigosPlazaCatalog.buscarPorPlaza('Tonala');
   * tonala.forEach(p => console.log(`Code ${p.codigo}: ${p.plaza}, ${p.estado}`));
   * // Output: Code 135: Tonala, Chiapas
   * //         Code 320: Tonala, Jalisco
   */
  static buscarPorPlaza(nombrePlaza: string): CodigoPlaza[] {
    this.getData(); // Ensure data is loaded
    const normalized = this.normalizeText(nombrePlaza);
    return this._byPlazaNormalized!.get(normalized) || [];
  }

  /**
   * Get all plazas in a state
   * @param estado - State name
   */
  static getPorEstado(estado: string): CodigoPlaza[] {
    this.getData(); // Ensure data is loaded
    return this._byEstado!.get(estado) || [];
  }

  /**
   * Get all plazas by INEGI state code
   * @param cveEntidad - 2-digit INEGI state code
   *
   * @example
   * const jalisco = CodigosPlazaCatalog.getPorCveEntidad('14');
   * console.log(`Jalisco has ${jalisco.length} plazas`);
   */
  static getPorCveEntidad(cveEntidad: string): CodigoPlaza[] {
    return this.getData().filter(p => p.cve_entidad === cveEntidad);
  }

  /**
   * Validate a CLABE plaza code
   * @param codigoPlaza - 3-digit plaza code
   */
  static validarCodigoCLABE(codigoPlaza: string): {
    valido: boolean;
    codigo: string;
    plazas: CodigoPlaza[];
    numPlazas: number;
  } {
    const codigoPadded = codigoPlaza.padStart(3, '0');
    const plazas = this.buscarPorCodigo(codigoPadded);

    return {
      valido: plazas.length > 0,
      codigo: codigoPadded,
      plazas,
      numPlazas: plazas.length
    };
  }

  /**
   * Get plazas with duplicate names in different states
   */
  static getPlazasDuplicadas(): Map<string, CodigoPlaza[]> {
    this.getData(); // Ensure data is loaded
    const duplicadas = new Map<string, CodigoPlaza[]>();

    for (const [nombre, plazas] of this._byPlazaNormalized!) {
      if (plazas.length > 1) {
        // Get the original names (with accents)
        const originalName = plazas[0].plaza;
        duplicadas.set(originalName, plazas);
      }
    }

    return duplicadas;
  }

  /**
   * Search plazas by partial name (accent-insensitive)
   * @param query - Search query
   *
   * @example
   * // Search works with or without accents
   * const results1 = CodigosPlazaCatalog.search('Tuxpam'); // without accent
   * const results2 = CodigosPlazaCatalog.search('Túxpam'); // with accent
   * // Both return the same results!
   *
   * const sanPlazas = CodigosPlazaCatalog.search('San');
   * console.log(`Found ${sanPlazas.length} plazas with "San" in name`);
   */
  static search(query: string): CodigoPlaza[] {
    const queryNormalized = this.normalizeText(query);
    return this.getData().filter(p =>
      this.normalizeText(p.plaza).includes(queryNormalized)
    );
  }

  /**
   * Get catalog statistics
   */
  static getEstadisticas(): {
    totalPlazas: number;
    codigosUnicos: number;
    estadosCubiertos: number;
    plazasDuplicadas: number;
  } {
    this.getData(); // Ensure data is loaded

    const estados = new Set(this._data!.map(p => p.estado));

    return {
      totalPlazas: this._data!.length,
      codigosUnicos: this._byCodigo!.size,
      estadosCubiertos: estados.size,
      plazasDuplicadas: this.getPlazasDuplicadas().size
    };
  }
}
