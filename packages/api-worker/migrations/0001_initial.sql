CREATE TABLE IF NOT EXISTS codigos_postales (
  cp TEXT NOT NULL,
  asentamiento TEXT NOT NULL,
  tipo_asentamiento TEXT NOT NULL,
  municipio TEXT NOT NULL,
  estado TEXT NOT NULL,
  ciudad TEXT,
  cp_oficina TEXT,
  codigo_estado TEXT,
  codigo_municipio TEXT,
  zona TEXT
);

CREATE INDEX IF NOT EXISTS idx_codigos_postales_cp
  ON codigos_postales (cp, asentamiento);

CREATE VIRTUAL TABLE IF NOT EXISTS codigos_postales_fts
  USING fts5(cp, asentamiento, municipio, estado, content='codigos_postales', content_rowid='rowid');

CREATE TABLE IF NOT EXISTS clave_prod_serv (
  clave TEXT PRIMARY KEY,
  descripcion TEXT NOT NULL,
  incluye_iva TEXT,
  incluye_ieps TEXT,
  complemento TEXT,
  fecha_inicio_vigencia TEXT,
  fecha_fin_vigencia TEXT,
  palabras_similares TEXT,
  estimulo_franja_fronteriza TEXT
);

CREATE INDEX IF NOT EXISTS idx_clave_prod_serv_clave
  ON clave_prod_serv (clave);

CREATE VIRTUAL TABLE IF NOT EXISTS clave_prod_serv_fts
  USING fts5(clave, descripcion, palabras_similares, content='clave_prod_serv', content_rowid='rowid');
