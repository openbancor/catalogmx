import fs from 'fs';
import path from 'path';

import { ISRCalculator } from '../src/calculators';
import { SalariosMinimos, UMACatalog } from '../src/catalogs';
import { validateClabe, validateCurp, validateNss, validateRfc } from '../src/validators';

type ValidationVector = {
  value: string;
  valid: boolean;
};

function loadValidationVectors(fileName: string): ValidationVector[] {
  const filePath = path.resolve(__dirname, `../../shared-data/tests/${fileName}`);
  return JSON.parse(fs.readFileSync(filePath, 'utf-8')) as ValidationVector[];
}

function firstValidValue(fileName: string): string {
  const vectors = loadValidationVectors(fileName);
  const entry = vectors.find((vector) => vector.valid);
  if (!entry) throw new Error(`No valid vector found in ${fileName}`);
  return entry.value;
}

describe('integration workflows', () => {
  test('validates shared identifiers and calculates ISR', () => {
    const validRfc = firstValidValue('rfc_validation.json');
    const validCurp = firstValidValue('curp_validation.json');
    const validClabe = firstValidValue('clabe_validation.json');
    const validNss = firstValidValue('nss_validation.json');

    expect(validateRfc(validRfc)).toBe(true);
    expect(validateCurp(validCurp)).toBe(true);
    expect(validateClabe(validClabe)).toBe(true);
    expect(validateNss(validNss)).toBe(true);

    const isr = ISRCalculator.calcular(15000, 2026, 'mensual', false);
    expect(isr.isr_a_retener).toBeGreaterThan(0);
    expect(isr.isr_a_retener).toBeLessThan(isr.ingreso_gravable);
  });

  test('reads mexico catalogs in the same workflow', () => {
    const salario2024 = SalariosMinimos.getPorAño(2024);
    const uma2024 = UMACatalog.getPorAño(2024);

    expect(salario2024).toBeDefined();
    expect(uma2024).toBeDefined();
    expect((salario2024?.resto_pais ?? salario2024?.zona_general ?? 0)).toBeGreaterThan(0);
    expect((uma2024?.valor_diario ?? 0)).toBeGreaterThan(0);
  });
});
