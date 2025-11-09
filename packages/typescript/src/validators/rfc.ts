/**
 * RFC (Registro Federal de Contribuyentes) Validator and Generator
 * Mexican Tax ID Code validation and generation for both natural persons (Persona Física)
 * and legal entities (Persona Moral)
 */

const CACOPHONIC_WORDS = [
  'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA', 'COGE', 'COJA', 'COJE',
  'COJI', 'COJO', 'CULO', 'FETO', 'GUEY', 'JOTO', 'KACA', 'KACO', 'KAGA', 'KAGO',
  'KOGE', 'KOJO', 'KAKA', 'KULO', 'MAME', 'MAMO', 'MEAR', 'MEON', 'MION', 'MOCO',
  'MULA', 'PEDA', 'PEDO', 'PENE', 'PUTA', 'PUTO', 'QULO', 'RATA', 'RUIN'
];

const EXCLUDED_WORDS_FISICAS = ['DE', 'LA', 'LAS', 'MC', 'VON', 'DEL', 'LOS', 'Y', 'MAC', 'VAN', 'MI'];

const EXCLUDED_WORDS_MORALES = [
  'EL', 'LA', 'DE', 'LOS', 'LAS', 'Y', 'DEL', 'MI',
  'COMPAÑIA', 'COMPAÑÍA', 'CIA', 'CIA.', 'SOCIEDAD', 'SOC', 'SOC.',
  'COOPERATIVA', 'COOP', 'COOP.', 'S.A.', 'SA', 'S.A', 'S. A.', 'S. A',
  'S.A.B.', 'SAB', 'S.A.B', 'S. A. B.', 'S. A. B', 'S. DE R.L.', 'S DE RL',
  'SRL', 'S.R.L.', 'S. R. L.', 'S. EN C.', 'S EN C', 'S.C.', 'SC',
  'A.C.', 'AC', 'A. C.', 'C.V.', 'CV', 'C. V.', 'THE', 'OF', 'COMPANY', 'AND', 'CO', 'CO.'
];

const CHECKSUM_TABLE: Record<string, string> = {
  '0': '00', '1': '01', '2': '02', '3': '03', '4': '04', '5': '05',
  '6': '06', '7': '07', '8': '08', '9': '09', 'A': '10', 'B': '11',
  'C': '12', 'D': '13', 'E': '14', 'F': '15', 'G': '16', 'H': '17',
  'I': '18', 'J': '19', 'K': '20', 'L': '21', 'M': '22', 'N': '23',
  '&': '24', 'O': '25', 'P': '26', 'Q': '27', 'R': '28', 'S': '29',
  'T': '30', 'U': '31', 'V': '32', 'W': '33', 'X': '34', 'Y': '35',
  'Z': '36', ' ': '37', 'Ñ': '38'
};

const HOMOCLAVE_CHARS = 'ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789';
const VOCALES = 'AEIOUÁÉÍÓÚ';
// const CONSONANTES = 'BCDFGHJKLMNÑPQRSTVWXYZ'; // Reserved for future use

/**
 * Remove accents from a string
 */
function removeAccents(str: string): string {
  const accentsMap: Record<string, string> = {
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'
  };
  return str.replace(/[ÁÉÍÓÚáéíóú]/g, char => accentsMap[char] || char);
}

/**
 * Calculate RFC checksum digit
 */
function calculateChecksum(rfc: string): string {
  let rfcBase = rfc.slice(0, -1);
  if (rfcBase.length === 11) {
    rfcBase = ' ' + rfcBase;
  }

  let sum = 0;
  for (let i = 0; i < rfcBase.length; i++) {
    const char = rfcBase[i];
    const value = parseInt(CHECKSUM_TABLE[char]);
    const position = 13 - i;
    sum += value * position;
  }

  const residual = sum % 11;
  if (residual === 0) return '0';
  const checksumValue = 11 - residual;
  return checksumValue === 10 ? 'A' : checksumValue.toString();
}

/**
 * RFC Validator class
 */
export class RFCValidator {
  private readonly rfc: string;
  private static readonly GENERAL_REGEX = /^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{2}[0-9A]$/;
  private static readonly GENERIC_RFCS = ['XAXX010101000', 'XEXX010101000'];

  constructor(rfc: string) {
    this.rfc = rfc.toUpperCase().trim();
  }

  /**
   * Validate RFC format using regex
   */
  validateGeneralRegex(): boolean {
    if (this.rfc.length !== 12 && this.rfc.length !== 13) return false;
    return RFCValidator.GENERAL_REGEX.test(this.rfc);
  }

  /**
   * Validate RFC date component
   */
  validateDate(): boolean {
    if (!this.validateGeneralRegex()) return false;
    const dateStr = this.rfc.slice(this.rfc.length === 13 ? 4 : 3, this.rfc.length === 13 ? 10 : 9);
    try {
      // const year = parseInt(dateStr.slice(0, 2)); // Not currently validated
      const month = parseInt(dateStr.slice(2, 4));
      const day = parseInt(dateStr.slice(4, 6));
      if (month < 1 || month > 12) return false;
      if (day < 1 || day > 31) return false;
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Validate homoclave characters
   */
  validateHomoclave(): boolean {
    if (!this.validateGeneralRegex()) return false;
    const homoclave = this.rfc.slice(-3, -1);
    return homoclave.split('').every(char => HOMOCLAVE_CHARS.includes(char));
  }

  /**
   * Validate RFC checksum
   */
  validateChecksum(): boolean {
    if (!this.validateGeneralRegex()) return false;
    if (this.isGeneric()) return true;
    const calculated = calculateChecksum(this.rfc);
    return this.rfc.slice(-1) === calculated;
  }

  /**
   * Check if RFC is generic (XAXX010101000 or XEXX010101000)
   */
  isGeneric(): boolean {
    return RFCValidator.GENERIC_RFCS.includes(this.rfc);
  }

  /**
   * Check if RFC belongs to Persona Física (individual)
   */
  isFisica(): boolean {
    if (!this.validateGeneralRegex()) throw new Error('Invalid RFC');
    if (this.isGeneric()) return false;
    return /^[A-ZÑ]{4}/.test(this.rfc);
  }

  /**
   * Check if RFC belongs to Persona Moral (company)
   */
  isMoral(): boolean {
    if (!this.validateGeneralRegex()) throw new Error('Invalid RFC');
    return /^[A-ZÑ&]{3}[0-9]/.test(this.rfc);
  }

  /**
   * Detect RFC type
   */
  detectType(): 'fisica' | 'moral' | 'generico' | 'invalido' {
    if (!this.validateGeneralRegex()) return 'invalido';
    if (this.isGeneric()) return 'generico';
    if (this.isFisica()) return 'fisica';
    if (this.isMoral()) return 'moral';
    return 'invalido';
  }

  /**
   * Complete RFC validation
   */
  validate(checkChecksum: boolean = true): boolean {
    if (!this.validateGeneralRegex()) return false;
    if (!this.validateDate()) return false;
    if (!this.validateHomoclave()) return false;
    if (checkChecksum && !this.validateChecksum()) return false;
    return true;
  }

  /**
   * Get validation details
   */
  getValidationDetails(strict: boolean = true): Record<string, boolean> {
    return {
      generalRegex: this.validateGeneralRegex(),
      dateFormat: this.validateDate(),
      homoclave: this.validateHomoclave(),
      ...(strict ? { checksum: this.validateChecksum() } : {})
    };
  }
}

/**
 * Generate RFC for Persona Física (natural person)
 */
export function generateRfcPersonaFisica(input: {
  nombre: string;
  apellidoPaterno: string;
  apellidoMaterno: string;
  fechaNacimiento: Date | string;
}): string {
  const fecha = typeof input.fechaNacimiento === 'string'
    ? new Date(input.fechaNacimiento)
    : input.fechaNacimiento;

  const nombre = removeAccents(input.nombre.toUpperCase().trim());
  const paterno = removeAccents(input.apellidoPaterno.toUpperCase().trim());
  const materno = removeAccents(input.apellidoMaterno.toUpperCase().trim());

  // Remove excluded words
  const cleanPaterno = EXCLUDED_WORDS_FISICAS.includes(paterno) ? '' : paterno;
  const cleanMaterno = EXCLUDED_WORDS_FISICAS.includes(materno) ? '' : materno;

  // Get first letter and first vowel of paterno
  let iniciales = cleanPaterno.charAt(0);
  const paternoVowel = cleanPaterno.slice(1).split('').find(c => VOCALES.includes(c)) || 'X';
  iniciales += paternoVowel;

  // Get first letter of materno
  iniciales += cleanMaterno.charAt(0) || 'X';

  // Get first letter of nombre
  iniciales += nombre.charAt(0);

  // Handle cacophonic words
  if (CACOPHONIC_WORDS.includes(iniciales)) {
    iniciales = iniciales.slice(0, 3) + 'X';
  }

  // Format date
  const year = fecha.getFullYear().toString().slice(-2);
  const month = (fecha.getMonth() + 1).toString().padStart(2, '0');
  const day = fecha.getDate().toString().padStart(2, '0');

  const rfcBase = iniciales + year + month + day;

  // Homoclave placeholder (XX) - would need full implementation for real generation
  const rfcWithHomoclave = rfcBase + 'XX';

  // Calculate checksum
  const checksum = calculateChecksum(rfcWithHomoclave);

  return rfcWithHomoclave + checksum;
}

/**
 * Generate RFC for Persona Moral (legal entity)
 */
export function generateRfcPersonaMoral(input: {
  razonSocial: string;
  fechaConstitucion: Date | string;
}): string {
  const fecha = typeof input.fechaConstitucion === 'string'
    ? new Date(input.fechaConstitucion)
    : input.fechaConstitucion;

  let razonSocial = removeAccents(input.razonSocial.toUpperCase().trim());

  // Remove excluded words
  EXCLUDED_WORDS_MORALES.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'g');
    razonSocial = razonSocial.replace(regex, ' ');
  });

  const words = razonSocial.split(/\s+/).filter(w => w.length > 0);

  let iniciales = '';

  if (words.length === 1) {
    // Single word: first 3 letters
    iniciales = words[0].slice(0, 3);
  } else if (words.length === 2) {
    // Two words: first letter of each + first vowel of first word
    iniciales = words[0].charAt(0);
    const vowel = words[0].slice(1).split('').find(c => VOCALES.includes(c)) || 'X';
    iniciales += vowel;
    iniciales += words[1].charAt(0);
  } else {
    // Three or more words: first letter of first 3 words
    iniciales = words[0].charAt(0) + words[1].charAt(0) + words[2].charAt(0);
  }

  // Pad if necessary
  iniciales = iniciales.padEnd(3, 'X').slice(0, 3);

  // Format date
  const year = fecha.getFullYear().toString().slice(-2);
  const month = (fecha.getMonth() + 1).toString().padStart(2, '0');
  const day = fecha.getDate().toString().padStart(2, '0');

  const rfcBase = iniciales + year + month + day;

  // Homoclave placeholder (XX)
  const rfcWithHomoclave = rfcBase + 'XX';

  // Calculate checksum
  const checksum = calculateChecksum(rfcWithHomoclave);

  return rfcWithHomoclave + checksum;
}

/**
 * Validate an RFC string
 */
export function validateRfc(rfc: string, checkChecksum: boolean = true): boolean {
  try {
    const validator = new RFCValidator(rfc);
    return validator.validate(checkChecksum);
  } catch {
    return false;
  }
}

/**
 * Detect RFC type
 */
export function detectRfcType(rfc: string): 'fisica' | 'moral' | 'generico' | 'invalido' {
  const validator = new RFCValidator(rfc);
  return validator.detectType();
}
