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

---

## 📅 Días Festivos e Inhábiles - Sistema Completo

### ¿Por qué se necesita?

En México existen **3 tipos diferentes** de días inhábiles que **NO coinciden entre sí**:

1. **Días inhábiles laborales** (Ley Federal del Trabajo)
2. **Días inhábiles bancarios** (CNBV/Banxico)
3. **Días inhábiles judiciales** (Poder Judicial)

**Diferencia clave**: Hay días que son **hábiles para empresas** pero **inhábiles para bancos**. Por ejemplo, **Viernes Santo**:
- Es **día hábil laboral** (la mayoría de empresas trabajan)
- Es **día inhábil bancario** (bancos cerrados)

### Tipos de Días Inhábiles

#### 1. Días Inhábiles Laborales (LFT - Ley Federal del Trabajo)

**Fuente**: Artículo 74 de la Ley Federal del Trabajo + DOF anual
**Publicación**: Procuraduría Federal de la Defensa del Trabajo (PROFEDET)

**7 días de descanso obligatorio (2025)**:
1. **1 de enero** - Año Nuevo
2. **Primer lunes de febrero** (3 feb 2025) - Día de la Constitución (conmemora 5 feb)
3. **Tercer lunes de marzo** (17 mar 2025) - Natalicio de Benito Juárez (conmemora 21 mar)
4. **1 de mayo** - Día del Trabajo
5. **16 de septiembre** - Independencia de México
6. **Tercer lunes de noviembre** (17 nov 2025) - Revolución Mexicana (conmemora 20 nov)
7. **25 de diciembre** - Navidad

**Adicional cada 6 años**:
- **1 de octubre** - Transmisión del Poder Ejecutivo (2024, 2030, 2036...)

**Características**:
- Si trabajas estos días: salario diario + doble pago (triple pago total)
- Aplica a TODOS los trabajadores en México
- Publicado anualmente en DOF

#### 2. Días Inhábiles Bancarios (CNBV)

**Fuente**: Comisión Nacional Bancaria y de Valores + Banxico
**Publicación**: DOF anual (diciembre del año anterior)
**URL**: https://www.gob.mx/cnbv/acciones-y-programas/calendario-cnbv

**10 días inhábiles bancarios (2025)**:
1. **1 de enero** - Año Nuevo
2. **3 de febrero** - Día de la Constitución
3. **17 de marzo** - Natalicio de Benito Juárez
4. **17 de abril (jueves)** - Jueves Santo ⚠️
5. **18 de abril (viernes)** - Viernes Santo ⚠️
6. **1 de mayo** - Día del Trabajo
7. **16 de septiembre** - Independencia
8. **17 de noviembre** - Revolución Mexicana
9. **12 de diciembre** - Día del Empleado Bancario ⚠️
10. **25 de diciembre** - Navidad

⚠️ = **Días que SON hábiles laboralmente pero NO bancariamente**

**Características**:
- Los bancos NO abren sucursales
- Cajeros automáticos y banca digital SÍ funcionan
- Casas de cambio pueden operar
- SPEI opera 24/7/365 (excepto mantenimientos programados)
- Publicado con ~1 año de anticipación

#### 3. Días Inhábiles Judiciales (Poder Judicial)

**Fuente**: Suprema Corte de Justicia de la Nación (SCJN)
**Publicación**: Cada año por cada tribunal
**URL**: https://www.scjn.gob.mx/

**Días inhábiles generales**:
- **TODOS los sábados y domingos** del año
- **1 de enero** - Año Nuevo
- **5 de febrero** - Día de la Constitución (fecha real, no lunes)
- **21 de marzo** - Natalicio de Benito Juárez (fecha real, no lunes)
- **1 de mayo** - Día del Trabajo
- **5 de mayo** - Batalla de Puebla ⚠️
- **14 de septiembre** - Incorporación del Batallón de San Patricio ⚠️
- **16 de septiembre** - Independencia
- **12 de octubre** - Día de la Raza ⚠️
- **20 de noviembre** - Revolución Mexicana (fecha real, no lunes)
- **25 de diciembre** - Navidad

**Períodos vacacionales**:
- **Semana Santa**: Jueves, Viernes y Sábado Santo + Lunes de Pascua
- **Receso de verano**: Variable (julio-agosto, aprox. 2 semanas)
- **Receso de fin de año**: ~20 dic - 6 ene

⚠️ = **Días inhábiles SOLO para tribunales**

**Características**:
- No corren plazos procesales
- Cada tribunal puede tener días adicionales
- Tribunales estatales pueden variar
- Publicado anualmente por cada órgano judicial

---

### Diferencias Resumidas

| Día | Laboral (LFT) | Bancario (CNBV) | Judicial (SCJN) |
|-----|---------------|-----------------|-----------------|
| Viernes Santo | ✅ Hábil | ❌ Inhábil | ❌ Inhábil |
| Día del Empleado Bancario (12 dic) | ✅ Hábil | ❌ Inhábil | ✅ Hábil |
| 5 de mayo | ✅ Hábil | ✅ Hábil | ❌ Inhábil |
| Sábados | ✅ Hábil* | ❌ Inhábil | ❌ Inhábil |
| Día de la Constitución | ❌ Inhábil (lunes) | ❌ Inhábil (lunes) | ❌ Inhábil (5 feb) |

\* = Para empresas que trabajan sábados

---

### Catálogo Propuesto: `catalogmx`

#### Estructura de Datos

```json
{
  "year": 2025,
  "types": {
    "labor": {
      "source": "Ley Federal del Trabajo + DOF",
      "authority": "PROFEDET",
      "holidays": [
        {
          "date": "2025-01-01",
          "name": "Año Nuevo",
          "law_article": "Art. 74 LFT",
          "mandatory_rest": true,
          "triple_pay": true
        },
        {
          "date": "2025-02-03",
          "name": "Día de la Constitución",
          "commemorates": "2025-02-05",
          "moved_to_monday": true,
          "mandatory_rest": true
        }
        // ...
      ]
    },
    "banking": {
      "source": "CNBV + Banxico",
      "authority": "CNBV",
      "published_dof": "2024-12-27",
      "holidays": [
        {
          "date": "2025-04-17",
          "name": "Jueves Santo",
          "banking_only": true,
          "labor_working_day": true
        },
        {
          "date": "2025-12-12",
          "name": "Día del Empleado Bancario",
          "banking_only": true,
          "labor_working_day": true
        }
        // ...
      ]
    },
    "judicial": {
      "source": "SCJN",
      "authority": "Suprema Corte de Justicia de la Nación",
      "holidays": [
        {
          "date": "2025-05-05",
          "name": "Batalla de Puebla",
          "judicial_only": true,
          "labor_working_day": true,
          "banking_working_day": true
        }
        // ...
      ],
      "vacation_periods": [
        {
          "start": "2025-04-14",
          "end": "2025-04-21",
          "name": "Semana Santa"
        }
      ]
    }
  }
}
```

#### API Python Propuesta

```python
from catalogmx.calendars import MexicanHolidays
from datetime import date, timedelta

# Inicializar calendario
cal = MexicanHolidays()

# Verificar si es día hábil
fecha = date(2025, 4, 18)  # Viernes Santo

cal.is_business_day(fecha)  # True (es hábil para empresas)
cal.is_banking_day(fecha)   # False (bancos cerrados)
cal.is_judicial_day(fecha)  # False (tribunales cerrados)

# Obtener siguiente día hábil
cal.next_business_day(fecha, type='labor')    # 2025-04-21 (lunes)
cal.next_business_day(fecha, type='banking')  # 2025-04-21 (lunes)

# Calcular días hábiles entre fechas
start = date(2025, 4, 16)  # Miércoles
end = date(2025, 4, 22)    # Martes
cal.business_days_between(start, end, type='banking')  # 3 días (lunes 21, martes 22, miércoles 16)

# Obtener festivos del año
holidays_2025 = cal.get_holidays(2025, type='banking')
for h in holidays_2025:
    print(f"{h['date']}: {h['name']}")

# Verificar tipo de día
info = cal.get_day_info(date(2025, 12, 12))
print(info)
# {
#   'date': '2025-12-12',
#   'is_labor_holiday': False,
#   'is_banking_holiday': True,
#   'is_judicial_holiday': False,
#   'banking_holiday_name': 'Día del Empleado Bancario'
# }

# Obtener histórico de festivos
historical = cal.get_holidays_range(
    start_year=2000,
    end_year=2030,
    type='banking'
)

# Calcular días hábiles bancarios para vencimiento
vencimiento = date(2025, 4, 15)  # Martes antes de Semana Santa
dias_habiles = 5
fecha_limite = cal.add_business_days(vencimiento, dias_habiles, type='banking')
# 2025-04-23 (miércoles) - salta Jueves Santo, Viernes Santo y fin de semana
```

#### Casos de Uso

**1. Vencimientos de pagos**:
```python
# Calcular fecha límite de pago
fecha_factura = date(2025, 4, 10)
dias_credito = 30
fecha_vencimiento = cal.add_business_days(fecha_factura, dias_credito, type='banking')
```

**2. Nóminas**:
```python
# Verificar si es día de pago (quincena)
fecha_pago_programada = date(2025, 12, 15)
if not cal.is_banking_day(fecha_pago_programada):
    fecha_pago_real = cal.previous_business_day(fecha_pago_programada, type='banking')
```

**3. Cumplimiento legal**:
```python
# Verificar días de descanso obligatorio para cálculo de aguinaldo
year = 2025
labor_holidays = cal.get_holidays(year, type='labor')
dias_obligatorios = len(labor_holidays)  # 7 días
```

**4. Procesos judiciales**:
```python
# Calcular plazo de 15 días hábiles para apelación
fecha_sentencia = date(2025, 4, 10)
fecha_limite = cal.add_business_days(fecha_sentencia, 15, type='judicial')
```

---

### Datos Históricos y Futuros

#### Histórico Recomendado

**Mínimo**: 2000-2024 (25 años)
- Suficiente para análisis financieros
- Cubre cambios en legislación laboral

**Ideal**: 1990-2024 (35 años)
- Cubre análisis económicos de largo plazo
- Incluye crisis económicas importantes

**Fuentes para histórico**:
- DOF (Diario Oficial de la Federación) - archivo digital desde 2000
- Banxico - registros históricos de días inhábiles
- SCJN - acuerdos históricos

#### Futuro Recomendado

**Mínimo**: 2025-2029 (5 años)
- Suficiente para planificación financiera
- Cubre periodo sexenal

**Ideal**: 2025-2034 (10 años)
- Planificación de largo plazo
- Previsión de presupuestos

**Actualización**:
- Anual (diciembre) cuando CNBV publica calendario siguiente
- Automatizable mediante scraping de DOF

---

### Fuentes Oficiales

**Días Inhábiles Laborales**:
- PROFEDET: https://www.gob.mx/profedet/articulos/dias-de-descanso-obligatorio
- DOF: https://www.dof.gob.mx/

**Días Inhábiles Bancarios**:
- CNBV: https://www.gob.mx/cnbv/acciones-y-programas/calendario-cnbv
- Banxico: https://www.banxico.org.mx/
- Publicación DOF: https://www.dof.gob.mx/ (diciembre año anterior)

**Días Inhábiles Judiciales**:
- SCJN: https://www.scjn.gob.mx/
- Calendario PDF: https://www.scjn.gob.mx/sites/default/files/pagina-micrositios/documentos/2024-11/Calendario_dias_inhabiles_2025.pdf

---

### Priorización

**Alta Prioridad**:
- Días inhábiles bancarios (2000-2034)
- Días inhábiles laborales (2000-2034)
- API de cálculo de días hábiles

**Media Prioridad**:
- Días inhábiles judiciales (2000-2034)
- Histórico ampliado (1990-1999)

**Baja Prioridad**:
- Días inhábiles por estado (pueden variar localmente)
- Días festivos no oficiales (Día de Muertos, etc.)

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

### Días Festivos
- [PROFEDET - Días de Descanso Obligatorio](https://www.gob.mx/profedet/articulos/dias-de-descanso-obligatorio)
- [CNBV - Calendario Oficial](https://www.gob.mx/cnbv/acciones-y-programas/calendario-cnbv)
- [SCJN - Días Inhábiles](https://www.scjn.gob.mx/)
- [DOF - Diario Oficial](https://www.dof.gob.mx/)
