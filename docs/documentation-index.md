# 📚 Índice de Documentación - catalogmx

**Guía completa de toda la documentación disponible**

---

## 🚀 Inicio Rápido

| Documento | Descripción | Idioma |
|-----------|-------------|--------|
| **[README.md](README.md)** | Documentación principal | 🌍 English |
| **[README.es.md](README.es.md)** | Documentación principal | 🇲🇽 Español |

**Recomendación**: Empieza con el README en tu idioma preferido.

---

## 📖 Documentación por Categoría

### 🎯 Para Usuarios

#### Empezar a Usar
- **[README.md](README.md)** / **[README.es.md](README.es.md)** - Inicio rápido y ejemplos
- **[README_CATALOGMX.md](README_CATALOGMX.md)** - Documentación detallada de catálogos

#### Descargar Datos
- **[DESCARGA_CATALOGOS_COMPLETOS.md](DESCARGA_CATALOGOS_COMPLETOS.md)** - Cómo obtener catálogos completos
- **[DESCARGA_RAPIDA.md](DESCARGA_RAPIDA.md)** - Guía rápida de descarga

#### Guías Especializadas
- **[VINCULACION_CP_LOCALIDAD.md](VINCULACION_CP_LOCALIDAD.md)** - Vincular códigos postales con localidades
- **[CURP_ESPECIFICACIONES_OFICIALES.md](CURP_ESPECIFICACIONES_OFICIALES.md)** - Especificaciones oficiales de CURP

---

### 👨‍💻 Para Desarrolladores

#### Arquitectura y Diseño
- **[AGENTS.md](AGENTS.md)** - Guía completa para desarrolladores e IA
- **[CLAUDE.md](CLAUDE.md)** - Arquitectura técnica y decisiones de diseño
- **[DOCUMENTACION_BILINGUE.md](DOCUMENTACION_BILINGUE.md)** - Estrategia de documentación

#### Contribuir
- **[CONTRIBUTING.rst](CONTRIBUTING.rst)** - Guía de contribución
- **[CATALOG_UPDATES.md](CATALOG_UPDATES.md)** - Cómo actualizar catálogos

#### Específico por Lenguaje
- **Python**: `packages/python/README.md` (si existe)
- **TypeScript**: `packages/typescript/README.md`

---

### 📊 Referencia

#### Catálogos
- **[RESUMEN_FINAL.md](RESUMEN_FINAL.md)** - Resumen completo de todos los catálogos
- **[CATALOGOS_ADICIONALES.md](CATALOGOS_ADICIONALES.md)** - Catálogos adicionales disponibles
- **[PROGRESO_DESCARGA.md](PROGRESO_DESCARGA.md)** - Estado de descargas

#### Historial
- **[CHANGELOG.rst](CHANGELOG.rst)** - Historial de cambios del proyecto
- **[CHANGELOG_CATALOGS.md](CHANGELOG_CATALOGS.md)** - Historial de cambios de catálogos
- **[SESION_COMPLETA.md](SESION_COMPLETA.md)** - Resumen de esta sesión (2025-11-08)

---

## 🗺️ Mapa de Navegación

### Si quieres...

#### Usar la librería
1. Lee **[README.md](README.md)** o **[README.es.md](README.es.md)**
2. Instala: `pip install catalogmx` o `npm install catalogmx`
3. Consulta ejemplos en los READMEs

#### Contribuir al proyecto
1. Lee **[CONTRIBUTING.rst](CONTRIBUTING.rst)**
2. Revisa **[AGENTS.md](AGENTS.md)** para estructura del código
3. Consulta **[CLAUDE.md](CLAUDE.md)** para arquitectura

#### Entender los catálogos
1. Lee **[RESUMEN_FINAL.md](RESUMEN_FINAL.md)** para visión general
2. Consulta **[README_CATALOGMX.md](README_CATALOGMX.md)** para detalles
3. Revisa **[VINCULACION_CP_LOCALIDAD.md](VINCULACION_CP_LOCALIDAD.md)** para vinculación

#### Actualizar catálogos
1. Lee **[CATALOG_UPDATES.md](CATALOG_UPDATES.md)**
2. Usa scripts en `scripts/`
3. Consulta **[DESCARGA_CATALOGOS_COMPLETOS.md](DESCARGA_CATALOGOS_COMPLETOS.md)**

#### Entender decisiones técnicas
1. Lee **[CLAUDE.md](CLAUDE.md)** - Arquitectura
2. Consulta **[AGENTS.md](AGENTS.md)** - Patrones de código
3. Revisa **[DOCUMENTACION_BILINGUE.md](DOCUMENTACION_BILINGUE.md)** - Estrategia

---

## 📂 Estructura de Archivos

```
catalogmx/
│
├── 📖 DOCUMENTACIÓN PRINCIPAL
│   ├── README.md                          (🌍 English)
│   ├── README.es.md                       (🇲🇽 Español)
│   ├── README_CATALOGMX.md                (Catálogos detallados)
│   └── DOCS_INDEX.md                      (Este archivo)
│
├── 📊 RESÚMENES Y REPORTES
│   ├── RESUMEN_FINAL.md                   (Resumen completo)
│   ├── SESION_COMPLETA.md                 (Sesión 2025-11-08)
│   └── PROGRESO_DESCARGA.md               (Estado de descargas)
│
├── 🔧 GUÍAS TÉCNICAS
│   ├── AGENTS.md                          (Guía desarrolladores)
│   ├── CLAUDE.md                          (Arquitectura)
│   ├── DOCUMENTACION_BILINGUE.md          (Estrategia docs)
│   └── CONTRIBUTING.rst                   (Cómo contribuir)
│
├── 📥 GUÍAS DE DESCARGA
│   ├── DESCARGA_CATALOGOS_COMPLETOS.md    (Catálogos completos)
│   ├── DESCARGA_RAPIDA.md                 (Descarga rápida)
│   └── VINCULACION_CP_LOCALIDAD.md        (Vinculación CP↔Loc)
│
├── 📋 CATÁLOGOS Y ACTUALIZACIONES
│   ├── CATALOGOS_ADICIONALES.md           (Catálogos extra)
│   ├── CATALOG_UPDATES.md                 (Procedimientos)
│   └── CHANGELOG_CATALOGS.md              (Historial)
│
├── 📜 ESPECIFICACIONES
│   └── CURP_ESPECIFICACIONES_OFICIALES.md (Specs oficiales CURP)
│
└── 📝 OTROS
    ├── CHANGELOG.rst                      (Historial proyecto)
    ├── AUTHORS.rst                        (Autores)
    └── LICENSE                            (Licencia BSD)
```

---

## 🔍 Búsqueda Rápida

### Por Tema

**Validadores**
- RFC → README.md / README.es.md
- CURP → README.md + CURP_ESPECIFICACIONES_OFICIALES.md
- CLABE → README.md / README.es.md
- NSS → README.md / README.es.md

**Catálogos**
- SAT → README_CATALOGMX.md
- INEGI → RESUMEN_FINAL.md
- SEPOMEX → RESUMEN_FINAL.md
- Banxico → README_CATALOGMX.md

**Geolocalización**
- GPS Search → README.md + RESUMEN_FINAL.md
- Localidades → RESUMEN_FINAL.md
- Vinculación → VINCULACION_CP_LOCALIDAD.md

**Desarrollo**
- Arquitectura → CLAUDE.md
- Patrones → AGENTS.md
- Contribuir → CONTRIBUTING.rst

---

## 🌍 Versiones de Idioma

| Documento | 🌍 English | 🇲🇽 Español |
|-----------|-----------|-----------|
| README principal | ✅ README.md | ✅ README.es.md |
| Guías técnicas | ❌ | ✅ AGENTS.md, CLAUDE.md |
| Guías de descarga | ❌ | ✅ DESCARGA_*.md |
| Resúmenes | ❌ | ✅ RESUMEN_FINAL.md |
| Contributing | ✅ CONTRIBUTING.rst | ❌ |

**Nota**: El código fuente (docstrings, comments) está 100% en inglés.

---

## 📊 Estadísticas de Documentación

```
Total documentos:        20+
Idiomas:                 2 (English + Español)
README principal:        Bilingüe
Guías técnicas:          Español
Código fuente:           Inglés
Ejemplos:                Bilingüe (planeado)
```

---

## 🎯 Recomendaciones

### Para Nuevos Usuarios
1. **[README.md](README.md)** o **[README.es.md](README.es.md)** - Empieza aquí
2. **[RESUMEN_FINAL.md](RESUMEN_FINAL.md)** - Revisa capacidades completas
3. Prueba los ejemplos de código

### Para Desarrolladores
1. **[AGENTS.md](AGENTS.md)** - Entiende la estructura
2. **[CLAUDE.md](CLAUDE.md)** - Entiende la arquitectura
3. **[CONTRIBUTING.rst](CONTRIBUTING.rst)** - Contribuye

### Para Mantenedores
1. **[CATALOG_UPDATES.md](CATALOG_UPDATES.md)** - Procedimientos
2. **[DESCARGA_CATALOGOS_COMPLETOS.md](DESCARGA_CATALOGOS_COMPLETOS.md)** - Descargas
3. Scripts en `scripts/` - Herramientas

---

**Última actualización**: 2025-11-08  
**catalogmx** v0.3.0  
**Documentos**: 20+ | **Idiomas**: 2

