/**
 * SAT Anexo 24 - Código agrupador de cuentas
 */

import { loadCatalogData, loadCatalogObject } from '../../../utils/catalog-loader';
import type { CodigoAgrupadorSAT } from '../../../types';

type CodigoAgrupadorVersion = '2024-01-22' | '2026-01-13';

const DEFAULT_VERSION: CodigoAgrupadorVersion = '2026-01-13';

const VERSION_FILES: Record<CodigoAgrupadorVersion, string> = {
  '2024-01-22': 'sat/contabilidad_electronica/codigo_agrupador_2024.json',
  '2026-01-13': 'sat/contabilidad_electronica/codigo_agrupador_2026.json',
};

const VERSION_ALIASES: Record<string, CodigoAgrupadorVersion> = {
  '2024': '2024-01-22',
  '2026': '2026-01-13',
  latest: DEFAULT_VERSION,
};

export class CodigoAgrupadorSATCatalog {
  private static _cache = new Map<CodigoAgrupadorVersion, CodigoAgrupadorSAT[]>();
  private static _byCodigo = new Map<CodigoAgrupadorVersion, Map<string, CodigoAgrupadorSAT>>();

  private static resolveVersion(version?: string): CodigoAgrupadorVersion {
    if (!version) return DEFAULT_VERSION;
    const normalized = version.trim().toLowerCase();
    if (normalized in VERSION_ALIASES) return VERSION_ALIASES[normalized];
    if (version in VERSION_FILES) return version as CodigoAgrupadorVersion;
    throw new Error(`Versión no soportada: ${version}`);
  }

  private static load(version: CodigoAgrupadorVersion): CodigoAgrupadorSAT[] {
    if (this._cache.has(version)) {
      return this._cache.get(version)!;
    }
    const data = loadCatalogObject<CodigoAgrupadorSAT>(VERSION_FILES[version]);
    this._cache.set(version, data);
    this._byCodigo.set(version, new Map(data.map((item) => [item.codigo, item])));
    return data;
  }

  static getVersions(): CodigoAgrupadorVersion[] {
    return Object.keys(VERSION_FILES) as CodigoAgrupadorVersion[];
  }

  static getDefaultVersion(): CodigoAgrupadorVersion {
    return DEFAULT_VERSION;
  }

  static getAll(version?: string): CodigoAgrupadorSAT[] {
    const resolved = this.resolveVersion(version);
    return this.load(resolved).slice();
  }

  static getByCodigo(codigo: string, version?: string): CodigoAgrupadorSAT | undefined {
    const resolved = this.resolveVersion(version);
    this.load(resolved);
    return this._byCodigo.get(resolved)?.get(codigo);
  }

  static isValid(codigo: string, version?: string): boolean {
    return this.getByCodigo(codigo, version) !== undefined;
  }

  static search(query: string, version?: string): CodigoAgrupadorSAT[] {
    if (!query) return [];
    const resolved = this.resolveVersion(version);
    const data = this.load(resolved);
    const normalized = query.toLowerCase();
    return data.filter((item) => item.nombre.toLowerCase().includes(normalized));
  }

  static count(version?: string): number {
    return this.getAll(version).length;
  }

  static getDiff2024_2026(): Record<string, unknown> {
    return loadCatalogData<Record<string, unknown>>(
      'sat/contabilidad_electronica/codigo_agrupador_diff_2024_2026.json'
    );
  }
}
