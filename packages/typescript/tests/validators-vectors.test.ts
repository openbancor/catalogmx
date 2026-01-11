import fs from 'fs';
import path from 'path';

import { validateRfc } from '../src/validators/rfc';
import { validateCurp } from '../src/validators/curp';
import { validateClabe } from '../src/validators/clabe';
import { validateNss } from '../src/validators/nss';

type ValidationVector = {
  value: string;
  valid: boolean;
};

function loadVectors(fileName: string): ValidationVector[] {
  const filePath = path.resolve(__dirname, `../../shared-data/tests/${fileName}`);
  return JSON.parse(fs.readFileSync(filePath, 'utf-8')) as ValidationVector[];
}

describe('shared validator vectors', () => {
  test.each(loadVectors('rfc_validation.json'))('RFC %s', (vector) => {
    expect(validateRfc(vector.value)).toBe(vector.valid);
  });

  test.each(loadVectors('curp_validation.json'))('CURP %s', (vector) => {
    expect(validateCurp(vector.value)).toBe(vector.valid);
  });

  test.each(loadVectors('clabe_validation.json'))('CLABE %s', (vector) => {
    expect(validateClabe(vector.value)).toBe(vector.valid);
  });

  test.each(loadVectors('nss_validation.json'))('NSS %s', (vector) => {
    expect(validateNss(vector.value)).toBe(vector.valid);
  });
});
