import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');
const sharedDataRoot = path.resolve(projectRoot, '../shared-data');
const publicDataDir = path.resolve(projectRoot, 'public/data');
const allowedExtensions = new Set(['.db', '.sqlite', '.sqlite3']);
const SAMPLE_MEXICO_PATH = path.resolve(publicDataDir, 'mexico.sqlite3');

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
      const stats = await fs.stat(fullPath);
      files.push({
        path: fullPath,
        name: entry.name,
        size: stats.size,
        mtimeMs: stats.mtimeMs,
      });
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

    // Prefer the largest (or newest) file when duplicates share the same name.
    const dedupedByName = new Map();
    for (const file of sqliteFiles) {
      const current = dedupedByName.get(file.name);
      const isLarger = !current || file.size > current.size;
      const isNewerSameSize = current && file.size === current.size && file.mtimeMs > current.mtimeMs;
      if (isLarger || isNewerSameSize) {
        dedupedByName.set(file.name, file);
      }
    }
    const filesToCopy = Array.from(dedupedByName.values());

    let copies = 0;
    for (const file of filesToCopy) {
      const destPath = path.join(publicDataDir, file.name);
      await fs.copyFile(file.path, destPath);
      copies += 1;
    }

    if (!silent) {
      console.log(`[sync-sqlite] Copied ${copies} file(s) into public/data.`);
    }

    await ensureMexicoSampleDb();
  } catch (error) {
    console.error('[sync-sqlite] Failed to copy SQLite assets:', error);
    process.exitCode = 1;
    throw error;
  }
}

async function ensureMexicoSampleDb() {
  const exists = await fs.stat(SAMPLE_MEXICO_PATH).then(() => true).catch(() => false);
  if (exists) return;

  const hasSqliteCli = await new Promise((resolve) => {
    import('node:child_process').then(({ exec }) => {
      exec('which sqlite3', (err, stdout) => {
        resolve(!err && stdout.trim().length > 0);
      });
    });
  });

  if (!hasSqliteCli) {
    console.warn('[sync-sqlite] sqlite3 CLI not found; cannot create sample mexico.sqlite3');
    return;
  }

  const { execSync } = await import('node:child_process');
  const statements = [
    // Banxico banks (sample)
    `CREATE TABLE banxico_banks (code TEXT PRIMARY KEY, name TEXT, full_name TEXT, rfc TEXT, spei INTEGER);`,
    `INSERT INTO banxico_banks VALUES ('002','BANAMEX','Banco Nacional de México, S.A.','BNM840515VB1',1);`,
    `INSERT INTO banxico_banks VALUES ('012','BBVA MEXICO','BBVA México, S.A.','BMB930121HT4',1);`,
    // UDIS (sample)
    `CREATE TABLE banxico_udis (fecha TEXT, valor REAL, moneda TEXT, tipo TEXT, notas TEXT);`,
    `INSERT INTO banxico_udis VALUES ('2025-01-01', 8.0, 'MXN', 'valor', 'Sample UDI');`,
    // Postal codes (sample)
    `CREATE TABLE codigos_postales_completo (cp TEXT, asentamiento TEXT, tipo_asentamiento TEXT, municipio TEXT, estado TEXT, ciudad TEXT, cp_oficina TEXT, codigo_estado TEXT, codigo_municipio TEXT, zona TEXT);`,
    `INSERT INTO codigos_postales_completo VALUES ('01000','San Ángel','Colonia','Álvaro Obregón','Ciudad de México','Ciudad de México','01000','09','010','U');`,
    `INSERT INTO codigos_postales_completo VALUES ('06700','Roma Norte','Colonia','Cuauhtémoc','Ciudad de México','Ciudad de México','06700','09','010','U');`,
    // Localidades (sample)
    `CREATE TABLE localidades (cvegeo TEXT, cve_entidad TEXT, cve_municipio TEXT, cve_localidad TEXT, nom_localidad TEXT, nom_municipio TEXT, nom_entidad TEXT, latitud REAL, longitud REAL, altitud REAL, poblacion_total INTEGER);`,
    `INSERT INTO localidades VALUES ('090010001','09','001','0001','Ciudad de México','Álvaro Obregón','Ciudad de México',19.35,-99.19,2240,100000);`,
    // ClaveProdServ (sample)
    `CREATE TABLE clave_prod_serv (id TEXT PRIMARY KEY, descripcion TEXT, incluirIVATrasladado TEXT, incluirIEPSTrasladado TEXT, complementoQueDebeIncluir TEXT, fechaInicioVigencia TEXT, fechaFinVigencia TEXT, estimuloFranjaFronteriza TEXT, palabrasSimilares TEXT);`,
    `INSERT INTO clave_prod_serv VALUES ('01010101','No aplica','No','No','','','','','servicio no aplica');`,
    `INSERT INTO clave_prod_serv VALUES ('10101501','Gatos vivos','Sí','No','','','','','gatos mascotas animales vivos');`
  ];

  const sql = statements.join('\n');
  execSync(`sqlite3 "${SAMPLE_MEXICO_PATH}" "${sql}"`);
  console.log('[sync-sqlite] Created sample mexico.sqlite3 in public/data (demo-sized data).');
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  syncSqliteData().catch(() => {
    process.exitCode = 1;
  });
}
