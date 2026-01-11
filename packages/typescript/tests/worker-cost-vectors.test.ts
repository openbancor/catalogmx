import fs from 'fs';
import path from 'path';

import { calcularCostoTotal, type CostoTotalResult } from '../src/calculators/worker-cost-calculator';
import type { IMSSYear } from '../src/calculators/imss-calculator';

type WorkerCostVector = {
  input: {
    salario_mensual_bruto: number;
    cve_estado: string;
    antiguedad_anos: number;
    dias_aguinaldo: number;
    incluir_ptu: boolean;
    porcentaje_ptu: number;
    year: number;
  };
  expected: CostoTotalResult;
};

const vectorsPath = path.resolve(__dirname, '../../shared-data/tests/costo_trabajador_vectors.json');
const vectors: WorkerCostVector[] = JSON.parse(fs.readFileSync(vectorsPath, 'utf-8'));

const round = (value: number) => Number(value.toFixed(6));

describe('Worker cost shared vectors', () => {
  test('calcular costo total', () => {
    for (const vector of vectors) {
      const result = calcularCostoTotal({
        salario_mensual_bruto: vector.input.salario_mensual_bruto,
        cve_estado: vector.input.cve_estado,
        antiguedad_anos: vector.input.antiguedad_anos,
        dias_aguinaldo: vector.input.dias_aguinaldo,
        incluir_ptu: vector.input.incluir_ptu,
        porcentaje_ptu: vector.input.porcentaje_ptu,
        year: vector.input.year as IMSSYear,
      });

      for (const [key, expectedValue] of Object.entries(vector.expected)) {
        const actual = result[key as keyof CostoTotalResult] as number;
        expect(round(actual)).toBe(expectedValue);
      }
    }
  });
});
