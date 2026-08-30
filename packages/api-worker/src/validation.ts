import { ApiError } from './errors';

export async function parseJsonObject(request: Request): Promise<Record<string, unknown>> {
  let parsed: unknown;
  try {
    parsed = JSON.parse(await request.text());
  } catch {
    throw new ApiError(400, 'invalid_request', 'Malformed JSON body');
  }

  if (!isRecord(parsed)) {
    throw new ApiError(400, 'invalid_request', 'JSON body must be an object');
  }
  return parsed;
}

export function requireString(body: Record<string, unknown>, field: string): string {
  if (!(field in body)) {
    throw new ApiError(400, 'invalid_request', `${field} is required`);
  }
  if (typeof body[field] !== 'string') {
    throw new ApiError(400, 'invalid_request', `${field} must be a string`);
  }
  return body[field];
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
