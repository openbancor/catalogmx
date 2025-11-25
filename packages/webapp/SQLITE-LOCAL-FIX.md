# Solución al error "file is not a database" en desarrollo local

## Problema

Cuando ejecutas el proyecto en local (`npm run dev`), SQLite falla con "file is not a database" porque:

1. El archivo `mexico.sqlite3` tiene archivos WAL asociados (`.sqlite3-shm`, `.sqlite3-wal`)
2. sql.js no puede leer archivos con WAL activo
3. Necesitas un archivo SQLite "limpio" sin journal

## Solución rápida

### Opción 1: Cerrar la base de datos antes de copiarla (Recomendado)

```bash
cd packages/shared-data

# Si tienes sqlite3 instalado
sqlite3 public/data/mexico.sqlite3 "PRAGMA wal_checkpoint(TRUNCATE); VACUUM;"

# Luego copia
cp public/data/mexico.sqlite3 ../webapp/public/data/mexico.sqlite3
```

### Opción 2: Regenerar sin WAL

```bash
cd packages/shared-data

# Regenera la base de datos
python build_unified_sqlite.py --output temp.sqlite3

# Asegúrate de que esté en modo DELETE (no WAL)
sqlite3 temp.sqlite3 "PRAGMA journal_mode=DELETE; VACUUM;"

# Copia al webapp
cp temp.sqlite3 ../webapp/public/data/mexico.sqlite3
```

### Opción 3: Automatizar en el script de build

Edita `scripts/build-sqlite-pipeline.mjs` para agregar:

```javascript
import { execSync } from 'child_process';

// Después de generar mexico.sqlite3
execSync('sqlite3 public/data/mexico.sqlite3 "PRAGMA wal_checkpoint(TRUNCATE); PRAGMA journal_mode=DELETE; VACUUM;"');
```

## Verificación

Para verificar que el archivo está limpio:

```bash
cd packages/webapp/public/data
ls -la mexico.sqlite3*

# Deberías ver SOLO mexico.sqlite3
# NO deberías ver mexico.sqlite3-shm o mexico.sqlite3-wal
```

## Nota sobre HTTP VFS

El SPEC-sqlite-vfs.MD menciona SQLite WASM con HTTP VFS, pero actualmente usan **sql.js** que:
- ✅ Funciona perfectamente en el navegador
- ❌ Descarga el archivo completo (no usa HTTP Range)
- ✅ Es más simple y compatible

Para implementar HTTP Range VFS real, necesitarían migrar a `@sqlite.org/sqlite-wasm` con `opfs-http`, pero eso es un cambio mayor.

