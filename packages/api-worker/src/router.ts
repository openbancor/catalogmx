import { authenticateRequest } from './auth';
import { handleCatalogRequest } from './catalogs';
import { calculateImss, calculateIsr } from './calculations';
import { ApiError, errorResponse, jsonResponse } from './errors';
import { enforceRateLimit } from './rate-limit';
import { parseJsonObject } from './validation';
import { validateIdentifier, type ValidatorKind } from './validators';
import type { Env } from './types';

interface Route {
  method: 'GET' | 'POST';
  kind: 'validator' | 'isr' | 'imss' | 'catalog';
  validator?: ValidatorKind;
}

export async function handleRequest(request: Request, env: Env): Promise<Response> {
  const route = resolveRoute(new URL(request.url).pathname);
  if (!route) {
    return errorResponse(new ApiError(404, 'not_found', 'Route not found'));
  }
  if (request.method !== route.method) {
    return errorResponse(
      new ApiError(405, 'method_not_allowed', 'Method not allowed', { Allow: route.method })
    );
  }

  try {
    const client = await authenticateRequest(request, env);
    await enforceRateLimit(env, client.keyId);

    if (route.kind === 'catalog') {
      return await handleCatalogRequest(request, env);
    }

    const body = await parseJsonObject(request);
    if (route.kind === 'validator') {
      return jsonResponse(validateIdentifier(route.validator!, body));
    }
    if (route.kind === 'isr') {
      return jsonResponse(calculateIsr(body));
    }
    return jsonResponse(calculateImss(body));
  } catch (error) {
    if (error instanceof ApiError) return errorResponse(error);
    return errorResponse(new ApiError(500, 'internal_error', 'Internal server error'));
  }
}

function resolveRoute(path: string): Route | undefined {
  const validatorRoutes: Record<string, ValidatorKind> = {
    '/api/v1/validate/rfc': 'rfc',
    '/api/v1/validate/curp': 'curp',
    '/api/v1/validate/clabe': 'clabe',
    '/api/v1/validate/nss': 'nss',
  };
  const validator = validatorRoutes[path];
  if (validator) return { method: 'POST', kind: 'validator', validator };
  if (path === '/api/v1/calc/isr') return { method: 'POST', kind: 'isr' };
  if (path === '/api/v1/calc/imss') return { method: 'POST', kind: 'imss' };
  if (path.startsWith('/api/v1/catalogs/')) return { method: 'GET', kind: 'catalog' };
  return undefined;
}
