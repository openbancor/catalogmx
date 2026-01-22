/**
 * RFC (Registro Federal de Contribuyentes) Validator and Generator
 * Mexican Tax ID Code validation and generation for both natural persons (Persona Física)
 * and legal entities (Persona Moral)
 *
 * Algorithm Reference:
 * https://www.mariovaldez.net/files/IFAI%200610100135506%20065%20Algoritmo%20para%20generar%20el%20RFC%20con%20homoclave%20para%20personas%20fisicas%20y%20morales.pdf
 *
 * Note: The algorithm generates a theoretical homoclave based on SAT rules.
 * The actual homoclave assigned by SAT may differ to ensure uniqueness.
 */

const CACOPHONIC_WORDS = [
  'BUEI',
  'BUEY',
  'CACA',
  'CACO',
  'CAGA',
  'CAGO',
  'CAKA',
  'COGE',
  'COJA',
  'COJE',
  'COJI',
  'COJO',
  'CULO',
  'FETO',
  'GUEY',
  'JOTO',
  'KACA',
  'KACO',
  'KAGA',
  'KAGO',
  'KOGE',
  'KOJO',
  'KAKA',
  'KULO',
  'MAME',
  'MAMO',
  'MEAR',
  'MEON',
  'MION',
  'MOCO',
  'MULA',
  'PEDA',
  'PEDO',
  'PENE',
  'PUTA',
  'PUTO',
  'QULO',
  'RATA',
  'RUIN',
];

const EXCLUDED_WORDS_FISICAS = [
  'DE',
  'LA',
  'LAS',
  'MC',
  'VON',
  'DEL',
  'LOS',
  'Y',
  'MAC',
  'VAN',
  'MI',
];

const EXCLUDED_WORDS_MORALES = [
  'EL',
  'LA',
  'DE',
  'LOS',
  'LAS',
  'Y',
  'DEL',
  'MI',
  'COMPAÑIA',
  'COMPAÑÍA',
  'COMPANIA', // without accent
  'CIA',
  'CIA.',
  'SOCIEDAD',
  'SOC',
  'SOC.',
  // Note: COOPERATIVA is NOT excluded according to SAT spec
  // The regla 11 only excludes: Compañía, Cía., Sociedad, Soc.
  // Note: HNOS (Hermanos) and NAL (Nacional) are NOT excluded - they form part of the RFC
  // Only abbreviations for society types are excluded
  'S.A.',
  'SA',
  'S.A',
  'S. A.',
  'S. A',
  'S.A.B.',
  'SAB',
  'S.A.B',
  'S. A. B.',
  'S. A. B',
  'S. DE R.L.',
  'S DE RL',
  'SRL',
  'S.R.L.',
  'S. R. L.',
  'S. EN C.',
  'S EN C',
  'S.C.',
  'SC',
  'S. EN C. POR A.',
  'S EN C POR A',
  'S. EN N.C.',
  'S EN NC',
  'A.C.',
  'AC',
  'A. C.',
  'A. EN P.',
  'A EN P',
  'S.C.L.',
  'SCL',
  'S.N.C.',
  'SNC',
  'C.V.',
  'CV',
  'C. V.',
  'SA DE CV',
  'S.A. DE C.V.',
  'SA DE CV MI',
  'S.A. DE C.V. MI',
  'S.A.B. DE C.V.',
  'SAB DE CV',
  'S.A.B DE C.V',
  'SRL DE CV',
  'S.R.L. DE C.V.',
  'SRL DE CV MI',
  'SRL MI',
  'THE',
  'OF',
  'COMPANY',
  'AND',
  'CO',
  'CO.',
  'MC',
  'VON',
  'MAC',
  'VAN',
  'PARA',
  'POR',
  'AL',
  'E',
  'EN',
  'CON',
  'SUS',
  'A',
];

const CHECKSUM_TABLE: Record<string, string> = {
  '0': '00',
  '1': '01',
  '2': '02',
  '3': '03',
  '4': '04',
  '5': '05',
  '6': '06',
  '7': '07',
  '8': '08',
  '9': '09',
  A: '10',
  B: '11',
  C: '12',
  D: '13',
  E: '14',
  F: '15',
  G: '16',
  H: '17',
  I: '18',
  J: '19',
  K: '20',
  L: '21',
  M: '22',
  N: '23',
  '&': '24',
  O: '25',
  P: '26',
  Q: '27',
  R: '28',
  S: '29',
  T: '30',
  U: '31',
  V: '32',
  W: '33',
  X: '34',
  Y: '35',
  Z: '36',
  ' ': '37',
  Ñ: '38',
};

const HOMOCLAVE_CHARS = 'ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789';
const HOMOCLAVE_TABLE: Record<string, string> = {
  ' ': '00',
  '0': '00',
  '1': '01',
  '2': '02',
  '3': '03',
  '4': '04',
  '5': '05',
  '6': '06',
  '7': '07',
  '8': '08',
  '9': '09',
  '&': '10',
  A: '11',
  B: '12',
  C: '13',
  D: '14',
  E: '15',
  F: '16',
  G: '17',
  H: '18',
  I: '19',
  J: '21',
  K: '22',
  L: '23',
  M: '24',
  N: '25',
  O: '26',
  P: '27',
  Q: '28',
  R: '29',
  S: '32',
  T: '33',
  U: '34',
  V: '35',
  W: '36',
  X: '37',
  Y: '38',
  Z: '39',
  Ñ: '40',
};

const HOMOCLAVE_ASSIGN_TABLE = [
  '1',
  '2',
  '3',
  '4',
  '5',
  '6',
  '7',
  '8',
  '9',
  'A',
  'B',
  'C',
  'D',
  'E',
  'F',
  'G',
  'H',
  'I',
  'J',
  'K',
  'L',
  'M',
  'N',
  'P',
  'Q',
  'R',
  'S',
  'T',
  'U',
  'V',
  'W',
  'X',
  'Y',
  'Z',
];
const VOCALES = 'AEIOUÁÉÍÓÚ';
// const CONSONANTES = 'BCDFGHJKLMNÑPQRSTVWXYZ'; // Reserved for future use

// Number conversion tables (Arabic and Roman to text) - SAT specification
const NUMEROS_TEXTO: Record<string, string> = {
  '0': 'CERO',
  '1': 'UNO',
  '2': 'DOS',
  '3': 'TRES',
  '4': 'CUATRO',
  '5': 'CINCO',
  '6': 'SEIS',
  '7': 'SIETE',
  '8': 'OCHO',
  '9': 'NUEVE',
  '10': 'DIEZ',
  '11': 'ONCE',
  '12': 'DOCE',
  '13': 'TRECE',
  '14': 'CATORCE',
  '15': 'QUINCE',
  '16': 'DIECISEIS',
  '17': 'DIECISIETE',
  '18': 'DIECIOCHO',
  '19': 'DIECINUEVE',
  '20': 'VEINTE',
  '21': 'VEINTIUNO',
  '22': 'VEINTIDOS',
  '23': 'VEINTITRES',
  '24': 'VEINTICUATRO',
  '25': 'VEINTICINCO',
  '26': 'VEINTISEIS',
  '27': 'VEINTISIETE',
  '28': 'VEINTIOCHO',
  '29': 'VEINTINUEVE',
  '30': 'TREINTA',
  '40': 'CUARENTA',
  '50': 'CINCUENTA',
  '60': 'SESENTA',
  '70': 'SETENTA',
  '80': 'OCHENTA',
  '90': 'NOVENTA',
  '100': 'CIEN',
  '200': 'DOSCIENTOS',
  '300': 'TRESCIENTOS',
  '400': 'CUATROCIENTOS',
  '500': 'QUINIENTOS',
  '600': 'SEISCIENTOS',
  '700': 'SETECIENTOS',
  '800': 'OCHOCIENTOS',
  '900': 'NOVECIENTOS',
};

const NUMEROS_ROMANOS: Record<string, number> = {
  I: 1,
  II: 2,
  III: 3,
  IV: 4,
  V: 5,
  VI: 6,
  VII: 7,
  VIII: 8,
  IX: 9,
  X: 10,
  XI: 11,
  XII: 12,
  XIII: 13,
  XIV: 14,
  XV: 15,
  XVI: 16,
  XVII: 17,
  XVIII: 18,
  XIX: 19,
  XX: 20,
  XXI: 21,
  XXII: 22,
  XXIII: 23,
  XXIV: 24,
  XXV: 25,
  XXVI: 26,
  XXVII: 27,
  XXVIII: 28,
  XXIX: 29,
  XXX: 30,
};

const ALLOWED_CHARS = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ&';

/**
 * Convert number (Arabic or Roman) to text according to SAT specification
 * Handles compound numbers like 505 → QUINIENTOS CINCO
 */
function convertirNumeroATexto(numero: string): string {
  const upper = numero.trim().toUpperCase();

  // Try as Roman numeral
  if (upper in NUMEROS_ROMANOS) {
    const arabigo = NUMEROS_ROMANOS[upper];
    return convertArabigoATexto(arabigo);
  }

  // Try as Arabic numeral
  const num = parseInt(upper, 10);
  if (!isNaN(num) && num >= 0) {
    return convertArabigoATexto(num);
  }

  return numero; // Return original if cannot convert
}

/**
 * Convert an Arabic number to text (supports 0-100000)
 * Examples:
 * - 12 → DOCE
 * - 505 → QUINIENTOS CINCO
 * - 9520 → NUEVE MIL QUINIENTOS VEINTE
 * - 100000 → CIEN MIL
 */
function convertArabigoATexto(num: number): string {
  if (num < 0) return num.toString();

  // Direct lookup for simple numbers
  if (num.toString() in NUMEROS_TEXTO) {
    return NUMEROS_TEXTO[num.toString()];
  }

  // Handle compound numbers
  const parts: string[] = [];

  // Handle 100000 specifically (CIEN MIL)
  if (num === 100000) {
    return 'CIEN MIL';
  }

  // Thousands (1000-99999)
  if (num >= 1000) {
    const thousands = Math.floor(num / 1000);
    if (thousands === 1) {
      parts.push('MIL');
    } else {
      // Convert the thousands part recursively
      const thousandsText = convertArabigoATexto(thousands);
      parts.push(thousandsText);
      parts.push('MIL');
    }
    num = num % 1000;
  }

  // Hundreds (100-999)
  if (num >= 100) {
    const hundreds = Math.floor(num / 100) * 100;
    if (hundreds.toString() in NUMEROS_TEXTO) {
      parts.push(NUMEROS_TEXTO[hundreds.toString()]);
    }
    num = num % 100;
  }

  // Tens and units (1-99)
  if (num > 0) {
    if (num.toString() in NUMEROS_TEXTO) {
      parts.push(NUMEROS_TEXTO[num.toString()]);
    } else if (num >= 30) {
      // 31-99 (except 30, 40, 50, etc.)
      const tens = Math.floor(num / 10) * 10;
      const units = num % 10;
      if (tens.toString() in NUMEROS_TEXTO) {
        parts.push(NUMEROS_TEXTO[tens.toString()]);
      }
      if (units > 0 && units.toString() in NUMEROS_TEXTO) {
        parts.push(NUMEROS_TEXTO[units.toString()]);
      }
    }
  }

  return parts.length > 0 ? parts.join(' ') : num.toString();
}

function cleanName(value: string, excluded: string[]): string {
  const upper = removeAccents(value.toUpperCase());
  // Remove apostrophes without adding space (O'farril -> OFARRIL)
  const noApostrophe = upper.replace(/'/g, '');
  // Replace other special characters with space
  const sanitized = noApostrophe.replace(/[^A-ZÑ&\s]/g, ' ');
  const parts = sanitized.split(/\s+/).filter((p) => p.length > 0 && !excluded.includes(p));
  return parts.join(' ');
}

/**
 * Remove accents from a string
 */
function removeAccents(str: string): string {
  const accentsMap: Record<string, string> = {
    Á: 'A',
    É: 'E',
    Í: 'I',
    Ó: 'O',
    Ú: 'U',
    á: 'a',
    é: 'e',
    í: 'i',
    ó: 'o',
    ú: 'u',
  };
  return str.replace(/[ÁÉÍÓÚáéíóú]/g, (char) => accentsMap[char] || char);
}

function cleanNameForHomoclave(value: string): string {
  return removeAccents(
    value
      .toUpperCase()
      .replace(/[^A-ZÑ&\s]/g, ' ')
      .trim()
  );
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
   * Extract RFC date component as a Date (birth or constitution date)
   */
  getDate(): Date | null {
    if (!this.validateGeneralRegex()) return null;
    const dateStr = this.rfc.slice(this.rfc.length === 13 ? 4 : 3, this.rfc.length === 13 ? 10 : 9);
    const yearTwo = parseInt(dateStr.slice(0, 2));
    const month = parseInt(dateStr.slice(2, 4));
    const day = parseInt(dateStr.slice(4, 6));
    if (Number.isNaN(yearTwo) || Number.isNaN(month) || Number.isNaN(day)) return null;
    if (month < 1 || month > 12 || day < 1 || day > 31) return null;
    const year = yearTwo <= 30 ? 2000 + yearTwo : 1900 + yearTwo;
    const date = new Date(year, month - 1, day);
    if (date.getMonth() !== month - 1 || date.getDate() !== day) return null;
    return date;
  }

  /**
   * Validate homoclave characters
   */
  validateHomoclave(): boolean {
    if (!this.validateGeneralRegex()) return false;
    const homoclave = this.rfc.slice(-3, -1);
    return homoclave.split('').every((char) => HOMOCLAVE_CHARS.includes(char));
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
      ...(strict ? { checksum: this.validateChecksum() } : {}),
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
  const fechaParts = parseDateInput(input.fechaNacimiento);

  const nombre = cleanName(input.nombre, EXCLUDED_WORDS_FISICAS);
  const paterno = cleanName(input.apellidoPaterno, EXCLUDED_WORDS_FISICAS);
  const materno = cleanName(input.apellidoMaterno, EXCLUDED_WORDS_FISICAS);

  // Handle compound names (skip MARIA/JOSE if first word)
  const nombreParts = nombre.split(' ').filter(Boolean);
  let nombreIniciales = nombre;
  if (nombreParts.length > 1 && (nombreParts[0] === 'MARIA' || nombreParts[0] === 'JOSE')) {
    nombreIniciales = nombreParts.slice(1).join(' ') || nombreParts[0];
  }

  // Get the first word of each compound name (for compound surnames)
  const paternoParts = paterno.split(' ').filter(Boolean);
  const maternoParts = materno.split(' ').filter(Boolean);

  const paternoFirst = paternoParts[0] || '';
  const nombreSafe = nombreIniciales || 'X';

  // Check if materno originally had prepositions (de, del, la, los, etc.)
  // If so, and paterno has 2+ words, use second word of paterno as effective materno
  const originalMaternoUpper = input.apellidoMaterno.toUpperCase().trim();
  const maternoHadPrepositions =
    originalMaternoUpper.startsWith('DE ') ||
    originalMaternoUpper.startsWith('DEL ') ||
    originalMaternoUpper.startsWith('LA ') ||
    originalMaternoUpper.startsWith('LOS ') ||
    originalMaternoUpper.startsWith('LAS ');

  // Determine effective materno: use second word of paterno if materno was preposition-based or empty
  let effectiveMaternoFirst = maternoParts[0] || '';
  if (paternoParts.length >= 2 && (maternoHadPrepositions || !effectiveMaternoFirst)) {
    effectiveMaternoFirst = paternoParts[1] || '';
  }

  let iniciales = '';

  // Regla 4: Apellido paterno de 1-2 letras
  // Se usa: inicial paterno + inicial materno + dos primeras del nombre
  if (paternoFirst.length > 0 && paternoFirst.length <= 2 && effectiveMaternoFirst.length > 0) {
    iniciales = paternoFirst.charAt(0);
    iniciales += effectiveMaternoFirst.charAt(0);
    iniciales += nombreSafe.charAt(0) || 'X';
    iniciales += nombreSafe.charAt(1) || 'X';
  }
  // Regla 7: Un solo apellido (sin materno)
  // Se usa: dos primeras del apellido + dos primeras del nombre
  else if (!effectiveMaternoFirst) {
    const apellido = paternoFirst || 'X';
    iniciales = apellido.charAt(0) || 'X';
    iniciales += apellido.charAt(1) || 'X';
    iniciales += nombreSafe.charAt(0) || 'X';
    iniciales += nombreSafe.charAt(1) || 'X';
  }
  // Regla 1: Formación básica (paterno con 3+ letras y con materno)
  // Se usa: primera letra + primera vocal interior paterno + inicial materno + inicial nombre
  else {
    iniciales = paternoFirst.charAt(0);
    const paternoVowel =
      paternoFirst
        .slice(1)
        .split('')
        .find((c) => VOCALES.includes(c)) || 'X';
    iniciales += paternoVowel;
    iniciales += effectiveMaternoFirst.charAt(0);
    iniciales += nombreSafe.charAt(0);
  }

  // Handle cacophonic words
  if (CACOPHONIC_WORDS.includes(iniciales)) {
    iniciales = iniciales.slice(0, 3) + 'X';
  }

  // Format date
  const year = fechaParts.year.toString().slice(-2);
  const month = fechaParts.month.toString().padStart(2, '0');
  const day = fechaParts.day.toString().padStart(2, '0');

  const rfcBase = iniciales + year + month + day;
  const homoclave = calculateHomoclave(`${paterno} ${materno} ${nombre}`);
  const rfcWithHomoclave = rfcBase + homoclave;

  // Calculate checksum (add placeholder '0' because calculateChecksum expects 13 chars and removes last one)
  const checksum = calculateChecksum(rfcWithHomoclave + '0');

  return rfcWithHomoclave + checksum;
}

function calculateHomoclave(fullName: string): string {
  const name = cleanNameForHomoclave(fullName);
  const parts: string[] = ['0'];
  for (const char of name) {
    parts.push(HOMOCLAVE_TABLE[char] ?? '00');
  }
  const cadena = parts.join('');
  let suma = 0;
  for (let i = 0; i < cadena.length - 1; i++) {
    const current = parseInt(cadena.slice(i, i + 2), 10);
    const next = parseInt(cadena[i + 1], 10);
    if (Number.isFinite(current) && Number.isFinite(next)) {
      suma += current * next;
    }
  }
  const modulo = suma % 1000;
  const idx1 = Math.floor(modulo / 34);
  const idx2 = modulo % 34;
  return (HOMOCLAVE_ASSIGN_TABLE[idx1] ?? '0') + (HOMOCLAVE_ASSIGN_TABLE[idx2] ?? '0');
}

// Special character to word conversions according to SAT specification
// These only apply when the character is standalone (surrounded by spaces/boundaries)
const SPECIAL_CHAR_WORDS: Record<string, string> = {
  '@': 'ARROBA',
  '%': 'PORCIENTO',
  '#': 'NUMERO',
  '(': 'ABRE',
  '/': 'DIAGONAL',
};

/**
 * Clean company name according to SAT official rules for Persona Moral
 * Following the complete algorithm from Python implementation
 *
 * Special character handling rules (SAT specification):
 * - Standalone special chars (@ % #) → converted to words (ARROBA, PORCIENTO, NUMERO)
 * - Special chars inside words (S@NDIA, C@FE) → removed entirely
 */
function cleanRazonSocialForRfc(razonSocial: string): string {
  let razon = razonSocial.toUpperCase().trim();

  // Step 0: Handle special characters - different treatment for standalone vs embedded
  // First, mark standalone special characters by surrounding with unique markers
  // A special char is standalone if it's surrounded by spaces or at string boundaries
  for (const [char, word] of Object.entries(SPECIAL_CHAR_WORDS)) {
    const escaped = escapeRegex(char);
    // Replace standalone special chars with their word equivalents
    // Pattern: start or space, then char, then space or end
    razon = razon.replace(new RegExp(`(^|\\s)${escaped}(\\s|$)`, 'g'), `$1${word}$2`);
  }

  // Remove special characters that are embedded inside words (not standalone)
  for (const char of Object.keys(SPECIAL_CHAR_WORDS)) {
    razon = razon.replace(new RegExp(escapeRegex(char), 'g'), '');
  }

  // Step 1: First pass - remove excluded words with punctuation patterns
  // Process longer words first to avoid partial matches (e.g., S.A.B. before S.A.)
  const sortedExcluded = [...EXCLUDED_WORDS_MORALES].sort((a, b) => b.length - a.length);
  for (const excluded of sortedExcluded) {
    // Try exact match with spaces
    razon = razon.replace(new RegExp(` ${escapeRegex(excluded)} `, 'g'), ' ');
    razon = razon.replace(new RegExp(` ${escapeRegex(excluded)},`, 'g'), ' ');
    razon = razon.replace(new RegExp(` ${escapeRegex(excluded)}\\.`, 'g'), ' ');
    // Try at beginning
    if (razon.startsWith(excluded + ' ')) {
      razon = razon.slice(excluded.length + 1);
    }
    // Try at end
    if (razon.endsWith(' ' + excluded)) {
      razon = razon.slice(0, -excluded.length - 1);
    }
    if (razon.endsWith(',' + excluded)) {
      razon = razon.slice(0, -excluded.length - 1);
    }
  }

  // Step 2: Remove special characters except spaces, letters, numbers, dots, and &
  // The & character is valid in RFC and represents "y" (and)
  // Characters to remove according to SAT: !, $, ", -, /, +, (, ), etc.
  const allowedForProcessing = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .ÑÁÉÍÓÚÜñáéíóúü&';
  razon = razon
    .split('')
    .map((c) => (allowedForProcessing.includes(c) ? c : ' '))
    .join('');

  // Step 3: Substitute Ñ with X
  razon = razon.replace(/Ñ/g, 'X').replace(/ñ/g, 'X');

  // Step 4: Handle initials (F.A.Z. → F A Z)
  // Track which words are initials to keep them even if they match excluded words
  const wordsTemp: string[] = [];
  const isInitial: boolean[] = [];

  for (const word of razon.split(/\s+/)) {
    const trimmed = word.trim();
    if (!trimmed) continue;

    // Detect initials pattern: letter.letter.letter or similar
    if (trimmed.includes('.') && trimmed.length <= 15) {
      const parts = trimmed.split('.').filter((c) => c.trim());
      // If all parts are 1-2 characters and alphabetic, they are initials
      if (parts.length > 0 && parts.every((p) => p.length <= 2 && /^[A-Z]+$/i.test(p))) {
        for (const part of parts) {
          wordsTemp.push(part.toUpperCase());
          isInitial.push(true);
        }
        continue;
      }
    }
    // Remove trailing dots from normal words
    const cleanWord = trimmed.replace(/\.+$/, '');
    if (cleanWord) {
      wordsTemp.push(cleanWord);
      isInitial.push(false);
    }
  }

  // Step 5: Convert numbers to text (Arabic and Roman)
  const wordsConverted: string[] = [];
  const isInitialConverted: boolean[] = [];

  for (let i = 0; i < wordsTemp.length; i++) {
    const word = wordsTemp[i];
    const isInit = isInitial[i];
    // Check if it's a number (Arabic or Roman)
    if (/^\d+$/.test(word) || word in NUMEROS_ROMANOS) {
      wordsConverted.push(convertirNumeroATexto(word));
    } else {
      wordsConverted.push(word);
    }
    isInitialConverted.push(isInit);
  }

  // Step 6: Second pass - Remove excluded words (but keep initials)
  // First, try filtering out excluded words
  const filteredWords: string[] = [];
  for (let i = 0; i < wordsConverted.length; i++) {
    const word = wordsConverted[i].trim().toUpperCase();
    if (!word) continue;
    // Keep initials even if they match excluded words
    if (isInitialConverted[i]) {
      filteredWords.push(word);
    } else if (!EXCLUDED_WORDS_MORALES.includes(word)) {
      filteredWords.push(word);
    }
  }

  // If ALL words were excluded, keep the original words (the company name itself)
  // This handles cases like "Al" where "AL" is an excluded word but is the actual name
  const wordsToUse =
    filteredWords.length === 0 ? wordsConverted.map((w) => w.toUpperCase()) : filteredWords;

  // Step 7: Clean remaining special characters and accents
  let result = '';
  for (const char of wordsToUse.join(' ')) {
    if (ALLOWED_CHARS.includes(char)) {
      result += char;
    } else if (char === ' ') {
      result += ' ';
    } else {
      // Use accent removal for accented characters
      const decoded = removeAccents(char);
      if (ALLOWED_CHARS.includes(decoded.toUpperCase())) {
        result += decoded.toUpperCase();
      }
    }
  }
  result = result.trim().toUpperCase();

  // Step 8: Handle consonant compounds (CH → C, LL → L) at the beginning of words
  const wordsFinal: string[] = [];
  for (const word of result.split(/\s+/)) {
    let processedWord = word;
    if (word.startsWith('CH')) {
      processedWord = 'C' + word.slice(2);
    } else if (word.startsWith('LL')) {
      processedWord = 'L' + word.slice(2);
    }
    wordsFinal.push(processedWord);
  }

  return wordsFinal.join(' ');
}

/**
 * Escape special regex characters
 */
function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Generate RFC for Persona Moral (legal entity)
 * Uses complete SAT algorithm including:
 * - Excluded words removal with punctuation patterns
 * - Ñ → X substitution
 * - Initials handling (F.A.Z. → F A Z)
 * - Number conversion (Arabic and Roman to text)
 * - Consonant compounds (CH → C, LL → L)
 */
export function generateRfcPersonaMoral(input: {
  razonSocial: string;
  fechaConstitucion: Date | string;
}): string {
  const fechaParts = parseDateInput(input.fechaConstitucion);

  const razonSocialClean = cleanRazonSocialForRfc(input.razonSocial);
  const words = razonSocialClean.split(/\s+/).filter((w) => w.length > 0);

  if (words.length === 0) {
    throw new Error('Razón social vacía después de limpiar');
  }

  let iniciales = '';

  if (words.length === 1) {
    // Single word: first 3 letters (pad with X if needed)
    const word = words[0];
    iniciales = (word[0] || 'X') + (word[1] || 'X') + (word[2] || 'X');
  } else if (words.length === 2) {
    // Two words: first letter of first word, first two letters of second word
    // According to SAT: "se toma la inicial de la primera y las dos primeras letras de la segunda"
    iniciales = words[0][0] + words[1][0] + (words[1][1] || 'X');
  } else {
    // Three or more words: first letter of each of the first three words
    iniciales = words[0][0] + words[1][0] + words[2][0];
  }

  // Check for cacophonic words
  if (CACOPHONIC_WORDS.includes(iniciales)) {
    iniciales = iniciales.slice(0, 2) + 'X';
  }

  // Format date
  const year = fechaParts.year.toString().slice(-2);
  const month = fechaParts.month.toString().padStart(2, '0');
  const day = fechaParts.day.toString().padStart(2, '0');

  const rfcBase = iniciales + year + month + day;

  // Calculate homoclave using the cleaned name
  const homoclave = calculateHomoclaveMoral(razonSocialClean);
  const rfcWithHomoclave = rfcBase + homoclave;

  // Calculate checksum
  const checksum = calculateChecksum(rfcWithHomoclave + '0');

  return rfcWithHomoclave + checksum;
}

/**
 * Calculate homoclave specifically for Persona Moral
 * Uses the cleaned razón social
 */
function calculateHomoclaveMoral(cleanedName: string): string {
  const parts: string[] = ['0'];
  for (const char of cleanedName) {
    if (char in HOMOCLAVE_TABLE) {
      parts.push(HOMOCLAVE_TABLE[char]);
    } else if (char === ' ') {
      parts.push(HOMOCLAVE_TABLE[' ']);
    }
  }
  const cadena = parts.join('');
  let suma = 0;
  for (let i = 0; i < cadena.length - 1; i++) {
    const current = parseInt(cadena.slice(i, i + 2), 10);
    const next = parseInt(cadena[i + 1], 10);
    if (Number.isFinite(current) && Number.isFinite(next)) {
      suma += current * next;
    }
  }
  const modulo = suma % 1000;
  const idx1 = Math.floor(modulo / 34);
  const idx2 = modulo % 34;
  return (HOMOCLAVE_ASSIGN_TABLE[idx1] ?? '0') + (HOMOCLAVE_ASSIGN_TABLE[idx2] ?? '0');
}

function parseDateInput(value: Date | string): { year: number; month: number; day: number } {
  if (value instanceof Date) {
    return {
      year: value.getFullYear(),
      month: value.getMonth() + 1,
      day: value.getDate(),
    };
  }

  const isoMatch = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (isoMatch) {
    return {
      year: Number(isoMatch[1]),
      month: Number(isoMatch[2]),
      day: Number(isoMatch[3]),
    };
  }

  const dmyMatch = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(value);
  if (dmyMatch) {
    return {
      day: Number(dmyMatch[1]),
      month: Number(dmyMatch[2]),
      year: Number(dmyMatch[3]),
    };
  }

  throw new Error('Fecha inválida. Usa YYYY-MM-DD o DD/MM/YYYY.');
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
