/**
 * CFDI signing helpers (sello)
 */

export interface SelloResult {
  sello: string;
}

export function signCadenaOriginal(cadena: string, privateKeyPem: string): SelloResult {
  if (typeof window !== 'undefined') {
    throw new Error('Signing is only supported in Node.js');
  }

  const crypto = require('crypto');
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(cadena);
  sign.end();
  const sello = sign.sign(privateKeyPem, 'base64');
  return { sello };
}

export interface AplicarSelloParams {
  xml: string;
  sello: string;
  certificado?: string;
  noCertificado?: string;
}

export function aplicarSelloAComprobante(params: AplicarSelloParams): string {
  const { xml, sello, certificado, noCertificado } = params;

  const comprobanteOpen = /<cfdi:Comprobante\b([^>]*)>/;
  const match = xml.match(comprobanteOpen);
  if (!match) {
    throw new Error('No se encontró el nodo cfdi:Comprobante');
  }

  let attrs = match[1];
  const setAttr = (name: string, value?: string) => {
    if (value === undefined || value === null) return;
    const re = new RegExp(`${name}="[^"]*"`);
    if (re.test(attrs)) {
      attrs = attrs.replace(re, `${name}="${value}"`);
    } else {
      attrs = `${attrs} ${name}="${value}"`;
    }
  };

  setAttr('Sello', sello);
  setAttr('Certificado', certificado);
  setAttr('NoCertificado', noCertificado);

  return xml.replace(comprobanteOpen, `<cfdi:Comprobante${attrs}>`);
}
