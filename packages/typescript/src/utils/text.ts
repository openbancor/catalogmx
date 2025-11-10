/**
 * Text normalization utilities for catalogmx
 *
 * Provides accent-insensitive text normalization for searching across catalogs.
 */

/**
 * Normalize text by removing accents and converting to uppercase.
 * Makes text searchable without worrying about accents or case.
 *
 * @param text - Text to normalize
 * @returns Normalized text (uppercase, no accents)
 *
 * @example
 * normalizeText('México');  // 'MEXICO'
 * normalizeText('San José');  // 'SAN JOSE'
 * normalizeText('Michoacán de Ocampo');  // 'MICHOACAN DE OCAMPO'
 */
export function normalizeText(text: string): string {
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase();
}

/**
 * Alias for normalizeText for clarity in search contexts.
 *
 * @param text - Text to normalize for searching
 * @returns Normalized text suitable for accent-insensitive search
 */
export function normalizeForSearch(text: string): string {
  return normalizeText(text);
}
