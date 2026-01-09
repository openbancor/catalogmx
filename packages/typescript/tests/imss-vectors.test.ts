import fs from 'fs';
import path from 'path';

import { IMSSCalculator, IMSSYear, ClaseRiesgo } from '../src/calculators/imss-calculator';

type ImssVectors = {
  cuotas_obrero_patronales: Array<{
    salario_diario: number;
    dias: number;
    year: number;
    clase_riesgo: number;
    expected: {
      total_imss: number;
      total_patron: number;
      total_trabajador: number;
    };
  }>;
  modalidad_40: Array<{
    salario_base_cotizacion: number;
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
  test('cuotas obrero patronales', () => {
    for (const vector of vectors.cuotas_obrero_patronales) {
      const result = IMSSCalculator.calcularCuotasObreroPatronales(
        vector.salario_diario,
        vector.dias,
        toIMSSYear(vector.year),
        toClaseRiesgo(vector.clase_riesgo)
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
        toIMSSYear(vector.year)
      );
      expect(round(result.cuota_mensual)).toBe(vector.expected.cuota_mensual);
      expect(round(result.porcentaje_total)).toBe(vector.expected.porcentaje_total);
    }
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
