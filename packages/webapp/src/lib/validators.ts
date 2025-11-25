/**
 * Mexican Data Validators - Browser-compatible implementations
 */

// ============================================================================
// RFC VALIDATOR
// ============================================================================

const CACOPHONIC_WORDS = [
  'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA', 'COGE', 'COJA',
  'COJE', 'COJI', 'COJO', 'CULO', 'FETO', 'GUEY', 'JOTO', 'KACA', 'KACO',
  'KAGA', 'KAGO', 'KOGE', 'KOJO', 'KAKA', 'KULO', 'MAME', 'MAMO', 'MEAR',
  'MEON', 'MION', 'MOCO', 'MULA', 'PEDA', 'PEDO', 'PENE', 'PUTA', 'PUTO',
  'QULO', 'RATA', 'RUIN'
];

const EXCLUDED_WORDS_FISICAS = [
  'DE', 'LA', 'LAS', 'MC', 'VON', 'DEL', 'LOS', 'Y', 'MAC', 'VAN', 'MI'
];

const CHECKSUM_TABLE: Record<string, string> = {
  '0': '00', '1': '01', '2': '02', '3': '03', '4': '04', '5': '05',
  '6': '06', '7': '07', '8': '08', '9': '09', A: '10', B: '11', C: '12',
  D: '13', E: '14', F: '15', G: '16', H: '17', I: '18', J: '19', K: '20',
  L: '21', M: '22', N: '23', '&': '24', O: '25', P: '26', Q: '27', R: '28',
  S: '29', T: '30', U: '31', V: '32', W: '33', X: '34', Y: '35', Z: '36',
  ' ': '37', 'Ñ': '38'
};

const HOMOCLAVE_TABLE: Record<string, string> = {
  ' ': '00', '0': '00', '1': '01', '2': '02', '3': '03', '4': '04', '5': '05',
  '6': '06', '7': '07', '8': '08', '9': '09', '&': '10', A: '11', B: '12',
  C: '13', D: '14', E: '15', F: '16', G: '17', H: '18', I: '19', J: '21',
  K: '22', L: '23', M: '24', N: '25', O: '26', P: '27', Q: '28', R: '29',
  S: '32', T: '33', U: '34', V: '35', W: '36', X: '37', Y: '38', Z: '39', 'Ñ': '40'
};

const HOMOCLAVE_ASSIGN_TABLE = [
  '1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','P','Q','R','S','T','U','V','W','X','Y','Z'
];

const VOCALES = 'AEIOUÁÉÍÓÚ';

function removeAccents(str: string): string {
  const accentsMap: Record<string, string> = {
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'
  };
  return str.replace(/[ÁÉÍÓÚáéíóú]/g, (char) => accentsMap[char] || char);
}

function cleanName(value: string, excluded: string[]): string {
  const upper = removeAccents(value.toUpperCase());
  const sanitized = upper.replace(/[^A-ZÑ&\s]/g, ' ');
  const parts = sanitized
    .split(/\s+/)
    .filter((p) => p.length > 0 && !excluded.includes(p));
  return parts.join(' ');
}

function cleanNameForHomoclave(value: string): string {
  return removeAccents(value.toUpperCase().replace(/[^A-ZÑ&\s]/g, ' ').trim());
}

function calculateRfcChecksum(rfc: string): string {
  let rfcBase = rfc.slice(0, -1);
  if (rfcBase.length === 11) rfcBase = ' ' + rfcBase;
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

export interface RFCValidationResult {
  isValid: boolean;
  type: 'persona_fisica' | 'persona_moral' | 'generic' | 'invalid';
  details: {
    format: boolean;
    date: boolean;
    checksum: boolean;
  };
  parsed?: {
    initials: string;
    date: string;
    homoclave: string;
    checkDigit: string;
  };
}

export function validateRFC(rfc: string): RFCValidationResult {
  const rfcClean = rfc.toUpperCase().trim();
  const GENERAL_REGEX = /^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{2}[0-9A]$/;
  const GENERIC_RFCS = ['XAXX010101000', 'XEXX010101000'];

  const result: RFCValidationResult = {
    isValid: false,
    type: 'invalid',
    details: { format: false, date: false, checksum: false }
  };

  // Format validation
  if (rfcClean.length !== 12 && rfcClean.length !== 13) return result;
  if (!GENERAL_REGEX.test(rfcClean)) return result;
  result.details.format = true;

  // Generic RFC check
  if (GENERIC_RFCS.includes(rfcClean)) {
    result.isValid = true;
    result.type = 'generic';
    result.details.date = true;
    result.details.checksum = true;
    return result;
  }

  // Date validation
  const dateStr = rfcClean.slice(rfcClean.length === 13 ? 4 : 3, rfcClean.length === 13 ? 10 : 9);
  const month = parseInt(dateStr.slice(2, 4));
  const day = parseInt(dateStr.slice(4, 6));
  if (month >= 1 && month <= 12 && day >= 1 && day <= 31) {
    result.details.date = true;
  }

  // Checksum validation
  const calculated = calculateRfcChecksum(rfcClean);
  result.details.checksum = rfcClean.slice(-1) === calculated;

  // Determine type
  if (/^[A-ZÑ]{4}/.test(rfcClean)) {
    result.type = 'persona_fisica';
  } else if (/^[A-ZÑ&]{3}[0-9]/.test(rfcClean)) {
    result.type = 'persona_moral';
  }

  // Parse components
  const isFisica = rfcClean.length === 13;
  result.parsed = {
    initials: rfcClean.slice(0, isFisica ? 4 : 3),
    date: rfcClean.slice(isFisica ? 4 : 3, isFisica ? 10 : 9),
    homoclave: rfcClean.slice(-3, -1),
    checkDigit: rfcClean.slice(-1)
  };

  result.isValid = result.details.format && result.details.date && result.details.checksum;
  return result;
}

export function generateRFC(data: {
  nombre: string;
  paterno: string;
  materno: string;
  fecha: Date;
}): string {
  const nombre = cleanName(data.nombre, EXCLUDED_WORDS_FISICAS);
  const paterno = cleanName(data.paterno, EXCLUDED_WORDS_FISICAS);
  const materno = cleanName(data.materno, EXCLUDED_WORDS_FISICAS);

  const nombreParts = nombre.split(' ').filter(Boolean);
  let nombreIniciales = nombre;
  if (nombreParts.length > 1 && (nombreParts[0] === 'MARIA' || nombreParts[0] === 'JOSE')) {
    nombreIniciales = nombreParts.slice(1).join(' ') || nombreParts[0];
  }

  const paternoSafe = paterno || 'X';
  let iniciales = paternoSafe.charAt(0);
  const paternoVowel = paternoSafe.slice(1).split('').find(c => VOCALES.includes(c)) || 'X';
  let extraLetter = false;
  iniciales += paternoVowel;

  const maternoSafe = materno || '';
  if (maternoSafe) {
    iniciales += maternoSafe.charAt(0);
  } else {
    extraLetter = true;
  }

  const nombreSafe = nombreIniciales || 'X';
  iniciales += nombreSafe.charAt(0);
  if (extraLetter && nombreSafe.length > 1) {
    iniciales += nombreSafe.charAt(1);
  }

  if (CACOPHONIC_WORDS.includes(iniciales)) {
    iniciales = iniciales.slice(0, 3) + 'X';
  }

  const year = data.fecha.getFullYear().toString().slice(-2);
  const month = (data.fecha.getMonth() + 1).toString().padStart(2, '0');
  const day = data.fecha.getDate().toString().padStart(2, '0');

  const rfcBase = iniciales + year + month + day;
  const homoclave = calculateHomoclave(`${paterno} ${materno} ${nombre}`);
  const rfcWithHomoclave = rfcBase + homoclave;
  return rfcWithHomoclave + calculateRfcChecksum(rfcWithHomoclave + '0');
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

// ============================================================================
// CURP VALIDATOR
// ============================================================================

const CURP_REGEX = /^[A-Z][AEIOUX][A-Z]{2}[0-9]{2}[0-1][0-9][0-3][0-9][MH][A-Z]{2}[BCDFGHJKLMNPQRSTVWXYZ]{3}[0-9A-Z][0-9]$/;
const CONSONANTES = 'BCDFGHJKLMNPQRSTVWXYZ';

function calculateCurpCheckDigit(curp17: string): string {
  const dictionary = '0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ';
  let sum = 0;
  for (let i = 0; i < 17; i++) {
    const value = dictionary.indexOf(curp17[i]);
    sum += value * (18 - i);
  }
  return ((10 - (sum % 10)) % 10).toString();
}

function getFirstConsonant(word: string): string {
  if (!word || word.length <= 1) return 'X';
  for (let i = 1; i < word.length; i++) {
    if (CONSONANTES.includes(word[i])) return word[i];
  }
  return 'X';
}

const STATE_NAMES: Record<string, string> = {
  'AS': 'Aguascalientes', 'BC': 'Baja California', 'BS': 'Baja California Sur',
  'CC': 'Campeche', 'CL': 'Coahuila', 'CM': 'Colima', 'CS': 'Chiapas',
  'CH': 'Chihuahua', 'DF': 'Ciudad de México', 'DG': 'Durango',
  'GT': 'Guanajuato', 'GR': 'Guerrero', 'HG': 'Hidalgo', 'JC': 'Jalisco',
  'MC': 'Estado de México', 'MN': 'Michoacán', 'MS': 'Morelos', 'NT': 'Nayarit',
  'NL': 'Nuevo León', 'OC': 'Oaxaca', 'PL': 'Puebla', 'QT': 'Querétaro',
  'QR': 'Quintana Roo', 'SP': 'San Luis Potosí', 'SL': 'Sinaloa', 'SR': 'Sonora',
  'TC': 'Tabasco', 'TS': 'Tamaulipas', 'TL': 'Tlaxcala', 'VZ': 'Veracruz',
  'YN': 'Yucatán', 'ZS': 'Zacatecas', 'NE': 'Nacido en el extranjero'
};

export interface CURPValidationResult {
  isValid: boolean;
  details: {
    format: boolean;
    checkDigit: boolean;
  };
  parsed?: {
    initials: string;
    birthDate: string;
    gender: string;
    state: string;
    stateName: string;
    consonants: string;
    differentiator: string;
    checkDigit: string;
  };
}

export function validateCURP(curp: string): CURPValidationResult {
  const curpClean = curp.toUpperCase().trim();

  const result: CURPValidationResult = {
    isValid: false,
    details: { format: false, checkDigit: false }
  };

  if (curpClean.length !== 18) return result;
  if (!CURP_REGEX.test(curpClean)) return result;
  result.details.format = true;

  const expected = calculateCurpCheckDigit(curpClean.slice(0, 17));
  result.details.checkDigit = expected === curpClean[17];

  const yearStr = curpClean.slice(4, 6);
  const year = parseInt(yearStr) < 25 ? '20' + yearStr : '19' + yearStr;
  const stateCode = curpClean.slice(11, 13);

  result.parsed = {
    initials: curpClean.slice(0, 4),
    birthDate: `${year}-${curpClean.slice(6, 8)}-${curpClean.slice(8, 10)}`,
    gender: curpClean[10] === 'H' ? 'Masculino' : 'Femenino',
    state: stateCode,
    stateName: STATE_NAMES[stateCode] || stateCode,
    consonants: curpClean.slice(13, 16),
    differentiator: curpClean[16],
    checkDigit: curpClean[17]
  };

  result.isValid = result.details.format && result.details.checkDigit;
  return result;
}

export function generateCURP(data: {
  nombre: string;
  paterno: string;
  materno: string;
  fecha: Date;
  sexo: 'H' | 'M';
  estado: string;
}): string {
  const nombre = removeAccents(data.nombre.toUpperCase().trim());
  const paterno = removeAccents(data.paterno.toUpperCase().trim());
  const materno = removeAccents(data.materno.toUpperCase().trim());

  let iniciales = paterno.charAt(0);
  const paternoVowel = paterno.slice(1).split('').find(c => 'AEIOU'.includes(c)) || 'X';
  iniciales += paternoVowel;
  iniciales += materno.charAt(0) || 'X';
  iniciales += nombre.charAt(0);

  const year = data.fecha.getFullYear().toString().slice(-2);
  const month = (data.fecha.getMonth() + 1).toString().padStart(2, '0');
  const day = data.fecha.getDate().toString().padStart(2, '0');

  const consonant1 = getFirstConsonant(paterno);
  const consonant2 = getFirstConsonant(materno);
  const consonant3 = getFirstConsonant(nombre);

  const curpBase = iniciales + year + month + day + data.sexo + data.estado + consonant1 + consonant2 + consonant3 + '0';
  return curpBase + calculateCurpCheckDigit(curpBase);
}

// ============================================================================
// CLABE VALIDATOR
// ============================================================================

const CLABE_WEIGHTS = [3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7];

const BANK_NAMES: Record<string, string> = {
  '002': 'BANAMEX', '006': 'BANCOMEXT', '009': 'BANOBRAS', '012': 'BBVA MEXICO',
  '014': 'SANTANDER', '019': 'BANJERCITO', '021': 'HSBC', '030': 'BAJIO',
  '036': 'INBURSA', '042': 'MIFEL', '044': 'SCOTIABANK', '058': 'BANREGIO',
  '059': 'INVEX', '060': 'BANSI', '062': 'AFIRME', '072': 'BANORTE',
  '106': 'BANK OF AMERICA', '108': 'MUFG', '110': 'JP MORGAN', '112': 'BMONEX',
  '113': 'VE POR MAS', '124': 'CITI MEXICO', '127': 'AZTECA', '128': 'KAPITAL',
  '129': 'BARCLAYS', '130': 'COMPARTAMOS', '132': 'MULTIVA', '133': 'ACTINVER',
  '135': 'NAFIN', '136': 'INTERCAM', '137': 'BANCOPPEL', '138': 'UALA',
  '140': 'CONSUBANCO', '141': 'VOLKSWAGEN', '145': 'BBASE', '147': 'BANKAOOL',
  '148': 'PAGATODO', '150': 'INMOBILIARIO', '151': 'DONDE', '152': 'BANCREA',
  '154': 'BANCO COVALTO', '155': 'ICBC', '156': 'SABADELL', '157': 'SHINHAN',
  '158': 'MIZUHO', '159': 'BANK OF CHINA', '160': 'BANCO S3', '166': 'BaBien',
  '167': 'HEY BANCO', '168': 'HIPOTECARIA FED',
  '600': 'MONEXCB', '601': 'GBM', '602': 'MASARI', '605': 'VALUE', '608': 'VECTOR',
  '616': 'FINAMEX', '617': 'VALMEX', '620': 'PROFUTURO', '630': 'CB INTERCAM',
  '631': 'CI BOLSA', '634': 'FINCOMUN', '638': 'NU MEXICO', '646': 'STP',
  '652': 'CREDICAPITAL', '653': 'KUSPIT', '656': 'UNAGRA', '659': 'ASP INTEGRA',
  '661': 'KLAR', '670': 'LIBERTAD', '677': 'CAJA POP MEXICA', '680': 'CRISTOBAL COLON',
  '683': 'CAJA TELEFONISTAS', '684': 'TRANSFER', '685': 'FIRA', '688': 'CREDICLUB',
  '699': 'FONDEADORA', '703': 'TESORED', '706': 'ARCUS', '710': 'NVIO',
  '715': 'CASHI', '720': 'MexPago', '721': 'albo', '722': 'Mercado Pago',
  '723': 'Cuenca', '725': 'COOPDESARROLLO', '728': 'SPIN BY OXXO',
  '729': 'Dep y Pag Dig', '732': 'Peibo', '734': 'FINCO PAY',
  '901': 'CLS', '902': 'INDEVAL', '903': 'CoDi Valida'
};

export interface CLABEValidationResult {
  isValid: boolean;
  details: {
    format: boolean;
    checkDigit: boolean;
  };
  parsed?: {
    bankCode: string;
    bankName: string;
    branchCode: string;
    accountNumber: string;
    checkDigit: string;
  };
}

export function validateCLABE(clabe: string): CLABEValidationResult {
  const clabeClean = clabe.trim();

  const result: CLABEValidationResult = {
    isValid: false,
    details: { format: false, checkDigit: false }
  };

  if (clabeClean.length !== 18) return result;
  if (!/^\d+$/.test(clabeClean)) return result;
  result.details.format = true;

  // Verify check digit
  let sum = 0;
  for (let i = 0; i < 17; i++) {
    const digit = parseInt(clabeClean[i]);
    const product = (digit * CLABE_WEIGHTS[i]) % 10;
    sum += product;
  }
  const checkDigit = (10 - (sum % 10)) % 10;
  result.details.checkDigit = clabeClean[17] === checkDigit.toString();

  const bankCode = clabeClean.slice(0, 3);
  result.parsed = {
    bankCode,
    bankName: BANK_NAMES[bankCode] || 'Banco desconocido',
    branchCode: clabeClean.slice(3, 6),
    accountNumber: clabeClean.slice(6, 17),
    checkDigit: clabeClean[17]
  };

  result.isValid = result.details.format && result.details.checkDigit;
  return result;
}

// ============================================================================
// NSS VALIDATOR
// ============================================================================

export interface NSSValidationResult {
  isValid: boolean;
  details: {
    format: boolean;
    checkDigit: boolean;
  };
  parsed?: {
    subdelegation: string;
    registrationYear: string;
    birthYear: string;
    sequential: string;
    checkDigit: string;
  };
}

export function validateNSS(nss: string): NSSValidationResult {
  const nssClean = nss.trim();

  const result: NSSValidationResult = {
    isValid: false,
    details: { format: false, checkDigit: false }
  };

  if (nssClean.length !== 11) return result;
  if (!/^\d+$/.test(nssClean)) return result;
  result.details.format = true;

  // Luhn algorithm variant
  let sum = 0;
  const digits = nssClean.slice(0, 10).split('').reverse();
  for (let i = 0; i < digits.length; i++) {
    let digit = parseInt(digits[i]);
    if (i % 2 === 0) {
      digit *= 2;
      if (digit > 9) digit = Math.floor(digit / 10) + (digit % 10);
    }
    sum += digit;
  }
  const checkDigit = (10 - (sum % 10)) % 10;
  result.details.checkDigit = nssClean[10] === checkDigit.toString();

  result.parsed = {
    subdelegation: nssClean.slice(0, 2),
    registrationYear: nssClean.slice(2, 4),
    birthYear: nssClean.slice(4, 6),
    sequential: nssClean.slice(6, 10),
    checkDigit: nssClean[10]
  };

  result.isValid = result.details.format && result.details.checkDigit;
  return result;
}
