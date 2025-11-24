import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');
const sharedDataRoot = path.resolve(projectRoot, '../shared-data');
const publicDataDir = path.resolve(projectRoot, 'public/data');
const allowedExtensions = new Set(['.db', '.sqlite', '.sqlite3']);

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function collectSqliteFiles(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...await collectSqliteFiles(fullPath));
    } else if (allowedExtensions.has(path.extname(entry.name).toLowerCase())) {
      files.push(fullPath);
    }
  }
  return files;
}

export async function syncSqliteData({ silent = false } = {}) {
  try {
    await ensureDir(publicDataDir);
    const sharedDirExists = await fs.stat(sharedDataRoot).then(() => true).catch(() => false);
    if (!sharedDirExists) {
      if (!silent) {
        console.warn(`[sync-sqlite] Shared data directory not found at ${sharedDataRoot}`);
      }
      return;
    }

    const sqliteFiles = await collectSqliteFiles(sharedDataRoot);
    if (sqliteFiles.length === 0) {
      if (!silent) {
        console.warn('[sync-sqlite] No SQLite files found in packages/shared-data.');
      }
      return;
    }

    let copies = 0;
    for (const filePath of sqliteFiles) {
      const fileName = path.basename(filePath);
      if (fileName === 'mexico.sqlite3') {
        continue;
      }
      const destPath = path.join(publicDataDir, fileName);
      await fs.copyFile(filePath, destPath);
      copies += 1;
    }

    if (!silent) {
      console.log(`[sync-sqlite] Copied ${copies} file(s) into public/data.`);
    }
  } catch (error) {
    console.error('[sync-sqlite] Failed to copy SQLite assets:', error);
    process.exitCode = 1;
    throw error;
  }
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  syncSqliteData().catch(() => {
    process.exitCode = 1;
  });
}
