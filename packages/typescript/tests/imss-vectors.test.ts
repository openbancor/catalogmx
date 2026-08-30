import fs from 'fs';
import path from 'path';

import { IMSSCalculator, IMSSYear, ClaseRiesgo } from '../src/calculators/imss-calculator';

type ImssVectors = {
  cuotas_obrero_patronales: Array<{
    salario_diario: number;
    dias: number;
    year: number;
    clase_riesgo: number;
    fecha?: string;
    expected: {
      total_imss: number;
      total_patron: number;
      total_trabajador: number;
    };
  }>;
  modalidad_40: Array<{
    salario_base_cotizacion: number;
    ultimo_sbc_mensual: number;
    year: number;
    expected: {
      cuota_mensual: number;
      porcentaje_total: number;
    };
  }>;
  modalidad_10: Array<{
    salario_base_cotizacion: number;
    year: number;
    expected: {
      cuota_mensual: number;
      cuota_fija_uma: number;
    };
  }>;
};

const vectorsPath = path.resolve(__dirname, '../../shared-data/tests/imss_vectors.json');
const vectors: ImssVectors = JSON.parse(fs.readFileSync(vectorsPath, 'utf-8'));

const round = (value: number) => Number(value.toFixed(6));
const toIMSSYear = (year: number): IMSSYear => year as IMSSYear;
const toClaseRiesgo = (value: number): ClaseRiesgo => value as ClaseRiesgo;

describe('IMSS shared vectors', () => {
  test('UMA public helpers expose the cross-runtime value shape only', () => {
    const expected = { diaria: 117.31, mensual: 3566.22, anual: 42794.64 };
    expect(IMSSCalculator.getUMA(2026)).toEqual(expected);
    expect(IMSSCalculator.getUMAForDate('2026-02-01')).toEqual(expected);
  });

  test('cuotas obrero patronales', () => {
    for (const vector of vectors.cuotas_obrero_patronales) {
      const result = IMSSCalculator.calcularCuotasObreroPatronales(
        vector.salario_diario,
        vector.dias,
        toIMSSYear(vector.year),
        toClaseRiesgo(vector.clase_riesgo),
        vector.fecha
      );
      expect(round(result.total_imss)).toBe(vector.expected.total_imss);
      expect(round(result.total_patron)).toBe(vector.expected.total_patron);
      expect(round(result.total_trabajador)).toBe(vector.expected.total_trabajador);
    }
  });

  test('modalidad 40', () => {
    for (const vector of vectors.modalidad_40) {
      const result = IMSSCalculator.calcularModalidad40(
        vector.salario_base_cotizacion,
        vector.ultimo_sbc_mensual,
        toIMSSYear(vector.year)
      );
      expect(round(result.cuota_mensual)).toBe(vector.expected.cuota_mensual);
      expect(round(result.porcentaje_total)).toBe(vector.expected.porcentaje_total);
    }
  });

  test('modalidad 40 rejects an SBC below the last registered SBC', () => {
    expect(() => IMSSCalculator.calcularModalidad40(10000, 12000, 2026)).toThrow(
      'no puede ser menor al último SBC'
    );
  });

  test('modalidad 40 preserves the special 1 SM CEAV band', () => {
    const monthlyMinimumWage = 315.04 * (3566.22 / 117.31);
    const result = IMSSCalculator.calcularModalidad40(monthlyMinimumWage, monthlyMinimumWage, 2026);
    expect(result.porcentaje_total).toBeCloseTo(0.10075, 8);
  });

  test('modalidad 40 rejects non-finite requested salary', () => {
    expect(() => IMSSCalculator.calcularModalidad40(Number.NaN, 10000, 2026)).toThrow(
      'debe ser mayor que cero'
    );
    expect(() => IMSSCalculator.calcularModalidad40(Number.POSITIVE_INFINITY, 10000, 2026)).toThrow(
      'debe ser mayor que cero'
    );
  });

  test('modalidad 10', () => {
    for (const vector of vectors.modalidad_10) {
      const result = IMSSCalculator.calcularModalidad10(
        vector.salario_base_cotizacion,
        toIMSSYear(vector.year)
      );
      expect(round(result.cuota_mensual)).toBe(vector.expected.cuota_mensual);
      expect(round(result.cuota_fija_uma)).toBe(vector.expected.cuota_fija_uma);
    }
  });
});
