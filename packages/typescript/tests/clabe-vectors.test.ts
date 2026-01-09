import fs from 'fs';
import path from 'path';

import { generateClabe } from '../src/validators/clabe';

type ClabeVector = {
  bank_code: string;
  branch_code: string;
  account_number: string;
  clabe: string;
};

const vectorsPath = path.resolve(__dirname, '../../shared-data/tests/clabe_vectors.json');
const vectors: ClabeVector[] = JSON.parse(fs.readFileSync(vectorsPath, 'utf-8'));

describe('CLABE shared vectors', () => {
  test.each(vectors)('matches %s', (vector) => {
    const clabe = generateClabe(vector.bank_code, vector.branch_code, vector.account_number);
    expect(clabe).toBe(vector.clabe);
  });
});
