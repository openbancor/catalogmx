import { loadCatalogArray } from '../../utils/catalog-loader';
import { PlacaFormato } from '../../types';

/**
 * Mexican License Plates Formats Catalog
 * Provides validation patterns and formats for Mexican vehicle license plates
 */
export class PlacasFormatosCatalog {
  private static _data: PlacaFormato[] | null = null;

  private static loadData(): void {
    if (this._data !== null) return;
    this._data = loadCatalogArray<PlacaFormato>('mexico/placas_formatos.json');
  }

  static getData(): PlacaFormato[] {
    this.loadData();
    return this._data!;
  }

  /**
   * Validate a license plate against all known formats
   */
  static validatePlaca(placa: string): boolean {
    const normalizedPlaca = placa.toUpperCase().trim();
    return this.getData().some(formato => {
      const regex = new RegExp(formato.pattern);
      return regex.test(normalizedPlaca) && formato.activo;
    });
  }

  /**
   * Get all formats for a specific state
   */
  static getFormatosPorEstado(estado: string): PlacaFormato[] {
    return this.getData().filter(f =>
      f.estado.toLowerCase().includes(estado.toLowerCase()) ||
      estado.toLowerCase() === 'nacional'
    );
  }

  /**
   * Get all formats by type
   */
  static getFormatosPorTipo(tipo: PlacaFormato['tipo']): PlacaFormato[] {
    return this.getData().filter(f => f.tipo === tipo && f.activo);
  }

  /**
   * Detect the format of a given license plate
   */
  static detectFormato(placa: string): PlacaFormato | undefined {
    const normalizedPlaca = placa.toUpperCase().trim();
    return this.getData().find(formato => {
      const regex = new RegExp(formato.pattern);
      return regex.test(normalizedPlaca);
    });
  }

  /**
   * Get all active formats
   */
  static getFormatosActivos(): PlacaFormato[] {
    return this.getData().filter(f => f.activo);
  }

  /**
   * Check if a plate is diplomatic
   */
  static isDiplomatica(placa: string): boolean {
    const formato = this.detectFormato(placa);
    return formato?.tipo === 'diplomatico';
  }

  /**
   * Check if a plate is federal (government, military, or federal service)
   */
  static isFederal(placa: string): boolean {
    const formato = this.detectFormato(placa);
    return formato?.tipo === 'gobierno_federal' ||
           formato?.tipo === 'servicio_publico_federal' ||
           formato?.tipo === 'carga_federal' ||
           formato?.tipo === 'policia_federal' ||
           formato?.tipo === 'remolque_federal';
  }
}
