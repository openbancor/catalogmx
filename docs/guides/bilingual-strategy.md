# 📖 Estrategia de Documentación Bilingüe

## 🌍 Filosofía

**catalogmx** es una librería mexicana con alcance global. Por ello, adoptamos una estrategia bilingüe:

- **Código e Interfaces**: Inglés (estándar internacional)
- **Documentación**: Bilingüe (inglés + español)
- **Contenido de Catálogos**: Español (datos oficiales mexicanos)

---

## 📝 Estructura de Documentación

### 🌍 Documentación en Inglés (International)

| Archivo | Propósito | Audiencia |
|---------|-----------|-----------|
| **README.md** | Documentación principal | Global |
| **API docstrings** | Documentación de código | Desarrolladores (IDEs) |
| **Type hints** | Anotaciones de tipo | Desarrolladores |
| **Code comments** | Comentarios técnicos | Desarrolladores |

### 🇲🇽 Documentación en Español (Local Context)

| Archivo | Propósito | Audiencia |
|---------|-----------|-----------|
| **README.es.md** | Documentación principal en español | México/LATAM |
| **AGENTS.md** | Guía para desarrolladores | Desarrolladores locales |
| **CLAUDE.md** | Arquitectura y diseño | Desarrolladores avanzados |
| **CATALOG_UPDATES.md** | Procedimientos de actualización | Mantenedores |
| **Catalog descriptions** | Descripciones de regímenes, etc. | Usuarios finales |

### 🔄 Documentación Bilingüe

| Archivo | Contenido | Razón |
|---------|-----------|-------|
| **CONTRIBUTING.rst** | Inglés (estándar open source) | Contribuidores globales |
| **LICENSE** | Inglés (estándar legal) | Claridad legal |
| **Ejemplos** | Ambos idiomas | Todos los usuarios |

---

## 💻 Código Fuente

### ✅ Siempre en Inglés

```python
# ✅ CORRECTO - Inglés
class LocalidadesCatalog:
    """Catalog of Mexican localities with 1,000+ inhabitants"""
    
    def get_by_coordinates(self, lat: float, lon: float, radius_km: float):
        """
        Find localities near GPS coordinates.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            radius_km: Search radius in kilometers
        
        Returns:
            List of localities within the radius
        """
        pass
```

```python
# ❌ INCORRECTO - Español en código
class CatalogoLocalidades:
    """Catálogo de localidades mexicanas con 1,000+ habitantes"""
    
    def obtener_por_coordenadas(self, lat: float, lon: float, radio_km: float):
        """
        Encuentra localidades cerca de coordenadas GPS.
        """
        pass
```

**Razón**: 
- Los IDEs y herramientas están optimizados para inglés
- Facilita colaboración internacional
- Estándar de la industria

---

## 📊 Contenido de Catálogos

### ✅ En Español (Datos Oficiales)

```json
{
  "code": "605",
  "description": "Sueldos y Salarios e Ingresos Asimilados a Salarios",
  "fisica": true,
  "moral": false
}
```

**Razón**: 
- Son datos oficiales del SAT/INEGI/SEPOMEX
- Los usuarios finales esperan español
- Precisión legal y fiscal

### ✅ Metadatos en Inglés

```json
{
  "metadata": {
    "catalog": "RegimenFiscal",
    "version": "2025",
    "source": "SAT",
    "total_records": 26
  }
}
```

**Razón**: 
- Facilita procesamiento programático
- Estándar JSON internacional

---

## 📖 Guía de Estilo

### Nombres de Variables y Funciones

```python
# ✅ CORRECTO
def calculate_rfc(name, first_surname, second_surname, birth_date):
    pass

# ❌ INCORRECTO
def calcular_rfc(nombre, apellido_paterno, apellido_materno, fecha_nacimiento):
    pass
```

### Comentarios en Código

```python
# ✅ CORRECTO - Inglés para lógica
def validate_clabe(clabe: str) -> bool:
    """Validate Mexican bank account (CLABE)"""
    # Check length
    if len(clabe) != 18:
        return False
    
    # Calculate check digit using Modulo 10
    weights = [3,7,1,3,7,1,3,7,1,3,7,1,3,7,1,3,7]
    ...
```

### Mensajes de Error

```python
# ✅ BILINGÜE cuando sea crítico
class ValidationError(Exception):
    def __init__(self, message_en: str, message_es: str = None):
        self.message_en = message_en
        self.message_es = message_es or message_en
        super().__init__(message_en)

# Uso
raise ValidationError(
    message_en="Invalid RFC: must be 12 or 13 characters",
    message_es="RFC inválido: debe tener 12 o 13 caracteres"
)
```

---

## 📚 Ejemplos de Uso

### README Examples

Proporcionar ambas versiones:

**README.md (English)**
```python
# Search localities near Mexico City
localities = LocalidadesCatalog.get_by_coordinates(
    lat=19.4326, lon=-99.1332, radius_km=50
)
```

**README.es.md (Spanish)**
```python
# Buscar localidades cerca de Ciudad de México
localidades = LocalidadesCatalog.get_by_coordinates(
    lat=19.4326, lon=-99.1332, radio_km=50
)
```

### Documentation Examples

Crear directorio `examples/` con versiones bilingües:

```
examples/
├── en/
│   ├── address_validation.py
│   ├── cfdi_validation.py
│   └── geographic_search.py
└── es/
    ├── validacion_direccion.py
    ├── validacion_cfdi.py
    └── busqueda_geografica.py
```

---

## 🔄 Proceso de Traducción

### Para Nuevas Funcionalidades

1. **Código**: Escribir en inglés
2. **Docstrings**: Escribir en inglés
3. **README.md**: Actualizar en inglés
4. **README.es.md**: Traducir al español
5. **Ejemplos**: Crear versiones en ambos idiomas

### Mantenimiento

- README.md y README.es.md deben mantenerse sincronizados
- Los cambios en el roadmap deben reflejarse en ambos
- Las versiones deben ser equivalentes, no traducciones literales

---

## 🎯 Beneficios de Esta Estrategia

### Para Desarrolladores Internacionales
✅ Código totalmente en inglés
✅ Documentation en inglés disponible
✅ Facilita contribuciones
✅ Compatible con herramientas estándar

### Para Desarrolladores Mexicanos
✅ README en español disponible
✅ Ejemplos en español
✅ Datos de catálogos en español
✅ Guías técnicas en español

### Para Usuarios Finales
✅ Descripciones de catálogos en español
✅ Datos oficiales sin traducción
✅ Precisión en términos legales/fiscales

---

## 📋 Checklist para Nuevas Contribuciones

Antes de hacer un Pull Request, verificar:

### Código
- [ ] Nombres de variables/funciones en inglés
- [ ] Docstrings en inglés
- [ ] Type hints correctos
- [ ] Comentarios técnicos en inglés

### Documentación
- [ ] README.md actualizado (inglés)
- [ ] README.es.md actualizado (español)
- [ ] Ambas versiones sincronizadas
- [ ] Ejemplos en ambos idiomas (si aplica)

### Catálogos
- [ ] Descripciones en español (datos oficiales)
- [ ] Metadatos en inglés
- [ ] JSON válido con encoding UTF-8

---

## 🌐 Recursos

### Herramientas
- **DeepL**: Traducción de alta calidad para documentación
- **Google Translate**: Verificación rápida
- **Grammarly**: Revisión de inglés
- **LanguageTool**: Revisión de español

### Referencias
- **PEP 8**: Guía de estilo Python (inglés)
- **SAT**: Glosarios oficiales (español)
- **INEGI**: Terminología geográfica (español)

---

## 📞 Contacto

¿Dudas sobre la estrategia de documentación?

- Abre un issue en GitHub
- Consulta [CONTRIBUTING.rst](CONTRIBUTING.rst)
- Revisa [AGENTS.md](AGENTS.md) para guías de desarrollo

---

**Última actualización**: 2025-11-08  
**catalogmx** v0.3.0

