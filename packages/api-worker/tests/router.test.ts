import { fetch as workerFetch } from '../src/index';
import { TEST_API_KEY, authorizedEnv, RecordingD1 } from './helpers';

const request = (path: string, init: RequestInit = {}): Request => {
  const headers = new Headers(init.headers);
  headers.set('X-API-Key', TEST_API_KEY);
  return new Request(`https://api.example.test${path}`, { ...init, headers });
};

async function bodyOf(response: Response): Promise<Record<string, unknown>> {
  return (await response.json()) as Record<string, unknown>;
}

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

  test('authenticates before parsing a request body', async () => {
    const response = await workerFetch(
      new Request('https://api.example.test/api/v1/calc/isr', {
        method: 'POST',
        body: 'not-json',
      }),
      {}
    );

    expect(response.status).toBe(401);
  });

  test('rejects an unsupported method with its Allow header', async () => {
    const response = await workerFetch(
      new Request('https://api.example.test/api/v1/validate/rfc', { method: 'GET' }),
      {}
    );

    expect(response.status).toBe(405);
    expect(response.headers.get('Allow')).toBe('POST');
  });

  test('rejects an unknown route with 404', async () => {
    const response = await workerFetch(
      new Request('https://api.example.test/api/v1/not-a-route', { method: 'GET' }),
      {}
    );

    expect(response.status).toBe(404);
  });

  test('routes a valid RFC request through authentication and validation', async () => {
    const response = await workerFetch(
      request('/api/v1/validate/rfc', {
        method: 'POST',
        body: JSON.stringify({ value: ' bacl891217nj5 ' }),
      }),
      authorizedEnv()
    );

    expect(response.status).toBe(200);
    expect(await bodyOf(response)).toMatchObject({ value: 'BACL891217NJ5', valid: true });
  });

  test('returns invalid JSON as 400 after authentication', async () => {
    const response = await workerFetch(
      request('/api/v1/validate/rfc', { method: 'POST', body: 'not-json' }),
      authorizedEnv()
    );

    expect(response.status).toBe(400);
  });

  test('fails closed for pending ISR data while routing catalog endpoints', async () => {
    const database = new RecordingD1();
    const isr = await workerFetch(
      request('/api/v1/calc/isr', {
        method: 'POST',
        body: JSON.stringify({ base_gravable: 15000, periodo: 'mensual', ejercicio: 2026 }),
      }),
      { ...authorizedEnv(), CATALOG_DB: database }
    );
    const catalog = await workerFetch(
      request('/api/v1/catalogs/inegi/estados', { method: 'GET' }),
      { ...authorizedEnv(), CATALOG_DB: database }
    );

    expect(isr.status).toBe(422);
    expect(await bodyOf(isr)).toMatchObject({ error: { code: 'unsupported_fiscal_data' } });
    expect(catalog.status).toBe(200);
  });

  test('routes the IMSS calculation endpoint', async () => {
    const response = await workerFetch(
      request('/api/v1/calc/imss', {
        method: 'POST',
        body: JSON.stringify({ sdi: 500, dias_cotizados: 30, ejercicio: 2026 }),
      }),
      authorizedEnv()
    );

    expect(response.status).toBe(200);
    expect(await bodyOf(response)).toMatchObject({ regla_aplicada: { clase_riesgo: 1 } });
  });

  test('converts unexpected failures to a generic 500 response', async () => {
    const database = {
      prepare: () => {
        throw new Error('private database details');
      },
    };
    const response = await workerFetch(
      request('/api/v1/catalogs/sepomex/codigos-postales?cp=06700', { method: 'GET' }),
      { ...authorizedEnv(), CATALOG_DB: database }
    );

    expect(response.status).toBe(500);
    expect(await response.text()).not.toContain('private database details');
  });

  test('serializes identical requests deterministically', async () => {
    const init = { method: 'POST', body: JSON.stringify({ value: 'BACL891217NJ5' }) };
    const first = await workerFetch(request('/api/v1/validate/rfc', init), authorizedEnv());
    const second = await workerFetch(request('/api/v1/validate/rfc', init), authorizedEnv());

    expect(await first.text()).toBe(await second.text());
  });
});
