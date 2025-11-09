# 🗺️ ROADMAP - catalogmx

**Roadmap detallado por catálogo, versiones y estrategia**

**Última actualización**: 2025-11-08  
**Versión actual**: v0.3.0  
**Siguiente release**: v0.4.0 (Q1 2025)

---

## 📊 Estado General del Proyecto

### Métricas Actuales (v0.3.0)
- ✅ **Catálogos totales**: 43 catálogos
- ✅ **Registros totales**: 170,505+ registros
- ✅ **Población cubierta**: 126,014,024 habitantes (100%)
- ✅ **Validadores**: 4 (RFC, CURP, CLABE, NSS)
- ✅ **Lenguajes**: Python 3.10+, TypeScript 5.0+
- ✅ **Documentación**: Bilingüe (English + Español)

---

## 🎯 Por Versión

### ✅ v0.3.0 (ACTUAL - Nov 2025) - COMPLETADO

#### Catálogos Completos Agregados
- [x] SEPOMEX: 157,252 códigos postales (43.53 MB)
- [x] INEGI: 2,478 municipios completos (0.98 MB)
- [x] INEGI: 10,635 localidades con GPS (5.22 MB)

#### Funcionalidades Nuevas
- [x] Búsqueda geográfica por coordenadas GPS
- [x] Filtros de población (min/max)
- [x] Clasificación urbano/rural
- [x] Búsqueda por proximidad (radio en km)

#### Infraestructura
- [x] Scripts de procesamiento para SEPOMEX e INEGI
- [x] Documentación bilingüe (README.md + README.es.md)
- [x] Type hints Python 3.10+ (PEP 604)
- [x] .gitignore actualizado

---

### 🚧 v0.4.0 (Q1 2025) - PLANEADO

#### TypeScript Sync
- [ ] Implementar `LocalidadesCatalog` en TypeScript
- [ ] Actualizar tipos TypeScript con nuevos campos
- [ ] Tests TypeScript para localidades
- [ ] Build y publish TypeScript actualizado

#### SQLite Implementation
- [ ] Convertir SEPOMEX a SQLite (~43 MB → ~25 MB)
- [ ] Convertir Localidades a SQLite (~5 MB → ~3 MB)
- [ ] API Python para SQLite catalogs
- [ ] Lazy loading desde SQLite
- [ ] Índices optimizados (B-tree)

#### Geocoding Integration
- [ ] Geocodificar códigos postales (añadir lat/lon)
- [ ] API de geocodificación (Google/OSM)
- [ ] Tabla CP con coordenadas GPS
- [ ] Vinculación precisa CP ↔ Localidad

#### Tabla de Correspondencia
- [ ] Pre-calcular vinculación CP ↔ Localidad
- [ ] Fuzzy matching de nombres
- [ ] Score de confianza (0-100)
- [ ] API: `get_cp_for_locality(cvegeo)`
- [ ] API: `get_localities_for_cp(cp)`

#### Examples & Documentation
- [ ] Directorio `examples/` con casos de uso
- [ ] FastAPI REST API example
- [ ] Next.js frontend example
- [ ] Flask simple server
- [ ] GraphQL API example

---

### 🔮 v0.5.0 (Q2-Q3 2025) - FUTURO

#### Nuevos Validadores
- [ ] ISAN - Identificador de Seguridad en Alimentos Nacionales
- [ ] Placas vehiculares (formato por estado)
- [ ] MRZ - Machine Readable Zone (pasaportes)
- [ ] Licencias de conducir

#### Nuevos Catálogos
- [ ] IFT - Catálogos de telecomunicaciones
- [ ] IMSS - Catálogos de seguridad social
- [ ] TIGIE - Arancel de aduanas (~10k partidas)
- [ ] PROFECO - Proveedores certificados

#### Machine Learning
- [ ] Normalización de direcciones con ML
- [ ] Corrección automática de errores
- [ ] Sugerencias de direcciones
- [ ] Detección de duplicados

#### Performance
- [ ] WebAssembly para validadores
- [ ] Cache layer (Redis opcional)
- [ ] CDN para catálogos JSON
- [ ] Compresión gzip/brotli

---

## 📦 Roadmap por Catálogo

### 1. SEPOMEX - Códigos Postales

#### ✅ v0.3.0 (COMPLETADO)
- [x] Catálogo completo: 157,252 códigos postales
- [x] Búsqueda por CP, municipio, estado
- [x] Validación de códigos postales
- [x] Formato JSON (43.53 MB)

#### 🚧 v0.4.0 (PLANEADO)
- [ ] **Geocodificación**: Añadir lat/lon a cada CP
  - Fuente: Google Geocoding API / OpenStreetMap
  - Script: `scripts/geocode_postal_codes.py`
  - Resultado: `codigos_postales_con_gps.json` (~55 MB)
  
- [ ] **SQLite Database**
  - Convertir a SQLite para consultas eficientes
  - Tamaño: ~25 MB (vs 43 MB JSON)
  - Índices: cp, municipio, estado, lat/lon (spatial)
  - API: `SepomexDB.query_by_location(lat, lon, radius)`

- [ ] **Vinculación con Localidades**
  - Tabla de correspondencia CP ↔ CVEGEO
  - Script: `scripts/link_cp_to_localities.py`
  - Precisión esperada: 70-80%

#### 🔮 v0.5.0 (FUTURO)
- [ ] Versiones históricas (2020, 2021, 2022...)
- [ ] API de cambios (CPs nuevos/eliminados)
- [ ] Auto-update desde SEPOMEX (mensual)

**Frecuencia de actualización**: Mensual (SEPOMEX publica actualizaciones)

---

### 2. INEGI - Municipios

#### ✅ v0.3.0 (COMPLETADO)
- [x] Catálogo completo: 2,478 municipios
- [x] Datos de población (Censo 2020)
- [x] Búsqueda por código, entidad
- [x] Formato JSON (0.98 MB)

#### 🚧 v0.4.0 (PLANEADO)
- [ ] **Datos Adicionales**
  - Superficie territorial (km²)
  - Densidad poblacional
  - Grado de marginación (CONAPO)
  - Indicadores económicos

- [ ] **Coordenadas de Cabeceras**
  - Lat/lon de cada cabecera municipal
  - Fuente: INEGI Marco Geoestadístico
  - Útil para mapas y visualización

- [ ] **API Enriquecida**
  - `get_by_population_range(min, max)`
  - `get_by_surface_area(min, max)`
  - `search_near_coordinate(lat, lon, radius)`
  - `get_by_marginalization_level(level)`

#### 🔮 v0.5.0 (FUTURO)
- [ ] Cambios históricos (creación/fusión de municipios)
- [ ] Límites territoriales (shapefiles)
- [ ] Integración con mapas (GeoJSON)

**Frecuencia de actualización**: Anual (INEGI actualiza raramente)

---

### 3. INEGI - Localidades

#### ✅ v0.3.0 (COMPLETADO)
- [x] Catálogo filtrado: 10,635 localidades (1,000+ hab)
- [x] Coordenadas GPS completas
- [x] Clasificación urbano/rural
- [x] Búsqueda geográfica por radio
- [x] Formato JSON (5.22 MB)

#### 🚧 v0.4.0 (PLANEADO)
- [ ] **SQLite Database**
  - Más eficiente para búsquedas geográficas
  - Tamaño: ~3 MB (vs 5.22 MB JSON)
  - Índices espaciales (R-tree para lat/lon)
  - Queries: `SELECT * WHERE distance(lat1,lon1,lat2,lon2) < radius`

- [ ] **Vinculación CP ↔ Localidad**
  - Tabla pre-calculada
  - Script: `scripts/link_localities_to_cp.py`
  - Método: Fuzzy matching + distancia geográfica
  - Resultado: `correspondencia_cp_localidad.json`

- [ ] **Filtros Adicionales**
  - `get_by_altitude_range(min, max)` - Por altitud
  - `get_coastal()` - Localidades costeras
  - `get_border()` - Localidades fronterizas
  - `get_tourist()` - Destinos turísticos (>10k turistas/año)

#### 🔮 v0.5.0 (FUTURO)
- [ ] Localidades pequeñas (100-999 hab) - opcional
- [ ] Rancherías y pueblos (<100 hab) - bajo demanda
- [ ] Datos climatológicos (temperatura, precipitación)
- [ ] Servicios disponibles (hospital, escuela, etc.)

**Frecuencia de actualización**: Anual (INEGI - Censo/Encuestas)

---

### 4. INEGI - Estados

#### ✅ v0.3.0 (ACTUAL)
- [x] Catálogo básico: 32 estados
- [x] Incluido en municipios y localidades

#### 🚧 v0.4.0 (PLANEADO)
- [ ] **Catálogo Enriquecido**
  - Capital de cada estado
  - Superficie territorial
  - Población total por estado
  - PIB estatal
  - Coordenadas centroides

- [ ] **Clase Dedicada**
  ```python
  from catalogmx.catalogs.inegi import EstadosCatalog
  
  estado = EstadosCatalog.get_estado("09")  # CDMX
  municipios = estado.get_municipios()
  localidades = estado.get_localidades()
  poblacion_total = estado.get_population()
  ```

**Frecuencia de actualización**: Anual

---

### 5. SAT - CFDI 4.0

#### ✅ v0.3.0 (ACTUAL)
- [x] 9 catálogos core implementados
- [x] Validación por tipo de persona
- [x] ~30 registros totales

#### 🚧 v0.4.0 (PLANEADO)
- [ ] **Catálogos Faltantes**
  - c_TipoFactor (2 tipos)
  - c_TasaOCuota (Tasas e ISR/IVA)
  - c_Meses (12 meses)
  - c_NumPedimentoAduana (validación de formato)
  - c_Periodicidad (7 periodicidades)

- [ ] **Validación Cruzada**
  - Validar combinaciones válidas (Régimen + Uso CFDI)
  - Validar impuestos aplicables por régimen
  - Sugerencias automáticas de campos

- [ ] **API de Validación Completa**
  ```python
  from catalogmx.validators.cfdi import CFDIValidator
  
  validator = CFDIValidator()
  result = validator.validate_full({
      'rfc_emisor': 'XAXX010101000',
      'regimen': '605',
      'uso_cfdi': 'G03',
      'forma_pago': '03',
      'metodo_pago': 'PUE'
  })
  
  if result.is_valid:
      print("✅ CFDI válido")
  else:
      print(f"❌ Errores: {result.errors}")
  ```

#### 🔮 v0.5.0 (FUTURO)
- [ ] Versiones históricas (CFDI 3.3, 4.0)
- [ ] Migraciones automáticas 3.3 → 4.0
- [ ] Catálogos deprecados marcados

**Frecuencia de actualización**: Trimestral (SAT actualiza cada 3-6 meses)

---

### 6. SAT - Comercio Exterior 2.0

#### ✅ v0.3.0 (ACTUAL)
- [x] 8 catálogos implementados
- [x] ~500 registros totales
- [x] Validación de países, monedas, incoterms

#### 🚧 v0.4.0 (PLANEADO)
- [ ] **Catálogos Faltantes**
  - c_TipoOperacion (2 tipos)
  - c_ClavePedimento completo (validación de formato)
  - Fracción arancelaria (conexión con TIGIE)

- [ ] **Validación Avanzada**
  - Validar Incoterm por tipo de transporte
  - Sugerir unidades de aduana por producto
  - Validar combinaciones país + registro tributario

**Frecuencia de actualización**: Semestral

---

### 7. SAT - Carta Porte 3.0

#### ✅ v0.3.0 (ACTUAL)
- [x] 7 catálogos implementados
- [x] ~3,400 registros (material peligroso)
- [x] Aeropuertos, puertos, carreteras

#### 🚧 v0.4.0 (PLANEADO)
- [ ] **Catálogos Faltantes**
  - c_Estacion (estaciones de ferrocarril)
  - c_ContenedorMaritimo (tipos de contenedor)
  - c_ClaveSTCC (Standard Transport Commodity Code)
  - c_ParteTransporte (partes del vehículo)

- [ ] **Rutas Pre-calculadas**
  - Distancias entre aeropuertos
  - Distancias entre puertos
  - Carreteras sugeridas entre ciudades
  - Tiempos estimados de traslado

- [ ] **Validación de Rutas**
  ```python
  from catalogmx.validators.carta_porte import RouteValidator
  
  route = RouteValidator.validate_route(
      origin='MEX',  # Aeropuerto CDMX
      destination='GDL',  # Aeropuerto Guadalajara
      transport_type='Aéreo'
  )
  
  print(f"Distancia: {route.distance_km} km")
  print(f"Tiempo estimado: {route.estimated_hours} hrs")
  ```

**Frecuencia de actualización**: Anual

---

### 8. SAT - Nómina 1.2

#### ✅ v0.3.0 (ACTUAL)
- [x] 7 catálogos implementados
- [x] ~100 registros totales
- [x] Validación de contratos, jornadas, riesgos

#### 🚧 v0.4.0 (PLANEADO)
- [ ] **Catálogos Faltantes**
  - c_OrigenRecurso (origen de recursos)
  - c_Estado (para ISR estatal)

- [ ] **Calculadora de Nómina**
  ```python
  from catalogmx.calculators.nomina import NominaCalculator
  
  calc = NominaCalculator(
      salario_diario=500,
      periodicidad='04',  # Semanal
      tipo_jornada='01',  # Diurna
      riesgo_puesto='I'   # Clase I
  )
  
  result = calc.calculate()
  print(f"Salario: ${result.salario_total}")
  print(f"IMSS: ${result.imss_patronal}")
  print(f"ISR: ${result.isr_retenido}")
  ```

**Frecuencia de actualización**: Anual

---

### 9. Banxico - Bancos

#### ✅ v0.3.0 (ACTUAL)
- [x] 110 instituciones financieras
- [x] Participantes SPEI
- [x] Códigos bancarios

#### 🚧 v0.4.0 (PLANEADO)
- [ ] **Datos Adicionales**
  - Tipo de institución (banco, SOFOM, etc.)
  - Fecha de constitución
  - Estado de operación (activo/inactivo)
  - URL del banco

- [ ] **Validación de CLABE Mejorada**
  ```python
  from catalogmx.validators import clabe
  from catalogmx.catalogs.banxico import BankCatalog
  
  result = clabe.validate_clabe_full("002010077777777771")
  # {
  #   'valid': True,
  #   'bank': 'Banamex',
  #   'branch': '01007',
  #   'account': '77777777',
  #   'spei_participant': True
  # }
  ```

**Frecuencia de actualización**: Trimestral

---

### 10. IFT - Telecomunicaciones (NUEVO)

#### 🔮 v0.5.0 (FUTURO)
- [ ] Operadores de telefonía móvil
- [ ] Operadores de televisión
- [ ] Operadores de internet
- [ ] Rangos de numeración telefónica
- [ ] Validador de números telefónicos mexicanos

---

### 11. IMSS - Seguridad Social (NUEVO)

#### 🔮 v0.5.0 (FUTURO)
- [ ] Subdelegaciones IMSS
- [ ] Clínicas y hospitales
- [ ] Catálogo de enfermedades
- [ ] Catálogo de medicamentos
- [ ] Validador NSS mejorado

---

### 12. TIGIE - Arancel de Aduanas (NUEVO)

#### 🔮 v0.5.0 (FUTURO)
- [ ] Fracciones arancelarias (~10,000)
- [ ] Tasas de impuesto por fracción
- [ ] Unidades de medida
- [ ] Regulaciones y restricciones
- [ ] Búsqueda por descripción

**Desafío**: Catálogo muy grande, requiere SQLite

---

## 🔄 Estrategia de Actualización de Catálogos

### 📅 Calendario de Actualizaciones

| Catálogo | Frecuencia | Fuente | Última Actualización |
|----------|------------|--------|---------------------|
| **SEPOMEX** | Mensual | correosdemexico.gob.mx | Nov 2025 ✅ |
| **INEGI Municipios** | Anual | inegi.org.mx | Oct 2025 ✅ |
| **INEGI Localidades** | Anual | inegi.org.mx | Oct 2025 ✅ |
| **SAT CFDI** | Trimestral | sat.gob.mx | Nov 2024 |
| **SAT Com. Ext.** | Semestral | sat.gob.mx | Jun 2024 |
| **SAT Carta Porte** | Anual | sat.gob.mx | 2024 |
| **SAT Nómina** | Anual | sat.gob.mx | 2023 |
| **Banxico** | Trimestral | banxico.org.mx | 2024 |

### 🤖 Automatización Propuesta

#### Script Unificado de Actualización
```bash
# v0.4.0 - Script de actualización automática
python scripts/update_all_catalogs.py --check

# Output:
# ✅ SEPOMEX: Nueva versión disponible (Nov 2025)
# ⏸️ INEGI: Sin cambios
# ✅ SAT CFDI: Actualización disponible (Dic 2024)
# ⏸️ Banxico: Sin cambios

python scripts/update_all_catalogs.py --download SEPOMEX SAT_CFDI

# Descarga y convierte automáticamente
```

#### Verificación de Integridad
```python
# v0.4.0 - Verificar integridad de catálogos
from catalogmx.integrity import verify_catalogs

result = verify_catalogs()

for catalog, status in result.items():
    print(f"{catalog}: {status['checksum_valid']}")
    print(f"  Records: {status['total_records']}")
    print(f"  Last updated: {status['last_updated']}")
```

#### CI/CD Integration
```yaml
# .github/workflows/update-catalogs.yml
name: Update Catalogs

on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly on the 1st

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check for updates
        run: python scripts/check_catalog_updates.py
      - name: Create PR if updates available
        if: updates_found
        uses: peter-evans/create-pull-request@v5
```

---

## 💾 Estrategia SQLite

### ¿Cuándo usar SQLite vs JSON?

| Catálogo | Registros | Formato Actual | Recomendación v0.4.0 |
|----------|-----------|----------------|---------------------|
| SEPOMEX | 157,252 | JSON (43 MB) | **SQLite** (~25 MB) ✅ |
| Localidades | 10,635 | JSON (5 MB) | **SQLite** (~3 MB) ✅ |
| Municipios | 2,478 | JSON (1 MB) | **JSON** (OK) |
| SAT CFDI | ~30 | JSON (<1 MB) | **JSON** (OK) |
| Material Peligroso | 3,000 | JSON (~2 MB) | **JSON** (OK) |

**Regla**: SQLite para catálogos >10,000 registros o con búsquedas geográficas

### Implementación SQLite (v0.4.0)

#### Estructura de Tabla SEPOMEX
```sql
CREATE TABLE codigos_postales (
    id INTEGER PRIMARY KEY,
    cp TEXT NOT NULL,
    asentamiento TEXT,
    tipo_asentamiento TEXT,
    municipio TEXT,
    estado TEXT,
    codigo_estado TEXT,
    codigo_municipio TEXT,
    latitud REAL,        -- Nuevo: geocodificado
    longitud REAL,       -- Nuevo: geocodificado
    zona TEXT,
    
    -- Índices
    UNIQUE(cp, asentamiento)
);

CREATE INDEX idx_cp ON codigos_postales(cp);
CREATE INDEX idx_municipio ON codigos_postales(municipio);
CREATE INDEX idx_estado ON codigos_postales(estado);
CREATE INDEX idx_location ON codigos_postales(latitud, longitud);  -- Spatial
```

#### Estructura de Tabla Localidades
```sql
CREATE TABLE localidades (
    cvegeo TEXT PRIMARY KEY,
    cve_entidad TEXT NOT NULL,
    nom_entidad TEXT,
    cve_municipio TEXT,
    nom_municipio TEXT,
    cve_localidad TEXT,
    nom_localidad TEXT,
    ambito TEXT,           -- U/R
    latitud REAL NOT NULL,
    longitud REAL NOT NULL,
    altitud INTEGER,
    poblacion_total INTEGER,
    poblacion_masculina INTEGER,
    poblacion_femenina INTEGER,
    viviendas_habitadas INTEGER
);

CREATE INDEX idx_municipio ON localidades(cve_municipio);
CREATE INDEX idx_estado ON localidades(cve_entidad);
CREATE INDEX idx_nombre ON localidades(nom_localidad);
CREATE INDEX idx_poblacion ON localidades(poblacion_total);

-- Índice espacial con extensión R*Tree
CREATE VIRTUAL TABLE localidades_spatial USING rtree(
    id,
    min_lat, max_lat,
    min_lon, max_lon
);
```

#### API Python para SQLite
```python
# v0.4.0 - Nueva API
from catalogmx.catalogs.sepomex import CodigosPostalesSQLite

# Lazy loading desde SQLite
cps = CodigosPostalesSQLite.query(
    where="estado = ? AND poblacion_total > ?",
    params=["Jalisco", 10000]
)

# Búsqueda geográfica eficiente
cercanos = CodigosPostalesSQLite.query_by_location(
    lat=19.4326,
    lon=-99.1332,
    radius_km=10
)
```

#### Script de Conversión
```bash
# v0.4.0 - Convertir JSON a SQLite
python scripts/json_to_sqlite.py \
  --input packages/shared-data/sepomex/codigos_postales_completo.json \
  --output packages/shared-data/sepomex/sepomex.db \
  --table codigos_postales \
  --indexes cp,municipio,estado
```

**Beneficios SQLite**:
- ✅ 30-40% más pequeño que JSON
- ✅ Búsquedas 10-100x más rápidas
- ✅ Índices espaciales (R-tree)
- ✅ Queries SQL complejos
- ✅ Sin cargar todo en RAM

---

## 🔗 Vinculación CP ↔ Localidad

### v0.4.0 - Tabla de Correspondencia

#### Objetivo
Crear tabla pre-calculada que vincule códigos postales con localidades.

#### Metodología

**Fase 1: Geocodificar CPs**
```bash
# Script que añade GPS a cada CP
python scripts/geocode_postal_codes.py \
  --api google \
  --batch-size 100 \
  --output codigos_postales_con_gps.json

# Resultado: 157,252 CPs con lat/lon
```

**Fase 2: Matching Geográfico**
```python
# Script que vincula por proximidad
python scripts/link_cp_to_localities.py \
  --max-distance 5 \
  --min-score 70

# Criterios:
# 1. Mismo municipio
# 2. Distancia GPS < 5 km
# 3. Similitud de nombre > 70%
```

**Fase 3: Tabla de Correspondencia**
```json
{
  "correspondencias": [
    {
      "cp": "06700",
      "cvegeo": "090150001",
      "nombre_cp": "Roma Norte",
      "nombre_localidad": "Cuauhtémoc",
      "distancia_km": 0.5,
      "score_nombre": 85,
      "metodo": "geografico"
    }
  ]
}
```

#### API de Vinculación
```python
from catalogmx.links import CPLocalityLinker

# Obtener localidad para un CP
localidad = CPLocalityLinker.get_locality_for_cp("06700")
print(localidad['nom_localidad'])  # "Cuauhtémoc"
print(localidad['latitud'], localidad['longitud'])

# Obtener CPs para una localidad
cps = CPLocalityLinker.get_cps_for_locality("090150001")
print(f"{len(cps)} códigos postales en esta localidad")
```

**Precisión esperada**: 75-85% (depende de geocodificación)

---

## 📊 Prioridades por Impacto

### 🔥 Alta Prioridad (v0.4.0 - Q1 2025)

1. **SQLite para SEPOMEX** ⭐⭐⭐⭐⭐
   - Impacto: Reduce tamaño 40%, queries 100x más rápidas
   - Esfuerzo: Medio (1-2 semanas)
   - Usuarios beneficiados: Todos

2. **Geocodificación de CPs** ⭐⭐⭐⭐⭐
   - Impacto: Habilita búsqueda geográfica de CPs
   - Esfuerzo: Alto (requiere API externa, 157k requests)
   - Usuarios beneficiados: Apps con mapas

3. **TypeScript Sync** ⭐⭐⭐⭐
   - Impacto: Paridad entre Python y TS
   - Esfuerzo: Medio (1 semana)
   - Usuarios beneficiados: Desarrolladores TS/JS

4. **Tabla CP ↔ Localidad** ⭐⭐⭐⭐
   - Impacto: Vinculación precisa
   - Esfuerzo: Medio (depende de geocodificación)
   - Usuarios beneficiados: Apps de direcciones

### 🔶 Media Prioridad (v0.4.0-v0.5.0)

5. **REST API Examples** ⭐⭐⭐
   - Impacto: Facilita adopción
   - Esfuerzo: Bajo (1-2 días)

6. **Catálogos SAT Faltantes** ⭐⭐⭐
   - Impacto: Validación CFDI más completa
   - Esfuerzo: Medio

7. **Versiones Históricas** ⭐⭐⭐
   - Impacto: Auditoría y compliance
   - Esfuerzo: Alto

### 🔵 Baja Prioridad (v0.5.0+)

8. **WebAssembly** ⭐⭐
   - Impacto: Performance en browser
   - Esfuerzo: Alto

9. **ML Normalization** ⭐⭐
   - Impacto: Corrección automática
   - Esfuerzo: Muy alto

10. **Nuevos Validadores** ⭐⭐
    - Impacto: Casos de uso específicos
    - Esfuerzo: Medio por validador

---

## 🛠️ Plan de Implementación v0.4.0

### Mes 1: SQLite + Geocoding

**Semana 1-2: Implementar SQLite**
```bash
# Tareas
- [ ] Crear schema SQLite para SEPOMEX
- [ ] Script de conversión JSON → SQLite
- [ ] API Python para SQLite
- [ ] Tests de performance
- [ ] Documentación
```

**Semana 3-4: Geocodificación**
```bash
# Tareas
- [ ] Seleccionar API (Google vs OSM)
- [ ] Script de geocodificación por lotes
- [ ] Procesar 157k CPs (~500/día = 314 días ❌)
- [ ] Alternativa: Usar dataset existente o pagar API
- [ ] Validar coordenadas
```

### Mes 2: TypeScript + Vinculación

**Semana 1-2: TypeScript**
```bash
# Tareas
- [ ] Implementar LocalidadesCatalog.ts
- [ ] Actualizar types
- [ ] Tests TypeScript
- [ ] Build y verify
```

**Semana 3-4: Vinculación**
```bash
# Tareas
- [ ] Script de vinculación CP ↔ Localidad
- [ ] Generar tabla de correspondencia
- [ ] API de vinculación
- [ ] Tests
```

### Mes 3: Examples + Documentation

**Semana 1-2: Examples**
```bash
# Crear ejemplos completos
- [ ] FastAPI REST API
- [ ] Next.js frontend
- [ ] Flask simple server
- [ ] GraphQL API
```

**Semana 3-4: Polish**
```bash
# Finalizar release
- [ ] Actualizar documentación
- [ ] Performance testing
- [ ] Bug fixes
- [ ] Preparar v0.4.0 release
```

---

## 📈 Métricas de Éxito

### v0.4.0 Goals

| Métrica | Objetivo |
|---------|----------|
| **Tamaño SQLite** | <30 MB (vs 43 MB JSON) |
| **Query performance** | <10ms (vs ~100ms JSON) |
| **CPs geocodificados** | 100% (157,252) |
| **Precisión vinculación** | >75% |
| **TypeScript coverage** | 100% (paridad con Python) |
| **Documentation** | Examples para 5+ frameworks |

### v0.5.0 Goals

| Métrica | Objetivo |
|---------|----------|
| **Nuevos catálogos** | +10 (IFT, IMSS, TIGIE) |
| **Nuevos validadores** | +3 (ISAN, Placas, MRZ) |
| **Performance** | Validadores 10x faster (WASM) |
| **ML accuracy** | >90% para normalización |

---

## 🔒 Mantenimiento y Soporte

### Estrategia de Branches

```
main                  - Producción estable (v0.3.0)
├── develop          - Desarrollo activo (v0.4.0-dev)
├── feature/sqlite   - SQLite implementation
├── feature/geocode  - Geocoding
└── feature/ts-sync  - TypeScript sync
```

### Release Cycle

- **Minor versions** (v0.x.0): Cada 3-4 meses
- **Patch versions** (v0.3.x): Según necesidad (bugs, catalog updates)
- **Major versions** (v1.0.0): Cuando API sea estable

---

## 📞 Contribuciones

### ¿Cómo Contribuir?

Ver [CONTRIBUTING.rst](CONTRIBUTING.rst) para guía completa.

**Áreas que necesitan ayuda**:
1. 🔥 Geocodificación de CPs (bulk geocoding)
2. 🔥 Implementación TypeScript de localidades
3. 🔥 Ejemplos de uso (FastAPI, Next.js, etc.)
4. Scripts de actualización automática
5. Tests adicionales
6. Documentación y traducciones

---

## 📊 Estado del Roadmap

### Resumen Visual

```
catalogmx Roadmap

v0.3.0 (ACTUAL) ████████████████████ 100% ✅
├─ SEPOMEX completo
├─ INEGI municipios completo
├─ INEGI localidades con GPS
├─ Búsqueda geográfica
└─ Documentación bilingüe

v0.4.0 (Q1 2025) ░░░░░░░░░░░░░░░░░░░░   0% 📋
├─ SQLite para SEPOMEX
├─ Geocodificación de CPs
├─ Vinculación CP ↔ Localidad
├─ TypeScript sync
└─ REST/GraphQL examples

v0.5.0 (Q2-Q3 2025) ░░░░░░░░░░░░░░░░░░░░   0% 🔮
├─ Nuevos validadores (ISAN, Placas)
├─ Catálogos IFT, IMSS, TIGIE
├─ ML normalization
├─ WebAssembly
└─ Versiones históricas
```

---

## 🎯 Conclusión

**catalogmx v0.3.0** está completo y listo para producción con:
- ✅ 170,505+ registros
- ✅ 126M habitantes cubiertos
- ✅ Búsqueda geográfica con GPS
- ✅ Documentación bilingüe profesional

**v0.4.0** se enfocará en:
- 🔥 SQLite para performance
- 🔥 Geocodificación completa
- 🔥 Vinculación precisa CP ↔ Localidad
- 🔥 Paridad TypeScript

**v0.5.0** expandirá con:
- 🚀 Nuevos catálogos y validadores
- 🚀 ML y WebAssembly
- 🚀 Herramientas avanzadas

---

**Última actualización**: 2025-11-08  
**Versión**: v0.3.0  
**Próximo release**: v0.4.0 (Q1 2025)

---

**¿Preguntas o sugerencias?** Abre un issue en GitHub o consulta [CONTRIBUTING.rst](CONTRIBUTING.rst)

