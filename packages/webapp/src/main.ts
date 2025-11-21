/**
 * catalogmx Demo Application
 * Interactive demonstration of Mexican data validation library
 */

// ============================================================================
// VALIDATORS (Browser-compatible implementations)
// ============================================================================

// RFC Validator
const CACOPHONIC_WORDS = [
  'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA', 'COGE', 'COJA',
  'COJE', 'COJI', 'COJO', 'CULO', 'FETO', 'GUEY', 'JOTO', 'KACA', 'KACO',
  'KAGA', 'KAGO', 'KOGE', 'KOJO', 'KAKA', 'KULO', 'MAME', 'MAMO', 'MEAR',
  'MEON', 'MION', 'MOCO', 'MULA', 'PEDA', 'PEDO', 'PENE', 'PUTA', 'PUTO',
  'QULO', 'RATA', 'RUIN'
];

const CHECKSUM_TABLE: Record<string, string> = {
  '0': '00', '1': '01', '2': '02', '3': '03', '4': '04', '5': '05',
  '6': '06', '7': '07', '8': '08', '9': '09', A: '10', B: '11', C: '12',
  D: '13', E: '14', F: '15', G: '16', H: '17', I: '18', J: '19', K: '20',
  L: '21', M: '22', N: '23', '&': '24', O: '25', P: '26', Q: '27', R: '28',
  S: '29', T: '30', U: '31', V: '32', W: '33', X: '34', Y: '35', Z: '36',
  ' ': '37', 'Ñ': '38'
};

const VOCALES = 'AEIOUÁÉÍÓÚ';

function removeAccents(str: string): string {
  const accentsMap: Record<string, string> = {
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'
  };
  return str.replace(/[ÁÉÍÓÚáéíóú]/g, (char) => accentsMap[char] || char);
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

class RFCValidator {
  private readonly rfc: string;
  private static readonly GENERAL_REGEX = /^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{2}[0-9A]$/;
  private static readonly GENERIC_RFCS = ['XAXX010101000', 'XEXX010101000'];

  constructor(rfc: string) {
    this.rfc = rfc.toUpperCase().trim();
  }

  validateGeneralRegex(): boolean {
    if (this.rfc.length !== 12 && this.rfc.length !== 13) return false;
    return RFCValidator.GENERAL_REGEX.test(this.rfc);
  }

  validateDate(): boolean {
    if (!this.validateGeneralRegex()) return false;
    const dateStr = this.rfc.slice(this.rfc.length === 13 ? 4 : 3, this.rfc.length === 13 ? 10 : 9);
    const month = parseInt(dateStr.slice(2, 4));
    const day = parseInt(dateStr.slice(4, 6));
    if (month < 1 || month > 12) return false;
    if (day < 1 || day > 31) return false;
    return true;
  }

  validateChecksum(): boolean {
    if (!this.validateGeneralRegex()) return false;
    if (RFCValidator.GENERIC_RFCS.includes(this.rfc)) return true;
    const calculated = calculateRfcChecksum(this.rfc);
    return this.rfc.slice(-1) === calculated;
  }

  validate(): boolean {
    return this.validateGeneralRegex() && this.validateDate() && this.validateChecksum();
  }

  detectType(): string {
    if (!this.validateGeneralRegex()) return 'invalid';
    if (RFCValidator.GENERIC_RFCS.includes(this.rfc)) return 'generic';
    if (/^[A-ZÑ]{4}/.test(this.rfc)) return 'persona_fisica';
    if (/^[A-ZÑ&]{3}[0-9]/.test(this.rfc)) return 'persona_moral';
    return 'invalid';
  }
}

function generateRfcPersonaFisica(nombre: string, paterno: string, materno: string, fecha: Date): string {
  nombre = removeAccents(nombre.toUpperCase().trim());
  paterno = removeAccents(paterno.toUpperCase().trim());
  materno = removeAccents(materno.toUpperCase().trim());

  let iniciales = paterno.charAt(0);
  const paternoVowel = paterno.slice(1).split('').find(c => VOCALES.includes(c)) || 'X';
  iniciales += paternoVowel;
  iniciales += materno.charAt(0) || 'X';
  iniciales += nombre.charAt(0);

  if (CACOPHONIC_WORDS.includes(iniciales)) {
    iniciales = iniciales.slice(0, 3) + 'X';
  }

  const year = fecha.getFullYear().toString().slice(-2);
  const month = (fecha.getMonth() + 1).toString().padStart(2, '0');
  const day = fecha.getDate().toString().padStart(2, '0');

  const rfcBase = iniciales + year + month + day;
  const rfcWithHomoclave = rfcBase + 'XX';
  const checksum = calculateRfcChecksum(rfcWithHomoclave + '0');
  return rfcWithHomoclave + checksum;
}

// CURP Validator
const CURP_REGEX = /^[A-Z][AEIOUX][A-Z]{2}[0-9]{2}[0-1][0-9][0-3][0-9][MH][A-Z]{2}[BCDFGHJKLMNPQRSTVWXYZ]{3}[0-9A-Z][0-9]$/;
const CONSONANTES_CURP = 'BCDFGHJKLMNPQRSTVWXYZ';

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
    if (CONSONANTES_CURP.includes(word[i])) return word[i];
  }
  return 'X';
}

class CURPValidator {
  private readonly curp: string;

  constructor(curp: string) {
    this.curp = curp.toUpperCase().trim();
  }

  isValid(): boolean {
    if (this.curp.length !== 18) return false;
    return CURP_REGEX.test(this.curp);
  }

  validateCheckDigit(): boolean {
    if (this.curp.length !== 18) return false;
    const expected = calculateCurpCheckDigit(this.curp.slice(0, 17));
    return expected === this.curp[17];
  }

  getBirthDate(): string {
    const yearStr = this.curp.slice(4, 6);
    const month = this.curp.slice(6, 8);
    const day = this.curp.slice(8, 10);
    const year = parseInt(yearStr) < 25 ? '20' + yearStr : '19' + yearStr;
    return `${year}-${month}-${day}`;
  }

  getGender(): string {
    return this.curp[10] === 'H' ? 'Male' : 'Female';
  }

  getState(): string {
    return this.curp.slice(11, 13);
  }
}

function generateCurp(nombre: string, paterno: string, materno: string, fecha: Date, sexo: string, estado: string): string {
  nombre = removeAccents(nombre.toUpperCase().trim());
  paterno = removeAccents(paterno.toUpperCase().trim());
  materno = removeAccents(materno.toUpperCase().trim());

  let iniciales = paterno.charAt(0);
  const paternoVowel = paterno.slice(1).split('').find(c => 'AEIOU'.includes(c)) || 'X';
  iniciales += paternoVowel;
  iniciales += materno.charAt(0) || 'X';
  iniciales += nombre.charAt(0);

  const year = fecha.getFullYear().toString().slice(-2);
  const month = (fecha.getMonth() + 1).toString().padStart(2, '0');
  const day = fecha.getDate().toString().padStart(2, '0');

  const consonant1 = getFirstConsonant(paterno);
  const consonant2 = getFirstConsonant(materno);
  const consonant3 = getFirstConsonant(nombre);

  const curpBase = iniciales + year + month + day + sexo + estado + consonant1 + consonant2 + consonant3 + '0';
  return curpBase + calculateCurpCheckDigit(curpBase);
}

// CLABE Validator
class CLABEValidator {
  private readonly clabe: string;
  private static readonly WEIGHTS = [3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7];

  constructor(clabe: string) {
    this.clabe = clabe.trim();
  }

  isValid(): boolean {
    if (this.clabe.length !== 18) return false;
    if (!/^\d+$/.test(this.clabe)) return false;
    return this.verifyCheckDigit();
  }

  private verifyCheckDigit(): boolean {
    const clabe17 = this.clabe.slice(0, 17);
    let sum = 0;
    for (let i = 0; i < 17; i++) {
      const digit = parseInt(clabe17[i]);
      const product = (digit * CLABEValidator.WEIGHTS[i]) % 10;
      sum += product;
    }
    const checkDigit = (10 - (sum % 10)) % 10;
    return this.clabe[17] === checkDigit.toString();
  }

  getComponents(): { bankCode: string; branchCode: string; accountNumber: string; checkDigit: string } | null {
    if (!this.isValid()) return null;
    return {
      bankCode: this.clabe.slice(0, 3),
      branchCode: this.clabe.slice(3, 6),
      accountNumber: this.clabe.slice(6, 17),
      checkDigit: this.clabe[17]
    };
  }
}

// NSS Validator
class NSSValidator {
  private readonly nss: string;

  constructor(nss: string) {
    this.nss = nss.trim();
  }

  isValid(): boolean {
    if (this.nss.length !== 11) return false;
    if (!/^\d+$/.test(this.nss)) return false;
    return this.verifyCheckDigit();
  }

  private verifyCheckDigit(): boolean {
    const nss10 = this.nss.slice(0, 10);
    let sum = 0;
    const digits = nss10.split('').reverse();
    for (let i = 0; i < digits.length; i++) {
      let digit = parseInt(digits[i]);
      if (i % 2 === 0) {
        digit *= 2;
        if (digit > 9) digit = Math.floor(digit / 10) + (digit % 10);
      }
      sum += digit;
    }
    const checkDigit = (10 - (sum % 10)) % 10;
    return this.nss[10] === checkDigit.toString();
  }

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

// ============================================================================
// CATALOG DATA (Sample data for demo)
// ============================================================================

interface CatalogInfo {
  name: string;
  description: string;
  count: string;
  data: Array<Record<string, unknown>>;
}

const CATALOGS: Record<string, Record<string, CatalogInfo>> = {
  banxico: {
    banks: {
      name: 'Banks',
      description: 'Mexican banks with SPEI support',
      count: '150+ banks',
      data: [
        { code: '002', name: 'BANAMEX', full_name: 'Banco Nacional de México', spei: true },
        { code: '012', name: 'BBVA MEXICO', full_name: 'BBVA México', spei: true },
        { code: '014', name: 'SANTANDER', full_name: 'Banco Santander', spei: true },
        { code: '021', name: 'HSBC', full_name: 'HSBC México', spei: true },
        { code: '030', name: 'BAJIO', full_name: 'Banco del Bajío', spei: true },
        { code: '036', name: 'INBURSA', full_name: 'Banco Inbursa', spei: true },
        { code: '042', name: 'MIFEL', full_name: 'Banca Mifel', spei: true },
        { code: '044', name: 'SCOTIABANK', full_name: 'Scotiabank Inverlat', spei: true },
        { code: '058', name: 'BANREGIO', full_name: 'Banco Regional de Monterrey', spei: true },
        { code: '072', name: 'BANORTE', full_name: 'Banco Mercantil del Norte', spei: true }
      ]
    },
    currencies: {
      name: 'Currencies',
      description: 'World currencies with ISO codes',
      count: '150+ currencies',
      data: [
        { code: 'MXN', name: 'Peso Mexicano', decimals: 2 },
        { code: 'USD', name: 'Dólar Estadounidense', decimals: 2 },
        { code: 'EUR', name: 'Euro', decimals: 2 },
        { code: 'GBP', name: 'Libra Esterlina', decimals: 2 },
        { code: 'JPY', name: 'Yen Japonés', decimals: 0 },
        { code: 'CAD', name: 'Dólar Canadiense', decimals: 2 },
        { code: 'CHF', name: 'Franco Suizo', decimals: 2 },
        { code: 'CNY', name: 'Yuan Chino', decimals: 2 }
      ]
    },
    udi: {
      name: 'UDI Values',
      description: 'Unidades de Inversión daily values',
      count: 'Historical data',
      data: [
        { date: '2024-01-01', value: 7.929618 },
        { date: '2024-06-01', value: 8.145692 },
        { date: '2024-12-01', value: 8.312456 }
      ]
    },
    instituciones: {
      name: 'Financial Institutions',
      description: 'Types of financial institutions',
      count: '20+ types',
      data: [
        { code: '01', name: 'Banco Múltiple' },
        { code: '02', name: 'Banco de Desarrollo' },
        { code: '03', name: 'Casa de Bolsa' },
        { code: '04', name: 'Sociedad Financiera Popular' }
      ]
    }
  },
  inegi: {
    states: {
      name: 'States',
      description: 'Mexican states with CURP codes',
      count: '32 states',
      data: [
        { code: 'AS', name: 'AGUASCALIENTES', clave_inegi: '01' },
        { code: 'BC', name: 'BAJA CALIFORNIA', clave_inegi: '02' },
        { code: 'BS', name: 'BAJA CALIFORNIA SUR', clave_inegi: '03' },
        { code: 'CC', name: 'CAMPECHE', clave_inegi: '04' },
        { code: 'CL', name: 'COAHUILA', clave_inegi: '05' },
        { code: 'CM', name: 'COLIMA', clave_inegi: '06' },
        { code: 'CS', name: 'CHIAPAS', clave_inegi: '07' },
        { code: 'CH', name: 'CHIHUAHUA', clave_inegi: '08' },
        { code: 'DF', name: 'CIUDAD DE MEXICO', clave_inegi: '09' },
        { code: 'DG', name: 'DURANGO', clave_inegi: '10' },
        { code: 'GT', name: 'GUANAJUATO', clave_inegi: '11' },
        { code: 'GR', name: 'GUERRERO', clave_inegi: '12' },
        { code: 'HG', name: 'HIDALGO', clave_inegi: '13' },
        { code: 'JC', name: 'JALISCO', clave_inegi: '14' },
        { code: 'MC', name: 'ESTADO DE MEXICO', clave_inegi: '15' },
        { code: 'MN', name: 'MICHOACAN', clave_inegi: '16' },
        { code: 'MS', name: 'MORELOS', clave_inegi: '17' },
        { code: 'NT', name: 'NAYARIT', clave_inegi: '18' },
        { code: 'NL', name: 'NUEVO LEON', clave_inegi: '19' },
        { code: 'OC', name: 'OAXACA', clave_inegi: '20' },
        { code: 'PL', name: 'PUEBLA', clave_inegi: '21' },
        { code: 'QT', name: 'QUERETARO', clave_inegi: '22' },
        { code: 'QR', name: 'QUINTANA ROO', clave_inegi: '23' },
        { code: 'SP', name: 'SAN LUIS POTOSI', clave_inegi: '24' },
        { code: 'SL', name: 'SINALOA', clave_inegi: '25' },
        { code: 'SR', name: 'SONORA', clave_inegi: '26' },
        { code: 'TC', name: 'TABASCO', clave_inegi: '27' },
        { code: 'TS', name: 'TAMAULIPAS', clave_inegi: '28' },
        { code: 'TL', name: 'TLAXCALA', clave_inegi: '29' },
        { code: 'VZ', name: 'VERACRUZ', clave_inegi: '30' },
        { code: 'YN', name: 'YUCATAN', clave_inegi: '31' },
        { code: 'ZS', name: 'ZACATECAS', clave_inegi: '32' }
      ]
    },
    municipalities: {
      name: 'Municipalities',
      description: 'Mexican municipalities',
      count: '2,458 municipalities',
      data: [
        { clave: '09015', name: 'Cuauhtémoc', state: 'Ciudad de México' },
        { clave: '09014', name: 'Benito Juárez', state: 'Ciudad de México' },
        { clave: '09016', name: 'Miguel Hidalgo', state: 'Ciudad de México' },
        { clave: '19039', name: 'Monterrey', state: 'Nuevo León' },
        { clave: '14039', name: 'Guadalajara', state: 'Jalisco' }
      ]
    },
    localities: {
      name: 'Localities',
      description: 'Localities with GPS coordinates',
      count: '300K+ localities',
      data: [
        { name: 'Ciudad de México', state: 'CDMX', lat: 19.4326, lon: -99.1332, population: 8918653 },
        { name: 'Guadalajara', state: 'Jalisco', lat: 20.6597, lon: -103.3496, population: 1495182 },
        { name: 'Monterrey', state: 'Nuevo León', lat: 25.6866, lon: -100.3161, population: 1142994 }
      ]
    }
  },
  sepomex: {
    postal_codes: {
      name: 'Postal Codes',
      description: 'Mexican postal codes',
      count: '157K+ codes',
      data: [
        { cp: '06600', colonia: 'Roma Norte', municipio: 'Cuauhtémoc', estado: 'Ciudad de México' },
        { cp: '06700', colonia: 'Roma Sur', municipio: 'Cuauhtémoc', estado: 'Ciudad de México' },
        { cp: '06100', colonia: 'Centro', municipio: 'Cuauhtémoc', estado: 'Ciudad de México' },
        { cp: '11560', colonia: 'Polanco', municipio: 'Miguel Hidalgo', estado: 'Ciudad de México' },
        { cp: '03100', colonia: 'Del Valle', municipio: 'Benito Juárez', estado: 'Ciudad de México' }
      ]
    }
  },
  'sat-cfdi': {
    regimen_fiscal: {
      name: 'Tax Regimes',
      description: 'SAT tax regime codes',
      count: '13 regimes',
      data: [
        { code: '601', description: 'General de Ley Personas Morales', fisica: false, moral: true },
        { code: '603', description: 'Personas Morales con Fines no Lucrativos', fisica: false, moral: true },
        { code: '605', description: 'Sueldos y Salarios', fisica: true, moral: false },
        { code: '606', description: 'Arrendamiento', fisica: true, moral: false },
        { code: '607', description: 'Régimen de Enajenación o Adquisición de Bienes', fisica: true, moral: false },
        { code: '608', description: 'Demás ingresos', fisica: true, moral: false },
        { code: '610', description: 'Residentes en el Extranjero', fisica: true, moral: true },
        { code: '611', description: 'Ingresos por Dividendos', fisica: true, moral: false },
        { code: '612', description: 'Actividades Empresariales y Profesionales', fisica: true, moral: false },
        { code: '614', description: 'Ingresos por intereses', fisica: true, moral: false },
        { code: '615', description: 'Régimen de los ingresos por obtención de premios', fisica: true, moral: false },
        { code: '616', description: 'Sin obligaciones fiscales', fisica: true, moral: false },
        { code: '620', description: 'RESICO', fisica: true, moral: false },
        { code: '625', description: 'Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas', fisica: true, moral: false },
        { code: '626', description: 'Régimen Simplificado de Confianza', fisica: false, moral: true }
      ]
    },
    uso_cfdi: {
      name: 'Invoice Usage',
      description: 'CFDI usage codes',
      count: '42 codes',
      data: [
        { code: 'G01', description: 'Adquisición de mercancías' },
        { code: 'G02', description: 'Devoluciones, descuentos o bonificaciones' },
        { code: 'G03', description: 'Gastos en general' },
        { code: 'I01', description: 'Construcciones' },
        { code: 'I02', description: 'Mobiliario y equipo de oficina' },
        { code: 'I03', description: 'Equipo de transporte' },
        { code: 'I04', description: 'Equipo de computo y accesorios' },
        { code: 'P01', description: 'Por definir' },
        { code: 'S01', description: 'Sin efectos fiscales' }
      ]
    },
    forma_pago: {
      name: 'Payment Methods',
      description: 'Payment method codes',
      count: '29 codes',
      data: [
        { code: '01', description: 'Efectivo' },
        { code: '02', description: 'Cheque nominativo' },
        { code: '03', description: 'Transferencia electrónica de fondos' },
        { code: '04', description: 'Tarjeta de crédito' },
        { code: '05', description: 'Monedero electrónico' },
        { code: '06', description: 'Dinero electrónico' },
        { code: '28', description: 'Tarjeta de débito' },
        { code: '29', description: 'Tarjeta de servicios' },
        { code: '99', description: 'Por definir' }
      ]
    },
    tipo_comprobante: {
      name: 'Document Types',
      description: 'Invoice document types',
      count: '7 types',
      data: [
        { code: 'I', description: 'Ingreso' },
        { code: 'E', description: 'Egreso' },
        { code: 'T', description: 'Traslado' },
        { code: 'N', description: 'Nómina' },
        { code: 'P', description: 'Pago' }
      ]
    },
    impuesto: {
      name: 'Tax Types',
      description: 'Tax classification codes',
      count: '3 taxes',
      data: [
        { code: '001', description: 'ISR - Impuesto Sobre la Renta' },
        { code: '002', description: 'IVA - Impuesto al Valor Agregado' },
        { code: '003', description: 'IEPS - Impuesto Especial sobre Producción y Servicios' }
      ]
    },
    clave_unidad: {
      name: 'Unit Codes',
      description: 'Product unit measurement codes',
      count: '600+ units',
      data: [
        { code: 'H87', description: 'Pieza' },
        { code: 'KGM', description: 'Kilogramo' },
        { code: 'LTR', description: 'Litro' },
        { code: 'MTR', description: 'Metro' },
        { code: 'E48', description: 'Servicio' },
        { code: 'ACT', description: 'Actividad' },
        { code: 'XBX', description: 'Caja' },
        { code: 'XUN', description: 'Unidad' }
      ]
    },
    prod_serv: {
      name: 'Products/Services',
      description: 'SAT product/service codes',
      count: '8,000+ codes',
      data: [
        { code: '01010101', description: 'No existe en el catálogo' },
        { code: '43211500', description: 'Software funcional específico de la empresa' },
        { code: '80131500', description: 'Servicios de arrendamiento de bienes raíces' },
        { code: '84111506', description: 'Servicios de contabilidad de impuestos' },
        { code: '92111500', description: 'Servicios de policía' }
      ]
    }
  },
  'sat-comext': {
    incoterms: {
      name: 'Incoterms',
      description: 'International trade terms',
      count: '13 incoterms',
      data: [
        { code: 'EXW', description: 'Ex Works (En fábrica)' },
        { code: 'FCA', description: 'Free Carrier (Franco transportista)' },
        { code: 'FAS', description: 'Free Alongside Ship (Franco al costado del buque)' },
        { code: 'FOB', description: 'Free On Board (Franco a bordo)' },
        { code: 'CFR', description: 'Cost and Freight (Costo y flete)' },
        { code: 'CIF', description: 'Cost, Insurance and Freight (Costo, seguro y flete)' },
        { code: 'CPT', description: 'Carriage Paid To (Transporte pagado hasta)' },
        { code: 'CIP', description: 'Carriage and Insurance Paid To (Transporte y seguro pagados hasta)' },
        { code: 'DAP', description: 'Delivered At Place (Entregado en lugar)' },
        { code: 'DPU', description: 'Delivered at Place Unloaded (Entregado en lugar descargado)' },
        { code: 'DDP', description: 'Delivered Duty Paid (Entregado con derechos pagados)' }
      ]
    },
    paises: {
      name: 'Countries',
      description: 'Country codes (ISO 3166)',
      count: '250+ countries',
      data: [
        { code: 'MEX', name: 'México' },
        { code: 'USA', name: 'Estados Unidos de América' },
        { code: 'CAN', name: 'Canadá' },
        { code: 'DEU', name: 'Alemania' },
        { code: 'CHN', name: 'China' },
        { code: 'JPN', name: 'Japón' },
        { code: 'ESP', name: 'España' },
        { code: 'GBR', name: 'Reino Unido' }
      ]
    }
  },
  'sat-cartaporte': {
    aeropuertos: {
      name: 'Airports',
      description: 'Mexican airports',
      count: '60+ airports',
      data: [
        { iata: 'MEX', icao: 'MMMX', name: 'Aeropuerto Internacional de la Ciudad de México' },
        { iata: 'GDL', icao: 'MMGL', name: 'Aeropuerto Internacional de Guadalajara' },
        { iata: 'MTY', icao: 'MMMY', name: 'Aeropuerto Internacional de Monterrey' },
        { iata: 'CUN', icao: 'MMUN', name: 'Aeropuerto Internacional de Cancún' },
        { iata: 'TIJ', icao: 'MMTJ', name: 'Aeropuerto Internacional de Tijuana' }
      ]
    },
    puertos: {
      name: 'Seaports',
      description: 'Mexican maritime ports',
      count: '50+ ports',
      data: [
        { code: 'VER', name: 'Puerto de Veracruz' },
        { code: 'MZT', name: 'Puerto de Mazatlán' },
        { code: 'MAN', name: 'Puerto de Manzanillo' },
        { code: 'LZC', name: 'Puerto Lázaro Cárdenas' },
        { code: 'ALT', name: 'Puerto de Altamira' }
      ]
    },
    material_peligroso: {
      name: 'Hazardous Materials',
      description: 'Hazmat classifications',
      count: '100+ classes',
      data: [
        { class: '1', description: 'Explosivos' },
        { class: '2', description: 'Gases' },
        { class: '3', description: 'Líquidos inflamables' },
        { class: '4', description: 'Sólidos inflamables' },
        { class: '5', description: 'Sustancias comburentes y peróxidos orgánicos' },
        { class: '6', description: 'Sustancias tóxicas e infecciosas' },
        { class: '7', description: 'Material radioactivo' },
        { class: '8', description: 'Sustancias corrosivas' },
        { class: '9', description: 'Sustancias y objetos peligrosos varios' }
      ]
    }
  },
  'sat-nomina': {
    tipo_contrato: {
      name: 'Contract Types',
      description: 'Employment contract types',
      count: '6 types',
      data: [
        { code: '01', description: 'Contrato de trabajo por tiempo indeterminado' },
        { code: '02', description: 'Contrato de trabajo para obra determinada' },
        { code: '03', description: 'Contrato de trabajo por tiempo determinado' },
        { code: '04', description: 'Contrato de trabajo por temporada' },
        { code: '05', description: 'Contrato de trabajo sujeto a prueba' },
        { code: '06', description: 'Contrato de trabajo con capacitación inicial' }
      ]
    },
    tipo_jornada: {
      name: 'Work Shifts',
      description: 'Working shift types',
      count: '8 types',
      data: [
        { code: '01', description: 'Diurna' },
        { code: '02', description: 'Nocturna' },
        { code: '03', description: 'Mixta' },
        { code: '04', description: 'Por hora' },
        { code: '05', description: 'Reducida' },
        { code: '06', description: 'Continuada' },
        { code: '07', description: 'Partida' },
        { code: '08', description: 'Por turnos' }
      ]
    },
    periodicidad: {
      name: 'Payment Frequency',
      description: 'Payroll frequency codes',
      count: '7 periods',
      data: [
        { code: '01', description: 'Diario' },
        { code: '02', description: 'Semanal' },
        { code: '03', description: 'Catorcenal' },
        { code: '04', description: 'Quincenal' },
        { code: '05', description: 'Mensual' },
        { code: '06', description: 'Bimestral' },
        { code: '99', description: 'Otra Periodicidad' }
      ]
    },
    riesgo_puesto: {
      name: 'Job Risk Levels',
      description: 'IMSS risk classifications',
      count: '5 levels',
      data: [
        { code: '1', description: 'Clase I', premium: 0.54355 },
        { code: '2', description: 'Clase II', premium: 1.13065 },
        { code: '3', description: 'Clase III', premium: 2.59840 },
        { code: '4', description: 'Clase IV', premium: 4.65325 },
        { code: '5', description: 'Clase V', premium: 7.58875 }
      ]
    }
  },
  ift: {
    lada: {
      name: 'Area Codes (LADA)',
      description: 'Mexican telephone area codes',
      count: '1,000+ codes',
      data: [
        { code: '55', city: 'Ciudad de México' },
        { code: '33', city: 'Guadalajara' },
        { code: '81', city: 'Monterrey' },
        { code: '222', city: 'Puebla' },
        { code: '664', city: 'Tijuana' }
      ]
    },
    operadores: {
      name: 'Mobile Operators',
      description: 'Mexican mobile carriers',
      count: '6+ operators',
      data: [
        { name: 'Telcel', owner: 'América Móvil' },
        { name: 'Movistar', owner: 'Telefónica' },
        { name: 'AT&T México', owner: 'AT&T Inc.' },
        { name: 'Altan', owner: 'Altan Redes' }
      ]
    }
  },
  mexico: {
    salarios_minimos: {
      name: 'Minimum Wages',
      description: 'Mexican minimum wage history',
      count: 'Historical data',
      data: [
        { year: 2024, general: 248.93, zona_libre: 374.89 },
        { year: 2023, general: 207.44, zona_libre: 312.41 },
        { year: 2022, general: 172.87, zona_libre: 260.34 }
      ]
    },
    uma: {
      name: 'UMA Values',
      description: 'Unidad de Medida y Actualización',
      count: 'Annual values',
      data: [
        { year: 2024, daily: 108.57, monthly: 3300.53, annual: 39606.36 },
        { year: 2023, daily: 103.74, monthly: 3153.70, annual: 37844.40 },
        { year: 2022, daily: 96.22, monthly: 2925.09, annual: 35101.08 }
      ]
    },
    hoy_no_circula: {
      name: 'Hoy No Circula CDMX',
      description: 'Vehicle circulation restrictions',
      count: 'Program rules',
      data: [
        { day: 'Monday', hologram: '1-2', ending: '5,6' },
        { day: 'Tuesday', hologram: '1-2', ending: '7,8' },
        { day: 'Wednesday', hologram: '1-2', ending: '3,4' },
        { day: 'Thursday', hologram: '1-2', ending: '1,2' },
        { day: 'Friday', hologram: '1-2', ending: '9,0' }
      ]
    }
  }
};

// ============================================================================
// APPLICATION CODE
// ============================================================================

// Navigation
function initNavigation(): void {
  const navButtons = document.querySelectorAll<HTMLButtonElement>('.nav-btn');
  const sections = document.querySelectorAll<HTMLElement>('.section');

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetSection = btn.dataset.section;
      if (!targetSection) return;

      navButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      sections.forEach(section => {
        section.classList.remove('active');
        if (section.id === targetSection) {
          section.classList.add('active');
        }
      });
    });
  });
}

// Validators
function initValidators(): void {
  // RFC Validator
  const rfcInput = document.getElementById('rfc-input') as HTMLInputElement;
  const rfcValidateBtn = document.getElementById('rfc-validate');
  const rfcResult = document.getElementById('rfc-result');

  rfcValidateBtn?.addEventListener('click', () => {
    const rfc = rfcInput.value.trim();
    if (!rfc) {
      showResult(rfcResult, 'Please enter an RFC', 'error');
      return;
    }

    const validator = new RFCValidator(rfc);
    const isValid = validator.validate();
    const type = validator.detectType();

    if (isValid) {
      showResult(rfcResult, `Valid RFC (${type.replace('_', ' ')})`, 'success');
    } else {
      showResult(rfcResult, `Invalid RFC`, 'error');
    }
  });

  // RFC Generator
  const rfcGenerateBtn = document.getElementById('rfc-generate');
  const rfcGenerated = document.getElementById('rfc-generated');

  rfcGenerateBtn?.addEventListener('click', () => {
    const nombre = (document.getElementById('rfc-nombre') as HTMLInputElement).value;
    const paterno = (document.getElementById('rfc-paterno') as HTMLInputElement).value;
    const materno = (document.getElementById('rfc-materno') as HTMLInputElement).value;
    const fechaStr = (document.getElementById('rfc-fecha') as HTMLInputElement).value;

    if (!nombre || !paterno || !materno || !fechaStr) {
      showResult(rfcGenerated, 'Please fill all fields', 'error');
      return;
    }

    const fecha = new Date(fechaStr);
    const rfc = generateRfcPersonaFisica(nombre, paterno, materno, fecha);
    showResult(rfcGenerated, `Generated RFC: ${rfc}`, 'success');
  });

  // CURP Validator
  const curpInput = document.getElementById('curp-input') as HTMLInputElement;
  const curpValidateBtn = document.getElementById('curp-validate');
  const curpResult = document.getElementById('curp-result');

  curpValidateBtn?.addEventListener('click', () => {
    const curp = curpInput.value.trim();
    if (!curp) {
      showResult(curpResult, 'Please enter a CURP', 'error');
      return;
    }

    const validator = new CURPValidator(curp);
    if (validator.isValid()) {
      const info = `Valid CURP\nBirth: ${validator.getBirthDate()}\nGender: ${validator.getGender()}\nState: ${validator.getState()}`;
      showResult(curpResult, info, 'success');
    } else {
      showResult(curpResult, 'Invalid CURP', 'error');
    }
  });

  // CURP Generator
  const curpGenerateBtn = document.getElementById('curp-generate');
  const curpGenerated = document.getElementById('curp-generated');

  curpGenerateBtn?.addEventListener('click', () => {
    const nombre = (document.getElementById('curp-nombre') as HTMLInputElement).value;
    const paterno = (document.getElementById('curp-paterno') as HTMLInputElement).value;
    const materno = (document.getElementById('curp-materno') as HTMLInputElement).value;
    const fechaStr = (document.getElementById('curp-fecha-nac') as HTMLInputElement).value;
    const sexo = (document.getElementById('curp-sexo') as HTMLSelectElement).value;
    const estado = (document.getElementById('curp-estado') as HTMLSelectElement).value;

    if (!nombre || !paterno || !materno || !fechaStr) {
      showResult(curpGenerated, 'Please fill all fields', 'error');
      return;
    }

    const fecha = new Date(fechaStr);
    const curp = generateCurp(nombre, paterno, materno, fecha, sexo, estado);
    showResult(curpGenerated, `Generated CURP: ${curp}`, 'success');
  });

  // CLABE Validator
  const clabeInput = document.getElementById('clabe-input') as HTMLInputElement;
  const clabeValidateBtn = document.getElementById('clabe-validate');
  const clabeResult = document.getElementById('clabe-result');

  clabeValidateBtn?.addEventListener('click', () => {
    const clabe = clabeInput.value.trim();
    if (!clabe) {
      showResult(clabeResult, 'Please enter a CLABE', 'error');
      return;
    }

    const validator = new CLABEValidator(clabe);
    if (validator.isValid()) {
      const components = validator.getComponents();
      if (components) {
        const info = `Valid CLABE\nBank: ${components.bankCode}\nBranch: ${components.branchCode}\nAccount: ${components.accountNumber}\nCheck: ${components.checkDigit}`;
        showResult(clabeResult, info, 'success');
      }
    } else {
      showResult(clabeResult, 'Invalid CLABE', 'error');
    }
  });

  // NSS Validator
  const nssInput = document.getElementById('nss-input') as HTMLInputElement;
  const nssValidateBtn = document.getElementById('nss-validate');
  const nssResult = document.getElementById('nss-result');

  nssValidateBtn?.addEventListener('click', () => {
    const nss = nssInput.value.trim();
    if (!nss) {
      showResult(nssResult, 'Please enter an NSS', 'error');
      return;
    }

    const validator = new NSSValidator(nss);
    if (validator.isValid()) {
      const components = validator.getComponents();
      if (components) {
        const info = `Valid NSS\nSubdelegation: ${components.subdelegation}\nYear: ${components.year}\nSerial: ${components.serial}\nCheck: ${components.checkDigit}`;
        showResult(nssResult, info, 'success');
      }
    } else {
      showResult(nssResult, 'Invalid NSS', 'error');
    }
  });
}

function showResult(element: HTMLElement | null, message: string, type: 'success' | 'error' | 'info'): void {
  if (!element) return;
  element.textContent = message;
  element.className = `result ${type}`;
}

// Catalogs
function initCatalogs(): void {
  const categoryMap: Record<string, string> = {
    banxico: 'banxico-catalogs',
    inegi: 'inegi-catalogs',
    sepomex: 'sepomex-catalogs',
    'sat-cfdi': 'sat-cfdi-catalogs',
    'sat-comext': 'sat-comext-catalogs',
    'sat-cartaporte': 'sat-cartaporte-catalogs',
    'sat-nomina': 'sat-nomina-catalogs',
    ift: 'ift-catalogs',
    mexico: 'mexico-catalogs'
  };

  Object.entries(CATALOGS).forEach(([category, catalogs]) => {
    const containerId = categoryMap[category];
    const container = document.getElementById(containerId);
    if (!container) return;

    Object.entries(catalogs).forEach(([_key, catalog]) => {
      const item = document.createElement('div');
      item.className = 'catalog-item';
      item.innerHTML = `
        <span class="name">${catalog.name}</span>
        <span class="count">${catalog.count}</span>
      `;
      item.addEventListener('click', () => openCatalogModal(catalog));
      container.appendChild(item);
    });
  });

  // Search
  const searchInput = document.getElementById('catalog-search') as HTMLInputElement;
  searchInput?.addEventListener('input', () => {
    const term = searchInput.value.toLowerCase();
    document.querySelectorAll('.catalog-item').forEach(item => {
      const name = item.querySelector('.name')?.textContent?.toLowerCase() || '';
      (item as HTMLElement).style.display = name.includes(term) ? '' : 'none';
    });
  });

  // Modal close
  const modal = document.getElementById('catalog-modal');
  const closeBtn = modal?.querySelector('.modal-close');
  closeBtn?.addEventListener('click', () => modal?.classList.remove('open'));
  modal?.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('open');
  });
}

let currentCatalogData: Array<Record<string, unknown>> = [];
let currentPage = 0;
const pageSize = 10;

function openCatalogModal(catalog: CatalogInfo): void {
  const modal = document.getElementById('catalog-modal');
  const title = document.getElementById('modal-title');
  const table = document.getElementById('catalog-table');
  const count = document.getElementById('modal-count');
  const searchInput = document.getElementById('modal-search') as HTMLInputElement;

  if (!modal || !title || !table || !count) return;

  title.textContent = catalog.name;
  currentCatalogData = catalog.data;
  currentPage = 0;

  searchInput.value = '';
  searchInput.oninput = () => {
    const term = searchInput.value.toLowerCase();
    const filtered = catalog.data.filter(item =>
      Object.values(item).some(v =>
        String(v).toLowerCase().includes(term)
      )
    );
    currentCatalogData = filtered;
    currentPage = 0;
    renderCatalogTable();
  };

  renderCatalogTable();
  modal.classList.add('open');
}

function renderCatalogTable(): void {
  const table = document.getElementById('catalog-table');
  const count = document.getElementById('modal-count');
  const pageInfo = document.getElementById('page-info');
  const prevBtn = document.getElementById('prev-page');
  const nextBtn = document.getElementById('next-page');

  if (!table || !count || !pageInfo || !prevBtn || !nextBtn) return;

  const thead = table.querySelector('thead');
  const tbody = table.querySelector('tbody');
  if (!thead || !tbody) return;

  // Get columns from first item
  if (currentCatalogData.length === 0) {
    thead.innerHTML = '<tr><th>No data</th></tr>';
    tbody.innerHTML = '<tr><td>No results found</td></tr>';
    count.textContent = '0 records';
    return;
  }

  const columns = Object.keys(currentCatalogData[0]);
  thead.innerHTML = `<tr>${columns.map(c => `<th>${c}</th>`).join('')}</tr>`;

  // Paginate
  const start = currentPage * pageSize;
  const end = Math.min(start + pageSize, currentCatalogData.length);
  const pageData = currentCatalogData.slice(start, end);

  tbody.innerHTML = pageData.map(item =>
    `<tr>${columns.map(c => `<td>${item[c] ?? ''}</td>`).join('')}</tr>`
  ).join('');

  count.textContent = `${currentCatalogData.length} records`;
  pageInfo.textContent = `Page ${currentPage + 1} of ${Math.ceil(currentCatalogData.length / pageSize) || 1}`;

  prevBtn.onclick = () => {
    if (currentPage > 0) {
      currentPage--;
      renderCatalogTable();
    }
  };

  nextBtn.onclick = () => {
    if (end < currentCatalogData.length) {
      currentPage++;
      renderCatalogTable();
    }
  };
}

// Tax Calculators
function initCalculators(): void {
  // ISR Calculator
  const isrCalculateBtn = document.getElementById('isr-calculate');
  const isrResult = document.getElementById('isr-result');

  isrCalculateBtn?.addEventListener('click', () => {
    const income = parseFloat((document.getElementById('isr-income') as HTMLInputElement).value);
    const period = (document.getElementById('isr-period') as HTMLSelectElement).value;

    if (isNaN(income) || income < 0) {
      showResult(isrResult, 'Please enter a valid income', 'error');
      return;
    }

    // Simplified ISR calculation (2024 monthly rates)
    const brackets = [
      { limit: 746.04, rate: 0.0192, fixed: 0 },
      { limit: 6332.05, rate: 0.0640, fixed: 14.32 },
      { limit: 11128.01, rate: 0.1088, fixed: 371.83 },
      { limit: 12935.82, rate: 0.16, fixed: 893.63 },
      { limit: 15487.71, rate: 0.1792, fixed: 1182.88 },
      { limit: 31236.49, rate: 0.2136, fixed: 1640.18 },
      { limit: 49233.00, rate: 0.2352, fixed: 5004.12 },
      { limit: 93993.90, rate: 0.30, fixed: 9236.89 },
      { limit: 125325.20, rate: 0.32, fixed: 22665.17 },
      { limit: 375975.61, rate: 0.34, fixed: 32691.18 },
      { limit: Infinity, rate: 0.35, fixed: 117912.32 }
    ];

    let taxableIncome = income;
    if (period === 'biweekly') taxableIncome *= 2;
    else if (period === 'annual') taxableIncome /= 12;

    let tax = 0;
    let bracketUsed = brackets[0];
    for (const bracket of brackets) {
      if (taxableIncome <= bracket.limit) {
        bracketUsed = bracket;
        break;
      }
      bracketUsed = bracket;
    }

    const prevLimit = brackets[brackets.indexOf(bracketUsed) - 1]?.limit || 0;
    tax = bracketUsed.fixed + (taxableIncome - prevLimit) * bracketUsed.rate;

    if (period === 'biweekly') tax /= 2;
    else if (period === 'annual') tax *= 12;

    const effectiveRate = (tax / income * 100).toFixed(2);
    showResult(isrResult, `ISR: $${tax.toFixed(2)} MXN\nEffective Rate: ${effectiveRate}%`, 'info');
  });

  // IVA Calculator
  const ivaCalculateBtn = document.getElementById('iva-calculate');
  const ivaResult = document.getElementById('iva-result');

  ivaCalculateBtn?.addEventListener('click', () => {
    const base = parseFloat((document.getElementById('iva-base') as HTMLInputElement).value);
    const rate = parseFloat((document.getElementById('iva-rate') as HTMLSelectElement).value);

    if (isNaN(base) || base < 0) {
      showResult(ivaResult, 'Please enter a valid amount', 'error');
      return;
    }

    const iva = base * (rate / 100);
    const total = base + iva;

    showResult(ivaResult, `Base: $${base.toFixed(2)}\nIVA (${rate}%): $${iva.toFixed(2)}\nTotal: $${total.toFixed(2)}`, 'info');
  });

  // IEPS Calculator
  const iepsCalculateBtn = document.getElementById('ieps-calculate');
  const iepsResult = document.getElementById('ieps-result');

  iepsCalculateBtn?.addEventListener('click', () => {
    const base = parseFloat((document.getElementById('ieps-base') as HTMLInputElement).value);
    const product = (document.getElementById('ieps-product') as HTMLSelectElement).value;

    if (isNaN(base) || base < 0) {
      showResult(iepsResult, 'Please enter a valid amount', 'error');
      return;
    }

    const rates: Record<string, { rate: number; name: string }> = {
      alcohol: { rate: 0.53, name: 'Alcoholic Beverages (53%)' },
      tobacco: { rate: 1.60, name: 'Tobacco (160%)' },
      fuel: { rate: 0.1639, name: 'Fuel (16.39%)' },
      sugary: { rate: 0.08, name: 'Sugary Drinks (8%)' }
    };

    const { rate, name } = rates[product];
    const ieps = base * rate;
    const total = base + ieps;

    showResult(iepsResult, `Product: ${name}\nBase: $${base.toFixed(2)}\nIEPS: $${ieps.toFixed(2)}\nTotal: $${total.toFixed(2)}`, 'info');
  });

  // Quick Summary
  const summaryCalculateBtn = document.getElementById('summary-calculate');
  const summaryResult = document.getElementById('summary-result');

  summaryCalculateBtn?.addEventListener('click', () => {
    const subtotal = parseFloat((document.getElementById('summary-base') as HTMLInputElement).value);

    if (isNaN(subtotal) || subtotal < 0) {
      showResult(summaryResult, 'Please enter a valid amount', 'error');
      return;
    }

    const iva = subtotal * 0.16;
    const total = subtotal + iva;

    showResult(summaryResult, `Subtotal: $${subtotal.toFixed(2)}\nIVA (16%): $${iva.toFixed(2)}\n━━━━━━━━━━━━━━━━\nTotal: $${total.toFixed(2)}`, 'info');
  });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initValidators();
  initCatalogs();
  initCalculators();
});
