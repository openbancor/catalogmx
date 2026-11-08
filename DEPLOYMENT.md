# 🚀 Flujo de Publicación a main/master

> **Modo de datos:** desde este cambio el modo por defecto del resolvedor es `offline` (cambio de comportamiento: corresponde a versión **menor**, no parche). Los entornos de CI que necesiten descargar deben fijar `CATALOGMX_DATA_MODE=fetch-missing` (los workflows de datos ya lo hacen). El comportamiento anterior se recupera con esa variable.

## Antes de Commitear

### 1. Ejecutar el Script de Validación Completo

```bash
cd /ruta/a/catalogmx
./scripts/full_check.sh
```

Este script ejecuta **TODO** el pipeline de calidad:

✅ **SQLite** (Genera y limpia mexico.sqlite3)
- `python build_unified_sqlite.py`
- `PRAGMA journal_mode=DELETE` ← Cierra WAL
- `rm *.sqlite3-shm *.sqlite3-wal` ← Limpia archivos
- Copia a `webapp/public/data/`

✅ **Webapp** (TypeScript + React)
- Build con Vite
- Type checking

✅ **TypeScript Package**
- Lint + fix
- Format
- Type check

✅ **Python Package**
- Format con `black`
- Lint con `ruff --fix`
- Type check con `mypy`
- Tests con cobertura >90%

✅ **Dart Package**
- Format con `dart format`
- Analyze con `dart analyze`
- Tests con `dart test`

### 2. Si TODO Pasa → Commit

```bash
git add .
git commit -m "feat: descripción de cambios"
git push origin main
```

## 🤖 Qué Sucede Automáticamente en GitHub

### Workflow 1: `sqlite-assets.yml`
Se activa cuando detecta cambios en `packages/shared-data/**`

```
1. Genera mexico.sqlite3 fresco
2. Cierra WAL (PRAGMA journal_mode=DELETE)
3. Limpia archivos .sqlite3-shm y .sqlite3-wal
4. Publica a GitHub Release "sqlite-assets"
```

**Resultado:** Assets disponibles en:
```
https://github.com/openbancor/catalogmx/releases/download/sqlite-assets/mexico.sqlite3
```

### Workflow 2: `webapp-pages.yml`
Se activa cuando detecta cambios en `packages/webapp/**` o `packages/shared-data/**`

```
1. Genera mexico.sqlite3 fresco en CI
2. Cierra WAL
3. Copia a public/data/
4. npm run build (webapp)
5. Deploy a GitHub Pages
```

**Resultado:** Webapp disponible en:
```
https://openbancor.github.io/catalogmx/
```

## 📦 Checklist Visual

```
┌──────────────────────────────────┐
│ 1. ./scripts/full_check.sh      │
│    ✓ Build SQLite (sin WAL)      │
│    ✓ Build webapp                │
│    ✓ Lint TypeScript             │
│    ✓ Tests Python (>90%)         │
│    ✓ Format Dart                 │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ 2. git add .                     │
│    git commit -m "mensaje"       │
│    git push origin main          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ 3. GitHub Actions (automático)   │
│    ├─ sqlite-assets.yml          │
│    │  └─ Publica mexico.sqlite3  │
│    └─ webapp-pages.yml           │
│       └─ Deploy webapp            │
└──────────────────────────────────┘
```

## ⚠️ Importante

- **SIEMPRE** ejecuta `./scripts/full_check.sh` antes de commitear
- Si falla algún check, **no commitees** hasta arreglarlo
- El script ya incluye el cierre de WAL, así que los assets quedan listos para navegador

## 🎯 One-liner (Si estás seguro)

```bash
./scripts/full_check.sh && git add . && git commit -m "feat: tu mensaje" && git push
```

Si `full_check.sh` pasa, todo está listo para producción. 🚀

