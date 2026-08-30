import { handleRequest } from './router';
import type { Env } from './types';

export const fetch = (request: Request, env: Env): Promise<Response> => handleRequest(request, env);

export default { fetch };
