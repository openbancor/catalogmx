# 🔗 Vinculación Código Postal ↔ Localidad

## Problema
- **INEGI Localidades**: 296,837 localidades con coordenadas GPS pero SIN código postal
- **SEPOMEX**: 157,252 códigos postales con municipio/asentamiento pero SIN coordenadas

## Estrategias de Vinculación

### 1️⃣ Por Municipio + Nombre (Aproximado)
```python
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import LocalidadesCatalog  # si lo procesamos

def vincular_por_nombre(localidad):
    """Buscar CP por municipio y similitud de nombre"""
    cps = CodigosPostales.get_by_municipio(localidad['nom_mun'])
    
    # Buscar coincidencia de nombre
    for cp in cps:
        if localidad['nom_loc'].lower() in cp['asentamiento'].lower():
            return cp['cp']
    
    return None

# Ejemplo:
localidad = {
    'nom_loc': 'Agua Azul',
    'nom_mun': 'Aguascalientes',
    'cve_mun': '001'
}
cp = vincular_por_nombre(localidad)  # Puede encontrar 20XXX
```

**Precisión**: ~60-70% (solo localidades urbanas con nombre coincidente)

---

### 2️⃣ Por Coordenadas GPS + Municipio (Preciso)
```python
from math import radians, sin, cos, sqrt, atan2

def distancia_haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia en km entre dos puntos GPS"""
    R = 6371  # Radio de la Tierra en km
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def vincular_por_gps(localidad, catalogo_cps_con_gps):
    """Buscar CP más cercano por coordenadas"""
    lat_loc = localidad['lat_decimal']
    lon_loc = localidad['lon_decimal']
    
    cp_mas_cercano = None
    distancia_minima = float('inf')
    
    # Filtrar por municipio primero
    cps_municipio = [cp for cp in catalogo_cps_con_gps 
                     if cp['codigo_municipio'] == localidad['cve_mun']]
    
    for cp in cps_municipio:
        distancia = distancia_haversine(
            lat_loc, lon_loc,
            cp['latitud'], cp['longitud']
        )
        
        if distancia < distancia_minima:
            distancia_minima = distancia
            cp_mas_cercano = cp
    
    # Solo retornar si está a menos de 5 km
    if distancia_minima < 5:
        return cp_mas_cercano['cp'], distancia_minima
    
    return None, None
```

**Problema**: SEPOMEX NO tiene coordenadas GPS 😞

**Solución**: Geocodificar códigos postales usando APIs externas:
- Google Geocoding API
- OpenStreetMap Nominatim
- INEGI API (si disponible)

---

### 3️⃣ Tabla de Correspondencia Pre-calculada
```python
# Crear tabla de correspondencia offline
import json
from fuzzywuzzy import fuzz  # similarity scoring

def generar_tabla_correspondencia():
    """
    Genera tabla de vinculación CP ↔ Localidad
    Guardado en: correspondencia_cp_localidad.json
    """
    correspondencias = []
    
    localidades = LocalidadesCatalog.get_all()
    codigos_postales = CodigosPostales.get_all()
    
    for localidad in localidades:
        if localidad['ambito'] == 'R':  # Rural, difícil vincular
            continue
        
        # Buscar en mismo municipio
        cps_mun = [cp for cp in codigos_postales 
                   if cp['codigo_municipio'] == localidad['cve_mun']]
        
        mejor_match = None
        mejor_score = 0
        
        for cp in cps_mun:
            # Calcular similitud de nombres
            score = fuzz.ratio(
                localidad['nom_loc'].lower(),
                cp['asentamiento'].lower()
            )
            
            if score > mejor_score:
                mejor_score = score
                mejor_match = cp
        
        # Solo guardar si hay buena coincidencia
        if mejor_score > 80:
            correspondencias.append({
                'cvegeo_localidad': localidad['cvegeo'],
                'nom_localidad': localidad['nom_loc'],
                'codigo_postal': mejor_match['cp'],
                'asentamiento': mejor_match['asentamiento'],
                'score_similitud': mejor_score
            })
    
    with open('correspondencia_cp_localidad.json', 'w') as f:
        json.dump(correspondencias, f, ensure_ascii=False, indent=2)
    
    return correspondencias
```

---

## 📊 Ejemplos de Localidades Microgranulares

### Localidades Urbanas (fácil de vincular)
```
Localidad: Aguascalientes (ciudad)
CVE_LOC: 010010001
Población: 863,893
Ámbito: U (Urbano)
GPS: 21.87982200, -102.29604600
→ CP: 20000-20999 (Aguascalientes tiene ~50 CPs)
```

### Localidades Rurales Pequeñas
```
Localidad: Granja Adelita
CVE_LOC: 010010094
Población: 5 habitantes
Ámbito: R (Rural)
GPS: 21.87187400, -102.37353000
→ CP: Probablemente 20xxx (mismo CP que localidad urbana cercana)
```

### Colonias dentro de Ciudad
```
Localidad: Roma Norte (si existiera en INEGI)
Municipio: Cuauhtémoc
→ CP: 06700

Localidad: Polanco
Municipio: Miguel Hidalgo
→ CP: 11550
```

---

## 🎯 Recomendaciones

### Para Aplicaciones Simples
✅ **Usar solo SEPOMEX** (157,252 CPs)
- Suficiente para validación de direcciones
- Cobertura urbana completa
- No requiere geocodificación

### Para Aplicaciones con Mapas
✅ **Usar Localidades INEGI** (296,837)
- Tiene coordenadas GPS precisas
- Útil para visualización en mapas
- Vincular con CP por nombre/municipio (aproximado)

### Para Máxima Precisión
✅ **Geocodificar CPs + Vincular con Localidades**
1. Geocodificar los 157,252 CPs usando API externa
2. Guardar lat/lon en base de datos
3. Vincular con localidades por proximidad GPS
4. Resultado: Tabla completa CP ↔ Localidad con coordenadas

---

## 💡 ¿Procesar las 296,837 Localidades?

**Ventajas:**
- ✅ Coordenadas GPS precisas
- ✅ Granularidad hasta rancherías
- ✅ Datos de población por localidad
- ✅ Útil para aplicaciones geográficas

**Desventajas:**
- ❌ Archivo muy grande (~60 MB JSON)
- ❌ Sin código postal (requiere vinculación)
- ❌ Mayoría son localidades rurales pequeñas

**Alternativa:**
- Filtrar solo localidades urbanas (ámbito='U')
- O solo localidades >1,000 habitantes
- Esto reduciría a ~10,000-15,000 localidades relevantes

