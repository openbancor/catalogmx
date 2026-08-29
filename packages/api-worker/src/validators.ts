import { BankCatalog } from '../../typescript/src/catalogs/banxico/banks';
import { getClabeInfo, validateClabe } from '../../typescript/src/validators/clabe';
import { validateCurp } from '../../typescript/src/validators/curp';
import { detectRfcType, validateRfc } from '../../typescript/src/validators/rfc';
import { validateNss } from '../../typescript/src/validators/nss';
import { ApiError } from './errors';
import { preloadSmallData } from './data';
import { requireString } from './validation';

export type ValidatorKind = 'rfc' | 'curp' | 'clabe' | 'nss';

export interface IdentifierValidationResponse {
  value: string;
  valid: boolean;
  tipo?: ReturnType<typeof detectRfcType>;
  details?: ReturnType<typeof getClabeInfo>;
  banco?: {
    code: string;
    name: string;
    full_name?: string;
    spei: boolean;
  };
}

export function validateIdentifier(
  kind: ValidatorKind,
  body: Record<string, unknown>
): IdentifierValidationResponse {
  preloadSmallData();
  const value = requireString(body, 'value').trim().toUpperCase();

  switch (kind) {
    case 'rfc':
      return { value, valid: validateRfc(value), tipo: detectRfcType(value) };
    case 'curp':
      return { value, valid: validateCurp(value) };
    case 'clabe':
      return validateClabeIdentifier(value);
    case 'nss':
      return { value, valid: validateNss(value) };
    default:
      throw new ApiError(404, 'not_found', 'Validator route not found');
  }
}

function validateClabeIdentifier(value: string): IdentifierValidationResponse {
  const details = getClabeInfo(value);
  const valid = validateClabe(value);
  if (!details) return { value, valid };

  const bank = BankCatalog.getBankByCode(details.bankCode);
  return {
    value,
    valid,
    details,
    ...(bank
      ? {
          banco: {
            code: bank.code,
            name: bank.name,
            full_name: bank.full_name,
            spei: bank.spei,
          },
        }
      : {}),
  };
}
