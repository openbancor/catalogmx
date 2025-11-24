# catalogmx

**Librería Completa de Validadores y Catálogos Oficiales Mexicanos**

Una librería multi-lenguaje (Python 3.10+ | TypeScript 5.0+) completa para validar identificadores mexicanos y acceder a catálogos oficiales del SAT, Banxico, INEGI, SEPOMEX y otras dependencias gubernamentales.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org)
[![Licencia](https://img.shields.io/badge/licencia-BSD--2--Clause-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-catalogmx-blue.svg)](https://pypi.org/project/catalogmx/)
[![NPM](https://img.shields.io/badge/npm-catalogmx-red.svg)](https://www.npmjs.com/package/catalogmx)

**Idiomas**: [English](README.md) | [Español](#)

---

## Descripción General

**catalogmx** proporciona herramientas listas para producción para validación de datos mexicanos y acceso a catálogos oficiales:

- **4 Validadores**: RFC, CURP, CLABE, NSS con algoritmos completos
- **40+ Catálogos Oficiales**: SAT (CFDI 4.0, Comercio Exterior, Carta Porte, Nómina), INEGI, SEPOMEX, Banxico
- **170,505+ Registros**: Bases de datos completas incluyendo 157K códigos postales, 2.4K municipios, 10K+ localidades con GPS
- **Soporte Multi-lenguaje**: Python y TypeScript con APIs idénticas
- **Type-Safe**: Type hints completos (PEP 604) y declaraciones TypeScript
- **Listo para Producción**: Probado, documentado y mantenido activamente

---

## Inicio Rápido

### Python

```bash
pip install catalogmx
```

```python
from catalogmx.validators import rfc, curp
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import LocalidadesCatalog

# Validar RFC
es_valido = rfc.validate_rfc("XAXX010101000")

# Buscar códigos postales
codigos_postales = CodigosPostales.get_by_cp("06700")
print(codigos_postales[0]['asentamiento'])  # "Roma Norte"

# Búsqueda geográfica con coordenadas GPS
localidades = LocalidadesCatalog.get_by_coordinates(
    lat=19.4326, lon=-99.1332, radio_km=10
)
```

### TypeScript

```bash
npm install catalogmx
```

```typescript
import { validateRFC, validateCURP } from 'catalogmx';
import { RegimenFiscalCatalog } from 'catalogmx/catalogs';

const esValido = validateRFC('XAXX010101000');
const regimen = RegimenFiscalCatalog.getRegimen('605');
```

---

## Características

### Validadores

**RFC (Registro Federal de Contribuyentes)**
- Persona Física (13 caracteres) y Persona Moral (12 caracteres)
- Cálculo de homoclave usando algoritmo Módulo 11
- Validación de dígito verificador
- Reemplazo de 170+ palabras altisonantes
- Soporte para residentes extranjeros

**CURP (Clave Única de Registro de Población)**
- Validación de 18 caracteres con algoritmo completo de RENAPO
- Verificación de dígito verificador (posición 18)
- Validación de código de estado (32 estados mexicanos)
- Manejo de 70+ palabras inconvenientes (Anexo 2)
- Extracción de fecha de nacimiento, sexo y estado

**CLABE (Clave Bancaria Estandarizada)**
- Validación de 18 dígitos
- Algoritmo de dígito verificador módulo 10
- Extracción de banco, sucursal y número de cuenta
- Integración con catálogo de bancos Banxico (110 instituciones)

**NSS (Número de Seguridad Social)**
- Validación de 11 dígitos IMSS
- Algoritmo Luhn modificado para dígito verificador
- Extracción de subdelegación, año y folio

### Catálogos Oficiales

**SAT (Servicio de Administración Tributaria)**
- CFDI 4.0 Núcleo: 9 catálogos (regímenes fiscales, usos de CFDI, formas de pago, etc.)
- Comercio Exterior 2.0: 8 catálogos (Incoterms, países, monedas, aduanas)
- Carta Porte 3.0: 7 catálogos (aeropuertos, puertos marítimos, carreteras, material peligroso)
- Nómina 1.2: 7 catálogos (tipos de nómina, contratos, jornadas, niveles de riesgo IMSS)

**INEGI (Datos Geográficos)**
- Municipios completos: 2,478 registros con datos de población (Censo 2020)
- Localidades con GPS: 10,635 localidades (1,000+ habitantes)
- Búsqueda geográfica por coordenadas
- Clasificación urbano/rural

**SEPOMEX (Servicio Postal)**
- Códigos postales completos: 157,252 registros
- Todos los 32 estados mexicanos (cobertura 100%)
- Búsqueda por código postal, municipio o estado

**Banxico (Banco Central)**
- Instituciones financieras: 110 bancos
- Estado de participación SPEI
- Validación de códigos bancarios

---

## Estadísticas

| Catálogo | Registros | Cobertura | Tamaño |
|---------|-----------|----------|--------|
| SEPOMEX Códigos Postales | 157,252 | 100% | 43.53 MB |
| INEGI Municipios | 2,478 | 100% | 0.98 MB |
| INEGI Localidades | 10,635 | 86% población | 5.22 MB |
| SAT CFDI 4.0 | ~30 | Completo | <1 MB |
| SAT Comercio Exterior | ~500 | Completo | <1 MB |
| SAT Carta Porte | ~3,400 | Completo | <2 MB |
| SAT Nómina | ~100 | Completo | <1 MB |
| Banxico Bancos | 110 | Completo | <1 MB |
| **TOTAL** | **170,505+** | **126M población** | **~50 MB** |

---

## Instalación

### Python

#### Desde PyPI (Recomendado)

```bash
pip install catalogmx
```

#### Desde Código Fuente

```bash
git clone https://github.com/openbancor/catalogmx.git
cd catalogmx/packages/python
pip install -e .
```

**Requisitos**:
- Python 3.10 o superior
- unidecode (para generación de RFC)
- click (para interfaz CLI)

### TypeScript/JavaScript

#### NPM

```bash
npm install catalogmx
```

#### Yarn

```bash
yarn add catalogmx
```

**Requisitos**:
- Node.js 18 o superior
- TypeScript 5.0+ (opcional, definiciones de tipos incluidas)

---

## Documentación

### Para Empezar
- [Guía de Instalación](docs/installation.rst)
- [Inicio Rápido](docs/quickstart.rst)
- [Referencia API](docs/api/)

### Guías
- [Guía de Arquitectura](docs/guides/architecture.md)
- [Guía del Desarrollador](docs/guides/developers-guide.md)
- [Actualización de Catálogos](docs/guides/catalog-updates.md)
- [Vinculación CP-Localidad](docs/guides/cp-locality-linking.md)

### Catálogos
- [Resumen de Catálogos](docs/catalogs/overview.md)
- [Documentación SEPOMEX](docs/catalogs/sepomex.md)
- [Documentación INEGI](docs/catalogs/inegi.md)
- [Documentación SAT](docs/catalogs/sat.md)

### Proyecto
- [Roadmap](docs/roadmap.md)
- [Historial de Cambios](CHANGELOG.rst)
- [Cambios de Catálogos](docs/changelog-catalogs.md)
- [Cómo Contribuir](CONTRIBUTING.rst)

---

## Ejemplos de Uso

### Validación de Dirección

```python
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import MunicipiosCatalog

def validar_direccion(codigo_postal, nombre_municipio):
    """Validar dirección mexicana"""
    
    if not CodigosPostales.is_valid(codigo_postal):
        return False, "Código postal inválido"
    
    info_cp = CodigosPostales.get_by_cp(codigo_postal)[0]
    
    if nombre_municipio.lower() not in info_cp['municipio'].lower():
        return False, f"El código postal {codigo_postal} no pertenece a {nombre_municipio}"
    
    return True, info_cp
```

### Análisis Geográfico

```python
from catalogmx.catalogs.inegi import LocalidadesCatalog

# Encontrar localidades cerca de una coordenada
cercanas = LocalidadesCatalog.get_by_coordinates(
    lat=19.4326,      # Ciudad de México
    lon=-99.1332,
    radio_km=50
)

for localidad in cercanas[:5]:
    print(f"{localidad['nom_localidad']}: {localidad['distancia_km']} km")
    print(f"  Población: {localidad['poblacion_total']:,}")
```

### Validación de CFDI

```python
from catalogmx.validators import rfc
from catalogmx.catalogs.sat.cfdi_4 import (
    RegimenFiscalCatalog,
    UsoCFDICatalog,
    FormaPagoCatalog
)

def validar_datos_cfdi(codigo_rfc, regimen_fiscal, uso_cfdi, forma_pago):
    """Validar datos de factura CFDI"""
    
    errores = []
    
    if not rfc.validate_rfc(codigo_rfc):
        errores.append("RFC inválido")
    
    if not RegimenFiscalCatalog.is_valid(regimen_fiscal):
        errores.append(f"Régimen fiscal inválido: {regimen_fiscal}")
    
    if not UsoCFDICatalog.is_valid(uso_cfdi):
        errores.append(f"Uso de CFDI inválido: {uso_cfdi}")
    
    if not FormaPagoCatalog.is_valid(forma_pago):
        errores.append(f"Forma de pago inválida: {forma_pago}")
    
    return len(errores) == 0, errores
```

---

## Roadmap

### Versión 0.3.0 (Actual - Noviembre 2025)

**Completado**:
- Códigos postales SEPOMEX completos (157,252 registros)
- Municipios INEGI completos (2,478 registros)
- Localidades INEGI con coordenadas GPS (10,635 registros)
- Búsqueda geográfica por coordenadas
- Datos de población y vivienda (Censo 2020)
- Clasificación urbano/rural
- Documentación bilingüe

### Versión 0.4.0 (Planeado - Q1 2025)

**Planeado**:
- Implementación SQLite para catálogos grandes
- Integración de geocodificación (añadir GPS a códigos postales)
- Tabla de correspondencia CP-Localidad pre-calculada
- Sincronización de catálogos TypeScript
- Ejemplos de servidor REST API
- Ejemplos de API GraphQL

### Versión 0.5.0 (Futuro - Q2-Q3 2025)

**Planeado**:
- Validadores adicionales (ISAN, placas vehiculares, MRZ)
- Catálogos IFT (telecomunicaciones)
- Catálogos IMSS (seguridad social)
- Catálogo TIGIE (arancel de aduanas)
- Versiones históricas de catálogos
- Normalización de direcciones con ML
- Compilación WebAssembly para validadores

**Roadmap Completo**: Ver [docs/roadmap.md](docs/roadmap.md) para roadmap detallado por catálogo y estrategia de implementación.

---

## Estrategia SQLite

Para catálogos con >10,000 registros, se proporcionará opción SQLite en v0.4.0:

**Beneficios**:
- 30-40% menor tamaño de archivo
- 10-100x consultas más rápidas
- Índices espaciales (R-tree para GPS)
- Consultas complejas sin cargar todo el conjunto de datos
- Eficiente en memoria

**Implementación Planeada** (v0.4.0):

| Catálogo | Tamaño JSON | Tamaño SQLite | Ganancia de Performance |
|---------|-------------|---------------|------------------------|
| SEPOMEX | 43.53 MB | ~25 MB | 100x consultas más rápidas |
| Localidades | 5.22 MB | ~3 MB | Soporte de índice espacial |

---

## Estrategia de Actualización de Catálogos

### Frecuencias de Actualización

| Catálogo | Frecuencia | Fuente | Auto-actualización |
|---------|-----------|--------|-------------------|
| SEPOMEX | Mensual | correosdemexico.gob.mx | Planeado (v0.4.0) |
| INEGI | Anual | inegi.org.mx | Manual |
| SAT CFDI | Trimestral | sat.gob.mx | Planeado (v0.4.0) |
| Banxico | Trimestral | banxico.org.mx | Planeado (v0.4.0) |

### Proceso Actual

```bash
# Verificar actualizaciones
python scripts/check_catalog_updates.py

# Descargar y procesar
python scripts/fetch_sat_catalogs.py
python scripts/process_sepomex_file.py
python scripts/process_inegi_municipios.py
```

**Actualizaciones automáticas planeadas para v0.4.0**

---

## Contribuir

Las contribuciones son bienvenidas. Consulta [CONTRIBUTING.rst](CONTRIBUTING.rst) para lineamientos.

### Configuración para Desarrollo

```bash
git clone https://github.com/openbancor/catalogmx.git
cd catalogmx

# Python
cd packages/python
pip install -e ".[dev]"
pytest

# TypeScript
cd packages/typescript
npm install
npm test
```

### Agregar Nuevos Catálogos

Ver [Guía del Desarrollador](docs/guides/developers-guide.md) para instrucciones detalladas sobre:
- Crear archivos JSON de catálogos
- Implementar clases de catálogos
- Escribir pruebas
- Actualizar documentación

---

## Estructura del Proyecto

```
catalogmx/
├── README.md                   # Este archivo (inglés)
├── README.es.md                # Este archivo (español)
├── LICENSE                     # Licencia BSD 2-Clause
├── CONTRIBUTING.rst            # Guía de contribución
├── CHANGELOG.rst               # Historial del proyecto
│
├── docs/                       # Documentación
│   ├── guides/                 # Guías técnicas
│   ├── catalogs/              # Documentación de catálogos
│   ├── api/                    # Referencia API
│   ├── roadmap.md             # Roadmap detallado
│   └── releases/              # Notas de release
│
├── packages/
│   ├── python/                # Implementación Python
│   │   ├── catalogmx/
│   │   ├── tests/
│   │   ├── pyproject.toml     # Configuración Python moderna
│   │   └── requirements.txt
│   │
│   ├── typescript/            # Implementación TypeScript
│   │   ├── src/
│   │   ├── tests/
│   │   └── package.json
│   │
│   └── shared-data/           # Datos de catálogos JSON
│       ├── sepomex/          # 157K códigos postales
│       ├── inegi/            # Municipios y localidades
│       ├── sat/              # Catálogos fiscales
│       └── banxico/          # Datos bancarios
│
└── scripts/                   # Scripts de procesamiento
    ├── process_sepomex_file.py
    ├── process_inegi_municipios.py
    └── process_inegi_localidades.py
```

---

## Licencia

Licencia BSD 2-Clause. Ver [LICENSE](LICENSE) para detalles.

---

## Reconocimientos

### Fuentes Oficiales de Datos

- **SAT** - Servicio de Administración Tributaria
- **INEGI** - Instituto Nacional de Estadística y Geografía
- **SEPOMEX** - Servicio Postal Mexicano
- **Banxico** - Banco de México
- **RENAPO** - Registro Nacional de Población

### Stack Tecnológico

- Python 3.10+ con type hints modernos (PEP 604)
- TypeScript 5.0+
- Sin dependencias externas (validadores)
- Arquitectura de carga perezosa (lazy loading)
- Almacenamiento de catálogos basado en JSON

---

## Soporte

- **Documentación**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/openbancor/catalogmx/issues)
- **Email**: luisfernando@informind.com

---

## Estadísticas del Proyecto

```
Tamaño del Paquete:  ~50 MB (todos los catálogos)
Total Catálogos:     43
Total Registros:     170,505+
Población:           126,014,024 (cobertura 100%)
Localidades GPS:     10,635
Municipios:          2,478
Códigos Postales:    157,252
Bancos:              110
```

---

**catalogmx** v0.3.0 | Noviembre 2025 | Hecho para la comunidad de desarrolladores mexicanos
