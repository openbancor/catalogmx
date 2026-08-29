import { fetch as workerFetch } from '../src/index';

describe('CatalogMX API Worker routing', () => {
  test('rejects a protected validation request without an API key', async () => {
    const response = await workerFetch(
      new Request('https://api.example.test/api/v1/validate/rfc', { method: 'POST' }),
      {}
    );

    expect(response.status).toBe(401);
    expect(response.headers.get('content-type')).toBe('application/json');
    expect(response.headers.get('cache-control')).toBe('no-store');
    expect(await response.json()).toEqual({
      error: { code: 'unauthorized', message: 'API key is required' },
    });
  });
});
