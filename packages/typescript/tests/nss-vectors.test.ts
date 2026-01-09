import fs from 'fs';
import path from 'path';

import { generateNss } from '../src/validators/nss';

type NssVector = {
  subdelegacion: string;
  registro_anio: string;
  nacimiento_anio: string;
  secuencial: string;
  nss: string;
};

const vectorsPath = path.resolve(__dirname, '../../shared-data/tests/nss_vectors.json');
const vectors: NssVector[] = JSON.parse(fs.readFileSync(vectorsPath, 'utf-8'));

describe('NSS shared vectors', () => {
  test.each(vectors)('matches %s', (vector) => {
    const nss = generateNss(
      vector.subdelegacion,
      vector.registro_anio,
      vector.nacimiento_anio,
      vector.secuencial
    );
    expect(nss).toBe(vector.nss);
  });
});
