import fs from 'fs';
import path from 'path';

import { ISRCalculator } from '../src/calculators/isr-calculator';

type IsrVector = {
  ingreso: number;
  periodo: 'mensual';
  year: number;
  expected: {
    isrFinal: number;
    subsidio: number;
    isrAntesSubsidio: number;
    tasaEfectiva: number;
  };
};

const vectorsPath = path.resolve(__dirname, '../../shared-data/tests/isr_vectors.json');
const vectors: IsrVector[] = JSON.parse(fs.readFileSync(vectorsPath, 'utf-8'));

const round = (value: number) => Number(value.toFixed(6));

describe('ISR shared vectors', () => {
  test.each(vectors)('matches %s', (vector) => {
    const result = ISRCalculator.calcular(
      vector.ingreso,
      vector.year,
      vector.periodo,
      true
    );

    expect(round(result.isr_a_retener)).toBe(vector.expected.isrFinal);
    expect(round(result.subsidio_empleo ?? 0)).toBe(vector.expected.subsidio);
    expect(round(result.isr_causado)).toBe(vector.expected.isrAntesSubsidio);
    expect(round(result.tasa_efectiva)).toBe(vector.expected.tasaEfectiva);
  });
});
