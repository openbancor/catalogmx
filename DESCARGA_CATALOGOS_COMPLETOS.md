# 📥 Cómo Obtener los Catálogos Completos

Este documento explica cómo descargar y usar los catálogos oficiales completos de INEGI y SEPOMEX.

## 🏛️ INEGI Municipios (2,469 total)

### Opción 1: Descarga Oficial INEGI

1. **Visita el sitio oficial de INEGI**:
   ```
   https://www.inegi.org.mx/app/ageeml/
   ```

2. **Selecciona**:
   - Agregación: "Área Geoestadística Municipal (AGEM)"
   - Fecha: "Más reciente disponible"
   - Formato: "Excel" o "TXT"

3. **Descarga el archivo** y guárdalo como `municipios_inegi.xlsx`

4. **Procesa con Python**:
   ```bash
   pip install pandas openpyxl
   python scripts/process_inegi_excel.py municipios_inegi.xlsx
   ```

### Opción 2: Marco Geoestadístico Completo

1. **Descarga el shapefile completo**:
   ```
   https://www.inegi.org.mx/app/biblioteca/ficha.html?upc=889463807469
   ```

2. **Archivo**: "Marco Geoestadístico, diciembre 2023"

3. **Requiere**: `geopandas` para procesar shapefiles

4. **Comando**:
   ```bash
   pip install geopandas
   python scripts/process_inegi_shapefile.py marco_geo.shp
   ```

### Opción 3: API de INEGI (si disponible)

```python
import requests

url = "https://www.inegi.org.mx/app/api/denue/v1/consulta/Nombre/..."
response = requests.get(url)
```

### Opción 4: Repositorio Open Source

Existen repositorios comunitarios con los datos:

```bash
git clone https://github.com/Cecilapp/Mexico-zip-codes.git
# O buscar "mexico municipios json" en GitHub
```

---

## 📮 SEPOMEX Códigos Postales (~150,000 total)

### Opción 1: Descarga Oficial SEPOMEX

1. **Sitio oficial**:
   ```
   https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx
   ```

2. **El archivo generalmente es**:
   - Formato: Excel (.xlsx) o TXT
   - Tamaño: ~15-20 MB
   - Registros: ~150,000 códigos postales

3. **Procesamiento**:
   ```bash
   pip install pandas openpyxl
   python scripts/download_sepomex_complete.py
   ```

### Opción 2: Base de Datos SQLite (Recomendado)

Para ~150,000 registros, se recomienda SQLite:

```bash
python scripts/create_sepomex_sqlite.py
```

Esto crea `sepomex.db` con búsquedas rápidas:

```python
from catalogmx.db import sepomex_db

# Buscar por código postal
results = sepomex_db.search_by_cp("06700")

# Buscar por colonia
results = sepomex_db.search_by_colonia("Roma Norte")

# Buscar por municipio
results = sepomex_db.search_by_municipio("Benito Juárez")
```

### Opción 3: API de SEPOMEX

```python
import requests

url = f"https://api.sepomex.gob.mx/codigopostal/{codigo}"
response = requests.get(url)
```

### Opción 4: Repositorios Open Source

```bash
# Catálogo community-maintained
git clone https://github.com/Cecilapp/Mexico-zip-codes.git

# O usar este dataset completo:
wget https://raw.githubusercontent.com/IcaliaLabs/sepomex/master/sepomex_db.csv
```

---

## 📊 Catálogos Actuales en catalogmx

### INEGI Municipios
- **Actual**: 209 municipios (todos los estados + capitales + ciudades principales)
- **Completo**: 2,469 municipios
- **Archivo**: `packages/shared-data/inegi/municipios_completo.json`

### SEPOMEX Códigos Postales
- **Actual**: 273 códigos postales (32 estados + ciudades principales + múltiples zonas)
- **Completo**: ~150,000 códigos postales
- **Archivo**: `packages/shared-data/sepomex/codigos_postales_completo.json`

---

## 🚀 Uso con catalogmx

Los catálogos actuales cubren:
- ✅ Todos los 32 estados
- ✅ Todas las capitales estatales
- ✅ Todas las ciudades principales (100k+ habitantes)
- ✅ Múltiples zonas por área metropolitana

```python
from catalogmx.catalogs.inegi import MunicipiosCatalog
from catalogmx.catalogs.sepomex import CodigosPostales

# Buscar municipio
mun = MunicipiosCatalog.get_municipio("09015")  # Cuauhtémoc, CDMX
print(mun['nom_municipio'])

# Buscar código postal
cp = CodigosPostales.get_by_cp("06700")  # Roma Norte
print(cp[0]['asentamiento'])

# Buscar por estado
municipios_jalisco = MunicipiosCatalog.get_by_entidad("14")
print(f"Municipios en Jalisco: {len(municipios_jalisco)}")
```

---

## 📦 Conversión a SQLite para Datasets Completos

Para los catálogos completos (~150k+ registros), se recomienda SQLite:

```bash
# Convertir SEPOMEX JSON a SQLite
python scripts/json_to_sqlite.py \
  --input packages/shared-data/sepomex/codigos_postales_completo.json \
  --output packages/shared-data/sepomex/sepomex.db \
  --table codigos_postales

# Usar la base de datos
python
>>> import sqlite3
>>> conn = sqlite3.connect('packages/shared-data/sepomex/sepomex.db')
>>> cursor = conn.execute("SELECT * FROM codigos_postales WHERE cp='06700'")
>>> results = cursor.fetchall()
```

---

## 🔄 Actualización de Catálogos

Los catálogos oficiales se actualizan:

- **INEGI Municipios**: Anualmente (generalmente sin cambios)
- **SEPOMEX Códigos Postales**: Mensualmente

Para actualizar:

```bash
# Descargar versiones más recientes
python scripts/update_all_catalogs.py

# Verificar cambios
python scripts/check_catalog_updates.py
```

---

## 💡 Recomendaciones

### Para Desarrollo / Testing
✅ **Usar catálogos actuales** (209 municipios, 273 CPs)
- Carga rápida
- Cobertura completa de casos comunes
- Fácil de versionar en Git

### Para Producción
✅ **Descargar catálogos completos** (2,469 municipios, 150k CPs)
- Usar SQLite para códigos postales
- Mantener JSON para municipios (archivo pequeño)
- Actualizar mensualmente

---

## 📞 Soporte

Si tienes problemas descargando los catálogos oficiales:

1. Verifica conectividad a sitios de gobierno
2. Usa VPN si es necesario
3. Consulta repositorios community-maintained
4. Abre un issue en GitHub con detalles del error
