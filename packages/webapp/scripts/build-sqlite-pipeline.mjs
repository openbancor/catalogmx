import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { syncSqliteData } from './sync-sqlite.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');
const sharedDataDir = path.resolve(projectRoot, '../shared-data');
const generatorScript = path.resolve(sharedDataDir, 'build_unified_sqlite.py');
const outputPath = path.resolve(sharedDataDir, 'mexico.sqlite3');

function findPythonInterpreter() {
  const candidates = [process.env.PYTHON, 'python3', 'python'].filter(Boolean);
  let lastError;
  for (const candidate of candidates) {
    const result = spawnSync(candidate, ['--version'], { stdio: 'ignore' });
    if (result.status === 0) {
      return candidate;
    }
    lastError = result.error;
  }
  throw lastError ?? new Error('Unable to find python interpreter. Set PYTHON env var.');
}

async function main() {
  const python = findPythonInterpreter();

  const spawnResult = spawnSync(
    python,
    [generatorScript, '--output', outputPath],
    { stdio: 'inherit', cwd: sharedDataDir }
  );

  if (spawnResult.status !== 0) {
    process.exitCode = spawnResult.status ?? 1;
    throw new Error('[data:build] build_unified_sqlite.py failed.');
  }

  await syncSqliteData();
}

main().catch((error) => {
  console.error(error?.message ?? error);
  process.exitCode = process.exitCode || 1;
});
