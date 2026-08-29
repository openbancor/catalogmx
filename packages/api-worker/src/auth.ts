import { ApiError } from './errors';
import type { AuthenticatedClient, Env } from './types';

interface ApiKeyRecord {
  id: string;
  active: boolean;
  digest: string;
}

export async function authenticateRequest(
  request: Request,
  env: Env
): Promise<AuthenticatedClient> {
  const rawKey = request.headers.get('X-API-Key')?.trim();
  if (!rawKey) {
    throw new ApiError(401, 'unauthorized', 'API key is required');
  }

  const records = parseKeyRecords(env.CATALOGMX_API_KEYS);
  const digest = new Uint8Array(
    await crypto.subtle.digest('SHA-256', new TextEncoder().encode(rawKey))
  );

  let matchedId: string | undefined;
  for (const record of records) {
    const matches = record.active && constantTimeEqual(digest, decodeHex(record.digest));
    if (matches && matchedId === undefined) {
      matchedId = record.id;
    }
  }

  if (!matchedId) {
    throw new ApiError(401, 'unauthorized', 'API key is invalid');
  }

  return { keyId: matchedId };
}

function parseKeyRecords(secret: string | undefined): ApiKeyRecord[] {
  if (!secret) {
    throw new ApiError(503, 'configuration_error', 'API key authentication is not configured');
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(secret);
  } catch {
    throw new ApiError(503, 'configuration_error', 'API key authentication is not configured');
  }

  if (!Array.isArray(parsed) || parsed.length === 0) {
    throw new ApiError(503, 'configuration_error', 'API key authentication is not configured');
  }

  return parsed.map((entry) => {
    if (
      !isRecord(entry) ||
      typeof entry.id !== 'string' ||
      !entry.id ||
      typeof entry.active !== 'boolean'
    ) {
      throw new ApiError(503, 'configuration_error', 'API key authentication is not configured');
    }
    if (typeof entry.digest !== 'string') {
      throw new ApiError(503, 'configuration_error', 'API key authentication is not configured');
    }
    const digest = entry.digest.toLowerCase();
    if (!/^[0-9a-f]{64}$/.test(digest)) {
      throw new ApiError(503, 'configuration_error', 'API key authentication is not configured');
    }
    return { id: entry.id, active: entry.active, digest };
  });
}

function decodeHex(value: string): Uint8Array {
  const bytes = new Uint8Array(value.length / 2);
  for (let index = 0; index < bytes.length; index += 1) {
    bytes[index] = Number.parseInt(value.slice(index * 2, index * 2 + 2), 16);
  }
  return bytes;
}

function constantTimeEqual(left: Uint8Array, right: Uint8Array): boolean {
  let difference = left.length ^ right.length;
  const length = Math.max(left.length, right.length);
  for (let index = 0; index < length; index += 1) {
    difference |= (left[index] ?? 0) ^ (right[index] ?? 0);
  }
  return difference === 0;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
