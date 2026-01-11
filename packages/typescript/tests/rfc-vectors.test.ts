import fs from 'fs';
import path from 'path';

import { generateRfcPersonaFisica, generateRfcPersonaMoral } from '../src/validators/rfc';

type RfcVector =
  | {
      type: 'fisica';
      nombre: string;
      apellido_paterno: string;
      apellido_materno: string;
      fecha: string;
      rfc: string;
    }
  | {
      type: 'moral';
      razon_social: string;
      fecha: string;
      rfc: string;
    };

const vectorsPath = path.resolve(__dirname, '../../shared-data/tests/rfc_vectors.json');
const vectors: RfcVector[] = JSON.parse(fs.readFileSync(vectorsPath, 'utf-8'));

describe('RFC shared vectors', () => {
  test.each(vectors)('matches %s', (vector) => {
    if (vector.type === 'fisica') {
      const rfc = generateRfcPersonaFisica({
        nombre: vector.nombre,
        apellidoPaterno: vector.apellido_paterno,
        apellidoMaterno: vector.apellido_materno,
        fechaNacimiento: vector.fecha,
      });
      expect(rfc).toBe(vector.rfc);
      return;
    }

    const rfc = generateRfcPersonaMoral({
      razonSocial: vector.razon_social,
      fechaConstitucion: vector.fecha,
    });
    expect(rfc).toBe(vector.rfc);
  });
});
