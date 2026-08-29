import { loadCatalogRows } from '../../typescript/src/utils/catalog-backend';
import { ApiError, errorResponse, jsonResponse } from './errors';
import {
  CATALOG_VERSION,
  CURRENT_FISCAL_VALIDITY,
  SAT_CFDI_CATALOGS,
  SAT_NOMINA_CATALOGS,
  preloadSmallData,
} from './data';
import { queryPostalCodes, queryProductServices, type Pagination } from './d1';
import type { D1Database, Env } from './types';

const MAX_PAGE_SIZE = 100;

export async function handleCatalogRequest(request: Request, env: Env): Promise<Response> {
  try {
    preloadSmallData();
    const url = new URL(request.url);
    const path = url.pathname;

    if (path.startsWith('/api/v1/catalogs/sat/nomina/')) {
      return handleNomina(url.pathname, url.searchParams);
    }
    if (path.startsWith('/api/v1/catalogs/sat/cfdi/')) {
      return await handleCfdi(url, env.CATALOG_DB);
    }
    if (path === '/api/v1/catalogs/inegi/estados') {
      return smallCatalog('inegi/states.json');
    }
    if (path === '/api/v1/catalogs/inegi/municipios') {
      return smallCatalog('inegi/municipios.json');
    }
    if (path === '/api/v1/catalogs/sepomex/codigos-postales') {
      return await handlePostalCodes(url, env.CATALOG_DB);
    }

    throw new ApiError(404, 'not_found', 'Catalog route not found');
  } catch (error) {
    if (error instanceof ApiError) return errorResponse(error);
    throw error;
  }
}

function handleNomina(path: string, searchParams: URLSearchParams): Response {
  const catalogo = path.slice('/api/v1/catalogs/sat/nomina/'.length);
  const source = SAT_NOMINA_CATALOGS[catalogo];
  if (!source) throw new ApiError(404, 'not_found', 'SAT Nómina catalog not found');

  const vigencia = searchParams.get('vigencia');
  if (!vigencia) {
    throw new ApiError(400, 'invalid_request', 'vigencia is required');
  }
  if (vigencia !== String(CURRENT_FISCAL_VALIDITY)) {
    throw new ApiError(422, 'unsupported_fiscal_data', 'SAT Nómina vigencia is not available');
  }

  return smallCatalog(source.path, { vigencia: CURRENT_FISCAL_VALIDITY });
}

function handleCfdi(url: URL, database: D1Database | undefined): Response | Promise<Response> {
  const catalogo = url.pathname.slice('/api/v1/catalogs/sat/cfdi/'.length);
  if (catalogo === 'clave-prod-serv') {
    return handleProductServices(url, database);
  }

  const source = SAT_CFDI_CATALOGS[catalogo];
  if (!source) throw new ApiError(404, 'not_found', 'SAT CFDI catalog not found');
  return smallCatalog(source.path);
}

async function handlePostalCodes(url: URL, database: D1Database | undefined): Promise<Response> {
  const cp = url.searchParams.get('cp');
  if (!cp || !/^\d{5}$/.test(cp)) {
    throw new ApiError(400, 'invalid_request', 'cp must be a five-digit postal code');
  }
  if (!database) {
    throw new ApiError(503, 'configuration_error', 'Catalog database is not configured');
  }

  const query = url.searchParams.get('q');
  if (query !== null && (query.length < 1 || query.length > 100)) {
    throw new ApiError(400, 'invalid_request', 'q is outside the supported range');
  }
  const pagination = parsePagination(url.searchParams);
  const items = await queryPostalCodes(database, cp, query, pagination);
  return catalogResponse(items);
}

async function handleProductServices(
  url: URL,
  database: D1Database | undefined
): Promise<Response> {
  const clave = url.searchParams.get('clave');
  const query = url.searchParams.get('q');
  if ((clave && query) || (!clave && !query)) {
    throw new ApiError(400, 'invalid_request', 'Provide exactly one of clave or q');
  }
  if (clave && !/^\d{8}$/.test(clave)) {
    throw new ApiError(400, 'invalid_request', 'clave must contain eight digits');
  }
  if (query !== null && (query.length < 1 || query.length > 100)) {
    throw new ApiError(400, 'invalid_request', 'q is outside the supported range');
  }
  if (!database) {
    throw new ApiError(503, 'configuration_error', 'Catalog database is not configured');
  }

  const pagination = parsePagination(url.searchParams);
  const items = await queryProductServices(
    database,
    { clave: clave ?? undefined, query: query ?? undefined },
    pagination
  );
  return catalogResponse(items);
}

function smallCatalog(path: string, metadata?: Record<string, number>): Response {
  const items = loadCatalogRows<Record<string, unknown>>(path);
  return catalogResponse(items, metadata);
}

function catalogResponse(
  items: Record<string, unknown>[],
  metadata?: Record<string, number>
): Response {
  return jsonResponse(metadata ? { items, metadata } : { items }, 200, {
    'X-Catalog-Version': CATALOG_VERSION,
  });
}

function parsePagination(searchParams: URLSearchParams): Pagination {
  const limitValue = searchParams.get('limit');
  const pageValue = searchParams.get('page');
  const limit = limitValue === null ? MAX_PAGE_SIZE : Number(limitValue);
  const page = pageValue === null ? 1 : Number(pageValue);
  if (
    !Number.isInteger(limit) ||
    limit < 1 ||
    limit > MAX_PAGE_SIZE ||
    !Number.isInteger(page) ||
    page < 1 ||
    page > 1_000_000
  ) {
    throw new ApiError(400, 'invalid_request', 'Pagination is outside the supported range');
  }
  return { limit, offset: (page - 1) * limit };
}
