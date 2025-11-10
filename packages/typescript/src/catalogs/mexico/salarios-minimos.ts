import { loadCatalogArray } from '../../utils/catalog-loader';
import { SalarioMinimo } from '../../types';

/**
 * Mexican Minimum Wages Catalog
 * Historical data of minimum wages in Mexico from 2010 to present
 */
export class SalariosMinimos {
  private static _data: SalarioMinimo[] | null = null;

  private static loadData(): void {
    if (this._data !== null) return;
    this._data = loadCatalogArray<SalarioMinimo>('mexico/salarios_minimos.json');
  }

  static getData(): SalarioMinimo[] {
    this.loadData();
    return this._data!;
  }

  /**
   * Get minimum wage for a specific year
   */
  static getPorAño(año: number): SalarioMinimo | undefined {
    return this.getData().find((s) => s.año === año);
  }

  /**
   * Get current minimum wage (most recent year)
   */
  static getActual(): SalarioMinimo {
    const sorted = [...this.getData()].sort((a, b) => b.año - a.año);
    return sorted[0];
  }

  /**
   * Get minimum wage for a specific date
   */
  static getPorFecha(fecha: string | Date): SalarioMinimo | undefined {
    const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
    const sorted = [...this.getData()].sort(
      (a, b) => new Date(b.vigencia_inicio).getTime() - new Date(a.vigencia_inicio).getTime()
    );

    return sorted.find((s) => new Date(s.vigencia_inicio) <= date);
  }

  /**
   * Get minimum wage value for a zone and year
   */
  static getValor(
    año: number,
    zona: 'frontera' | 'pais' | 'general' | 'a' | 'b' = 'pais'
  ): number | undefined {
    const salario = this.getPorAño(año);
    if (!salario) return undefined;

    switch (zona) {
      case 'frontera':
        return salario.zona_frontera_norte;
      case 'pais':
        return salario.resto_pais ?? salario.zona_general;
      case 'general':
        return salario.zona_general;
      case 'a':
        return salario.zona_a;
      case 'b':
        return salario.zona_b;
      default:
        return salario.resto_pais ?? salario.zona_general;
    }
  }

  static getUmaEquivalente(
    año: number,
    tipo: 'diario' | 'mensual' | 'anual' = 'diario'
  ): number | undefined {
    const salario = this.getPorAño(año);
    if (!salario) return undefined;

    switch (tipo) {
      case 'diario':
        return salario.uma_equivalente_diario;
      case 'mensual':
        return salario.uma_equivalente_mensual;
      case 'anual':
        return salario.uma_equivalente_anual;
      default:
        return salario.uma_equivalente_diario;
    }
  }

  static getFuenteUmaEquivalente(año: number): SalarioMinimo['fuente_uma_equivalente'] {
    const salario = this.getPorAño(año);
    return salario?.fuente_uma_equivalente;
  }

  /**
   * Calculate monthly minimum wage (assuming 30.4 days)
   */
  static calcularMensual(año: number, zona: 'frontera' | 'pais' = 'pais'): number | undefined {
    const diario = this.getValor(año, zona);
    return diario ? diario * 30.4 : undefined;
  }

  /**
   * Calculate annual minimum wage (assuming 365 days)
   */
  static calcularAnual(año: number, zona: 'frontera' | 'pais' = 'pais'): number | undefined {
    const diario = this.getValor(año, zona);
    return diario ? diario * 365 : undefined;
  }

  /**
   * Get historical evolution of minimum wages
   */
  static getHistorico(añoInicio: number, añoFin: number): SalarioMinimo[] {
    return this.getData()
      .filter((s) => s.año >= añoInicio && s.año <= añoFin)
      .sort((a, b) => a.año - b.año);
  }

  /**
   * Calculate percentage increase between two years
   */
  static calcularIncremento(
    añoInicial: number,
    añoFinal: number,
    zona: 'frontera' | 'pais' = 'pais'
  ): number | undefined {
    const inicial = this.getValor(añoInicial, zona);
    const final = this.getValor(añoFinal, zona);

    if (!inicial || !final) return undefined;
    return ((final - inicial) / inicial) * 100;
  }
}
