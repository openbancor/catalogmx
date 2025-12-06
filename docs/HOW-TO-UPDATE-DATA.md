# 📊 Cómo se Actualiza la Información en catalogmx

Este documento explica cómo funciona el sistema de actualización automática de datos dinámicos (UDI, tipo de cambio, etc.) **sin necesidad de hacer releases de la librería**.

---

## 🎯 Problema Resuelto

**Antes (Sistema Antiguo):**
```
Datos de Banxico actualizados → Commit JSON → Release v1.2.301 → pip install
Datos de Banxico actualizados → Commit JSON → Release v1.2.302 → pip install
Datos de Banxico actualizados → Commit JSON → Release v1.2.303 → pip install
...
365 releases al año = INVIABLE ❌
```

**Ahora (Sistema Nuevo):**
```
Datos de Banxico actualizados → Publicar en GitHub Releases
                                      ↓
                          Usuario ejecuta catalogmx
                                      ↓
                     Auto-descarga si datos > 24 horas
                                      ↓
                           Datos actualizados ✅

Releases de código: ~12 al año (solo cuando cambia código)
```

---

## 🔄 Flujo de Actualización Automática

### 1. GitHub Actions (Diariamente)

**Workflow:** `.github/workflows/update-dynamic-data.yml`

```yaml
schedule:
  - cron: '0 10 * * *'  # 4 AM Ciudad de México
```

**Pasos:**
1. 🌐 Fetch datos desde API de Banxico
   - UDIs
   - Tipo de Cambio USD/MXN
   - TIIE 28 días
   - CETES 28 días
   - Inflación
   - Salarios Mínimos

2. 📝 Actualizar JSONs en `packages/shared-data/banxico/`

3. 🔨 Generar SQLite unificado:
   ```bash
   python scripts/json_to_sqlite_dynamic.py
   # Genera: mexico_dynamic.sqlite3 (6.38 MB)
   ```

4. ✅ Verificar integridad de la base de datos

5. 📦 Publicar en GitHub Releases:
   ```
   Tag: latest
   Asset: mexico_dynamic.sqlite3
   ```

---

## 💻 Desde el Lado del Usuario

### Primera Ejecución

```python
from catalogmx.catalogs.banxico import get_udi_actual

# Primera vez
udi = get_udi_actual()
```

**Qué sucede internamente:**
```
1. Buscar caché local (~/.catalogmx/)
   ├─ ❌ No existe
   └─ Usar datos empaquetados (fallback)

2. Datos empaquetados:
   └─ catalogmx/data/mexico_dynamic.sqlite3
      └─ Incluido en el wheel/package
         └─ Versión: fecha del último release
```

### Segunda Ejecución (>24 horas después)

```python
from catalogmx.catalogs.banxico import get_udi_actual

# Automático
udi = get_udi_actual()
```

**Qué sucede internamente:**
```
1. Buscar caché local (~/.catalogmx/)
   ├─ ✅ Existe
   └─ Verificar edad

2. Edad > 24 horas?
   ├─ ✅ Sí → Descargar actualización
   │   ├─ URL: github.com/.../releases/download/latest/mexico_dynamic.sqlite3
   │   ├─ Guardar en ~/.catalogmx/mexico_dynamic.sqlite3
   │   └─ Actualizar ~/.catalogmx/version.json
   │
   └─ ❌ No → Usar caché local

3. Consultar datos desde SQLite local
```

### Actualización Manual (Opcional)

```python
from catalogmx.data import update_now

# Forzar actualización inmediata
update_now(force=True, verbose=True)
# 📥 Downloading data from GitHub Releases...
# ✅ Data updated to version 2025-12-04
```

---

## 🗄️ Arquitectura de Almacenamiento

### Caché Local

**Python:**
```
~/.catalogmx/
├── mexico_dynamic.sqlite3  # Base de datos actualizada
└── version.json            # Metadata de versión
```

**TypeScript (Node.js):**
```
~/.catalogmx/
├── mexico_dynamic.sqlite3
└── version.json
```

**TypeScript (Browser):**
```
IndexedDB: catalogmx_cache
├── database (blob)
└── version (json)
```

**Dart/Flutter (Mobile):**
```
/data/user/0/{app}/files/catalogmx/
├── mexico_dynamic.sqlite3
└── version.json
```

**Dart/Flutter (Web):**
```
IndexedDB: catalogmx_cache
├── database (blob)
└── version (json)
```

### Datos Empaquetados (Fallback)

**Python:**
```
site-packages/catalogmx/data/
└── mexico_dynamic.sqlite3  # Incluido en wheel
```

**TypeScript:**
```
node_modules/catalogmx/data/
└── mexico_dynamic.sqlite3  # Incluido en npm package
```

**Dart:**
```
assets/data/
└── mexico_dynamic.sqlite3  # Incluido en APK/IPA
```

---

## ⚙️ Configuración

### Python

```python
import os

# Deshabilitar auto-actualización (usar solo datos empaquetados)
os.environ['CATALOGMX_AUTO_UPDATE'] = 'false'

# Cambiar directorio de caché
os.environ['CATALOGMX_CACHE_DIR'] = '/custom/path'

# Cambiar intervalo de actualización (en horas)
from catalogmx.data import DataUpdater
updater = DataUpdater()
db_path = updater.auto_update(max_age_hours=12)  # Actualizar cada 12h

# URL personalizada (para self-hosted)
os.environ['CATALOGMX_DATA_URL'] = 'https://mycdn.com/mexico.sqlite3'
```

### TypeScript

```typescript
import { DataUpdater } from 'catalogmx';

const updater = new DataUpdater({
  autoUpdate: false,  // Deshabilitar auto-update
  cacheDir: '/custom/path',
  maxAgeHours: 12,    // Actualizar cada 12h
  dataUrl: 'https://mycdn.com/mexico.sqlite3'
});
```

### Dart

```dart
import 'package:catalogmx/src/data/updater.dart';

final updater = DataUpdater(
  DataUpdaterConfig(
    autoUpdate: false,
    maxAgeHours: 12,
    dataUrl: 'https://mycdn.com/mexico.sqlite3',
  ),
);
```

---

## 📅 Frecuencia de Actualización

| Dato | Fuente | Frecuencia Banxico | Actualización Catalogmx |
|------|--------|-------------------|------------------------|
| UDI | Banxico SP68257 | Diaria | Diaria (4 AM) |
| Tipo Cambio FIX | Banxico SF43718 | Diaria | Diaria (4 AM) |
| TIIE 28 | Banxico SF43783 | Diaria | Diaria (4 AM) |
| CETES 28 | Banxico SF43936 | Semanal | Diaria (4 AM) |
| Inflación | Banxico SP30579 | Mensual | Diaria (4 AM) |
| Salarios Mínimos | Banxico SL11298 | Anual | Diaria (4 AM) |

**Usuario descarga:** Cada 24 horas (o cuando lo configure)

---

## 🔍 Verificación Manual

### Ver Versión Local

```python
from catalogmx.data import get_version

print(get_version())
# Output: "2025-12-04"
```

### Ver Edad de Datos

```python
from catalogmx.data import DataUpdater

updater = DataUpdater()
age_hours = updater.get_local_age_hours()

if age_hours:
    print(f"Datos actualizados hace {age_hours:.1f} horas")
else:
    print("No hay caché local")
```

### Ver Metadata Completa

```python
from catalogmx.data import DataUpdater

updater = DataUpdater()
info = updater.get_version_info()

print(info)
# {
#   'version': '2025-12-04',
#   'age_hours': '12.5',
#   'updated_at': '2025-12-04T09:30:00',
#   'source': 'github_releases',
#   'url': 'https://github.com/...'
# }
```

---

## 🚨 Troubleshooting

### "No internet connection, using embedded data"

**Causa:** No hay conexión a internet o GitHub está caído

**Solución:**
- Catalogmx funciona offline usando datos empaquetados
- Los datos pueden estar desactualizados según la fecha del último release
- Cuando vuelva la conexión, se actualizará automáticamente

### "FileNotFoundError: No database available"

**Causa:** Auto-update está deshabilitado y no hay caché local

**Solución:**
```python
# Opción 1: Habilitar auto-update
import os
os.environ['CATALOGMX_AUTO_UPDATE'] = 'true'

# Opción 2: Descargar manualmente
from catalogmx.data import update_now
update_now()
```

### "Database is locked"

**Causa:** Múltiples procesos intentando escribir al SQLite

**Solución:**
- Catalogmx solo LEE de la base de datos (no debería pasar)
- Si ocurre, cerrar otros procesos que usen catalogmx
- Verificar permisos del archivo

### Datos parecen desactualizados

**Verificar:**
```python
from catalogmx.data import get_version
print(f"Versión local: {get_version()}")

# Comparar con versión en GitHub Releases
# https://github.com/openbancor/catalogmx/releases/latest
```

**Forzar actualización:**
```python
from catalogmx.data import update_now
update_now(force=True, verbose=True)
```

---

## 📊 Métricas de Rendimiento

### Tamaños de Descarga

| Componente | Tamaño | Frecuencia |
|------------|--------|------------|
| mexico_dynamic.sqlite3 | 6.38 MB | Primera vez + cada 24h |
| Incremental (futuro) | ~20 KB | Cada consulta |

### Tiempos de Respuesta

| Operación | Python | TypeScript | Dart |
|-----------|--------|------------|------|
| Primera carga (descarga) | 2-3s | 2-3s | 2-3s |
| Caché local (SQLite) | <1ms | <1ms | <1ms |
| get_udi_actual() | <1ms | <1ms | <1ms |
| get_por_anio() (365 registros) | 5-10ms | 10-15ms | 5-10ms |

---

## 🎉 Beneficios

### Para Usuarios

- ✅ **Datos siempre actualizados** (sin reinstalar)
- ✅ **Funciona offline** (fallback a caché)
- ✅ **Zero configuración** (automático por defecto)
- ✅ **Multiplataforma** (Python/TS/Dart)

### Para Desarrolladores

- ✅ **Sin releases diarios** (solo cuando cambia código)
- ✅ **Versionado semántico real** (1.2.3 → 1.3.0)
- ✅ **Pipeline simplificado** (datos separados de código)

### Números

- 🚫 **Antes:** 1,095 releases/año (365 por plataforma)
- ✅ **Después:** 36 releases/año (12 por plataforma)
- 💾 **Ahorro:** 97% menos releases

---

## 📚 Referencias

- [Diseño completo](./SQLITE-UPDATE-DECOUPLING.md)
- [Arquitectura multiplataforma](./MULTI-PLATFORM-SQLITE.md)
- [Guía de implementación](./IMPLEMENTATION-GUIDE.md)
- [Workflow de GitHub Actions](../.github/workflows/update-dynamic-data.yml)

---

**Última actualización:** 2025-12-04
**Versión del sistema:** 1.0
