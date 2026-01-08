/**
 * Tests for validators
 */

import {
  validateRfc,
  generateRfcPersonaFisica,
  validateCurp,
  generateCurp,
  validateClabe,
  generateClabe,
  calculateClabeCheckDigit,
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

describe('CLABE Generator', () => {
  test('should generate CLABE with string inputs', () => {
    const clabe = generateClabe('002', '010', '07777777777');
    expect(clabe).toBe('002010077777777771');
    expect(validateClabe(clabe)).toBe(true);
  });

  test('should generate CLABE with numeric inputs', () => {
    const clabe = generateClabe(2, 10, 7777777777);
    expect(clabe).toBe('002010077777777771');
    expect(validateClabe(clabe)).toBe(true);
  });

  test('should generate CLABE with mixed inputs', () => {
    const clabe = generateClabe('002', 10, '07777777777');
    expect(clabe).toBe('002010077777777771');
    expect(validateClabe(clabe)).toBe(true);
  });

  test('should pad short bank code', () => {
    const clabe = generateClabe('2', '010', '07777777777');
    expect(clabe).toBe('002010077777777771');
    expect(validateClabe(clabe)).toBe(true);
  });

  test('should pad short branch code', () => {
    const clabe = generateClabe('002', '10', '07777777777');
    expect(clabe).toBe('002010077777777771');
    expect(validateClabe(clabe)).toBe(true);
  });

  test('should pad short account number', () => {
    const clabe = generateClabe('002', '010', '7777777777');
    expect(clabe).toBe('002010077777777771');
    expect(validateClabe(clabe)).toBe(true);
  });

  test('should generate different CLABEs for different banks', () => {
    const clabe1 = generateClabe('002', '010', '07777777777');
    const clabe2 = generateClabe('012', '010', '07777777777');
    expect(clabe1).not.toBe(clabe2);
    expect(validateClabe(clabe1)).toBe(true);
    expect(validateClabe(clabe2)).toBe(true);
  });

  test('should throw error for invalid components', () => {
    expect(() => generateClabe('ABC', '010', '07777777777')).toThrow('Invalid CLABE components');
  });

  test('should calculate check digit correctly', () => {
    const checkDigit = calculateClabeCheckDigit('00201007777777777');
    expect(checkDigit).toBe('1');
  });

  test('should calculate different check digits for different CLABEs', () => {
    const checkDigit1 = calculateClabeCheckDigit('00201007777777777');
    const checkDigit2 = calculateClabeCheckDigit('01201007777777777');
    expect(checkDigit1).not.toBe(checkDigit2);
  });

  test('should throw error for invalid length in check digit calculation', () => {
    expect(() => calculateClabeCheckDigit('12345')).toThrow('CLABE must be 17 digits');
  });

  test('generated CLABE should have correct structure', () => {
    const clabe = generateClabe('002', '010', '07777777777');
    expect(clabe).toHaveLength(18);
    expect(clabe).toMatch(/^\d{18}$/);
    expect(clabe.slice(0, 3)).toBe('002'); // Bank code
    expect(clabe.slice(3, 6)).toBe('010'); // Branch code
    expect(clabe.slice(6, 17)).toBe('07777777777'); // Account number
    expect(clabe[17]).toBe('1'); // Check digit
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
