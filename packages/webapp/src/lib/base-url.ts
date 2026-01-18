export const getBaseUrl = (): string => {
  const baseUrl = (import.meta as any).env?.BASE_URL || '/';
  return baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
};
