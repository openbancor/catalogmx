#!/usr/bin/env node

import { cpSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const sharedDataRoot = resolve(packageRoot, '..', 'shared-data');
const destinationRoot = resolve(packageRoot, 'dist', 'shared-data');

const runtimeSources = [
  'banxico',
  'cnbv',
  'ift',
  'inegi',
  'mexico',
  'sat',
  'sepomex',
  'imss-catalogs.json',
  'imss-tables.json',
  'isr-tables.json',
  'resico-tables.json',
];

mkdirSync(destinationRoot, { recursive: true });
for (const source of runtimeSources) {
  cpSync(resolve(sharedDataRoot, source), resolve(destinationRoot, source), {
    recursive: true,
    filter: (path) => !path.endsWith('.pdf'),
  });
}
