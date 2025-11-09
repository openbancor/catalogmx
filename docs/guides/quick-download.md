# 🚀 Descarga Rápida de Catálogos Completos

## ⚡ Solución Rápida (Recomendada)

### Opción 1: Descarga Directa de Archivos Procesados

**SEPOMEX Completo** (~150,000 códigos postales):
```bash
# Descarga desde repositorio community-maintained
wget https://raw.githubusercontent.com/IcaliaLabs/sepomex/master/sepomex_db.csv

# Convierte a JSON de catalogmx
python scripts/csv_to_catalogmx.py sepomex_db.csv
```

**INEGI Municipios Completos** (2,478 municipios):
```bash
# Descarga catálogo oficial procesado
wget https://raw.githubusercontent.com/angelmotta/mexico-municipality-catalog/main/municipalities.json

# Convierte al formato catalogmx
python scripts/json_to_catalogmx_municipios.py municipalities.json
```

### Opción 2: Descarga Oficial y Procesa

**SEPOMEX**:
1. Ve a: https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx
2. Descarga el Excel
3. Ejecuta: `python scripts/process_sepomex_excel.py archivo.xlsx`

**INEGI**:
1. Ve a: https://www.inegi.org.mx/app/ageeml/
2. Descarga formato TXT o Excel
3. Ejecuta: `python scripts/process_inegi_data.py archivo.txt`

---

## 📊 Situación Actual

**Catálogos en el repositorio**:
- ✅ SEPOMEX: 273 códigos (32 estados, ciudades principales)
- ✅ INEGI: 209 municipios (32 estados, capitales + ciudades 100k+)

**Para producción** necesitas:
- 📥 SEPOMEX: ~150,000 códigos postales completos
- 📥 INEGI: 2,478 municipios completos

---

## 🔧 Scripts de Conversión

He creado scripts para procesar archivos oficiales:

```bash
# SEPOMEX de CSV/Excel a catalogmx JSON
python scripts/csv_to_catalogmx.py <archivo>

# INEGI de TXT/Excel a catalogmx JSON
python scripts/process_inegi_data.py <archivo>

# Cualquier JSON externo a formato catalogmx
python scripts/convert_to_catalogmx_format.py <archivo>
```

---

## 🌐 Fuentes de Datos Oficiales

### SEPOMEX (Correos de México)
- **Oficial**: https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx
- **API**: https://api.sepomex.com/ (no oficial, pero funcional)
- **GitHub**: https://github.com/IcaliaLabs/sepomex (procesado)

### INEGI (Municipios)
- **Oficial**: https://www.inegi.org.mx/app/ageeml/
- **Marco Geo**: https://www.inegi.org.mx/app/biblioteca/ficha.html?upc=889463807469
- **API**: https://www.inegi.org.mx/servicios/api_indicadores.html

---

## 💾 Formato Esperado

Los scripts convierten a este formato:

**INEGI** (`municipios_completo.json`):
```json
{
  "metadata": {
    "total_records": 2478,
    "source": "INEGI"
  },
  "municipios": [
    {
      "cve_entidad": "01",
      "nom_entidad": "Aguascalientes",
      "cve_municipio": "001",
      "nom_municipio": "Aguascalientes",
      "cve_completa": "01001"
    }
  ]
}
```

**SEPOMEX** (`codigos_postales_completo.json`):
```json
{
  "metadata": {
    "total_records": 150000,
    "source": "SEPOMEX"
  },
  "codigos_postales": [
    {
      "cp": "01000",
      "asentamiento": "San Ángel",
      "tipo_asentamiento": "Colonia",
      "municipio": "Álvaro Obregón",
      "estado": "Ciudad de México",
      "ciudad": "Ciudad de México",
      "cp_oficina": "01001",
      "codigo_estado": "09",
      "codigo_municipio": "010"
    }
  ]
}
```

---

## ⚠️ Problemas de Conectividad

Si los servidores oficiales no responden:

1. **Espera y reintenta** (servidores gubernamentales a veces lentos)
2. **Usa VPN** si estás fuera de México
3. **Usa repositorios community-maintained** (GitHub)
4. **Descarga en navegador** y luego procesa localmente

---

## 🎯 Próximos Pasos

1. **Descarga uno de los archivos** usando las URLs arriba
2. **Ejecuta el script de conversión** correspondiente
3. **Los archivos se guardarán** en `packages/shared-data/`
4. **catalogmx los cargará automáticamente** (lazy loading)

¿Necesitas ayuda con algún paso específico?
