import { authenticateRequest } from '../src/auth';
import { ApiError } from '../src/errors';
import { enforceRateLimit, MemoryRateLimiter } from '../src/rate-limit';
import type { Env } from '../src/types';

const request = (apiKey?: string): Request =>
  new Request('https://api.example.test/api/v1/validate/rfc', {
    method: 'POST',
    headers: apiKey ? { 'X-API-Key': apiKey } : undefined,
  });

const env = (overrides: Partial<Env> = {}): Env => ({
  CATALOGMX_API_KEYS: JSON.stringify([
    {
      id: 'primary',
      active: true,
      digest: '4c806362b613f7496abf284146efd31da90e4b16169fe001841ca17290f427c4',
    },
  ]),
  API_RATE_LIMITER: new MemoryRateLimiter(),
  ...overrides,
});

describe('API key authentication', () => {
  test('rejects a missing API key with 401', async () => {
    await expect(authenticateRequest(request(), env())).rejects.toMatchObject(
      new ApiError(401, 'unauthorized', 'API key is required')
    );
  });

  test('rejects an unknown API key with 401 without echoing it', async () => {
    const rawKey = 'never-echo-this-key';

    await expect(authenticateRequest(request(rawKey), env())).rejects.toMatchObject({
      status: 401,
      code: 'unauthorized',
    });
    await expect(authenticateRequest(request(rawKey), env())).rejects.not.toMatchObject({
      message: expect.stringContaining(rawKey),
    });
  });

  test('accepts two active digests during zero-downtime rotation', async () => {
    const result = await authenticateRequest(
      request('rotated-key'),
      env({
        CATALOGMX_API_KEYS: JSON.stringify([
          {
            id: 'primary',
            active: true,
            digest: '4c806362b613f7496abf284146efd31da90e4b16169fe001841ca17290f427c4',
          },
          {
            id: 'rotated',
            active: true,
            digest: '5be3b05a2339aecdb0c543afefc6a563085f5861e6c109dce236363b3319566e',
          },
        ]),
      })
    );

    expect(result).toEqual({ keyId: 'rotated' });
  });

  test('rejects an inactive digest', async () => {
    await expect(
      authenticateRequest(
        request('inactive-key'),
        env({
          CATALOGMX_API_KEYS: JSON.stringify([
            {
              id: 'inactive',
              active: false,
              digest: '98ee7df095bb2746407197a0946abd1ce9d82be9e1f9f800663129c918631316',
            },
          ]),
        })
      )
    ).rejects.toMatchObject({ status: 401, code: 'unauthorized' });
  });

  test.each([undefined, 'not-json'])('fails closed for a bad key secret: %s', async (secret) => {
    await expect(
      authenticateRequest(request('test-api-key'), env({ CATALOGMX_API_KEYS: secret }))
    ).rejects.toMatchObject({ status: 503, code: 'configuration_error' });
  });
});

describe('API rate limiting', () => {
  test('passes only the authenticated key id to the limiter', async () => {
    const keys: string[] = [];
    const limiter = {
      limit: async ({ key }: { key: string }) => (keys.push(key), { success: true }),
    };

    await enforceRateLimit({ API_RATE_LIMITER: limiter }, 'primary');

    expect(keys).toEqual(['primary']);
  });

  test('returns 429 with Retry-After when the limiter denies the key', async () => {
    await expect(
      enforceRateLimit(
        {
          API_RATE_LIMITER: { limit: async () => ({ success: false }) },
        },
        'primary'
      )
    ).rejects.toMatchObject({
      status: 429,
      code: 'rate_limited',
      headers: { 'Retry-After': '60' },
    });
  });

  test('fails closed when the limiter binding is absent', async () => {
    await expect(enforceRateLimit({}, 'primary')).rejects.toMatchObject({
      status: 503,
      code: 'configuration_error',
    });
  });
});
