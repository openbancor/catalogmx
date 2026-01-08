/**
 * catalogmx - Validators
 * Mexican identifier validators
 */

export {
  RFCValidator,
  generateRfcPersonaFisica,
  generateRfcPersonaMoral,
  validateRfc,
  detectRfcType,
} from './rfc';

export { CURPValidator, generateCurp, validateCurp } from './curp';

export { CLABEValidator, validateClabe, generateClabe, getClabeInfo } from './clabe';
export type { ClabeInfo } from './clabe';

export { NSSValidator, validateNss, generateNss } from './nss';
