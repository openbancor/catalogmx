# 📋 Catálogos Adicionales - Documentación Detallada

## 🌎 Comercio Exterior - Estados y Provincias de EE.UU. y Canadá

### ¿Por qué se necesitan?

El SAT requiere especificar el estado o provincia cuando se emite un CFDI con **Complemento de Comercio Exterior** para operaciones con Estados Unidos y Canadá.

### Catálogo c_Estado (para USA/Canadá)

**Fuente oficial**: SAT - Catálogos de Comercio Exterior
**URL**: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/catalogos_emision_cfdi_complemento_ce.htm

#### Estados Unidos (50 estados + DC + territorios)

Utiliza códigos ISO 3166-2:US:
- AL - Alabama
- AK - Alaska
- AZ - Arizona
- AR - Arkansas
- CA - California
- CO - Colorado
- CT - Connecticut
- DE - Delaware
- FL - Florida
- ...
- DC - District of Columbia
- PR - Puerto Rico
- VI - Virgin Islands
- GU - Guam

#### Canadá (13 provincias y territorios)

Utiliza códigos ISO 3166-2:CA:
- AB - Alberta
- BC - British Columbia
- MB - Manitoba
- NB - New Brunswick
- NL - Newfoundland and Labrador
- NT - Northwest Territories
- NS - Nova Scotia
- NU - Nunavut
- ON - Ontario
- PE - Prince Edward Island
- QC - Quebec
- SK - Saskatchewan
- YT - Yukon

### Reglas de Validación SAT

1. **Cuando c_Pais = USA o CAN**: El campo c_Estado es **obligatorio** y debe seleccionarse de este catálogo
2. **Para otros países**: Se usa el mismo código del país en el campo estado
3. **NumRegIdTrib**: Para USA/Canadá debe ser 9 dígitos numéricos

### Caso de Uso

```python
from catalogmx.catalogs.sat import ComercioExteriorCatalog

# Validar estado de EE.UU. para factura de exportación
estado = ComercioExteriorCatalog.get_estado_usa('CA')
print(estado)  # {'code': 'CA', 'name': 'California', 'country': 'USA'}

# Validar provincia canadiense
provincia = ComercioExteriorCatalog.get_provincia_canada('ON')
print(provincia)  # {'code': 'ON', 'name': 'Ontario', 'country': 'CAN'}

# Validar CFDI comercio exterior
cfdi_data = {
    'pais': 'USA',
    'estado': 'TX',
    'num_reg_id_trib': '123456789'  # 9 dígitos requerido
}
is_valid = ComercioExteriorCatalog.validate_foreign_address(cfdi_data)
```

---

## 🚛 Carta Porte 3.0 - Infraestructura de Transporte

El **Complemento Carta Porte** es obligatorio para el transporte de bienes y mercancías en territorio nacional. Versión actual: 3.0 (vigente 2025).

### Catálogos de Carta Porte

**Fuente oficial**: SAT - Carta Porte 3.0
**URL Excel**: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/CatalogosCartaPorte30.xls

---

### 1. c_Estaciones - Estaciones de Transporte

**Descripción**: Catálogo de estaciones de origen/destino para transporte de mercancías.

**Tipos de estaciones**:
- Estaciones de autobús
- Estaciones ferroviarias
- Puertos marítimos
- Aeropuertos
- Centros de distribución

**Campos**:
- `id_estacion`: Clave única
- `nombre`: Nombre de la estación
- `tipo`: Tipo de estación (Marítima, Aérea, Ferroviaria, Autotransporte)
- `clave_transporte`: Código específico del modo de transporte
- `municipio`: Municipio donde se ubica
- `estado`: Estado

**Ejemplo**:
```json
{
  "id_estacion": "EST001",
  "nombre": "Puerto de Veracruz",
  "tipo": "Marítima",
  "clave_transporte": "VER01",
  "estado": "Veracruz"
}
```

---

### 2. c_CodigoTransporteAereo - Aeropuertos (IATA/ICAO)

**Descripción**: Catálogo de aeropuertos mexicanos con códigos IATA e ICAO.

**Códigos incluidos**:
- **IATA**: Código de 3 letras (MEX, GDL, MTY, CUN, etc.)
- **ICAO**: Código de 4 letras (MMMX, MMGL, MMMY, MMUN, etc.)

**Aeropuertos principales**:

| IATA | ICAO | Nombre | Ciudad |
|------|------|--------|--------|
| MEX | MMMX | Aeropuerto Internacional de la Ciudad de México | Ciudad de México |
| GDL | MMGL | Aeropuerto Internacional de Guadalajara | Guadalajara |
| MTY | MMMY | Aeropuerto Internacional de Monterrey | Monterrey |
| CUN | MMUN | Aeropuerto Internacional de Cancún | Cancún |
| TIJ | MMTJ | Aeropuerto Internacional de Tijuana | Tijuana |
| BJX | MMLO | Aeropuerto Internacional del Bajío | León/Guanajuato |
| PVR | MMPR | Aeropuerto Internacional de Puerto Vallarta | Puerto Vallarta |

**Total**: ~76 aeropuertos nacionales e internacionales

**Caso de uso**:
```python
from catalogmx.catalogs.sat import CartaPorteCatalog

# Buscar aeropuerto por código IATA
airport = CartaPorteCatalog.get_airport_by_iata('MEX')
print(airport['icao'])  # 'MMMX'
print(airport['name'])  # 'Aeropuerto Internacional de la Ciudad de México'

# Validar código de transporte aéreo en Carta Porte
cfdi = {
    'transporte_aereo': {
        'codigo_aeropuerto_origen': 'GDL',
        'codigo_aeropuerto_destino': 'MTY'
    }
}
```

---

### 3. c_NumAutorizacionNaviero - Puertos Marítimos

**Descripción**: Catálogo de puertos marítimos autorizados por la SCT y números de autorización naviera.

**Puertos principales**:

| Puerto | Estado | Tipo |
|--------|--------|------|
| Veracruz | Veracruz | Comercial |
| Altamira | Tamaulipas | Comercial |
| Manzanillo | Colima | Comercial |
| Lázaro Cárdenas | Michoacán | Comercial |
| Ensenada | Baja California | Comercial |
| Mazatlán | Sinaloa | Comercial/Turístico |
| Puerto Progreso | Yucatán | Comercial |
| Tuxpan | Veracruz | Comercial |
| Coatzacoalcos | Veracruz | Industrial |

**Total**: ~100+ puertos y terminales marítimas

**Información incluida**:
- Nombre del puerto
- Clave SCT
- Número de autorización naviera
- Tipo de puerto (comercial, industrial, turístico, pesquero)
- Servicios disponibles

---

### 4. c_Carreteras - Catálogo de Carreteras Federales SCT

**Descripción**: Catálogo de carreteras federales bajo jurisdicción de la SCT y Guardia Nacional.

**Fuente**: Secretaría de Comunicaciones y Transportes + Guardia Nacional
**URL**: https://www.gob.mx/guardianacional/documentos/catalogo-de-carreteras-y-tramos-competencia-de-las-coordinaciones-estatales-de-la-guardia-nacional

**Clasificación de carreteras**:

1. **Red Federal** (~50,000 km)
   - Carreteras de cuota (autopistas)
   - Carreteras libres

2. **Por región**:
   - Carreteras troncales
   - Carreteras alimentadoras
   - Caminos rurales

**Información por carretera**:
- Número de carretera (ej: "Carretera Federal 57")
- Tramos (inicio - fin)
- Kilometraje
- Jurisdicción (Coordinación Estatal GN)
- Tipo de superficie
- Número de carriles
- Estado de conservación

**Ejemplo**:
```json
{
  "numero": "57",
  "nombre": "México - Piedras Negras",
  "tipo": "Troncal",
  "tramos": [
    {
      "inicio": "Ciudad de México",
      "fin": "Querétaro",
      "km_inicio": 0,
      "km_fin": 211,
      "tipo_superficie": "Pavimento",
      "carriles": 4,
      "jurisdiccion": "Centro"
    }
  ]
}
```

---

### 5. Otros Catálogos Carta Porte

#### c_TipoPermiso - Tipos de Permiso SCT

Permisos otorgados por la Secretaría de Comunicaciones y Transportes:
- TPAF01 - Autotransporte Federal de Carga General
- TPAF02 - Transporte Privado de Carga
- TPAF03 - Paquetería y Mensajería
- TPAF09 - Grúas
- TPTM01 - Transporte Marítimo
- TPTA01 - Transporte Aéreo Regular

#### c_ConfigAutotransporte - Configuración Vehicular

Configuraciones de vehículos de carga:
- C2 - Camión Unitario (2 ejes)
- C3 - Camión Unitario (3 ejes)
- T3S2 - Tractocamión articulado (3 ejes + 2 ejes)
- T3S3 - Tractocamión articulado (3 ejes + 3 ejes)
- C2R2 - Camión con remolque
- Etc.

#### c_TipoEmbalaje - Tipos de Embalaje

Tipos de empaque para mercancías:
- 1A - Tambor de acero
- 1B - Tambor de aluminio
- 4A - Caja de madera natural
- 4C - Caja de madera contrachapada
- 5H - Saco tejido de plástico
- Etc. (según normas internacionales)

#### c_MaterialPeligroso - Materiales Peligrosos

Catálogo de sustancias peligrosas según la NOM-002-SCT:
- Clase 1: Explosivos
- Clase 2: Gases
- Clase 3: Líquidos inflamables
- Clase 4: Sólidos inflamables
- Clase 5: Comburentes y peróxidos orgánicos
- Clase 6: Sustancias tóxicas e infecciosas
- Clase 7: Sustancias radioactivas
- Clase 8: Sustancias corrosivas
- Clase 9: Sustancias peligrosas diversas

---

## 📈 Banxico SIE API - Tasas de Interés Históricas

### ¿Qué es el SIE?

El **Sistema de Información Económica (SIE)** de Banxico proporciona acceso a series de tiempo económicas y financieras mediante un API REST.

**URL oficial**: https://www.banxico.org.mx/SieAPIRest/

### Series de Tasas de Interés

#### TIIE - Tasa de Interés Interbancaria de Equilibrio

La TIIE es la tasa de referencia para préstamos interbancarios en México.

**Series disponibles**:
- **SF60648**: TIIE 28 días
- **SF60649**: TIIE 91 días
- **SF111916**: TIIE 182 días

**Frecuencia**: Diaria
**Período disponible**: 1996 - presente

#### CETES - Certificados de la Tesorería

Tasa de rendimiento de los Certificados de la Tesorería (deuda gubernamental).

**Series disponibles**:
- **SF60633**: CETES 28 días
- **SF43783**: CETES 91 días
- **SF43878**: CETES 182 días
- **SF43936**: CETES 364 días

**Frecuencia**: Diaria
**Período disponible**: 1978 - presente

#### Tasa Objetivo Banco de México

- **SF61745**: Tasa objetivo de Banxico (tasa de referencia para política monetaria)

**Frecuencia**: Diaria
**Período disponible**: 2008 - presente

### Uso del API

#### Autenticación

Requiere un **token de consulta** que se obtiene registrándose en:
https://www.banxico.org.mx/SieAPIRest/service/v1/token

#### Endpoints

**1. Datos más recientes**:
```
GET https://www.banxico.org.mx/SieAPIRest/service/v1/series/{idSerie}/datos/oportuno
```

**2. Rango de fechas**:
```
GET https://www.banxico.org.mx/SieAPIRest/service/v1/series/{idSerie}/datos/{fechaInicio}/{fechaFin}
```

**3. Múltiples series**:
```
GET https://www.banxico.org.mx/SieAPIRest/service/v1/series/{idSerie1,idSerie2}/datos/{fechaInicio}/{fechaFin}
```

### Ejemplo de Implementación

```python
from catalogmx.catalogs.banxico import InterestRatesAPI

# Inicializar con token de Banxico
api = InterestRatesAPI(token='YOUR_BANXICO_TOKEN')

# Obtener TIIE 28 días actual
tiie_28 = api.get_latest('TIIE_28')
print(tiie_28)  # {'date': '2025-01-15', 'value': 10.50}

# Obtener histórico de CETES 28 días
cetes_historical = api.get_historical(
    series='CETES_28',
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Obtener múltiples tasas en un solo request
rates = api.get_multiple_latest(['TIIE_28', 'CETES_28', 'TASA_OBJETIVO'])
print(rates)
# {
#   'TIIE_28': 10.50,
#   'CETES_28': 10.25,
#   'TASA_OBJETIVO': 10.50
# }

# Calcular estadísticas
stats = api.get_statistics('TIIE_28', start='2024-01-01', end='2024-12-31')
print(stats)
# {
#   'mean': 10.75,
#   'min': 10.25,
#   'max': 11.25,
#   'std': 0.25
# }
```

### Librerías Existentes

Ya existen librerías Python para el SIE de Banxico:
- **sie-banxico** (PyPI): Cliente simple para el API
- **Banxico-SIE** (PyPI): Cliente alternativo

`catalogmx` puede integrar una de estas o crear un wrapper simplificado.

### Casos de Uso

1. **Aplicaciones financieras**: Cálculo de intereses variables
2. **Análisis económico**: Series históricas para modelos
3. **Reportes**: Generación automática de reportes con tasas actualizadas
4. **Compliance**: Validación de tasas en contratos y facturas
5. **Dashboards**: Visualización de tendencias de tasas

---

## 🎯 Priorización Recomendada

### Alta Prioridad
1. **Comercio Exterior (c_Estado USA/Canadá)** - Requerido por SAT para CFDI exportación
2. **Aeropuertos (c_CodigoTransporteAereo)** - Muy usado en Carta Porte

### Prioridad Media
3. **Puertos marítimos** - Importante para comercio internacional
4. **TIIE/CETES (Banxico SIE)** - Muy útil para sector financiero
5. **Estaciones de transporte** - Complementa Carta Porte

### Prioridad Baja
6. **Carreteras federales** - Catálogo grande, uso específico
7. **Configuración vehicular** - Muy específico de transporte
8. **Materiales peligrosos** - Nicho específico

---

## 📦 Estructura de Datos Propuesta

### Archivos JSON

```
packages/shared-data/
├── sat/
│   ├── comercio_exterior/
│   │   ├── estados_usa.json          # 50 estados + DC + territorios
│   │   └── provincias_canada.json    # 13 provincias
│   └── carta_porte/
│       ├── aeropuertos.json           # ~76 aeropuertos (IATA/ICAO)
│       ├── puertos.json               # ~100 puertos marítimos
│       ├── estaciones.json            # Estaciones de transporte
│       ├── tipo_permiso.json          # Permisos SCT
│       ├── config_vehicular.json      # Configuraciones de vehículos
│       ├── tipo_embalaje.json         # Tipos de empaque
│       └── materiales_peligrosos.json # Catálogo HAZMAT
│
├── sct/
│   └── carreteras_federales.json      # O SQLite si es muy grande
│
└── banxico/
    └── sie_series.json                 # Mapeo de series (TIIE, CETES, etc.)
```

### Módulos Python

```python
# packages/python/catalogmx/catalogs/sat/comercio_exterior.py
class ComercioExteriorCatalog:
    @classmethod
    def get_estado_usa(cls, code): ...

    @classmethod
    def get_provincia_canada(cls, code): ...

# packages/python/catalogmx/catalogs/sat/carta_porte.py
class CartaPorteCatalog:
    @classmethod
    def get_airport_by_iata(cls, code): ...

    @classmethod
    def get_airport_by_icao(cls, code): ...

    @classmethod
    def get_puerto(cls, name): ...

# packages/python/catalogmx/catalogs/banxico/interest_rates.py
class InterestRatesAPI:
    def __init__(self, token): ...

    def get_latest(self, series): ...

    def get_historical(self, series, start_date, end_date): ...
```

---

## 🔗 Referencias

### SAT
- [Carta Porte 3.0 - Instructivo](http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/Instructivo_de_llenado_del_CFDI_con_complemento_carta_porte.pdf)
- [Catálogos Excel Carta Porte](http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/CatalogosCartaPorte30.xls)
- [Comercio Exterior - Catálogos](http://omawww.sat.gob.mx/tramitesyservicios/Paginas/catalogos_emision_cfdi_complemento_ce.htm)

### Banxico
- [SIE API Documentación](https://www.banxico.org.mx/SieAPIRest/)
- [Tasas de Interés Representativas](https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=18&accion=consultarCuadroAnalitico&idCuadro=CA51)

### SCT
- [Portal de Carreteras](https://www.sct.gob.mx/carreteras/)
- [Información de Carreteras](https://www.sct.gob.mx/carreteras-v2/servicios/informacion-de-carreteras/)

### Guardia Nacional
- [Catálogo de Carreteras - Competencia GN](https://www.gob.mx/guardianacional/documentos/catalogo-de-carreteras-y-tramos-competencia-de-las-coordinaciones-estatales-de-la-guardia-nacional)
