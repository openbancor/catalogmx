import { ApiError } from './errors';
import type { Env, RateLimiterBinding } from './types';

export async function enforceRateLimit(
  env: Pick<Env, 'API_RATE_LIMITER'>,
  keyId: string
): Promise<void> {
  const limiter = env.API_RATE_LIMITER;
  if (!limiter) {
    throw new ApiError(503, 'configuration_error', 'Rate limiting is not configured');
  }

  const result = await limiter.limit({ key: keyId });
  if (!result.success) {
    throw new ApiError(429, 'rate_limited', 'Rate limit exceeded', { 'Retry-After': '60' });
  }
}

export class MemoryRateLimiter implements RateLimiterBinding {
  private readonly deniedKeys: Set<string>;

  constructor(deniedKeys: Iterable<string> = []) {
    this.deniedKeys = new Set(deniedKeys);
  }

  async limit({ key }: { key: string }): Promise<{ success: boolean }> {
    return { success: !this.deniedKeys.has(key) };
  }
}
