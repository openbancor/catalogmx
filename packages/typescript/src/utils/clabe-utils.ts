/**
 * CLABE Utilities - Enhanced CLABE generation, decoding, and validation
 *
 * This module provides comprehensive CLABE (Clave Bancaria Estandarizada) utilities
 * including generation with optional parameters, decoding with full bank/plaza info,
 * and example generation.
 *
 * @example
 * ```ts
 * import { decodeClabe, generateClabeRandom } from 'catalogmx';
 *
 * // Generate a random CLABE for BBVA in CDMX
 * const clabe = generateClabeRandom({ bankCode: '012', plazaCode: '180' });
 *
 * // Decode a CLABE to get full info
 * const info = decodeClabe('002010077777777771');
 * console.log(info?.bank?.name); // 'BANAMEX'
 * ```
 */

import { generateClabe, validateClabe } from '../validators/clabe';
import { BankCatalog } from '../catalogs/banxico/banks';
import { CodigosPlazaCatalog, type CodigoPlaza } from '../catalogs/banxico/codigos-plaza';
import type { Bank } from '../types';

/**
 * Bank information for decoded CLABE
 */
export interface BankInfo {
  code: string;
  name: string;
  fullName?: string;
  rfc?: string;
  spei: boolean;
}

/**
 * Plaza information for decoded CLABE
 */
export interface PlazaInfo {
  codigo: string;
  plaza: string;
  estado: string;
  cveEntidad: string;
}

/**
 * Full decoded CLABE information
 */
export interface DecodedCLABE {
  clabe: string;
  isValid: boolean;
  bankCode: string;
  plazaCode: string;
  accountNumber: string;
  checkDigit: string;
  bank: BankInfo | null;
  plaza: PlazaInfo | null;
  allPlazas: PlazaInfo[];
}

/**
 * Options for generating random CLABE
 */
export interface GenerateClabeOptions {
  bankCode?: string;
  plazaCode?: string;
  accountNumber?: string;
}

/**
 * Decode a CLABE to extract all information including bank and plaza details.
 *
 * @param clabe - 18-digit CLABE number
 * @returns Decoded CLABE info or null if format is invalid
 *
 * @example
 * ```ts
 * const info = decodeClabe('002010077777777771');
 * console.log(info?.isValid); // true
 * console.log(info?.bank?.name); // 'BANAMEX'
 * console.log(info?.bank?.fullName); // 'Banco Nacional de México, S.A.'
 *
 * // Get plaza info
 * const info2 = decodeClabe('012180000000000001');
 * console.log(info2?.plaza?.plaza); // 'Ciudad de México'
 * ```
 */
export function decodeClabe(clabe: string): DecodedCLABE | null {
  const trimmed = clabe?.trim() ?? '';

  if (trimmed.length !== 18 || !/^\d+$/.test(trimmed)) {
    return null;
  }

  const bankCode = trimmed.slice(0, 3);
  const plazaCode = trimmed.slice(3, 6);
  const accountNumber = trimmed.slice(6, 17);
  const checkDigit = trimmed[17];

  // Get bank info
  const bankData = BankCatalog.getBankByCode(bankCode);
  let bankInfo: BankInfo | null = null;
  if (bankData) {
    bankInfo = {
      code: bankData.code,
      name: bankData.name,
      fullName: bankData.full_name,
      rfc: bankData.rfc,
      spei: bankData.spei,
    };
  }

  // Get plaza info (may have multiple matches)
  const allPlazasRaw = CodigosPlazaCatalog.buscarPorCodigo(plazaCode);
  const allPlazas: PlazaInfo[] = allPlazasRaw.map((p) => ({
    codigo: p.codigo,
    plaza: p.plaza,
    estado: p.estado,
    cveEntidad: p.cve_entidad,
  }));

  const plazaInfo = allPlazas.length > 0 ? allPlazas[0] : null;

  return {
    clabe: trimmed,
    isValid: validateClabe(trimmed),
    bankCode,
    plazaCode,
    accountNumber,
    checkDigit,
    bank: bankInfo,
    plaza: plazaInfo,
    allPlazas,
  };
}

/**
 * Generate a valid CLABE with optional parameters.
 * Any parameter not provided will be randomly generated.
 *
 * @param options - Optional parameters (bankCode, plazaCode, accountNumber)
 * @returns Valid 18-digit CLABE
 *
 * @example
 * ```ts
 * // Fully random CLABE
 * const clabe = generateClabeRandom();
 *
 * // CLABE for BBVA (code 012)
 * const clabe2 = generateClabeRandom({ bankCode: '012' });
 *
 * // CLABE for any bank in CDMX (plaza 180)
 * const clabe3 = generateClabeRandom({ plazaCode: '180' });
 *
 * // Fully specified
 * const clabe4 = generateClabeRandom({ bankCode: '012', plazaCode: '180', accountNumber: '12345678901' });
 * ```
 */
export function generateClabeRandom(options: GenerateClabeOptions = {}): string {
  let { bankCode, plazaCode, accountNumber } = options;

  // Get or generate bank code
  if (!bankCode) {
    const speiBanks = BankCatalog.getSPEIBanks();
    if (speiBanks.length > 0) {
      const randomIndex = Math.floor(Math.random() * speiBanks.length);
      bankCode = speiBanks[randomIndex].code;
    } else {
      bankCode = String(Math.floor(Math.random() * 999) + 1).padStart(3, '0');
    }
  }

  // Get or generate plaza code
  if (!plazaCode) {
    const allPlazas = CodigosPlazaCatalog.getAll();
    if (allPlazas.length > 0) {
      const randomIndex = Math.floor(Math.random() * allPlazas.length);
      plazaCode = allPlazas[randomIndex].codigo;
    } else {
      plazaCode = String(Math.floor(Math.random() * 999) + 1).padStart(3, '0');
    }
  }

  // Get or generate account number
  if (!accountNumber) {
    accountNumber = String(Math.floor(Math.random() * 99999999999) + 1).padStart(11, '0');
  }

  return generateClabe(bankCode, plazaCode, accountNumber);
}

/**
 * Generate example CLABEs with full decoded information.
 *
 * @param count - Number of examples to generate (default 5)
 * @returns Array of decoded CLABE objects
 *
 * @example
 * ```ts
 * const examples = generateClabeExamples(3);
 * examples.forEach(ex => {
 *   console.log(`${ex.bank?.name}: ${ex.clabe}`);
 * });
 * ```
 */
export function generateClabeExamples(count: number = 5): DecodedCLABE[] {
  const examples: DecodedCLABE[] = [];

  for (let i = 0; i < count; i++) {
    const clabe = generateClabeRandom();
    const decoded = decodeClabe(clabe);
    if (decoded) {
      examples.push(decoded);
    }
  }

  return examples;
}

/**
 * Generate a CLABE for a specific bank (by name).
 *
 * @param bankName - Bank name (case-insensitive)
 * @param plazaName - Optional plaza name (case-insensitive)
 * @returns Valid 18-digit CLABE or null if bank not found
 *
 * @example
 * ```ts
 * const clabe = generateClabeForBank('BBVA');
 * const info = decodeClabe(clabe!);
 * console.log(info?.bank?.name); // 'BBVA'
 *
 * const clabe2 = generateClabeForBank('Santander', 'Guadalajara');
 * ```
 */
export function generateClabeForBank(bankName: string, plazaName?: string): string | null {
  const bank = BankCatalog.getBankByName(bankName);
  if (!bank) {
    return null;
  }

  const options: GenerateClabeOptions = {
    bankCode: bank.code,
  };

  if (plazaName) {
    const plazas = CodigosPlazaCatalog.buscarPorPlaza(plazaName);
    if (plazas.length > 0) {
      options.plazaCode = plazas[0].codigo;
    }
  }

  return generateClabeRandom(options);
}

/**
 * Get list of common banks used for CLABE generation.
 */
export function getCommonBanks(): Bank[] {
  return BankCatalog.getSPEIBanks();
}

/**
 * Search plazas by name for autocomplete/suggestions.
 */
export function getPlazaSuggestions(query: string): CodigoPlaza[] {
  return CodigosPlazaCatalog.search(query);
}

/**
 * Format a CLABE with separators for readability.
 *
 * @param clabe - 18-digit CLABE
 * @param separator - Separator character (default '-')
 * @returns Formatted CLABE: XXX-XXX-XXXXXXXXXXX-X
 *
 * @example
 * ```ts
 * formatClabe('002010077777777771'); // '002-010-07777777777-1'
 * formatClabe('002010077777777771', ' '); // '002 010 07777777777 1'
 * ```
 */
export function formatClabe(clabe: string, separator: string = '-'): string {
  if (clabe.length !== 18) {
    return clabe;
  }
  return `${clabe.slice(0, 3)}${separator}${clabe.slice(3, 6)}${separator}${clabe.slice(6, 17)}${separator}${clabe[17]}`;
}

/**
 * Get a human-readable description of a CLABE.
 *
 * @param clabe - 18-digit CLABE
 * @returns Human-readable description
 *
 * @example
 * ```ts
 * console.log(describeClabe('002010077777777771'));
 * // CLABE: 002-010-07777777777-1
 * // Estado: Valida
 * // Banco: BANAMEX (Banco Nacional de Mexico, S.A.)
 * // Plaza: Aguascalientes, Aguascalientes
 * // Cuenta: 07777777777
 * ```
 */
export function describeClabe(clabe: string): string {
  const info = decodeClabe(clabe);
  if (!info) {
    return `CLABE invalida: ${clabe}`;
  }

  const lines: string[] = [
    `CLABE: ${formatClabe(clabe)}`,
    `Estado: ${info.isValid ? 'Valida' : 'Invalida'}`,
  ];

  if (info.bank) {
    let bankLine = `Banco: ${info.bank.name}`;
    if (info.bank.fullName) {
      bankLine += ` (${info.bank.fullName})`;
    }
    lines.push(bankLine);
  } else {
    lines.push(`Banco: Codigo ${info.bankCode} (no encontrado)`);
  }

  if (info.plaza) {
    lines.push(`Plaza: ${info.plaza.plaza}, ${info.plaza.estado}`);
    if (info.allPlazas.length > 1) {
      lines.push(`  (Nota: ${info.allPlazas.length} ubicaciones con este codigo)`);
    }
  } else {
    lines.push(`Plaza: Codigo ${info.plazaCode} (no encontrado)`);
  }

  lines.push(`Cuenta: ${info.accountNumber}`);

  return lines.join('\n');
}
