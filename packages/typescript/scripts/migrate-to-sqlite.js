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

  // Read JSON data
  const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
  const localidades = jsonData.localidades;

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
      insert.run(
        record.cvegeo,
        record.cve_ent,
        record.nom_ent,
        record.cve_mun,
        record.nom_mun,
        record.cve_loc,
        record.nom_loc,
        record.ambito || null,
        record.lat || null,
        record.lon || null,
        record.altitud || null,
        record.poblacion_total || 0,
        record.poblacion_masculina || 0,
        record.poblacion_femenina || 0,
        record.viviendas_habitadas || 0
      );

      insertFts.run(
        record.cvegeo,
        record.nom_loc,
        record.nom_mun,
        record.nom_ent
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

// Run migrations
try {
  migrateClaveProdServ();
  migrateLocalidades();

  console.log('✅ All migrations completed successfully!');
  console.log('\n📊 Summary:');
  console.log('   - c_ClaveProdServ: 52,514 products/services');
  console.log('   - Localidades: ~200,000 localities');
  console.log(`\n💾 Databases created in: ${SQLITE_DIR}`);

} catch (error) {
  console.error('❌ Migration failed:', error);
  process.exit(1);
}
