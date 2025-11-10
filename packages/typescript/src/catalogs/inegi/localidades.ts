/**
 * Catálogo de Localidades INEGI (filtrado por población >= 1,000 habitantes)
 *
 * Incluye:
 * - 10,635 localidades con población >= 1,000 habitantes
 * - Coordenadas GPS (latitud, longitud)
 * - Población y viviendas habitadas
 * - Clasificación urbano/rural
 */

import * as fs from 'fs';
import * as path from 'path';
import { Localidad } from '../../types';

export class LocalidadesCatalog {
  private static _data: Localidad[] | null = null;
  private static _byCvegeo: Map<string, Localidad> | null = null;
  private static _byMunicipio: Map<string, Localidad[]> | null = null;
  private static _byEntidad: Map<string, Localidad[]> | null = null;

  private static loadData(): void {
    if (this._data !== null) return;

    const dataPath = path.resolve(__dirname, '../../../../shared-data/inegi/localidades.json');
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    this._data = JSON.parse(rawData) as Localidad[];

    // Crear índices
    this._byCvegeo = new Map();
    this._byMunicipio = new Map();
    this._byEntidad = new Map();

    for (const item of this._data) {
      // Índice por CVEGEO
      this._byCvegeo.set(item.cvegeo, item);

      // Índice por municipio
      const munKey = item.cve_municipio;
      if (!this._byMunicipio.has(munKey)) {
        this._byMunicipio.set(munKey, []);
      }
      this._byMunicipio.get(munKey)!.push(item);

      // Índice por entidad
      const entKey = item.cve_entidad;
      if (!this._byEntidad.has(entKey)) {
        this._byEntidad.set(entKey, []);
      }
      this._byEntidad.get(entKey)!.push(item);
    }
  }

  /**
   * Obtiene una localidad por su clave geoestadística (CVEGEO)
   * @param cvegeo - Clave geoestadística (ej: "010010001")
   * @returns Localidad o undefined si no existe
   */
  static getLocalidad(cvegeo: string): Localidad | undefined {
    this.loadData();
    return this._byCvegeo!.get(cvegeo);
  }

  /**
   * Verifica si una clave geoestadística existe
   * @param cvegeo - Clave geoestadística
   * @returns true si existe, false en caso contrario
   */
  static isValid(cvegeo: string): boolean {
    return this.getLocalidad(cvegeo) !== undefined;
  }

  /**
   * Obtiene todas las localidades de un municipio
   * @param cveMunicipio - Código del municipio (ej: "001")
   * @returns Lista de localidades del municipio
   */
  static getByMunicipio(cveMunicipio: string): Localidad[] {
    this.loadData();
    return [...(this._byMunicipio!.get(cveMunicipio) || [])];
  }

  /**
   * Obtiene todas las localidades de un estado
   * @param cveEntidad - Código del estado (ej: "01")
   * @returns Lista de localidades del estado
   */
  static getByEntidad(cveEntidad: string): Localidad[] {
    this.loadData();
    const cveEnt = cveEntidad.padStart(2, '0');
    return [...(this._byEntidad!.get(cveEnt) || [])];
  }

  /**
   * Obtiene todas las localidades
   * WARNING: Retorna 10,635 localidades. Considere usar paginación.
   * @returns Lista completa de localidades
   */
  static getAll(): Localidad[] {
    this.loadData();
    return [...this._data!];
  }

  /**
   * Obtiene solo localidades urbanas (ámbito = 'U')
   * @returns Lista de localidades urbanas
   */
  static getUrbanas(): Localidad[] {
    this.loadData();
    return this._data!.filter((loc) => loc.ambito === 'U');
  }

  /**
   * Obtiene solo localidades rurales (ámbito = 'R')
   * @returns Lista de localidades rurales
   */
  static getRurales(): Localidad[] {
    this.loadData();
    return this._data!.filter((loc) => loc.ambito === 'R');
  }

  /**
   * Busca localidades por nombre (búsqueda parcial, case-insensitive)
   * @param nombre - Nombre o parte del nombre a buscar
   * @returns Lista de localidades que coinciden
   */
  static searchByName(nombre: string): Localidad[] {
    this.loadData();
    const nombreLower = nombre.toLowerCase();
    return this._data!.filter((loc) => loc.nom_localidad.toLowerCase().includes(nombreLower));
  }

  /**
   * Calcula la distancia haversine entre dos puntos GPS en kilómetros
   * @param lat1 - Latitud del punto 1
   * @param lon1 - Longitud del punto 1
   * @param lat2 - Latitud del punto 2
   * @param lon2 - Longitud del punto 2
   * @returns Distancia en kilómetros
   */
  private static haversineDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371; // Radio de la Tierra en km
    const toRad = (deg: number): number => (deg * Math.PI) / 180;

    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  /**
   * Busca localidades cercanas a unas coordenadas GPS
   * @param lat - Latitud
   * @param lon - Longitud
   * @param radioKm - Radio de búsqueda en kilómetros (default: 10)
   * @returns Lista de localidades dentro del radio, ordenadas por distancia
   */
  static getByCoordinates(lat: number, lon: number, radioKm: number = 10): Localidad[] {
    this.loadData();

    const resultados: Localidad[] = [];
    for (const loc of this._data!) {
      if (loc.latitud === null || loc.longitud === null) {
        continue;
      }

      const distancia = this.haversineDistance(lat, lon, loc.latitud, loc.longitud);
      if (distancia <= radioKm) {
        const locConDistancia = { ...loc };
        locConDistancia.distancia_km = Math.round(distancia * 100) / 100;
        resultados.push(locConDistancia);
      }
    }

    // Ordenar por distancia
    resultados.sort((a, b) => (a.distancia_km || 0) - (b.distancia_km || 0));
    return resultados;
  }

  /**
   * Obtiene localidades en un rango de población
   * @param minPob - Población mínima
   * @param maxPob - Población máxima (undefined para sin límite)
   * @returns Lista de localidades en el rango
   */
  static getByPopulationRange(minPob: number, maxPob?: number): Localidad[] {
    this.loadData();

    if (maxPob === undefined) {
      return this._data!.filter((loc) => loc.poblacion_total >= minPob);
    } else {
      return this._data!.filter(
        (loc) => minPob <= loc.poblacion_total && loc.poblacion_total <= maxPob
      );
    }
  }

  /**
   * Obtiene el total de localidades en el catálogo
   * @returns Número total de localidades (10,635)
   */
  static getTotalCount(): number {
    this.loadData();
    return this._data!.length;
  }

  /**
   * Obtiene estadísticas del catálogo
   * @returns Estadísticas de localidades
   */
  static getStatistics(): {
    totalLocalidades: number;
    urbanas: number;
    rurales: number;
    estados: number;
    municipios: number;
  } {
    this.loadData();

    return {
      totalLocalidades: this._data!.length,
      urbanas: this._data!.filter((loc) => loc.ambito === 'U').length,
      rurales: this._data!.filter((loc) => loc.ambito === 'R').length,
      estados: this._byEntidad!.size,
      municipios: this._byMunicipio!.size,
    };
  }

  /**
   * Busca las N localidades más grandes por población
   * @param n - Número de localidades a retornar
   * @returns Lista de las N localidades más pobladas
   */
  static getTopByPopulation(n: number = 10): Localidad[] {
    this.loadData();
    return [...this._data!].sort((a, b) => b.poblacion_total - a.poblacion_total).slice(0, n);
  }
}
