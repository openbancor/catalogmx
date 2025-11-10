/**
 * CLABE (Clave Bancaria Estandarizada) Validator
 * Mexican standardized 18-digit bank account number for interbank electronic transfers (SPEI)
 *
 * Structure:
 *   - 3 digits: Bank code
 *   - 3 digits: Branch/Plaza code
 *   - 11 digits: Account number
 *   - 1 digit: Check digit (modulo 10 algorithm)
 *
 * Example: 002010077777777771
 *   002: Banamex
 *   010: Branch code
 *   07777777777: Account number
 *   1: Check digit
 */

export class CLABEValidator {
  private readonly clabe: string;
  private static readonly LENGTH = 18;
  private static readonly WEIGHTS = [3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7];

  constructor(clabe: string) {
    this.clabe = clabe.trim();
  }

  /**
   * Validate CLABE structure and check digit
   */
  validate(): boolean {
    // Check length
    if (this.clabe.length !== CLABEValidator.LENGTH) {
      throw new Error(
        `CLABE length must be ${CLABEValidator.LENGTH} digits, got ${this.clabe.length}`
      );
    }

    // Check if all characters are digits
    if (!/^\d+$/.test(this.clabe)) {
      throw new Error('CLABE must contain only digits');
    }

    // Validate check digit
    if (!this.verifyCheckDigit()) {
      throw new Error('Invalid CLABE check digit');
    }

    return true;
  }

  /**
   * Check if CLABE is valid without throwing errors
   */
  isValid(): boolean {
    try {
      return this.validate();
    } catch {
      return false;
    }
  }

  /**
   * Verify the check digit
   */
  private verifyCheckDigit(): boolean {
    const clabe17 = this.clabe.slice(0, 17);
    const calculatedDigit = CLABEValidator.calculateCheckDigit(clabe17);
    return this.clabe[17] === calculatedDigit;
  }

  /**
   * Calculate check digit for a 17-digit CLABE
   *
   * Algorithm:
   * 1. Multiply each digit by its weight (3,7,1 pattern)
   * 2. Take modulo 10 of each result
   * 3. Sum all results
   * 4. Take modulo 10 of the sum
   * 5. Subtract from 10
   * 6. Take modulo 10 of the result
   */
  static calculateCheckDigit(clabe17: string): string {
    if (clabe17.length !== 17) {
      throw new Error('CLABE must be 17 digits for check digit calculation');
    }

    let sum = 0;
    for (let i = 0; i < 17; i++) {
      const digit = parseInt(clabe17[i]);
      const weight = this.WEIGHTS[i];
      const product = (digit * weight) % 10;
      sum += product;
    }

    const checkDigit = (10 - (sum % 10)) % 10;
    return checkDigit.toString();
  }

  /**
   * Extract bank code (first 3 digits)
   */
  getBankCode(): string | null {
    if (!this.isValid()) return null;
    return this.clabe.slice(0, 3);
  }

  /**
   * Extract branch code (digits 4-6)
   */
  getBranchCode(): string | null {
    if (!this.isValid()) return null;
    return this.clabe.slice(3, 6);
  }

  /**
   * Extract account number (digits 7-17)
   */
  getAccountNumber(): string | null {
    if (!this.isValid()) return null;
    return this.clabe.slice(6, 17);
  }

  /**
   * Get CLABE components
   */
  getComponents(): {
    bankCode: string;
    branchCode: string;
    accountNumber: string;
    checkDigit: string;
  } | null {
    if (!this.isValid()) return null;
    return {
      bankCode: this.clabe.slice(0, 3),
      branchCode: this.clabe.slice(3, 6),
      accountNumber: this.clabe.slice(6, 17),
      checkDigit: this.clabe[17],
    };
  }
}

/**
 * Validate a CLABE string
 */
export function validateClabe(clabe: string): boolean {
  try {
    const validator = new CLABEValidator(clabe);
    return validator.isValid();
  } catch {
    return false;
  }
}

/**
 * Generate a CLABE from components
 */
export function generateClabe(bankCode: string, branchCode: string, accountNumber: string): string {
  // Validate and pad components
  const bank = bankCode.padStart(3, '0').slice(0, 3);
  const branch = branchCode.padStart(3, '0').slice(0, 3);
  const account = accountNumber.padStart(11, '0').slice(0, 11);

  const clabe17 = bank + branch + account;

  if (clabe17.length !== 17 || !/^\d+$/.test(clabe17)) {
    throw new Error('Invalid CLABE components');
  }

  const checkDigit = CLABEValidator.calculateCheckDigit(clabe17);
  return clabe17 + checkDigit;
}
