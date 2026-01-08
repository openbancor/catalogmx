/**
 * CLABE Generator Example
 * Demonstrates how to generate and validate CLABEs
 */

import {
  generateClabe,
  calculateClabeCheckDigit,
  validateClabe,
  getClabeInfo,
} from '../src/validators/clabe';

// Example 1: Generate CLABE with string inputs
const clabe1 = generateClabe('002', '010', '07777777777');
console.log('CLABE from strings:', clabe1); // 002010077777777771

// Example 2: Generate CLABE with numeric inputs
const clabe2 = generateClabe(2, 10, 7777777777);
console.log('CLABE from numbers:', clabe2); // 002010077777777771

// Example 3: Generate CLABE with mixed inputs
const clabe3 = generateClabe('002', 10, '07777777777');
console.log('CLABE from mixed:', clabe3); // 002010077777777771

// Example 4: Calculate check digit only
const checkDigit = calculateClabeCheckDigit('00201007777777777');
console.log('Check digit:', checkDigit); // 1

// Example 5: Validate the generated CLABE
console.log('Is valid:', validateClabe(clabe1)); // true

// Example 6: Get CLABE information
const info = getClabeInfo(clabe1);
console.log('CLABE Info:', info);
// {
//   clabe: '002010077777777771',
//   bankCode: '002',
//   branchCode: '010',
//   accountNumber: '07777777777',
//   checkDigit: '1',
//   isValid: true
// }

// Example 7: Different banks produce different CLABEs
const banamex = generateClabe('002', '010', '12345678901');
const hsbc = generateClabe('021', '010', '12345678901');
console.log('Banamex CLABE:', banamex);
console.log('HSBC CLABE:', hsbc);
console.log('Different CLABEs:', banamex !== hsbc); // true
