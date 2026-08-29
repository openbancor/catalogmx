export type ApiErrorCode =
  | 'bad_request'
  | 'unauthorized'
  | 'not_found'
  | 'method_not_allowed'
  | 'rate_limited'
  | 'unsupported_fiscal_data'
  | 'configuration_error'
  | 'internal_error';

export class ApiError extends Error {
  readonly status: number;
  readonly code: ApiErrorCode;
  readonly headers: Record<string, string>;

  constructor(
    status: number,
    code: ApiErrorCode,
    message: string,
    headers: Record<string, string> = {}
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.headers = headers;
  }
}

export function jsonResponse(
  payload: unknown,
  status = 200,
  headers: Record<string, string> = {}
): Response {
  const responseHeaders: Record<string, string> = {
    'Cache-Control': 'no-store',
    'Content-Type': 'application/json',
    ...headers,
  };
  return new Response(JSON.stringify(payload), { status, headers: responseHeaders });
}

export function errorResponse(error: ApiError): Response {
  return jsonResponse(
    { error: { code: error.code, message: error.message } },
    error.status,
    error.headers
  );
}
