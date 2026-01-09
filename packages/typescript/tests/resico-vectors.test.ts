import fs from 'fs';
import path from 'path';

import { RESICOCalculator, RESICOYear } from '../src/calculators/resico-calculator';

type ResicoVector = {
  ingreso: number;
  periodo: 'mensual' | 'anual';
  year: number;
  expected: {
    resicoCalculado: number;
    tasaEfectiva: number;
  };
};

const vectorsPath = path.resolve(__dirname, '../../shared-data/tests/resico_vectors.json');
const vectors: ResicoVector[] = JSON.parse(fs.readFileSync(vectorsPath, 'utf-8'));

const round = (value: number) => Number(value.toFixed(6));
const toRESICOYear = (year: number): RESICOYear => year as RESICOYear;

describe('RESICO shared vectors', () => {
  test.each(vectors)('matches %s', (vector) => {
    const result = RESICOCalculator.calcular(
      vector.ingreso,
      toRESICOYear(vector.year),
      vector.periodo
    );
    expect(round(result.resicoCalculado)).toBe(vector.expected.resicoCalculado);
    expect(round(result.tasaEfectiva)).toBe(vector.expected.tasaEfectiva);
  });
});
