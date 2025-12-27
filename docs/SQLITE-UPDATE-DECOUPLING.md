# 🔄 Desacoplamiento de Actualizaciones SQLite

## 📋 Problema

**Situación actual:**
- Datos de Banxico cambian **diariamente** (UDI, tipo de cambio, TIIE, CETES, inflación)
- GitHub Actions actualiza JSONs diariamente
- Los JSONs están **empaquetados dentro de la librería**
- ❌ **Cada actualización requiere un nuevo release** de catalogmx

**¿Por qué es inviable?**
- Releases diarios contaminan versionado semántico
- Requiere changelog, git tags, CI/CD completo
- Usuarios deben `pip install --upgrade` diariamente
- PyPI, npm, pub.dev se saturan de versiones innecesarias

## 🎯 Solución Propuesta

### Arquitectura de Datos en Capas

```
┌─────────────────────────────────────────┐
│  Datos ESTÁTICOS (empaquetados)         │
│  - Catálogos SAT (cambian 1-2 veces/año)│
│  - Códigos postales SEPOMEX             │
│  - Municipios/Estados INEGI             │
│  - Placas, UMA, etc.                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Datos DINÁMICOS (SQLite remoto)        │
│  - UDIs Banxico (diario)                │
│  - Tipo de cambio (diario)              │
│  - TIIE, CETES (diario/semanal)         │
│  - Inflación (mensual)                  │
│  - Salarios mínimos (mensual)           │
└─────────────────────────────────────────┘
```

### Mecanismo de Actualización

**1. GitHub Releases como CDN de Datos**
```
Workflow diario:
├── Fetch datos de Banxico API
├── Actualizar mexico.sqlite3
└── Publicar en GitHub Releases (latest)
    └── Tag: data-YYYY-MM-DD
```

**2. Auto-actualización en la Librería**
```python
from catalogmx.data import DataUpdater

# Automático (recomendado)
updater = DataUpdater()
updater.auto_update(max_age_hours=24)

# Manual
updater.download_latest()
updater.get_version()  # "2025-12-04"
```

**3. Caché Local + Fallback**
```
~/.catalogmx/
├── mexico.sqlite3          # Última versión descargada
├── version.json            # Metadata de versión
└── embedded/               # Fallback empaquetado
    └── mexico.sqlite3
```

**Flujo de carga:**
1. ¿Existe caché local? → Verificar edad
2. ¿Edad > 24 horas? → Intentar actualizar
3. ¿Falló descarga? → Usar caché local
4. ¿No hay caché? → Usar datos empaquetados

## 🏗️ Implementación

### Fase 1: Infraestructura de Datos

**1.1. Crear `mexico_dynamic.sqlite3`**
```sql
-- Tablas para datos dinámicos de Banxico
CREATE TABLE udis (
    fecha TEXT PRIMARY KEY,
    valor REAL NOT NULL,
    año INTEGER,
    mes INTEGER,
    tipo TEXT,  -- 'diario', 'mensual', 'anual'
    updated_at TEXT
);

CREATE TABLE tipo_cambio (
    fecha TEXT PRIMARY KEY,
    tipo_cambio REAL NOT NULL,
    año INTEGER,
    fuente TEXT,  -- 'FIX', 'liquidacion', 'historico'
    updated_at TEXT
);

CREATE TABLE tiie (
    fecha TEXT,
    plazo INTEGER,  -- 28, 91, 182
    tasa REAL,
    updated_at TEXT,
    PRIMARY KEY (fecha, plazo)
);

CREATE TABLE cetes (
    fecha TEXT,
    plazo INTEGER,  -- 28, 91, 182, 364
    tasa REAL,
    updated_at TEXT,
    PRIMARY KEY (fecha, plazo)
);

CREATE TABLE inflacion (
    fecha TEXT PRIMARY KEY,
    inflacion_mensual REAL,
    inflacion_anual REAL,
    inpc REAL,
    updated_at TEXT
);

-- Metadata de versión
CREATE TABLE _metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT
);

INSERT INTO _metadata (key, value, updated_at) VALUES
('version', '2025-12-04', datetime('now')),
('source', 'banxico', datetime('now')),
('auto_update', 'true', datetime('now'));
```

**1.2. Script de Conversión JSON → SQLite**
```python
# packages/shared-data/scripts/json_to_sqlite.py
import json
import sqlite3
from pathlib import Path

def migrate_banxico_to_sqlite():
    """Migrar todos los JSONs de Banxico a SQLite"""
    db = sqlite3.connect("mexico_dynamic.sqlite3")

    # UDIs
    with open("banxico/udis.json") as f:
        udis = json.load(f)
        db.executemany(
            "INSERT OR REPLACE INTO udis VALUES (?, ?, ?, ?, ?, datetime('now'))",
            [(r["fecha"], r["valor"], r["año"], r["mes"], r["tipo"]) for r in udis]
        )

    # Tipo de cambio
    # TIIE, CETES, etc...

    db.commit()
    db.close()
```

### Fase 2: Módulo de Actualización

**2.1. `catalogmx/data/updater.py`**
```python
"""
Data Updater - Descarga automática de datos dinámicos desde GitHub Releases
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import urllib.request
import shutil

GITHUB_RELEASE_URL = "https://github.com/openbancor/catalogmx/releases/download/latest/mexico_dynamic.sqlite3"
CACHE_DIR = Path.home() / ".catalogmx"
CACHE_DB = CACHE_DIR / "mexico.sqlite3"
VERSION_FILE = CACHE_DIR / "version.json"
EMBEDDED_DB = Path(__file__).parent.parent / "data" / "mexico_embedded.sqlite3"

class DataUpdater:
    """Maneja la actualización automática de datos dinámicos"""

    def __init__(self):
        CACHE_DIR.mkdir(exist_ok=True)

    def get_local_version(self) -> str | None:
        """Obtener versión de datos locales"""
        if not VERSION_FILE.exists():
            return None
        with open(VERSION_FILE) as f:
            return json.load(f).get("version")

    def get_local_age_hours(self) -> float | None:
        """Obtener edad de datos locales en horas"""
        if not VERSION_FILE.exists():
            return None
        with open(VERSION_FILE) as f:
            updated = datetime.fromisoformat(json.load(f)["updated_at"])
            return (datetime.now() - updated).total_seconds() / 3600

    def download_latest(self, force: bool = False) -> bool:
        """Descargar última versión de datos desde GitHub Releases"""
        try:
            print(f"📥 Descargando datos desde {GITHUB_RELEASE_URL}...")

            # Descargar a temporal
            temp_db = CACHE_DIR / "mexico.sqlite3.tmp"
            urllib.request.urlretrieve(GITHUB_RELEASE_URL, temp_db)

            # Verificar integridad
            db = sqlite3.connect(temp_db)
            version = db.execute("SELECT value FROM _metadata WHERE key = 'version'").fetchone()[0]
            db.close()

            # Mover a caché
            shutil.move(temp_db, CACHE_DB)

            # Guardar metadata
            with open(VERSION_FILE, "w") as f:
                json.dump({
                    "version": version,
                    "updated_at": datetime.now().isoformat(),
                    "source": "github_releases"
                }, f)

            print(f"✅ Datos actualizados a versión {version}")
            return True

        except Exception as e:
            print(f"❌ Error descargando datos: {e}")
            return False

    def auto_update(self, max_age_hours: int = 24) -> Path:
        """
        Auto-actualización inteligente con fallback

        :param max_age_hours: Edad máxima antes de actualizar (default 24h)
        :return: Path a la base de datos a usar
        """
        age = self.get_local_age_hours()

        # Si no existe caché o es muy viejo, intentar actualizar
        if age is None or age > max_age_hours:
            if self.download_latest():
                return CACHE_DB

        # Si hay caché local válido, usar
        if CACHE_DB.exists():
            return CACHE_DB

        # Fallback: datos empaquetados
        print("⚠️  Usando datos empaquetados (puede estar desactualizado)")
        return EMBEDDED_DB

    def get_database_path(self, auto_update: bool = True) -> Path:
        """Obtener path a la base de datos (con o sin auto-update)"""
        if auto_update:
            return self.auto_update()

        if CACHE_DB.exists():
            return CACHE_DB

        return EMBEDDED_DB
```

**2.2. Migrar Catálogos a Usar DataUpdater**
```python
# catalogmx/catalogs/banxico/udis.py (NUEVO)
import sqlite3
from catalogmx.data.updater import DataUpdater

class UDICatalog:
    _db_path: Path | None = None

    @classmethod
    def _get_db(cls) -> sqlite3.Connection:
        """Obtener conexión a base de datos"""
        if cls._db_path is None:
            updater = DataUpdater()
            cls._db_path = updater.auto_update(max_age_hours=24)

        return sqlite3.connect(cls._db_path)

    @classmethod
    def get_por_fecha(cls, fecha: str) -> dict | None:
        """Obtener UDI por fecha"""
        db = cls._get_db()
        cursor = db.execute(
            "SELECT fecha, valor, año, mes, tipo FROM udis WHERE fecha = ?",
            (fecha,)
        )
        row = cursor.fetchone()
        db.close()

        if not row:
            return None

        return {
            "fecha": row[0],
            "valor": row[1],
            "año": row[2],
            "mes": row[3],
            "tipo": row[4]
        }

    # ... resto de métodos usando SQL queries
```

### Fase 3: Workflow de GitHub Actions

**3.1. `.github/workflows/update-dynamic-data.yml`**
```yaml
name: Update Dynamic Data (Daily)

on:
  schedule:
    - cron: '0 10 * * *'  # 4 AM México (10 UTC)
  workflow_dispatch:

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Fetch latest data from Banxico
        env:
          BANXICO_TOKEN: ${{ secrets.BANXICO_TOKEN }}
        run: |
          cd packages/shared-data
          python scripts/fetch_all_banxico.py

      - name: Build SQLite from JSONs
        run: |
          cd packages/shared-data
          python scripts/json_to_sqlite.py

      - name: Create Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          VERSION=$(date +%Y-%m-%d)
          TAG="data-${VERSION}"

          gh release create "${TAG}" \
            packages/shared-data/mexico_dynamic.sqlite3 \
            --title "Data Update ${VERSION}" \
            --notes "Daily data update from Banxico (UDI, tipo cambio, TIIE, CETES, inflación)"

          # Mover tag 'latest' a esta release
          gh release delete latest --yes || true
          gh release create latest \
            packages/shared-data/mexico_dynamic.sqlite3 \
            --title "Latest Data" \
            --notes "Always points to most recent data"
```

## 📊 Comparación: Antes vs Después

### Antes (Actual)
```
❌ Actualización de datos
├── 1. GitHub Action actualiza JSON
├── 2. Commit a main
├── 3. Crear release v1.2.301, v1.2.302, ...
├── 4. Publicar en PyPI, npm, pub.dev
└── 5. Usuario: pip install --upgrade catalogmx

Frecuencia: Diaria → 365 releases/año 🤯
```

### Después (Propuesto)
```
✅ Actualización de datos
├── 1. GitHub Action actualiza SQLite
└── 2. Publica en GitHub Releases (data-YYYY-MM-DD)

Usuario:
├── Automático: DataUpdater descarga si >24h
└── Manual: catalogmx.data.update()

Frecuencia de releases de CÓDIGO: 1-2 veces/mes
Frecuencia de datos: Diaria (sin tocar código)
```

## 🚀 Migración

### Para Usuarios

**Antes:**
```python
from catalogmx.catalogs.banxico import get_udi_actual

udi = get_udi_actual()  # Usa datos empaquetados (puede estar viejo)
```

**Después:**
```python
from catalogmx.catalogs.banxico import get_udi_actual
from catalogmx.data import DataUpdater

# Opción 1: Automático (recomendado)
udi = get_udi_actual()  # Auto-descarga si >24h

# Opción 2: Forzar actualización
updater = DataUpdater()
updater.download_latest(force=True)
udi = get_udi_actual()

# Opción 3: Verificar versión
print(updater.get_local_version())  # "2025-12-04"
print(f"Edad: {updater.get_local_age_hours():.1f} horas")
```

### Retrocompatibilidad

✅ **100% compatible** con código existente
- Misma API pública
- Mismo comportamiento
- Solo cambia el backend de datos

## 🎯 Beneficios

### Para Desarrolladores
- ✅ Releases solo cuando cambia **código**
- ✅ Versionado semántico real (1.2.3 → 1.3.0)
- ✅ Menos PRs automáticos

### Para Usuarios
- ✅ Datos **siempre actualizados** (sin reinstalar)
- ✅ Funciona offline (fallback a caché)
- ✅ Sin breaking changes

### Para CI/CD
- ✅ GitHub Releases gratuito (100 GB)
- ✅ CDN global de GitHub
- ✅ Versionado de datos independiente

## 📝 Plan de Implementación

### Sprint 1: Base de Datos (1-2 días)
- [ ] Crear `mexico_dynamic.sqlite3` con schema
- [ ] Script `json_to_sqlite.py`
- [ ] Migrar UDIs, tipo_cambio, TIIE, CETES
- [ ] Tests de integridad

### Sprint 2: DataUpdater (2-3 días)
- [ ] Implementar `catalogmx.data.updater`
- [ ] Caché local + fallback
- [ ] Tests de descarga y fallback
- [ ] CLI: `catalogmx data update`

### Sprint 3: Migración de Catálogos (2 días)
- [ ] Migrar `UDICatalog` a SQLite
- [ ] Migrar `TipoCambioUSDCatalog` a SQLite
- [ ] Migrar otros catálogos Banxico
- [ ] Tests end-to-end

### Sprint 4: Workflow (1 día)
- [ ] GitHub Actions workflow
- [ ] Publicar primera release de datos
- [ ] Documentación de uso

### Sprint 5: Testing & Docs (1 día)
- [ ] Tests de integración
- [ ] Actualizar README.md
- [ ] Guía de migración

**Total: ~1 semana** de desarrollo

## 🔧 Configuración

### Variables de Entorno
```bash
# Deshabilitar auto-actualización (útil para CI/CD)
export CATALOGMX_AUTO_UPDATE=false

# Cambiar directorio de caché
export CATALOGMX_CACHE_DIR=/custom/path

# URL personalizada (self-hosted)
export CATALOGMX_DATA_URL=https://mycdn.com/mexico.sqlite3
```

### Configuración Programática
```python
from catalogmx.data import config

config.AUTO_UPDATE = False
config.CACHE_DIR = Path("/custom/path")
config.MAX_AGE_HOURS = 12  # Actualizar cada 12h
```

## 📚 Referencias

- [SQLite as CDN](https://til.simonwillison.net/sqlite/one-line-csv-operations)
- [GitHub Releases API](https://docs.github.com/en/rest/releases)
- [Data Versioning Best Practices](https://dvc.org/doc/start/data-versioning)

---

**Autor:** Claude AI + Luis Fernando Barrera
**Fecha:** 2025-12-04
**Estado:** ✅ Propuesta Aprobada → En Implementación
