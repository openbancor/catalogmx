# 🔑 Configuración del Token de Banxico

## Paso 1: Obtener Token (Gratis, 2 minutos)

1. Ve a: **https://www.banxico.org.mx/SieAPIRest/service/v1/token**
2. Llena el formulario con tu email
3. Recibirás el token por correo en segundos (ejemplo: `abc123def456ghi789...`)

## Paso 2: Configurar Token Localmente

### Opción A: Variable de entorno permanente (Recomendado)

**En macOS/Linux:**
```bash
# Edita tu archivo de configuración del shell
nano ~/.zshrc  # o ~/.bashrc si usas bash

# Agrega esta línea al final:
export BANXICO_TOKEN="abc123def456ghi789..."

# Guarda y recarga
source ~/.zshrc
```

**En Windows:**
```powershell
# PowerShell (permanente)
[System.Environment]::SetEnvironmentVariable('BANXICO_TOKEN', 'abc123def456...', 'User')
```

### Opción B: Variable temporal (solo sesión actual)

```bash
export BANXICO_TOKEN="abc123def456ghi789..."
```

### Verificar que funciona:

```bash
echo $BANXICO_TOKEN  # Debe mostrar tu token
```

## Paso 3: Ejecutar

### Primera vez (Descarga histórico completo):

```bash
cd catalogmx
export BANXICO_TOKEN="tu_token"  # Si no lo configuraste permanente
python3 packages/shared-data/scripts/fetch_udis_banxico.py --full
```

Esto descargará ~11,000 registros desde 1995. Tomará ~21 segundos.

### Actualizaciones diarias (Solo nuevos datos):

```bash
cd catalogmx
./scripts/full_check.sh
```

Si tienes `BANXICO_TOKEN` configurado, automáticamente:
- ✅ Detecta la última fecha en `udis.json`
- ✅ Solo descarga días faltantes (1-2 requests)
- ✅ Actualiza el archivo
- ✅ Continúa con el resto del build

Si NO tienes token:
- ℹ️ Muestra mensaje informativo
- ✅ Continúa normalmente con datos existentes

## 🤖 GitHub Actions (Automático)

Para que GitHub Actions actualice automáticamente cada día:

1. Ve a tu repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `BANXICO_TOKEN`
4. Value: Tu token de Banxico
5. Click **Add secret**

El workflow `.github/workflows/update-udi.yml` se ejecutará diariamente y creará PRs con datos actualizados.

## 📊 Comportamiento Incremental

```bash
# Primera ejecución (sin udis.json o con --full)
[fetch] Full download mode: starting from 1995-04-04
[fetch] Requesting 1995-04-04 to 1996-04-03... ✓ 365 records
...
[fetch] ✓ Total: 11,000 records

# Ejecuciones siguientes (incremental)
[fetch] Incremental mode: last record is 2025-01-30, fetching from 2025-01-31
[fetch] Requesting 2025-01-31 to 2025-01-31... ✓ 1 record
[fetch] ✓ New records added: 1
[fetch] ✓ Total: 11,001 records
```

## 🎯 Resumen

**Dónde poner el token:**
- Local: `~/.zshrc` → `export BANXICO_TOKEN="..."`
- GitHub: Settings → Secrets → `BANXICO_TOKEN`

**Cuándo correrlo:**
- Primera vez: `python3 ... --full` (manual, una sola vez)
- Después: `./scripts/full_check.sh` (automático, incremental)

