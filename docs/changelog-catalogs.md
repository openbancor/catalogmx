# 📜 Historial de Actualizaciones de Catálogos

Este archivo registra todos los cambios en los catálogos oficiales de catalogmx.

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

---

## [2025-11-08] - Implementación inicial

### Added

#### SAT Comercio Exterior 2.0
- ✅ c_INCOTERM (11 Incoterms 2020)
  - 7 multimodales: EXW, FCA, CPT, CIP, DAP, DPU, DDP
  - 4 marítimos: FAS, FOB, CFR, CIF
  - Validación por modo de transporte

- ✅ c_ClavePedimento (42 claves de pedimento aduanero)
  - Claves de exportación (A1, A3, A4, J1, etc.)
  - Claves de importación (V1-V7)
  - Regímenes especiales (IMMEX, tránsito, etc.)

- ✅ c_UnidadAduana (32 unidades de medida aduanera)
  - Unidades de peso, volumen, longitud, área
  - Contenedores (C20, C40)

- ✅ c_MotivoTraslado (6 motivos de traslado)
  - Para CFDI tipo "T" (Traslado)
  - Validación de nodo Propietario

- ✅ c_RegistroIdentTribReceptor (15 tipos de ID tributaria)
  - Tax ID (USA), Business Number (CAN), VAT (UE)
  - Validación con regex

- ✅ c_Moneda (150 monedas ISO 4217)
  - Catálogo completo de monedas activas
  - Validación de conversión a USD

- ✅ c_Pais (249 países ISO 3166-1)
  - Códigos Alpha-3 y Alpha-2
  - Marcadores de subdivisión requerida

- ✅ c_Estado (63 estados USA + provincias CAN)
  - 50 estados USA + DC + 5 territorios
  - 13 provincias/territorios canadienses
  - ISO 3166-2 codes

#### Banxico
- ✅ Catálogo de bancos (102 instituciones)
  - Incluye código, nombre completo, RFC
  - Flag SPEI

#### INEGI
- ✅ Catálogo de estados (32 estados)
  - Códigos CURP, INEGI
  - Nombres oficiales

#### RENAPO
- ✅ Palabras antisonantes CURP (~1,400 palabras)
  - Para validación de RFC/CURP

### Infrastructure
- ✅ Sistema de monitoreo de actualizaciones
  - `.catalog-versions.json` para tracking de versiones
  - `scripts/check_catalog_updates.py` para verificación automática
  - `scripts/download_tigie.py` para descarga de TIGIE
  - `CATALOG_UPDATES.md` con documentación completa

---

## [Pendiente] - Próximas actualizaciones

### High Priority

#### SAT CFDI 4.0 - Anexo 20
- [ ] c_RegimenFiscal (~40 regímenes fiscales)
- [ ] c_UsoCFDI (~25 usos de CFDI)
- [ ] c_FormaPago (~20 formas de pago)
- [ ] c_MetodoPago (4 métodos)
- [ ] c_TipoComprobante (5 tipos)
- [ ] c_Impuesto (4 impuestos)
- [ ] c_TasaOCuota (~50 tasas)
- [ ] c_TipoRelacion (10 tipos)
- [ ] c_Exportacion (4 opciones)
- [ ] c_ObjetoImp (8 opciones - actualizado 2024-12-13)

#### SAT Comercio Exterior
- [ ] c_FraccionArancelaria (~20,000 fracciones TIGIE/NICO)
  - Requiere SQLite
  - Actualización trimestral

#### SEPOMEX
- [ ] Códigos Postales (~150,000 registros)
  - Requiere SQLite
  - Actualización mensual

### Medium Priority

#### SAT Carta Porte 3.0
- [ ] c_CodigoTransporteAereo (76 aeropuertos)
- [ ] c_NumAutorizacionNaviero (100 puertos)
- [ ] c_Estaciones (~500 estaciones)
- [ ] c_Carreteras (~200 carreteras)
- [ ] c_TipoPermiso (~20 permisos)
- [ ] c_ConfigAutotransporte (~15 configuraciones)
- [ ] c_TipoEmbalaje (~30 embalajes)
- [ ] c_MaterialPeligroso (~3,000 materiales - SQLite)

#### INEGI
- [ ] Municipios (2,469 municipios)
- [ ] Localidades (~90,000 - SQLite)
- [ ] AGEBs (~200,000 - SQLite)

### Low Priority

#### SAT Nómina 1.2
- [ ] c_TipoNomina (2 tipos)
- [ ] c_TipoContrato (10 tipos)
- [ ] c_TipoJornada (8 jornadas)
- [ ] c_TipoRegimen (13 regímenes)
- [ ] c_PeriodicidadPago (10 periodicidades)
- [ ] c_RiesgoPuesto (5 niveles)

#### IFT
- [ ] Códigos LADA (~400 códigos)
- [ ] Zonas de numeración (~50 zonas)

#### Banxico SIE
- [ ] Tasas de interés históricas (TIIE, CETES, Tasa Objetivo)
  - API-based, no descarga necesaria

---

## Formato de Entrada

Cada actualización debe seguir este formato:

```markdown
## [YYYY-MM-DD] - Fuente: Nombre del Catálogo

### Added
- Nuevos registros agregados
- Nuevas validaciones

### Changed
- Registros modificados
- Cambios en estructura

### Deprecated
- Campos/registros marcados para eliminación

### Removed
- Registros eliminados
- Campos eliminados

### Fixed
- Correcciones de errores
- Ajustes de validación

### Impact
- ALTO / MEDIO / BAJO
- Descripción del impacto
- Fecha efectiva de cambios SAT
```

---

## Verificación de Actualizaciones

Para verificar si hay actualizaciones disponibles:

```bash
# Verificar todos los catálogos
python scripts/check_catalog_updates.py --check-all

# Verificar solo SAT
python scripts/check_catalog_updates.py --source sat

# Generar reporte de estado
python scripts/check_catalog_updates.py --report
```

---

## Notas Importantes

### Frecuencias de Actualización

- **Diaria**: Banxico SIE (solo si se implementa)
- **Mensual**: SAT CFDI 4.0, Banxico bancos, SEPOMEX
- **Trimestral**: TIGIE/NICO, Banxico SIE series
- **Semestral**: Carta Porte 3.0, ISO standards
- **Anual**: Nómina 1.2, INEGI, IFT
- **Irregular**: INCOTERMS (cada 10 años)

### Criticidad

- 🔴 **ALTA**: SAT CFDI 4.0, TIGIE → Actualización inmediata requerida
- 🟠 **MEDIA**: Bancos, SEPOMEX, Carta Porte → Actualización en 1 semana
- 🟡 **BAJA**: INEGI, IFT, ISO → Actualización en 1 mes
- ⚪ **INFO**: Documentación, aclaraciones → Solo seguimiento

---

## Enlaces de Referencias

- **SAT Anexo 20**: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/anexo_20_version3-3.htm
- **SAT Comercio Exterior**: http://omawww.sat.gob.mx/tramitesyservicios/Paginas/catalogos_emision_cfdi_complemento_ce.htm
- **Banxico Bancos**: https://www.banxico.org.mx/sistemas-de-pago/
- **INEGI**: https://www.inegi.org.mx/app/ageeml/
- **SEPOMEX**: https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/
- **ISO 4217**: https://www.iso.org/iso-4217-currency-codes.html
- **ISO 3166**: https://www.iso.org/iso-3166-country-codes.html
