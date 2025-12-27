-- ============================================================================
-- Schema para mexico_dynamic.sqlite3
-- Base de datos de datos dinámicos de Banxico (actualizados diariamente)
-- ============================================================================

-- Tabla de UDIs (Unidades de Inversión)
-- Fuente: Banxico Serie SP68257
-- Frecuencia: Diaria
CREATE TABLE IF NOT EXISTS udis (
    fecha TEXT PRIMARY KEY,
    valor REAL NOT NULL,
    anio INTEGER,
    mes INTEGER,
    tipo TEXT CHECK(tipo IN ('diario', 'oficial_banxico', 'promedio_mensual', 'promedio_anual')),
    moneda TEXT DEFAULT 'MXN',
    notas TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_udis_anio_mes ON udis(anio, mes);
CREATE INDEX idx_udis_tipo ON udis(tipo);

-- Tabla de Tipo de Cambio USD/MXN
-- Fuentes:
--   - Banxico Serie SF43718 (FIX - Fecha determinación)
--   - Banxico Serie SF60653 (Liquidación)
--   - Banxico Serie SF63528 (Histórico 1954-presente)
-- Frecuencia: Diaria
CREATE TABLE IF NOT EXISTS tipo_cambio (
    fecha TEXT NOT NULL,
    fuente TEXT NOT NULL CHECK(fuente IN ('FIX', 'liquidacion', 'historico')),
    tipo_cambio REAL NOT NULL,
    anio INTEGER,
    mes INTEGER,
    moneda_origen TEXT DEFAULT 'USD',
    moneda_destino TEXT DEFAULT 'MXN',
    updated_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (fecha, fuente)
);

CREATE INDEX idx_tipo_cambio_anio ON tipo_cambio(anio);
CREATE INDEX idx_tipo_cambio_fuente ON tipo_cambio(fuente);

-- Tabla de TIIE (Tasa de Interés Interbancaria de Equilibrio)
-- Fuentes:
--   - Banxico Serie SF43783 (TIIE 28 días)
--   - Banxico Serie SF43784 (TIIE 91 días)
--   - Banxico Serie SF43878 (TIIE 182 días)
-- Frecuencia: Diaria
CREATE TABLE IF NOT EXISTS tiie (
    fecha TEXT NOT NULL,
    plazo INTEGER NOT NULL CHECK(plazo IN (28, 91, 182)),
    tasa REAL NOT NULL,
    anio INTEGER,
    mes INTEGER,
    updated_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (fecha, plazo)
);

CREATE INDEX idx_tiie_plazo ON tiie(plazo);
CREATE INDEX idx_tiie_anio ON tiie(anio);

-- Tabla de CETES (Certificados de la Tesorería)
-- Fuentes:
--   - Banxico Serie SF43936 (CETES 28 días)
--   - Banxico Serie SF43939 (CETES 182 días)
--   - Banxico Serie SF43942 (CETES 364 días)
-- Frecuencia: Semanal
CREATE TABLE IF NOT EXISTS cetes (
    fecha TEXT NOT NULL,
    plazo INTEGER NOT NULL CHECK(plazo IN (28, 91, 182, 364)),
    tasa REAL NOT NULL,
    anio INTEGER,
    mes INTEGER,
    updated_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (fecha, plazo)
);

CREATE INDEX idx_cetes_plazo ON cetes(plazo);
CREATE INDEX idx_cetes_anio ON cetes(anio);

-- Tabla de Inflación
-- Fuentes:
--   - Banxico Serie SP30577 (INPC General)
--   - Banxico Serie SP1 (Inflación mensual)
--   - Banxico Serie SP30579 (Inflación anual)
-- Frecuencia: Mensual
CREATE TABLE IF NOT EXISTS inflacion (
    fecha TEXT PRIMARY KEY,
    anio INTEGER,
    mes INTEGER,
    inpc REAL,
    inflacion_mensual REAL,
    inflacion_anual REAL,
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_inflacion_anio_mes ON inflacion(anio, mes);

-- Tabla de Salarios Mínimos
-- Fuentes:
--   - Banxico Serie SL11298 (General)
--   - Banxico Serie SL11295 (Zona Libre Frontera Norte)
-- Frecuencia: Mensual (cambios oficiales)
CREATE TABLE IF NOT EXISTS salarios_minimos (
    fecha TEXT NOT NULL,
    zona TEXT NOT NULL CHECK(zona IN ('general', 'frontera_norte')),
    salario_diario REAL NOT NULL,
    anio INTEGER,
    mes INTEGER,
    updated_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (fecha, zona)
);

CREATE INDEX idx_salarios_zona ON salarios_minimos(zona);
CREATE INDEX idx_salarios_anio ON salarios_minimos(anio);

-- Tabla de Metadata (información de la base de datos)
CREATE TABLE IF NOT EXISTS _metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Valores iniciales de metadata
INSERT OR REPLACE INTO _metadata (key, value) VALUES
    ('version', date('now')),
    ('source', 'banxico'),
    ('auto_update', 'true'),
    ('schema_version', '1.0'),
    ('created_at', datetime('now'));

-- ============================================================================
-- Views para consultas comunes
-- ============================================================================

-- Vista: UDI más reciente
CREATE VIEW IF NOT EXISTS v_udi_actual AS
SELECT fecha, valor, anio, mes
FROM udis
WHERE tipo IN ('diario', 'oficial_banxico')
ORDER BY fecha DESC
LIMIT 1;

-- Vista: Tipo de cambio FIX más reciente
CREATE VIEW IF NOT EXISTS v_tipo_cambio_actual AS
SELECT fecha, tipo_cambio, anio
FROM tipo_cambio
WHERE fuente = 'FIX'
ORDER BY fecha DESC
LIMIT 1;

-- Vista: TIIE 28 días más reciente
CREATE VIEW IF NOT EXISTS v_tiie_28_actual AS
SELECT fecha, tasa, anio
FROM tiie
WHERE plazo = 28
ORDER BY fecha DESC
LIMIT 1;

-- Vista: CETES 28 días más reciente
CREATE VIEW IF NOT EXISTS v_cetes_28_actual AS
SELECT fecha, tasa, anio
FROM cetes
WHERE plazo = 28
ORDER BY fecha DESC
LIMIT 1;

-- Vista: Inflación anual más reciente
CREATE VIEW IF NOT EXISTS v_inflacion_actual AS
SELECT fecha, inflacion_anual, inpc, anio, mes
FROM inflacion
ORDER BY fecha DESC
LIMIT 1;

-- ============================================================================
-- Triggers para mantener consistencia
-- ============================================================================

-- Trigger: Auto-calcular año y mes al insertar UDIs
CREATE TRIGGER IF NOT EXISTS trg_udis_fecha_parts
AFTER INSERT ON udis
WHEN NEW.anio IS NULL OR NEW.mes IS NULL
BEGIN
    UPDATE udis
    SET anio = CAST(substr(fecha, 1, 4) AS INTEGER),
        mes = CAST(substr(fecha, 6, 2) AS INTEGER)
    WHERE fecha = NEW.fecha;
END;

-- Trigger: Auto-calcular año y mes al insertar tipo_cambio
CREATE TRIGGER IF NOT EXISTS trg_tipo_cambio_fecha_parts
AFTER INSERT ON tipo_cambio
WHEN NEW.anio IS NULL OR NEW.mes IS NULL
BEGIN
    UPDATE tipo_cambio
    SET anio = CAST(substr(fecha, 1, 4) AS INTEGER),
        mes = CAST(substr(fecha, 6, 2) AS INTEGER)
    WHERE fecha = NEW.fecha AND fuente = NEW.fuente;
END;

-- Trigger: Auto-calcular año y mes al insertar TIIE
CREATE TRIGGER IF NOT EXISTS trg_tiie_fecha_parts
AFTER INSERT ON tiie
WHEN NEW.anio IS NULL OR NEW.mes IS NULL
BEGIN
    UPDATE tiie
    SET anio = CAST(substr(fecha, 1, 4) AS INTEGER),
        mes = CAST(substr(fecha, 6, 2) AS INTEGER)
    WHERE fecha = NEW.fecha AND plazo = NEW.plazo;
END;

-- Trigger: Auto-calcular año y mes al insertar CETES
CREATE TRIGGER IF NOT EXISTS trg_cetes_fecha_parts
AFTER INSERT ON cetes
WHEN NEW.anio IS NULL OR NEW.mes IS NULL
BEGIN
    UPDATE cetes
    SET anio = CAST(substr(fecha, 1, 4) AS INTEGER),
        mes = CAST(substr(fecha, 6, 2) AS INTEGER)
    WHERE fecha = NEW.fecha AND plazo = NEW.plazo;
END;

-- Trigger: Auto-calcular año y mes al insertar inflación
CREATE TRIGGER IF NOT EXISTS trg_inflacion_fecha_parts
AFTER INSERT ON inflacion
WHEN NEW.anio IS NULL OR NEW.mes IS NULL
BEGIN
    UPDATE inflacion
    SET anio = CAST(substr(fecha, 1, 4) AS INTEGER),
        mes = CAST(substr(fecha, 6, 2) AS INTEGER)
    WHERE fecha = NEW.fecha;
END;

-- Trigger: Actualizar versión cuando se modifican datos
CREATE TRIGGER IF NOT EXISTS trg_update_version_on_udis
AFTER INSERT ON udis
BEGIN
    UPDATE _metadata SET value = date('now'), updated_at = datetime('now') WHERE key = 'version';
END;

CREATE TRIGGER IF NOT EXISTS trg_update_version_on_tipo_cambio
AFTER INSERT ON tipo_cambio
BEGIN
    UPDATE _metadata SET value = date('now'), updated_at = datetime('now') WHERE key = 'version';
END;

-- ============================================================================
-- Consultas de ejemplo para verificar datos
-- ============================================================================

-- SELECT * FROM v_udi_actual;
-- SELECT * FROM v_tipo_cambio_actual;
-- SELECT * FROM v_tiie_28_actual;
-- SELECT * FROM v_cetes_28_actual;
-- SELECT * FROM v_inflacion_actual;
-- SELECT * FROM _metadata;
