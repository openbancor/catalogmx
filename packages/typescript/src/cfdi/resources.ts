/**
 * SAT CFDI resource helpers (XSD/XSLT paths)
 */

import { isNodeRuntime, resolveSharedDataPath } from '../utils/catalog-backend';

export function satUrlToLocalPath(url: string): string {
  const parsed = new URL(url);
  return `sat/xsd/resources/${parsed.host}${parsed.pathname}`;
}

export function getCfdiXsdPath(url: string): string {
  const relative = satUrlToLocalPath(url);
  return isNodeRuntime() ? resolveSharedDataPath(relative) : relative;
}

export function getCfdiXsltPath(url: string): string {
  const relative = satUrlToLocalPath(url);
  return isNodeRuntime() ? resolveSharedDataPath(relative) : relative;
}

export async function loadResourceText(pathOrUrl: string): Promise<string> {
  if (isNodeRuntime()) {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const fs = require('fs');
    return fs.readFileSync(pathOrUrl, 'utf-8') as string;
  }
  const response = await fetch(pathOrUrl);
  if (!response.ok) {
    throw new Error(`Failed to load resource: ${response.status} ${response.statusText}`);
  }
  return await response.text();
}
