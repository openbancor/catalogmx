export const TEST_API_KEY = 'test-api-key';
export const TEST_API_KEY_DIGEST =
  '4c806362b613f7496abf284146efd31da90e4b16169fe001841ca17290f427c4';

export function authorizedEnv(): Record<string, unknown> {
  return {
    CATALOGMX_API_KEYS: JSON.stringify([
      { id: 'test-client', active: true, digest: TEST_API_KEY_DIGEST },
    ]),
    API_RATE_LIMITER: {
      limit: async () => ({ success: true }),
    },
  };
}
