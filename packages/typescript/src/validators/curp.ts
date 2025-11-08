/**
 * CURP (Clave Única de Registro de Población) Validator and Generator
 * Mexican unique population registry code
 */

const STATE_CODES: Record<string, string> = {
  'AGUASCALIENTES': 'AS', 'BAJA CALIFORNIA': 'BC', 'BAJA CALIFORNIA SUR': 'BS',
  'CAMPECHE': 'CC', 'COAHUILA': 'CL', 'COLIMA': 'CM', 'CHIAPAS': 'CS',
  'CHIHUAHUA': 'CH', 'CIUDAD DE MEXICO': 'DF', 'DISTRITO FEDERAL': 'DF',
  'CDMX': 'DF', 'DURANGO': 'DG', 'GUANAJUATO': 'GT', 'GUERRERO': 'GR',
  'HIDALGO': 'HG', 'JALISCO': 'JC', 'ESTADO DE MEXICO': 'MC', 'MEXICO': 'MC',
  'MICHOACAN': 'MN', 'MORELOS': 'MS', 'NAYARIT': 'NT', 'NUEVO LEON': 'NL',
  'OAXACA': 'OC', 'PUEBLA': 'PL', 'QUERETARO': 'QT', 'QUINTANA ROO': 'QR',
  'SAN LUIS POTOSI': 'SP', 'SINALOA': 'SL', 'SONORA': 'SR', 'TABASCO': 'TC',
  'TAMAULIPAS': 'TS', 'TLAXCALA': 'TL', 'VERACRUZ': 'VZ', 'YUCATAN': 'YN',
  'ZACATECAS': 'ZS', 'NACIDO EN EL EXTRANJERO': 'NE', 'EXTRANJERO': 'NE'
};

const CACOPHONIC_WORDS_CURP = [
  'BACA', 'BAKA', 'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA', 'KAKO',
  'COGE', 'COGI', 'COJA', 'COJE', 'COJI', 'COJO', 'COLA', 'CULO', 'FALO', 'FETO',
  'GETA', 'GUEI', 'GUEY', 'JETA', 'JOTO', 'KACA', 'KACO', 'KAGA', 'KAGO', 'KAKA',
  'KAKO', 'KOGE', 'KOGI', 'KOJA', 'KOJE', 'KOJI', 'KOJO', 'KOLA', 'KULO', 'LILO',
  'LOCA', 'LOCO', 'LOKA', 'LOKO', 'MAME', 'MAMO', 'MEAR', 'MEAS', 'MEON', 'MIAR',
  'MION', 'MOCO', 'MOKO', 'MULA', 'MULO', 'NACA', 'NACO', 'PEDA', 'PEDO', 'PENE',
  'PIPI', 'PITO', 'POPO', 'PUTA', 'PUTO', 'QULO', 'RATA', 'ROBA', 'ROBE', 'ROBO',
  'RUIN', 'SENO', 'TETA', 'VACA', 'VAGA', 'VAGO', 'VAKA', 'VUEI', 'VUEY', 'WUEI', 'WUEY'
];

const EXCLUDED_WORDS_CURP = [
  'DE', 'LA', 'LAS', 'MC', 'VON', 'DEL', 'LOS', 'Y', 'MAC', 'VAN', 'MI',
  'DA', 'DAS', 'DER', 'DI', 'DIE', 'DD', 'EL', 'LE', 'LES'
];

const VOCALES_CURP = 'AEIOU';
const CONSONANTES_CURP = 'BCDFGHJKLMNPQRSTVWXYZ';

/**
 * Remove accents from string
 */
function removeAccentsCurp(str: string): string {
  return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

/**
 * Calculate CURP check digit (position 18)
 */
function calculateCurpCheckDigit(curp17: string): string {
  const dictionary = '0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ';
  let sum = 0;

  for (let i = 0; i < 17; i++) {
    const char = curp17[i];
    const value = dictionary.indexOf(char);
    sum += value * (18 - i);
  }

  const remainder = sum % 10;
  const checkDigit = (10 - remainder) % 10;
  return checkDigit.toString();
}

/**
 * Get first internal consonant from a word
 */
function getFirstConsonant(word: string): string {
  if (!word || word.length <= 1) return 'X';
  for (let i = 1; i < word.length; i++) {
    if (CONSONANTES_CURP.includes(word[i])) {
      return word[i];
    }
  }
  return 'X';
}

/**
 * Clean name by removing excluded words
 */
function cleanNameCurp(name: string): string {
  if (!name) return '';
  let cleaned = removeAccentsCurp(name.toUpperCase().trim());
  EXCLUDED_WORDS_CURP.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'g');
    cleaned = cleaned.replace(regex, ' ');
  });
  return cleaned.split(/\s+/).filter(w => w.length > 0).join(' ');
}

/**
 * Get state code from state name
 */
function getStateCode(state: string): string {
  if (!state) return 'NE';
  const stateUpper = state.toUpperCase().trim();

  // Try exact match
  if (STATE_CODES[stateUpper]) return STATE_CODES[stateUpper];

  // Try partial match
  for (const [stateName, code] of Object.entries(STATE_CODES)) {
    if (stateName.includes(stateUpper) || stateUpper.includes(stateName)) {
      return code;
    }
  }

  // If already a 2-letter code, return it
  if (stateUpper.length === 2 && /^[A-Z]{2}$/.test(stateUpper)) {
    return stateUpper;
  }

  return 'NE';
}

/**
 * CURP Validator class
 */
export class CURPValidator {
  private readonly curp: string;
  private static readonly GENERAL_REGEX = /^[A-Z][AEIOUX][A-Z]{2}[0-9]{2}[0-1][0-9][0-3][0-9][MH][A-Z]{2}[BCDFGHJKLMNPQRSTVWXYZ]{3}[0-9A-Z]{2}$/;
  private static readonly LENGTH = 18;

  constructor(curp: string) {
    this.curp = curp.toUpperCase().trim();
  }

  /**
   * Validate CURP structure
   */
  validate(): boolean {
    if (this.curp.length !== CURPValidator.LENGTH) {
      throw new Error('CURP length must be 18');
    }
    if (!CURPValidator.GENERAL_REGEX.test(this.curp)) {
      throw new Error('Invalid CURP structure');
    }
    return true;
  }

  /**
   * Check if CURP is valid without throwing errors
   */
  isValid(): boolean {
    try {
      return this.validate();
    } catch {
      return false;
    }
  }

  /**
   * Validate check digit (position 18)
   */
  validateCheckDigit(): boolean {
    if (this.curp.length !== 18) return false;
    const curp17 = this.curp.slice(0, 17);
    const expectedDigit = calculateCurpCheckDigit(curp17);
    const actualDigit = this.curp[17];
    return expectedDigit === actualDigit;
  }

  /**
   * Extract birth date from CURP
   */
  getBirthDate(): Date | null {
    if (!this.isValid()) return null;
    const yearStr = this.curp.slice(4, 6);
    const month = parseInt(this.curp.slice(6, 8));
    const day = parseInt(this.curp.slice(8, 10));

    // Determine century (00-24 = 2000s, 25-99 = 1900s)
    const year = parseInt(yearStr) < 25 ? 2000 + parseInt(yearStr) : 1900 + parseInt(yearStr);

    try {
      return new Date(year, month - 1, day);
    } catch {
      return null;
    }
  }

  /**
   * Extract gender from CURP
   */
  getGender(): 'H' | 'M' | null {
    if (!this.isValid()) return null;
    const gender = this.curp[10];
    return gender === 'H' || gender === 'M' ? gender : null;
  }

  /**
   * Extract state code from CURP
   */
  getStateCode(): string | null {
    if (!this.isValid()) return null;
    return this.curp.slice(11, 13);
  }
}

/**
 * Generate CURP for a Mexican citizen
 */
export function generateCurp(input: {
  nombre: string;
  apellidoPaterno: string;
  apellidoMaterno: string;
  fechaNacimiento: Date | string;
  sexo: 'H' | 'M';
  estado: string;
  differentiator?: string;
}): string {
  const fecha = typeof input.fechaNacimiento === 'string'
    ? new Date(input.fechaNacimiento)
    : input.fechaNacimiento;

  const nombre = cleanNameCurp(input.nombre);
  const paterno = cleanNameCurp(input.apellidoPaterno);
  const materno = cleanNameCurp(input.apellidoMaterno);

  // Get first letter and first vowel of paterno
  let iniciales = paterno.charAt(0);
  const paternoVowel = paterno.slice(1).split('').find(c => VOCALES_CURP.includes(c)) || 'X';
  iniciales += paternoVowel;

  // First letter of materno
  iniciales += (materno.charAt(0) || 'X');

  // First letter of nombre
  iniciales += nombre.charAt(0);

  // Handle cacophonic words
  if (CACOPHONIC_WORDS_CURP.includes(iniciales)) {
    iniciales = iniciales[0] + 'X' + iniciales.slice(2);
  }

  // Format date
  const year = fecha.getFullYear().toString().slice(-2);
  const month = (fecha.getMonth() + 1).toString().padStart(2, '0');
  const day = fecha.getDate().toString().padStart(2, '0');

  // Gender
  const sexo = input.sexo.toUpperCase();

  // State code
  const estadoCode = getStateCode(input.estado);

  // Internal consonants
  const consonant1 = getFirstConsonant(paterno);
  const consonant2 = getFirstConsonant(materno);
  const consonant3 = getFirstConsonant(nombre);

  // Base CURP (17 characters)
  const curpBase = iniciales + year + month + day + sexo + estadoCode +
                   consonant1 + consonant2 + consonant3 +
                   (input.differentiator || '0');

  // Calculate check digit
  const checkDigit = calculateCurpCheckDigit(curpBase);

  return curpBase + checkDigit;
}

/**
 * Validate a CURP string
 */
export function validateCurp(curp: string, checkDigit: boolean = true): boolean {
  try {
    const validator = new CURPValidator(curp);
    if (!validator.isValid()) return false;
    if (checkDigit) return validator.validateCheckDigit();
    return true;
  } catch {
    return false;
  }
}
