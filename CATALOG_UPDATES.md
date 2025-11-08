# 📅 Gestión de Actualizaciones de Catálogos

Sistema de monitoreo y actualización de catálogos oficiales mexicanos.

---

## 🎯 Resumen Ejecutivo

| Prioridad | Frecuencia | Catálogos | Última Verificación |
|-----------|------------|-----------|---------------------|
| 🔴 ALTA | Mensual | SAT CFDI 4.0 (12 catálogos) | Pendiente |
| 🟠 MEDIA | Trimestral | TIGIE/NICO Fracciones Arancelarias | Pendiente |
| 🟡 BAJA | Semestral | Banxico Bancos, SEPOMEX | Pendiente |
| 🟢 MONITOR | Anual | INEGI Estados/Municipios | Pendiente |
| ⚪ ESTÁTICO | N/A | INCOTERMS, ISO standards | 2025-11-08 |

---

## 📋 Catálogos por Fuente Oficial

### 🏛️ SAT (Servicio de Administración Tributaria)

#### **Catálogos CFDI 4.0 - Anexo 20**
📍 **Fuente**: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/anexo_20_version3-3.htm
🔄 **Frecuencia**: **Mensual** (SAT publica actualizaciones frecuentes)
⚠️ **Criticidad**: ALTA - Afecta validación de facturas electrónicas

| # | Catálogo | Estado | Registros | Última Actualización SAT |
|---|----------|--------|-----------|--------------------------|
| 1 | c_RegimenFiscal | ⏳ Pendiente | ~40 | Variable |
| 2 | c_UsoCFDI | ⏳ Pendiente | ~25 | Variable |
| 3 | c_FormaPago | ⏳ Pendiente | ~20 | Variable |
| 4 | c_MetodoPago | ⏳ Pendiente | 4 | Estable |
| 5 | c_TipoComprobante | ⏳ Pendiente | 5 | Estable |
| 6 | c_Impuesto | ⏳ Pendiente | 4 | Estable |
| 7 | c_TasaOCuota | ⏳ Pendiente | ~50 | Variable |
| 8 | c_Moneda | ✅ Implementado | 180 | Estable (ISO) |
| 9 | c_Pais | ✅ Implementado | 249 | Estable (ISO) |
| 10 | c_TipoRelacion | ⏳ Pendiente | 10 | Estable |
| 11 | c_Exportacion | ⏳ Pendiente | 4 | Estable |
| 12 | c_ObjetoImp | ⏳ Pendiente | 8 | Actualizado 2024 |

**URL de descarga**:
```
http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/catCFDI.xls
```

**Formato**: Excel (.xls) con múltiples hojas
**Proceso**: Descargar → Parsear Excel → Convertir a JSON → Validar cambios

---

#### **Comercio Exterior 2.0**
📍 **Fuente**: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/catalogos_emision_cfdi_complemento_ce.htm
🔄 **Frecuencia**: **Trimestral**
⚠️ **Criticidad**: ALTA - Exportaciones/Importaciones

| # | Catálogo | Estado | Registros | Frecuencia Actualización |
|---|----------|--------|-----------|--------------------------|
| 1 | c_INCOTERM | ✅ Implementado | 11 | Cada 10 años (próx: 2030) |
| 2 | c_ClavePedimento | ✅ Implementado | 42 | Anual (RGCE) |
| 3 | c_FraccionArancelaria (TIGIE/NICO) | ⏳ Pendiente | ~20,000 | **TRIMESTRAL** ⚠️ |
| 4 | c_UnidadAduana | ✅ Implementado | 32 | Raro |
| 5 | c_RegistroIdentTribReceptor | ✅ Implementado | 15 | Raro |
| 6 | c_MotivoTraslado | ✅ Implementado | 6 | Raro |
| 7 | c_Moneda | ✅ Implementado | 180 | Raro (ISO) |
| 8 | c_Pais | ✅ Implementado | 249 | Raro (ISO) |
| 9 | c_Estado (USA/CAN) | ✅ Implementado | 63 | Casi nunca |

**Fuentes TIGIE**:
- **SNICE**: https://www.snice.gob.mx (oficial - requiere autenticación)
- **VUCEM**: https://www.ventanillaunica.gob.mx
- **SIICEX**: http://www.siicex.gob.mx

**Proceso actualización TIGIE**:
1. Consultar SNICE para última versión
2. Descargar archivo completo (~20,000 fracciones)
3. Actualizar SQLite database
4. Validar integridad
5. Notificar cambios

---

#### **Carta Porte 3.0**
📍 **Fuente**: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/CatalogosCartaPorte30.xls
🔄 **Frecuencia**: **Semestral**
⚠️ **Criticidad**: MEDIA - Transporte de mercancías

| # | Catálogo | Registros | Estado |
|---|----------|-----------|--------|
| 1 | c_CodigoTransporteAereo | 76 | ⏳ Pendiente |
| 2 | c_NumAutorizacionNaviero | 100 | ⏳ Pendiente |
| 3 | c_Estaciones | ~500 | ⏳ Pendiente |
| 4 | c_Carreteras | ~200 | ⏳ Pendiente |
| 5 | c_TipoPermiso | ~20 | ⏳ Pendiente |
| 6 | c_ConfigAutotransporte | ~15 | ⏳ Pendiente |
| 7 | c_TipoEmbalaje | ~30 | ⏳ Pendiente |
| 8 | c_MaterialPeligroso | ~3000 | ⏳ Pendiente (SQLite) |

**Formato**: Excel (.xls)
**Actualización**: SAT publica nuevas versiones semestralmente

---

#### **Complemento Nómina 1.2**
📍 **Fuente**: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/catalogos_emision_cfdi_nomina.htm
🔄 **Frecuencia**: **Anual**
⚠️ **Criticidad**: MEDIA

| # | Catálogo | Registros | Estado |
|---|----------|-----------|--------|
| 1 | c_TipoNomina | 2 | ⏳ Pendiente |
| 2 | c_TipoContrato | 10 | ⏳ Pendiente |
| 3 | c_TipoJornada | 8 | ⏳ Pendiente |
| 4 | c_TipoRegimen | 13 | ⏳ Pendiente |
| 5 | c_PeriodicidadPago | 10 | ⏳ Pendiente |
| 6 | c_Banco (para nómina) | ~50 | ⏳ Pendiente |
| 7 | c_RiesgoPuesto | 5 | ⏳ Pendiente |

---

### 🏦 Banxico (Banco de México)

#### **Catálogo de Instituciones Financieras**
📍 **Fuente**: https://www.banxico.org.mx/sistemas-de-pago/d/%7B5D5F2CAC-5C39-F7B7-44BC-AA5D7D0AABF9%7D.pdf
🔄 **Frecuencia**: **Mensual** (nuevos bancos raros, pero fusiones/cambios frecuentes)
⚠️ **Criticidad**: MEDIA

| Catálogo | Estado | Registros | Última Actualización |
|----------|--------|-----------|----------------------|
| Bancos (ABM) | ✅ Implementado | 100+ | 2025-11-08 |
| Bancos SPEI | ✅ Implementado | En banks.json | 2025-11-08 |

**Proceso**:
1. Descargar PDF mensual de Banxico
2. Extraer tabla de instituciones
3. Comparar con catálogo actual
4. Identificar: nuevos, eliminados, cambios de nombre/RFC
5. Actualizar banks.json

**URL descarga automática**: Pendiente investigar si existe API

---

#### **SIE - Sistema de Información Económica**
📍 **Fuente**: https://www.banxico.org.mx/SieAPIRest/service/v1/
🔄 **Frecuencia**: **Diaria** (datos), **Trimestral** (series nuevas)
⚠️ **Criticidad**: BAJA (solo si implementamos tasas históricas)

**Series relevantes**:
- TIIE 28d: SF60648
- CETES 28d: SF60633
- Tasa Objetivo: SF61745
- Tipo de cambio FIX: SF43718

**Proceso**: API REST - actualización automática vía consultas

---

### 🗺️ INEGI (Instituto Nacional de Estadística y Geografía)

#### **Catálogo de Estados**
📍 **Fuente**: https://www.inegi.org.mx/app/ageeml/
🔄 **Frecuencia**: **Casi nunca** (últimos cambios: creación de CDMX 2016)
⚠️ **Criticidad**: BAJA

| Catálogo | Estado | Registros |
|----------|--------|-----------|
| Estados | ✅ Implementado | 32 |
| Municipios | ⏳ Pendiente | 2,469 |
| Localidades | ⏳ Pendiente | ~90,000 |
| AGEBs | ⏳ Pendiente | ~200,000 |

**Formato**: Shapefile, Excel, CSV
**URL**: https://www.inegi.org.mx/app/biblioteca/ficha.html?upc=889463807469

**Proceso**:
1. Verificar anualmente si hay cambios
2. Descargar Marco Geoestadístico actualizado
3. Extraer catálogos
4. Actualizar JSON/SQLite

---

### 📮 SEPOMEX (Servicio Postal Mexicano)

#### **Códigos Postales**
📍 **Fuente**: https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx
🔄 **Frecuencia**: **Mensual** (nuevos desarrollos urbanos)
⚠️ **Criticidad**: MEDIA

| Catálogo | Registros | Estado |
|----------|-----------|--------|
| Códigos Postales | ~150,000 | ⏳ Pendiente (SQLite) |

**Formato**: TXT delimitado por pipe `|`
**Tamaño**: ~30 MB

**Proceso**:
1. Descargar TXT mensual
2. Parsear y validar
3. Actualizar SQLite con índices
4. Comparar cambios (nuevos, modificados)

---

### 📡 IFT (Instituto Federal de Telecomunicaciones)

#### **Códigos LADA**
📍 **Fuente**: http://www.ift.org.mx/usuarios-y-audiencias/recursos-usuarios/recursos/numeracion
🔄 **Frecuencia**: **Raro** (cambios en plan de numeración)
⚠️ **Criticidad**: BAJA

| Catálogo | Registros | Estado |
|----------|-----------|--------|
| LADA | ~400 | ⏳ Pendiente |
| Zonas numeración | ~50 | ⏳ Pendiente |

---

### 🌍 ISO (International Organization for Standardization)

#### **Standards internacionales**
🔄 **Frecuencia**: **Raro** (años entre cambios)
⚠️ **Criticidad**: BAJA

| Standard | Estado | Última Actualización | Próxima Actualización |
|----------|--------|----------------------|----------------------|
| ISO 4217 (Monedas) | ✅ Implementado | 2025 | Irregular |
| ISO 3166-1 (Países) | ✅ Implementado | 2024 | Irregular |
| ISO 3166-2 (Subdivisiones) | ✅ Implementado | 2024 | Irregular |
| INCOTERMS 2020 | ✅ Implementado | 2020 | 2030 |

**Fuentes**:
- https://www.iso.org/iso-4217-currency-codes.html
- https://www.iso.org/iso-3166-country-codes.html
- https://iccwbo.org/business-solutions/incoterms-rules/

---

### 🏛️ RENAPO (Registro Nacional de Población)

#### **CURP - Catálogos auxiliares**
📍 **Fuente**: https://www.gob.mx/curp
🔄 **Frecuencia**: **Casi nunca**
⚠️ **Criticidad**: BAJA

| Catálogo | Estado | Registros |
|----------|--------|-----------|
| Palabras antisonantes | ✅ Implementado | ~1,400 |
| Estados nacimiento | ✅ Implementado | 32 + extranjero |

---

## 🤖 Sistema de Monitoreo Automático

### Archivo: `scripts/check_catalog_updates.py`

**Funcionalidades**:
1. ✅ Verificar versiones de catálogos SAT
2. ✅ Descargar archivos si hay actualizaciones
3. ✅ Comparar con versión local (diff)
4. ✅ Generar reporte de cambios
5. ✅ Notificar vía email/slack (opcional)
6. ✅ Actualizar `.catalog-versions.json`

**Uso**:
```bash
# Verificar todos los catálogos
python scripts/check_catalog_updates.py --check-all

# Verificar solo SAT
python scripts/check_catalog_updates.py --source sat

# Verificar y descargar automáticamente
python scripts/check_catalog_updates.py --auto-update --source sat

# Generar reporte
python scripts/check_catalog_updates.py --report
```

---

### Archivo: `.catalog-versions.json`

**Tracking de versiones actuales**:
```json
{
  "last_check": "2025-11-08T00:00:00Z",
  "catalogs": {
    "sat": {
      "cfdi_4.0": {
        "version": "2024-12-01",
        "url": "http://omawww.sat.gob.mx/...",
        "checksum": "abc123...",
        "last_updated": "2024-12-01",
        "next_check": "2025-01-01"
      },
      "comercio_exterior": {
        "tigie": {
          "version": "2024-Q4",
          "records": 20145,
          "checksum": "def456...",
          "last_updated": "2024-10-01",
          "next_check": "2025-01-01"
        }
      }
    },
    "banxico": {
      "banks": {
        "version": "2025-11",
        "records": 102,
        "last_updated": "2025-11-08",
        "next_check": "2025-12-01"
      }
    },
    "inegi": {
      "estados": {
        "version": "2020",
        "records": 32,
        "last_updated": "2020-01-01",
        "next_check": "2026-01-01"
      }
    }
  }
}
```

---

## 📅 Calendario de Actualizaciones

### Verificación Mensual (Día 1 de cada mes)
- ✅ SAT CFDI 4.0 (Anexo 20)
- ✅ Banxico instituciones financieras
- ✅ SEPOMEX códigos postales

### Verificación Trimestral (Enero, Abril, Julio, Octubre)
- ✅ SAT TIGIE/NICO (Fracciones Arancelarias)
- ✅ Banxico SIE (nuevas series)

### Verificación Semestral (Enero, Julio)
- ✅ SAT Carta Porte 3.0
- ✅ INEGI (verificar cambios)

### Verificación Anual (Enero)
- ✅ SAT Nómina 1.2
- ✅ SAT Claves Pedimento (RGCE)
- ✅ IFT LADA
- ✅ ISO standards (4217, 3166)
- ✅ INCOTERMS (cada 10 años)

---

## 🔔 Sistema de Notificaciones

### Niveles de Alertas

**🔴 CRÍTICO** - Actualización inmediata requerida:
- Cambios en TIGIE que afecten fracciones en uso
- Cambios en catálogos CFDI que rompan validación
- Nuevos requisitos SAT obligatorios

**🟠 IMPORTANTE** - Actualización en 1 semana:
- Nuevos bancos/fusiones
- Cambios en Carta Porte
- Actualizaciones SEPOMEX grandes (>1000 CPs)

**🟡 NORMAL** - Actualización en 1 mes:
- Cambios menores en catálogos
- Nuevas series Banxico SIE
- Actualizaciones ISO

**🟢 INFO** - Solo seguimiento:
- Cambios en documentación
- Clarificaciones SAT
- Notas técnicas

---

## 📊 Métricas de Calidad

### Indicadores a monitorear:

1. **Freshness** (Frescura):
   - Días desde última actualización vs frecuencia esperada
   - Meta: 0 días de retraso en catálogos críticos

2. **Coverage** (Cobertura):
   - % de catálogos implementados vs planeados
   - Meta: 100% de catálogos críticos

3. **Accuracy** (Exactitud):
   - Diferencias detectadas entre fuente oficial y local
   - Meta: 0 diferencias en producción

4. **Response Time** (Tiempo de respuesta):
   - Tiempo desde que SAT publica hasta que actualizamos
   - Meta: <7 días para críticos, <30 para normales

---

## 🚀 Proceso de Actualización

### 1. Detección
```bash
# Ejecutar verificación automática
python scripts/check_catalog_updates.py --check-all
```

### 2. Descarga
```bash
# Descargar catálogos actualizados
python scripts/download_catalogs.py --source sat --catalog cfdi_4.0
```

### 3. Validación
```bash
# Validar integridad y formato
python scripts/validate_catalogs.py --catalog cfdi_4.0
```

### 4. Diff
```bash
# Generar reporte de cambios
python scripts/diff_catalogs.py --catalog cfdi_4.0 --old v1 --new v2
```

### 5. Actualización
```python
# Actualizar archivos JSON/SQLite
python scripts/update_catalogs.py --catalog cfdi_4.0 --apply
```

### 6. Testing
```bash
# Ejecutar tests de validación
pytest tests/catalogs/test_cfdi_4.0.py
```

### 7. Commit
```bash
git add packages/shared-data/sat/cfdi_4.0/
git commit -m "Update SAT CFDI 4.0 catalogs - $(date +%Y-%m-%d)"
git push
```

### 8. Release
```bash
# Bump version y publicar
python scripts/release.py --minor
```

---

## 📝 Registro de Cambios

Ver archivo `CHANGELOG_CATALOGS.md` para historial detallado de actualizaciones.

**Formato**:
```markdown
## [2025-11-08] - SAT CFDI 4.0

### Added
- 3 nuevos regímenes fiscales

### Changed
- c_ObjetoImp: agregadas claves 06, 07, 08

### Removed
- Ninguno

### Impact
- ALTO: Requiere actualización inmediata
- Afecta validación de facturas emitidas desde 2024-12-13
```

---

## 🔗 Enlaces Útiles

### SAT
- Anexo 20 CFDI 4.0: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/anexo_20_version3-3.htm
- Comercio Exterior: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/catalogos_emision_cfdi_complemento_ce.htm
- Carta Porte: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/complemento_carta_porte.htm

### Banxico
- Catálogo bancos: https://www.banxico.org.mx/sistemas-de-pago/
- SIE API: https://www.banxico.org.mx/SieAPIRest/service/v1/

### INEGI
- Marco Geoestadístico: https://www.inegi.org.mx/temas/mg/

### SEPOMEX
- Códigos Postales: https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/

### ISO
- ISO 4217: https://www.iso.org/iso-4217-currency-codes.html
- ISO 3166: https://www.iso.org/iso-3166-country-codes.html

---

## ✅ TODO List

### Prioridad ALTA (Próximos 7 días)
- [ ] Implementar `scripts/check_catalog_updates.py`
- [ ] Implementar `scripts/download_tigie.py`
- [ ] Implementar c_FraccionArancelaria con SQLite
- [ ] Crear `.catalog-versions.json` inicial
- [ ] Configurar CI/CD para verificación mensual

### Prioridad MEDIA (Próximos 30 días)
- [ ] Implementar catálogos SAT CFDI 4.0 restantes
- [ ] Implementar SEPOMEX con SQLite
- [ ] Crear dashboard de estado de catálogos
- [ ] Configurar notificaciones (email/Slack)

### Prioridad BAJA (Próximos 90 días)
- [ ] Implementar Carta Porte 3.0
- [ ] Implementar Nómina 1.2
- [ ] Implementar INEGI completo (municipios, localidades)
- [ ] Crear API REST para catálogos
