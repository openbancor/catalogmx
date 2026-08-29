import { loadCatalogRows } from '../../../packages/typescript/src/utils/catalog-backend';
import { preloadSmallData } from '../src/data';
import { validateIdentifier } from '../src/validators';

beforeAll(() => {
  preloadSmallData();
});

describe('identifier validation adapters', () => {
  test.each([
    ['rfc', 'BACL891217NJ5'],
    ['curp', 'BACL891217HDFRSS09'],
    ['clabe', '002010077777777771'],
    ['nss', '23198900013'],
  ] as const)('validates a normalized %s identifier', (kind, value) => {
    const result = validateIdentifier(kind, { value: ` ${value.toLowerCase()} ` });

    expect(result.value).toBe(value);
    expect(result.valid).toBe(true);
  });

  test('returns false for an invalid but present identifier', () => {
    expect(validateIdentifier('rfc', { value: '' })).toEqual({
      value: '',
      valid: false,
      tipo: 'invalido',
    });
  });

  test('includes RFC type', () => {
    expect(validateIdentifier('rfc', { value: 'XAXX010101000' })).toMatchObject({
      valid: true,
      tipo: 'generico',
    });
  });

  test('includes CLABE details and a non-personal bank catalog object', () => {
    expect(validateIdentifier('clabe', { value: '002010077777777771' })).toMatchObject({
      valid: true,
      details: {
        bankCode: '002',
        accountNumber: '07777777777',
      },
      banco: {
        code: '002',
        name: 'BANAMEX',
        full_name: 'Banco Nacional de México, S.A.',
        spei: true,
      },
    });
  });

  test('preloads small data through the existing CatalogMX loader seam', () => {
    expect(loadCatalogRows('inegi/states.json')).toHaveLength(33);
    expect(loadCatalogRows('sat/nomina_1.2/tipo_nomina.json')).toHaveLength(2);
    expect(loadCatalogRows('sat/cfdi_4.0/c_FormaPago.json')).toHaveLength(22);
  });
});
