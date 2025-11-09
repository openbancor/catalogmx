/**
 * Tests for validators
 */

import {
  validateRfc,
  generateRfcPersonaFisica,
  validateCurp,
  generateCurp,
  validateClabe,
  validateNss
} from '../src/validators';

describe('RFC Validator', () => {
  test('should validate valid RFC for persona física', () => {
    expect(validateRfc('PEGJ900515XXA', false)).toBe(true);
  });

  test('should reject invalid RFC', () => {
    expect(validateRfc('INVALID')).toBe(false);
  });

  test('should generate RFC for persona física', () => {
    const rfc = generateRfcPersonaFisica({
      nombre: 'Juan',
      apellidoPaterno: 'Pérez',
      apellidoMaterno: 'García',
      fechaNacimiento: new Date('1990-05-15')
    });
    expect(rfc).toMatch(/^[A-Z]{4}\d{6}[A-Z0-9]{3}$/);
  });

  test('should validate generic RFC', () => {
    expect(validateRfc('XAXX010101000', false)).toBe(true);
    expect(validateRfc('XEXX010101000', false)).toBe(true);
  });
});

describe('CURP Validator', () => {
  test('should validate valid CURP structure', () => {
    expect(validateCurp('PEGJ900512HJCRRS04', false)).toBe(true);
  });

  test('should reject invalid CURP', () => {
    expect(validateCurp('INVALID')).toBe(false);
  });

  test('should generate CURP', () => {
    const curp = generateCurp({
      nombre: 'Juan',
      apellidoPaterno: 'Pérez',
      apellidoMaterno: 'García',
      fechaNacimiento: new Date('1990-05-12'),
      sexo: 'H',
      estado: 'JALISCO'
    });
    expect(curp).toMatch(/^[A-Z]{4}\d{6}[HM][A-Z]{2}[BCDFGHJKLMNPQRSTVWXYZ]{3}[0-9A-Z]{2}$/);
    expect(curp.length).toBe(18);
  });
});

describe('CLABE Validator', () => {
  test('should validate valid CLABE', () => {
    expect(validateClabe('002010077777777771')).toBe(true);
  });

  test('should reject invalid CLABE', () => {
    expect(validateClabe('002010077777777770')).toBe(false);
    expect(validateClabe('INVALID')).toBe(false);
  });

  test('should reject wrong length', () => {
    expect(validateClabe('12345')).toBe(false);
  });
});

describe('NSS Validator', () => {
  test('should validate valid NSS', () => {
    expect(validateNss('12345678903')).toBe(true);
  });

  test('should reject invalid NSS', () => {
    expect(validateNss('12345678900')).toBe(false);
    expect(validateNss('INVALID')).toBe(false);
  });

  test('should reject wrong length', () => {
    expect(validateNss('123456')).toBe(false);
  });
});
