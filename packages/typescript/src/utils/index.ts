/**
 * catalogmx - Utilities
 */

// Text utilities
export { normalizeText } from './text';

// CLABE utilities
export {
  decodeClabe,
  generateClabeRandom,
  generateClabeExamples,
  generateClabeForBank,
  getCommonBanks,
  getPlazaSuggestions,
  formatClabe,
  describeClabe,
} from './clabe-utils';

export type { BankInfo, PlazaInfo, DecodedCLABE, GenerateClabeOptions } from './clabe-utils';
