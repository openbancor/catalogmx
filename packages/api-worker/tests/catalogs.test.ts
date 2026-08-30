import { handleCatalogRequest } from '../src/catalogs';
import { authorizedEnv, RecordingD1 } from './helpers';

const catalogRequest = (path: string): Request =>
  new Request(`https://api.example.test${path}`, { method: 'GET' });

async function bodyOf(response: Response): Promise<Record<string, unknown>> {
  return (await response.json()) as Record<string, unknown>;
}

describe('small catalog endpoints', () => {
  test('requires the current fiscal vigencia for SAT Nómina', async () => {
    const missing = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sat/nomina/tipo-nomina'),
      authorizedEnv()
    );
    const old = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sat/nomina/tipo-nomina?vigencia=2025'),
      authorizedEnv()
    );

    expect(missing.status).toBe(400);
    expect(old.status).toBe(422);
  });

  test('returns a versioned SAT Nómina catalog for vigencia 2026', async () => {
    const response = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sat/nomina/tipo-nomina?vigencia=2026'),
      authorizedEnv()
    );
    const body = await bodyOf(response);

    expect(response.status).toBe(200);
    expect(response.headers.get('X-Catalog-Version')).toBe('2026-01-05');
    expect(body).toMatchObject({ metadata: { vigencia: 2026 } });
    // Catalog data is authoritative: assert shape, versioning and the two
    // SAT-defined codes exist, without hardcoding the full list.
    const items = body.items as Array<{ code: string; descripcion: string }>;
    expect(items.length).toBeGreaterThanOrEqual(2);
    expect(items.map((item) => item.code)).toEqual(expect.arrayContaining(['O', 'E']));
    for (const item of items) {
      expect(typeof item.code).toBe('string');
      expect(typeof item.descripcion).toBe('string');
    }
  });

  test.each([
    'banco',
    'periodicidad-pago',
    'riesgo-puesto',
    'tipo-contrato',
    'tipo-jornada',
    'tipo-nomina',
    'tipo-regimen',
  ])('serves the allowlisted SAT Nómina catalog %s', async (catalogo) => {
    const response = await handleCatalogRequest(
      catalogRequest(`/api/v1/catalogs/sat/nomina/${catalogo}?vigencia=2026`),
      authorizedEnv()
    );

    expect(response.status).toBe(200);
    expect(Array.isArray((await bodyOf(response)).items)).toBe(true);
  });

  test('serves a small SAT CFDI c_* catalog', async () => {
    const response = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sat/cfdi/forma-pago'),
      authorizedEnv()
    );

    expect(response.status).toBe(200);
    expect((await bodyOf(response)).items).toEqual(
      expect.arrayContaining([{ valor: '03', descripcion: 'Transferencia electrónica de fondos' }])
    );
  });

  test('serves the normalized SAT CFDI tasa-o-cuota catalog', async () => {
    const response = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sat/cfdi/tasa-o-cuota'),
      authorizedEnv()
    );

    expect(response.status).toBe(200);
    expect(Array.isArray((await bodyOf(response)).items)).toBe(true);
  });

  test('serves INEGI states and municipalities with a version header', async () => {
    const states = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/inegi/estados'),
      authorizedEnv()
    );
    const municipalities = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/inegi/municipios'),
      authorizedEnv()
    );

    expect(states.status).toBe(200);
    expect((await bodyOf(states)).items).toHaveLength(33);
    expect(municipalities.status).toBe(200);
    expect((await bodyOf(municipalities)).items).toHaveLength(50);
    expect(states.headers.get('X-Catalog-Version')).toBe('2026-01-05');
  });

  test('rejects unsupported catalog names with 404', async () => {
    const response = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sat/nomina/not-allowed?vigencia=2026'),
      authorizedEnv()
    );

    expect(response.status).toBe(404);
  });

  test.each(['/api/v1/catalogs/sat/nomina/', '/api/v1/catalogs/unknown/catalog'])(
    'returns 404 for an unknown catalog route: %s',
    async (path) => {
      const response = await handleCatalogRequest(catalogRequest(path), authorizedEnv());

      expect(response.status).toBe(404);
    }
  );
});

describe('large D1-backed catalogs', () => {
  test('looks up SEPOMEX by cp with a bound exact-match query', async () => {
    const database = new RecordingD1();
    database.rows = [{ cp: '06700', asentamiento: 'Roma Norte' }];
    const response = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sepomex/codigos-postales?cp=06700'),
      { ...authorizedEnv(), CATALOG_DB: database }
    );

    expect(response.status).toBe(200);
    expect((await bodyOf(response)).items).toEqual(database.rows);
    expect(database.queries).toHaveLength(1);
    expect(database.queries[0].sql).toContain('WHERE cp = ?');
    expect(database.queries[0].sql).toContain('ORDER BY cp, asentamiento');
    expect(database.queries[0].values).toEqual(['06700', 100, 0]);
  });

  test('supports bounded SEPOMEX FTS diagnostics and caps page size at 100', async () => {
    const database = new RecordingD1();
    const response = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sepomex/codigos-postales?cp=06700&q=roma&limit=100&page=2'),
      { ...authorizedEnv(), CATALOG_DB: database }
    );
    const tooLarge = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sepomex/codigos-postales?cp=06700&limit=101'),
      { ...authorizedEnv(), CATALOG_DB: database }
    );

    expect(response.status).toBe(200);
    expect(database.queries[0].sql).toContain('MATCH ?');
    expect(database.queries[0].values).toEqual(['"roma"', '06700', 100, 100]);
    expect(tooLarge.status).toBe(400);
  });

  test.each([
    '/api/v1/catalogs/sepomex/codigos-postales?cp=06700',
    '/api/v1/catalogs/sat/cfdi/clave-prod-serv?clave=10101501',
  ])('fails closed when D1 is unavailable for %s', async (path) => {
    const response = await handleCatalogRequest(catalogRequest(path), authorizedEnv());

    expect(response.status).toBe(503);
  });

  test('looks up clave-prod-serv by exact key with a bound query', async () => {
    const database = new RecordingD1();
    database.rows = [{ clave: '10101501', descripcion: 'Gatos vivos' }];
    const response = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sat/cfdi/clave-prod-serv?clave=10101501'),
      { ...authorizedEnv(), CATALOG_DB: database }
    );

    expect(response.status).toBe(200);
    expect((await bodyOf(response)).items).toEqual(database.rows);
    expect(database.queries[0].sql).toContain('WHERE clave = ?');
    expect(database.queries[0].values).toEqual(['10101501', 100, 0]);
  });

  test('looks up clave-prod-serv by FTS query and rejects missing selectors', async () => {
    const database = new RecordingD1();
    const response = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sat/cfdi/clave-prod-serv?q=gatos&limit=2'),
      { ...authorizedEnv(), CATALOG_DB: database }
    );
    const missing = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sat/cfdi/clave-prod-serv'),
      { ...authorizedEnv(), CATALOG_DB: database }
    );

    expect(response.status).toBe(200);
    expect(database.queries[0].sql).toContain('WHERE fts MATCH ?');
    expect(database.queries[0].values).toEqual(['"gatos"', 2, 0]);
    expect(missing.status).toBe(400);
  });

  test('returns 503 instead of an empty successful catalog when D1 is absent', async () => {
    const response = await handleCatalogRequest(
      catalogRequest('/api/v1/catalogs/sepomex/codigos-postales?cp=06700'),
      authorizedEnv()
    );

    expect(response.status).toBe(503);
  });

  test.each([
    '/api/v1/catalogs/sepomex/codigos-postales?cp=bad',
    '/api/v1/catalogs/sepomex/codigos-postales?cp=06700&q=',
    `/api/v1/catalogs/sepomex/codigos-postales?cp=06700&q=${'x'.repeat(101)}`,
    '/api/v1/catalogs/sat/cfdi/clave-prod-serv?clave=bad',
    '/api/v1/catalogs/sat/cfdi/clave-prod-serv?q=',
    `/api/v1/catalogs/sat/cfdi/clave-prod-serv?q=${'x'.repeat(101)}`,
  ])('rejects an invalid large-catalog selector: %s', async (path) => {
    const response = await handleCatalogRequest(catalogRequest(path), {
      ...authorizedEnv(),
      CATALOG_DB: new RecordingD1(),
    });

    expect(response.status).toBe(400);
  });
});
