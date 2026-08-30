import type { D1Database } from './types';

export interface Pagination {
  limit: number;
  offset: number;
}

export async function queryPostalCodes(
  database: D1Database,
  cp: string,
  query: string | null,
  pagination: Pagination
): Promise<Record<string, unknown>[]> {
  if (query) {
    const statement = database
      .prepare(
        `SELECT codigos_postales.*
         FROM codigos_postales_fts
         JOIN codigos_postales ON codigos_postales.rowid = codigos_postales_fts.rowid
         WHERE codigos_postales_fts MATCH ? AND codigos_postales.cp = ?
         ORDER BY codigos_postales.cp, codigos_postales.asentamiento
         LIMIT ? OFFSET ?`
      )
      .bind(toFtsQuery(query), cp, pagination.limit, pagination.offset);
    return (await statement.all<Record<string, unknown>>()).results;
  }

  const statement = database
    .prepare(
      `SELECT cp, asentamiento, tipo_asentamiento, municipio, estado, ciudad,
              cp_oficina, codigo_estado, codigo_municipio, zona
       FROM codigos_postales
       WHERE cp = ?
       ORDER BY cp, asentamiento
       LIMIT ? OFFSET ?`
    )
    .bind(cp, pagination.limit, pagination.offset);
  return (await statement.all<Record<string, unknown>>()).results;
}

export async function queryProductServices(
  database: D1Database,
  selector: { clave?: string; query?: string },
  pagination: Pagination
): Promise<Record<string, unknown>[]> {
  if (selector.clave) {
    const statement = database
      .prepare(
        `SELECT clave, descripcion, incluye_iva, incluye_ieps, complemento,
                fecha_inicio_vigencia, fecha_fin_vigencia, palabras_similares,
                estimulo_franja_fronteriza
         FROM clave_prod_serv
         WHERE clave = ?
         ORDER BY clave
         LIMIT ? OFFSET ?`
      )
      .bind(selector.clave, pagination.limit, pagination.offset);
    return (await statement.all<Record<string, unknown>>()).results;
  }

  const statement = database
    .prepare(
      `SELECT cps.clave, cps.descripcion, cps.incluye_iva, cps.incluye_ieps,
              cps.complemento, cps.fecha_inicio_vigencia, cps.fecha_fin_vigencia,
              cps.palabras_similares, cps.estimulo_franja_fronteriza
       FROM clave_prod_serv_fts AS fts
       JOIN clave_prod_serv AS cps ON cps.rowid = fts.rowid
       WHERE clave_prod_serv_fts MATCH ?
       ORDER BY cps.clave
       LIMIT ? OFFSET ?`
    )
    .bind(toFtsQuery(selector.query ?? ''), pagination.limit, pagination.offset);
  return (await statement.all<Record<string, unknown>>()).results;
}

function toFtsQuery(value: string): string {
  return `"${value.replace(/"/g, '""')}"`;
}
