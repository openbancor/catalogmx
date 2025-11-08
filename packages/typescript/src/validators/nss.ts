/**
 * NSS (Número de Seguridad Social) Validator
 * Mexican Social Security Number (IMSS)
 *
 * Structure (11 digits):
 *   - 5 digits: Subdelegation code
 *   - 2 digits: Registration year
 *   - 4 digits: Serial number
 *   - 1 digit: Check digit (modified Luhn algorithm)
 *
 * Example: 12345678903
 *   12345: Subdelegation
 *   67: Year
 *   8903: Serial
 *   Last digit may vary
 */

export class NSSValidator {
  private readonly nss: string;
  private static readonly LENGTH = 11;

  constructor(nss: string) {
    this.nss = nss.trim();
  }

  /**
   * Validate NSS structure and check digit
   */
  validate(): boolean {
    // Check length
    if (this.nss.length !== NSSValidator.LENGTH) {
      throw new Error(`NSS length must be ${NSSValidator.LENGTH} digits, got ${this.nss.length}`);
    }

    // Check if all characters are digits
    if (!/^\d+$/.test(this.nss)) {
      throw new Error('NSS must contain only digits');
    }

    // Validate check digit using modified Luhn algorithm
    if (!this.verifyCheckDigit()) {
      throw new Error('Invalid NSS check digit');
    }

    return true;
  }

  /**
   * Check if NSS is valid without throwing errors
   */
  isValid(): boolean {
    try {
      return this.validate();
    } catch {
      return false;
    }
  }

  /**
   * Verify check digit using modified Luhn algorithm
   */
  private verifyCheckDigit(): boolean {
    const nss10 = this.nss.slice(0, 10);
    const calculatedDigit = NSSValidator.calculateCheckDigit(nss10);
    return this.nss[10] === calculatedDigit.toString();
  }

  /**
   * Calculate check digit using modified Luhn algorithm
   *
   * Algorithm:
   * 1. For each digit from right to left (excluding check digit):
   *    - If position is odd (from right): double the digit
   *    - If result > 9: sum the digits of the result
   * 2. Sum all processed digits
   * 3. Check digit = (10 - (sum % 10)) % 10
   */
  static calculateCheckDigit(nss10: string): number {
    if (nss10.length !== 10) {
      throw new Error('NSS must be 10 digits for check digit calculation');
    }

    let sum = 0;
    const digits = nss10.split('').reverse(); // Reverse for easier processing

    for (let i = 0; i < digits.length; i++) {
      let digit = parseInt(digits[i]);

      // Double every other digit (odd positions from right)
      if (i % 2 === 0) {
        digit *= 2;
        // If result > 9, sum the digits
        if (digit > 9) {
          digit = Math.floor(digit / 10) + (digit % 10);
        }
      }

      sum += digit;
    }

    const checkDigit = (10 - (sum % 10)) % 10;
    return checkDigit;
  }

  /**
   * Extract subdelegation code (first 5 digits)
   */
  getSubdelegation(): string | null {
    if (!this.isValid()) return null;
    return this.nss.slice(0, 5);
  }

  /**
   * Extract registration year (digits 6-7)
   */
  getRegistrationYear(): string | null {
    if (!this.isValid()) return null;
    return this.nss.slice(5, 7);
  }

  /**
   * Extract serial number (digits 8-11, excluding check digit)
   */
  getSerialNumber(): string | null {
    if (!this.isValid()) return null;
    return this.nss.slice(7, 10);
  }

  /**
   * Get NSS components
   */
  getComponents(): { subdelegation: string; year: string; serial: string; checkDigit: string } | null {
    if (!this.isValid()) return null;
    return {
      subdelegation: this.nss.slice(0, 5),
      year: this.nss.slice(5, 7),
      serial: this.nss.slice(7, 10),
      checkDigit: this.nss[10]
    };
  }
}

/**
 * Validate an NSS string
 */
export function validateNss(nss: string): boolean {
  try {
    const validator = new NSSValidator(nss);
    return validator.isValid();
  } catch {
    return false;
  }
}

/**
 * Generate an NSS from components
 */
export function generateNss(subdelegation: string, year: string, serial: string): string {
  // Validate and format components
  const subdelPadded = subdelegation.padStart(5, '0').slice(0, 5);
  const yearPadded = year.padStart(2, '0').slice(0, 2);
  const serialPadded = serial.padStart(3, '0').slice(0, 3);

  const nss10 = subdelPadded + yearPadded + serialPadded;

  if (nss10.length !== 10 || !/^\d+$/.test(nss10)) {
    throw new Error('Invalid NSS components');
  }

  const checkDigit = NSSValidator.calculateCheckDigit(nss10);
  return nss10 + checkDigit;
}
