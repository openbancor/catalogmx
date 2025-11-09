#!/usr/bin/env node
/**
 * Migration script to convert large JSON catalogs to SQLite databases
 *
 * This script creates optimized SQLite databases for large catalogs (>10k records)
 * while maintaining API compatibility.
 */

const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

const SHARED_DATA = path.resolve(__dirname, '../../shared-data');
const SQLITE_DIR = path.join(SHARED_DATA, 'sqlite');

// Ensure SQLite directory exists
if (!fs.existsSync(SQLITE_DIR)) {
  fs.mkdirSync(SQLITE_DIR, { recursive: true });
}

console.log('🗄️  Creating SQLite databases for large catalogs...\n');

/**
 * Migrate c_ClaveProdServ (52k products/services)
 */
function migrateClaveProdServ() {
  console.log('📦 Migrating c_ClaveProdServ (52,514 records)...');

  const jsonPath = path.join(SHARED_DATA, 'sat/cfdi_4.0/clave_prod_serv.json');
  const dbPath = path.join(SQLITE_DIR, 'clave_prod_serv.db');

  // Read JSON data
  const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

  // Create database
  const db = new Database(dbPath);

  // Create table with optimized schema
  db.exec(`
    CREATE TABLE IF NOT EXISTS clave_prod_serv (
      clave TEXT PRIMARY KEY,
      descripcion TEXT NOT NULL,
      incluye_iva INTEGER NOT NULL,
      incluye_ieps INTEGER NOT NULL,
      complemento TEXT,
      palabras_similares TEXT,
      fecha_inicio_vigencia TEXT,
      fecha_fin_vigencia TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_descripcion ON clave_prod_serv(descripcion);
    CREATE INDEX IF NOT EXISTS idx_incluye_iva ON clave_prod_serv(incluye_iva);
    CREATE INDEX IF NOT EXISTS idx_incluye_ieps ON clave_prod_serv(incluye_ieps);

    -- Full-text search index for better search performance
    CREATE VIRTUAL TABLE IF NOT EXISTS clave_prod_serv_fts USING fts5(
      clave UNINDEXED,
      descripcion,
      complemento,
      palabras_similares
    );
  `);

  // Prepare insert statement
  const insert = db.prepare(`
    INSERT OR REPLACE INTO clave_prod_serv VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);

  const insertFts = db.prepare(`
    INSERT OR REPLACE INTO clave_prod_serv_fts VALUES (?, ?, ?, ?)
  `);

  // Batch insert for better performance
  const insertMany = db.transaction((records) => {
    for (const record of records) {
      // Map camelCase JSON fields to snake_case DB fields
      const includeIVA = record.incluirIVATrasladado?.toLowerCase() === 'sí' || record.incluirIVATrasladado?.toLowerCase() === 'si';
      const includeIEPS = record.incluirIEPSTrasladado?.toLowerCase() === 'sí' || record.incluirIEPSTrasladado?.toLowerCase() === 'si';

      insert.run(
        record.id,  // JSON uses 'id', DB uses 'clave'
        record.descripcion,
        includeIVA ? 1 : 0,
        includeIEPS ? 1 : 0,
        record.complementoQueDebeIncluir || null,
        record.palabrasSimilares || null,
        record.fechaInicioVigencia || null,
        record.fechaFinVigencia || null
      );

      insertFts.run(
        record.id,  // JSON uses 'id', DB uses 'clave'
        record.descripcion,
        record.complementoQueDebeIncluir || '',
        record.palabrasSimilares || ''
      );
    }
  });

  // Insert all records
  insertMany(jsonData);

  const count = db.prepare('SELECT COUNT(*) as count FROM clave_prod_serv').get();
  console.log(`   ✓ Inserted ${count.count} records`);

  // Get database size
  const stats = fs.statSync(dbPath);
  console.log(`   ✓ Database size: ${(stats.size / 1024 / 1024).toFixed(2)} MB\n`);

  db.close();
}

/**
 * Migrate INEGI Localidades (~200k localities)
 */
function migrateLocalidades() {
  console.log('🏘️  Migrating INEGI Localidades (~200k records)...');

  const jsonPath = path.join(SHARED_DATA, 'inegi/localidades.json');
  const dbPath = path.join(SQLITE_DIR, 'localidades.db');

  // Delete existing DB if it exists to ensure a clean migration
  if (fs.existsSync(dbPath)) {
    fs.unlinkSync(dbPath);
  }

  // Read JSON data
  const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
  const localidades = Array.isArray(jsonData) ? jsonData : jsonData.localidades;

  if (!Array.isArray(localidades)) {
    throw new Error('Invalid localidades JSON format. Expected an array or object with a localidades array.');
  }

  const getValue = (record, ...keys) => {
    for (const key of keys) {
      const value = record[key];
      if (value !== undefined && value !== null) {
        return value;
      }
    }
    return null;
  };

  // Create database
  const db = new Database(dbPath);

  // Create table with optimized schema
  db.exec(`
    CREATE TABLE IF NOT EXISTS localidades (
      cvegeo TEXT PRIMARY KEY,
      cve_ent TEXT,
      nom_ent TEXT,
      cve_mun TEXT,
      nom_mun TEXT,
      cve_loc TEXT,
      nom_loc TEXT,
      ambito TEXT,
      lat REAL,
      lon REAL,
      altitud INTEGER,
      poblacion_total INTEGER,
      poblacion_masculina INTEGER,
      poblacion_femenina INTEGER,
      viviendas_habitadas INTEGER
    );

    CREATE INDEX IF NOT EXISTS idx_cve_ent ON localidades(cve_ent);
    CREATE INDEX IF NOT EXISTS idx_cve_mun ON localidades(cve_mun);
    CREATE INDEX IF NOT EXISTS idx_nom_loc ON localidades(nom_loc);
    CREATE INDEX IF NOT EXISTS idx_ambito ON localidades(ambito);
    CREATE INDEX IF NOT EXISTS idx_poblacion ON localidades(poblacion_total);
    CREATE INDEX IF NOT EXISTS idx_coords ON localidades(lat, lon);

    -- Full-text search for locality names
    CREATE VIRTUAL TABLE IF NOT EXISTS localidades_fts USING fts5(
      cvegeo,
      nom_loc,
      nom_mun,
      nom_ent,
      content=localidades
    );
  `);

  // Prepare insert statement
  const insert = db.prepare(`
    INSERT OR REPLACE INTO localidades VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  const insertFts = db.prepare(`
    INSERT OR REPLACE INTO localidades_fts VALUES (?, ?, ?, ?)
  `);

  // Batch insert
  const insertMany = db.transaction((records) => {
    for (const record of records) {
      const cvegeo = getValue(record, 'cvegeo', 'CVEGEO');
      const cveEnt = getValue(record, 'cve_ent', 'cve_entidad', 'CVE_ENT');
      const nomEnt = getValue(record, 'nom_ent', 'nom_entidad', 'NOM_ENT');
      const cveMun = getValue(record, 'cve_mun', 'cve_municipio', 'CVE_MUN');
      const nomMun = getValue(record, 'nom_mun', 'nom_municipio', 'NOM_MUN');
      const cveLoc = getValue(record, 'cve_loc', 'cve_localidad', 'CVE_LOC');
      const nomLoc = getValue(record, 'nom_loc', 'nom_localidad', 'NOM_LOC');
      const ambito = getValue(record, 'ambito', 'AMBITO');
      const lat = getValue(record, 'lat', 'latitud', 'LAT_DECIMAL');
      const lon = getValue(record, 'lon', 'longitud', 'LON_DECIMAL');
      const altitud = getValue(record, 'altitud', 'ALTITUD');
      const pobTotal = getValue(record, 'poblacion_total', 'POB_TOTAL');
      const pobMasc = getValue(record, 'poblacion_masculina', 'POB_MASCULINA');
      const pobFem = getValue(record, 'poblacion_femenina', 'POB_FEMENINA');
      const viviendas = getValue(record, 'viviendas_habitadas', 'TOTAL DE VIVIENDAS HABITADAS', 'total_viviendas_habitadas');

      if (!cvegeo) {
        continue;
      }

      insert.run(
        cvegeo,
        cveEnt,
        nomEnt,
        cveMun,
        nomMun,
        cveLoc,
        nomLoc,
        ambito || null,
        lat !== null ? Number(lat) : null,
        lon !== null ? Number(lon) : null,
        altitud !== null ? Number(altitud) : null,
        pobTotal !== null ? Number(pobTotal) : 0,
        pobMasc !== null ? Number(pobMasc) : 0,
        pobFem !== null ? Number(pobFem) : 0,
        viviendas !== null ? Number(viviendas) : 0
      );

      insertFts.run(
        cvegeo,
        nomLoc || '',
        nomMun || '',
        nomEnt || ''
      );
    }
  });

  // Insert all records
  insertMany(localidades);

  const count = db.prepare('SELECT COUNT(*) as count FROM localidades').get();
  console.log(`   ✓ Inserted ${count.count} records`);

  // Get database size
  const stats = fs.statSync(dbPath);
  console.log(`   ✓ Database size: ${(stats.size / 1024 / 1024).toFixed(2)} MB\n`);

  db.close();
}

/**
 * Migrate SEPOMEX Postal Codes (~157k records)
 */
function migrateSepomex() {
  console.log('📬 Migrating SEPOMEX Codigos Postales (~157k records)...');

  const jsonPath = path.join(SHARED_DATA, 'sepomex/codigos_postales_completo.json');
  const dbPath = path.join(SQLITE_DIR, 'sepomex.db');

  // Delete existing DB if it exists
  if (fs.existsSync(dbPath)) {
    fs.unlinkSync(dbPath);
  }

  // Read JSON data
  const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

  // Create database
  const db = new Database(dbPath);

  // Create table with optimized schema
  db.exec(`
    CREATE TABLE IF NOT EXISTS codigos_postales (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cp TEXT NOT NULL,
      asentamiento TEXT NOT NULL,
      tipo_asentamiento TEXT,
      municipio TEXT,
      estado TEXT,
      ciudad TEXT,
      codigo_estado TEXT,
      codigo_municipio TEXT,
      zona TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_cp ON codigos_postales(cp);
    CREATE INDEX IF NOT EXISTS idx_municipio ON codigos_postales(municipio);
    CREATE INDEX IF NOT EXISTS idx_estado ON codigos_postales(estado);
  `);

  // Prepare insert statement
  const insert = db.prepare(`
    INSERT INTO codigos_postales (cp, asentamiento, tipo_asentamiento, municipio, estado, ciudad, codigo_estado, codigo_municipio, zona)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  // Batch insert for better performance
  const insertMany = db.transaction((records) => {
    for (const record of records) {
      insert.run(
        record.cp,
        record.asentamiento,
        record.tipo_asentamiento,
        record.municipio,
        record.estado,
        record.ciudad,
        record.codigo_estado,
        record.codigo_municipio,
        record.zona
      );
    }
  });

  // Insert all records
  insertMany(jsonData);

  const count = db.prepare('SELECT COUNT(*) as count FROM codigos_postales').get();
  console.log(`   ✓ Inserted ${count.count} records`);

  // Get database size
  const stats = fs.statSync(dbPath);
  console.log(`   ✓ Database size: ${(stats.size / 1024 / 1024).toFixed(2)} MB\n`);

  db.close();
}

// Run migrations
try {
  migrateClaveProdServ();
  migrateLocalidades();
  migrateSepomex();

  console.log('✅ All migrations completed successfully!');
  console.log('\n📊 Summary:');
  console.log('   - c_ClaveProdServ: 52,514 products/services');
  console.log('   - Localidades: ~200,000 localities');
  console.log('   - SEPOMEX: ~157,000 postal codes');
  console.log(`\n💾 Databases created in: ${SQLITE_DIR}`);

} catch (error) {
  console.error('❌ Migration failed:', error);
  process.exit(1);
}
