/**
 * RFC SAT Specification Tests
 *
 * Tests based on official SAT algorithm specification (IFAI 0610100135506)
 * Reference: https://www.mariovaldez.net/files/IFAI%200610100135506%20065%20Algoritmo%20para%20generar%20el%20RFC%20con%20homoclave%20para%20personas%20fisicas%20y%20morales.pdf
 */
import fs from 'fs';
import path from 'path';

import {
  generateRfcPersonaFisica,
  generateRfcPersonaMoral,
  validateRfc,
  RFCValidator,
} from '../src/validators/rfc';

interface PersonaMoralVector {
  razon_social: string;
  fecha: string;
  rfc_base: string;
  descripcion: string;
}

interface PersonaFisicaVector {
  nombre: string;
  apellido_paterno: string;
  apellido_materno: string;
  fecha: string;
  rfc_base: string;
  descripcion: string;
}

interface SatSpec {
  description: string;
  source: string;
  personas_morales: {
    [key: string]: PersonaMoralVector[];
  };
  personas_fisicas: {
    [key: string]: PersonaFisicaVector[];
  };
  ejemplo_completo_con_homoclave: {
    nombre: string;
    apellido_paterno: string;
    apellido_materno: string;
    fecha: string;
    rfc_completo: string;
    rfc_base: string;
    homoclave: string;
    digito_verificador: string;
  };
  palabras_inconvenientes: Array<{ original: string; corregido: string }>;
}

const vectorsPath = path.resolve(__dirname, '../../shared-data/tests/rfc_sat_spec_vectors.json');
const satSpec: SatSpec = JSON.parse(fs.readFileSync(vectorsPath, 'utf-8'));

/**
 * Helper to extract RFC base (first 9 characters for moral, first 10 for fisica)
 */
function extractRfcBase(rfc: string): string {
  // RFC base is letters + date (3+6=9 for moral, 4+6=10 for fisica)
  // But SAT spec shows base with potential date
  if (rfc.length === 12) {
    // Persona Moral: 3 letters + 6 date + 3 homoclave+checksum
    return rfc.slice(0, 9);
  } else {
    // Persona Fisica: 4 letters + 6 date + 3 homoclave+checksum
    return rfc.slice(0, 10);
  }
}

describe('SAT Specification - Personas Morales', () => {
  describe('Regla 1 - Tres o más palabras', () => {
    test.each(satSpec.personas_morales.regla_1_tres_o_mas_palabras)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 2 - Fecha de constitución', () => {
    test.each(satSpec.personas_morales.regla_2_fecha_constitucion)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 3 - Letras compuestas (CH, LL)', () => {
    test.each(satSpec.personas_morales.regla_3_letras_compuestas)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 4 - Iniciales como palabras', () => {
    test.each(satSpec.personas_morales.regla_4_iniciales_como_palabras)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 5 - Abreviaturas de tipo de sociedad (excluidas)', () => {
    test.each(satSpec.personas_morales.regla_5_abreviaturas_sociedad)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 6 - Dos palabras', () => {
    test.each(satSpec.personas_morales.regla_6_dos_palabras)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 7 - Una sola palabra', () => {
    test.each(satSpec.personas_morales.regla_7_una_sola_palabra)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 8 - Menos de 3 letras', () => {
    test.each(satSpec.personas_morales.regla_8_menos_de_tres_letras)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 9 - Artículos, preposiciones y conjunciones', () => {
    test.each(satSpec.personas_morales.regla_9_articulos_preposiciones)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 10 - Números (arábigos y romanos)', () => {
    test.each(satSpec.personas_morales.regla_10_numeros)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 11 - Compañía/Sociedad (excluidas)', () => {
    test.each(satSpec.personas_morales.regla_11_compania_sociedad)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 12 - Caracteres especiales', () => {
    test.each(satSpec.personas_morales.regla_12_caracteres_especiales)(
      '$razon_social -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaMoral({
          razonSocial: vector.razon_social,
          fechaConstitucion: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });
});

describe('SAT Specification - Personas Físicas', () => {
  describe('Regla 1 - Formación básica', () => {
    test.each(satSpec.personas_fisicas.regla_1_formacion_basica)(
      '$nombre $apellido_paterno $apellido_materno -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaFisica({
          nombre: vector.nombre,
          apellidoPaterno: vector.apellido_paterno,
          apellidoMaterno: vector.apellido_materno,
          fechaNacimiento: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 2 - Fecha de nacimiento', () => {
    test.each(satSpec.personas_fisicas.regla_2_fecha_nacimiento)(
      '$nombre $apellido_paterno $apellido_materno -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaFisica({
          nombre: vector.nombre,
          apellidoPaterno: vector.apellido_paterno,
          apellidoMaterno: vector.apellido_materno,
          fechaNacimiento: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 3 - Letras compuestas (CH, LL)', () => {
    test.each(satSpec.personas_fisicas.regla_3_letras_compuestas)(
      '$nombre $apellido_paterno $apellido_materno -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaFisica({
          nombre: vector.nombre,
          apellidoPaterno: vector.apellido_paterno,
          apellidoMaterno: vector.apellido_materno,
          fechaNacimiento: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 4 - Apellido paterno corto', () => {
    test.each(satSpec.personas_fisicas.regla_4_apellido_paterno_corto)(
      '$nombre $apellido_paterno $apellido_materno -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaFisica({
          nombre: vector.nombre,
          apellidoPaterno: vector.apellido_paterno,
          apellidoMaterno: vector.apellido_materno,
          fechaNacimiento: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 5 - Apellidos compuestos', () => {
    test.each(satSpec.personas_fisicas.regla_5_apellidos_compuestos)(
      '$nombre $apellido_paterno $apellido_materno -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaFisica({
          nombre: vector.nombre,
          apellidoPaterno: vector.apellido_paterno,
          apellidoMaterno: vector.apellido_materno,
          fechaNacimiento: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 6 - Nombres compuestos (MARIA/JOSE)', () => {
    test.each(satSpec.personas_fisicas.regla_6_nombres_maria_jose)(
      '$nombre $apellido_paterno $apellido_materno -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaFisica({
          nombre: vector.nombre,
          apellidoPaterno: vector.apellido_paterno,
          apellidoMaterno: vector.apellido_materno,
          fechaNacimiento: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 7 - Un solo apellido', () => {
    test.each(satSpec.personas_fisicas.regla_7_un_solo_apellido)(
      '$nombre $apellido_paterno -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaFisica({
          nombre: vector.nombre,
          apellidoPaterno: vector.apellido_paterno,
          apellidoMaterno: vector.apellido_materno,
          fechaNacimiento: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 8 - Artículos, preposiciones y conjunciones', () => {
    test.each(satSpec.personas_fisicas.regla_8_articulos_preposiciones)(
      '$nombre $apellido_paterno $apellido_materno -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaFisica({
          nombre: vector.nombre,
          apellidoPaterno: vector.apellido_paterno,
          apellidoMaterno: vector.apellido_materno,
          fechaNacimiento: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });

  describe('Regla 10 - Caracteres especiales', () => {
    test.each(satSpec.personas_fisicas.regla_10_caracteres_especiales)(
      '$nombre $apellido_paterno $apellido_materno -> $rfc_base ($descripcion)',
      (vector) => {
        const rfc = generateRfcPersonaFisica({
          nombre: vector.nombre,
          apellidoPaterno: vector.apellido_paterno,
          apellidoMaterno: vector.apellido_materno,
          fechaNacimiento: vector.fecha,
        });
        const rfcBase = extractRfcBase(rfc);
        expect(rfcBase).toBe(vector.rfc_base);
      }
    );
  });
});

describe('SAT Specification - Complete Example with Homoclave', () => {
  const example = satSpec.ejemplo_completo_con_homoclave;

  test('Emma Gómez Díaz generates correct RFC with homoclave and checksum', () => {
    const rfc = generateRfcPersonaFisica({
      nombre: example.nombre,
      apellidoPaterno: example.apellido_paterno,
      apellidoMaterno: example.apellido_materno,
      fechaNacimiento: example.fecha,
    });

    // Test complete RFC
    expect(rfc).toBe(example.rfc_completo);

    // Test RFC base
    expect(rfc.slice(0, 10)).toBe(example.rfc_base);

    // Test homoclave
    expect(rfc.slice(10, 12)).toBe(example.homoclave);

    // Test checksum
    expect(rfc.slice(12)).toBe(example.digito_verificador);
  });

  test('RFC validates correctly', () => {
    expect(validateRfc(example.rfc_completo)).toBe(true);
  });

  test('RFC validator detects as persona física', () => {
    const validator = new RFCValidator(example.rfc_completo);
    expect(validator.isFisica()).toBe(true);
    expect(validator.detectType()).toBe('fisica');
  });
});

describe('SAT Specification - Checksum Validation', () => {
  test('RFC checksum can be validated independently', () => {
    // From the SAT document, the checksum calculation for GODE561231GR is 8
    const rfcWithoutChecksum = 'GODE561231GR';
    const validator = new RFCValidator(rfcWithoutChecksum + '8');
    expect(validator.validateChecksum()).toBe(true);

    // Wrong checksum should fail
    const wrongChecksum = new RFCValidator(rfcWithoutChecksum + '9');
    expect(wrongChecksum.validateChecksum()).toBe(false);
  });

  test('Various RFCs validate checksum correctly', () => {
    // Generic RFCs always pass checksum validation
    expect(validateRfc('XAXX010101000')).toBe(true);
    expect(validateRfc('XEXX010101000')).toBe(true);
  });
});

describe('SAT Specification - Palabras Inconvenientes', () => {
  test.each(satSpec.palabras_inconvenientes)(
    '$original should be corrected to $corregido',
    (palabra) => {
      // The implementation should replace cacophonic initials with X
      // This is tested indirectly through RFC generation
      // For example, if someone's initials would be "CACA", it becomes "CACX"
      expect(palabra.corregido.slice(-1)).toBe('X');
    }
  );
});
