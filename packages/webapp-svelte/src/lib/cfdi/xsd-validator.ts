export interface XsdValidationResult {
  valid: boolean;
  errors: string[];
}

let libxmlPromise: Promise<any> | null = null;

async function getLibxml() {
  if (!libxmlPromise) {
    libxmlPromise = import('libxml2-wasm');
  }
  return libxmlPromise;
}

export async function validateXmlWithXsd(xml: string, xsd: string): Promise<XsdValidationResult> {
  const libxml = await getLibxml();
  const { XmlDocument, XsdValidator, XmlValidateError } = libxml;

  try {
    const xmlDoc = XmlDocument.fromString(xml);
    const xsdDoc = XmlDocument.fromString(xsd);
    const validator = XsdValidator.fromDoc(xsdDoc);
    validator.validate(xmlDoc);
    return { valid: true, errors: [] };
  } catch (err: any) {
    if (err instanceof XmlValidateError && Array.isArray(err.details)) {
      return {
        valid: false,
        errors: err.details.map((d: { message?: string }) => d.message || 'Invalid'),
      };
    }
    return { valid: false, errors: [String(err?.message || err)] };
  }
}
