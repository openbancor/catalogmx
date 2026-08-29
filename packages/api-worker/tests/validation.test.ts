import { parseJsonObject, requireString } from '../src/validation';

describe('API request body validation', () => {
  test('parses a JSON object', async () => {
    const body = await parseJsonObject(
      new Request('https://api.example.test', {
        method: 'POST',
        body: JSON.stringify({ value: 'abc' }),
      })
    );

    expect(body).toEqual({ value: 'abc' });
  });

  test.each(['not-json', JSON.stringify([]), JSON.stringify(null)])(
    'rejects malformed or non-object JSON: %s',
    async (body) => {
      await expect(
        parseJsonObject(new Request('https://api.example.test', { method: 'POST', body }))
      ).rejects.toMatchObject({ status: 400, code: 'invalid_request' });
    }
  );

  test('requires a string field but permits an empty string for validator semantics', () => {
    expect(requireString({ value: '' }, 'value')).toBe('');
    expect(() => requireString({}, 'value')).toThrow('value is required');
    expect(() => requireString({ value: 123 }, 'value')).toThrow('value must be a string');
  });
});
