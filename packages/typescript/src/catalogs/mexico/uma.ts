import { loadCatalogArray } from '../../utils/catalog-loader';
import { UMA } from '../../types';
import { SalariosMinimos } from './salarios-minimos';

/**
 * UMA (Unidad de Medida y Actualización) Catalog
 * Reference unit for fines, taxes, and economic calculations in Mexico
 * Replaced minimum wage as reference unit in 2017
 */
export class UMACatalog {
  private static _data: UMA[] | null = null;

  private static loadData(): void {
    if (this._data !== null) return;
    this._data = loadCatalogArray<UMA>('mexico/uma.json');
  }

  static getData(): UMA[] {
    this.loadData();
    return this._data!;
  }

  /**
   * Get UMA for a specific year
   */
  static getPorAño(año: number): UMA | undefined {
    const existente = this.getData().find((u) => u.año === año);
    if (existente) {
      return existente;
    }

    const equivalencia = SalariosMinimos.getUmaEquivalente(año, 'diario');
    if (equivalencia === undefined) {
      return undefined;
    }

    const salario = SalariosMinimos.getPorAño(año);
    const vigenciaInicio = salario?.vigencia_inicio ?? `${año}-01-01`;
    const vigenciaFin = salario?.vigencia_inicio ? `${año}-12-31` : `${año}-12-31`;
    const valorDiario = equivalencia;
    const valorMensual =
      SalariosMinimos.getUmaEquivalente(año, 'mensual') ?? Number((valorDiario * 30.4).toFixed(2));
    const valorAnual =
      SalariosMinimos.getUmaEquivalente(año, 'anual') ?? Number((valorDiario * 365).toFixed(2));

    return {
      año,
      vigencia_inicio: vigenciaInicio,
      vigencia_fin: vigenciaFin,
      valor_diario: Number(valorDiario.toFixed(2)),
      valor_mensual: Number(valorMensual.toFixed(2)),
      valor_anual: Number(valorAnual.toFixed(2)),
      moneda: salario?.moneda ?? 'MXN',
      publicacion_dof: salario?.vigencia_inicio ?? `${año}-01-01`,
      incremento_porcentual: null,
      notas: 'Equivalencia de UMA generada a partir del salario mínimo vigente antes de 2017',
    };
  }

  /**
   * Get current UMA (most recent year)
   */
  static getActual(): UMA {
    const sorted = [...this.getData()].sort((a, b) => b.año - a.año);
    return sorted[0];
  }

  /**
   * Get UMA value for a specific date
   */
  static getPorFecha(fecha: string | Date): UMA | undefined {
    const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
    const sorted = [...this.getData()].sort(
      (a, b) => new Date(b.vigencia_inicio).getTime() - new Date(a.vigencia_inicio).getTime()
    );

    return (
      sorted.find((u) => {
        const inicio = new Date(u.vigencia_inicio);
        const fin = new Date(u.vigencia_fin);
        return date >= inicio && date <= fin;
      }) ?? this.getPorAño(date.getFullYear())
    );
  }

  /**
   * Get UMA value by type (diario, mensual, anual)
   */
  static getValor(
    año: number,
    tipo: 'diario' | 'mensual' | 'anual' = 'diario'
  ): number | undefined {
    const uma = this.getPorAño(año);
    if (!uma) return undefined;

    switch (tipo) {
      case 'diario':
        return uma.valor_diario;
      case 'mensual':
        return uma.valor_mensual;
      case 'anual':
        return uma.valor_anual;
    }
  }

  /**
   * Calculate amount in UMAs for a given monetary value
   */
  static calcularUMAs(
    monto: number,
    año: number,
    tipo: 'diario' | 'mensual' | 'anual' = 'diario'
  ): number | undefined {
    const valorUMA = this.getValor(año, tipo);
    return valorUMA ? monto / valorUMA : undefined;
  }

  /**
   * Calculate monetary value from UMAs
   */
  static calcularMonto(
    umas: number,
    año: number,
    tipo: 'diario' | 'mensual' | 'anual' = 'diario'
  ): number | undefined {
    const valorUMA = this.getValor(año, tipo);
    return valorUMA ? umas * valorUMA : undefined;
  }

  /**
   * Get historical evolution of UMA values
   */
  static getHistorico(añoInicio: number, añoFin: number): UMA[] {
    return this.getData()
      .filter((u) => u.año >= añoInicio && u.año <= añoFin)
      .sort((a, b) => a.año - b.año);
  }

  /**
   * Calculate percentage increase between two years
   */
  static calcularIncremento(añoInicial: number, añoFinal: number): number | undefined {
    const inicial = this.getValor(añoInicial);
    const final = this.getValor(añoFinal);

    if (!inicial || !final) return undefined;
    return ((final - inicial) / inicial) * 100;
  }

  /**
   * Get UMA increment percentage for a specific year
   */
  static getIncrementoAnual(año: number): number | null | undefined {
    const uma = this.getPorAño(año);
    return uma?.incremento_porcentual;
  }
}
