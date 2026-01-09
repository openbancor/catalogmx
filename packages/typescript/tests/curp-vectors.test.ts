import fs from 'fs';
import path from 'path';

import { generateCurp } from '../src/validators/curp';

type CurpVector = {
  nombre: string;
  apellido_paterno: string;
  apellido_materno: string;
  fecha: string;
  sexo: 'H' | 'M';
  estado: string;
  curp: string;
};

const vectorsPath = path.resolve(__dirname, '../../shared-data/tests/curp_vectors.json');
const vectors: CurpVector[] = JSON.parse(fs.readFileSync(vectorsPath, 'utf-8'));

describe('CURP shared vectors', () => {
  test.each(vectors)('matches %s', (vector) => {
    const curp = generateCurp({
      nombre: vector.nombre,
      apellidoPaterno: vector.apellido_paterno,
      apellidoMaterno: vector.apellido_materno,
      fechaNacimiento: vector.fecha,
      sexo: vector.sexo,
      estado: vector.estado,
    });

    expect(curp).toBe(vector.curp);
  });
});
