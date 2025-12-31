import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Normalize text by removing accents and converting to uppercase.
 * Makes text searchable without worrying about accents or case.
 *
 * @param text - Text to normalize
 * @returns Normalized text (uppercase, no accents)
 *
 * @example
 * normalizeText('México');  // 'MEXICO'
 * normalizeText('Las Águilas');  // 'LAS AGUILAS'
 * normalizeText('San José');  // 'SAN JOSE'
 */
export function normalizeText(text: string): string {
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase();
}
