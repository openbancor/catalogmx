/**
 * Banxico (Banco de México) catalogs
 *
 * NOTE: Dynamic catalogs (UDI, tipo cambio, TIIE, CETES, inflación, salarios)
 * now use SQLite for auto-updating data. Old JSON-based versions are deprecated.
 */

export { BankCatalog } from './banks';
export { CodigosPlazaCatalog } from './codigos-plaza';
export { InstitucionesFinancieras } from './instituciones-financieras';
export { MonedasDivisas } from './monedas-divisas';

// SQLite-backed catalogs (auto-updating)
export { UDICatalog } from './udis-sqlite';
export { TipoCambioUSDCatalog } from './tipo-cambio-usd-sqlite';
export { TIIE28Catalog } from './tiie-28-sqlite';
export { CETES28Catalog } from './cetes-28-sqlite';
export { InflacionAnualCatalog } from './inflacion-anual-sqlite';
export { SalariosMinimosCatalog } from './salarios-minimos-sqlite';
