/**
 * CFDI validation and cadena original generation
 */

export interface XsdValidationResult {
  valid: boolean;
  errors: string[];
}

export interface CadenaOriginalResult {
  cadena: string;
}

export async function generateCadenaOriginal(
  xml: string,
  xslt: string
): Promise<CadenaOriginalResult> {
  if (typeof window !== 'undefined' && typeof DOMParser !== 'undefined') {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xml, 'application/xml');
    const xsltDoc = parser.parseFromString(xslt, 'application/xml');
    const processor = new XSLTProcessor();
    processor.importStylesheet(xsltDoc);
    const result = processor.transformToDocument(xmlDoc);
    const cadena = result.documentElement?.textContent?.trim() ?? '';
    return { cadena };
  }

  // Node.js fallback using xslt-processor

  const xsltProcessor = require('xslt-processor');
  const { xmlParse, xsltProcess } = xsltProcessor;
  const xmlDoc = xmlParse(xml);
  const xsltDoc = xmlParse(xslt);
  const cadena = xsltProcess(xmlDoc, xsltDoc);
  return { cadena: String(cadena).trim() };
}

export async function validateCfdiXsd(xml: string, xsd: string): Promise<XsdValidationResult> {
  if (typeof window !== 'undefined') {
    throw new Error('XSD validation is only supported in Node.js');
  }

  let libxml: any;
  try {
    libxml = require('libxmljs2');
  } catch (error: any) {
    const message = error?.message?.includes('Cannot find module')
      ? 'libxmljs2 is not installed. Install optional dependency libxmljs2 for XSD validation.'
      : String(error?.message || error);
    throw new Error(message);
  }
  const xmlDoc = libxml.parseXml(xml);
  const xsdDoc = libxml.parseXml(xsd);
  const valid = xmlDoc.validate(xsdDoc);
  const errors = (xmlDoc.validationErrors || []).map((err: { message: string }) =>
    String(err.message).trim()
  );
  return { valid, errors };
}
