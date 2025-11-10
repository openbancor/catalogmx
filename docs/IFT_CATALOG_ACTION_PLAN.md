# IFT Catalogs - Critical Gaps & Action Plan

**Date**: 2025-11-10
**Status**: CRITICAL - Incomplete Data
**Priority**: HIGH (v0.4.0)

---

## 🚨 Current State Analysis

### 1. LADA Codes Catalog (codigos_lada.json)

**Completeness**: ⚠️ **58% Complete** (231 / 397 codes)

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Total LADA codes | 231 | ~397 | **-166 codes** |
| States covered | 32 | 32 | ✅ Complete |
| Geographical mapping | ❌ None | Full INEGI | **Critical** |
| Python implementation | ❌ Empty | Full parity | **Critical** |

**Data Structure Issues**:
```json
{
  "lada": "33",
  "ciudad": "Guadalajara",
  "estado": "Jalisco",           // ✅ Has state NAME
  "tipo": "metropolitana",
  "region": "occidente"

  // ❌ MISSING:
  // "cve_entidad": "14",         // INEGI state code
  // "cve_municipio": "039",      // INEGI municipality code
  // "cvegeo": "14039",           // Optional: locality link
  // "cve_localidad": "0001"      // Optional: locality code
}
```

**Missing LADA codes** (examples based on known Mexican cities):
- Many secondary cities in each state
- Rural municipal seats
- Some tourist destinations
- Border crossings

### 2. Mobile Operators Catalog (operadores_moviles.json)

**Status**: ✅ **Appears Complete** (need verification)

- Has major operators: Telcel, AT&T, Movistar, Altán, MVNOs
- Good data structure with market share, technologies
- **No geographical mapping** (could add coverage by state)

---

## 🎯 Action Plan - v0.4.0

### Phase 1: Complete LADA Codes Data (Week 1)

**Tasks**:
1. **Source official IFT plan de numeración**
   - URL: https://www.ift.org.mx/industria/numeracion-y-operacion
   - Download complete LADA code registry
   - Verify total count (~397 codes)

2. **Add missing ~166 LADA codes**
   - Parse official IFT data
   - Extract LADA, ciudad, estado for each
   - Classify tipo (metropolitana/fronteriza/turistica/normal)
   - Assign region (noroeste, norte, noreste, occidente, centro, golfo, sur, sureste)

3. **Quality assurance**
   - Verify all 32 states have complete coverage
   - Cross-check with INEGI municipalities catalog
   - Ensure no duplicates

**Script to create**:
```bash
scripts/ift/fetch_complete_lada_codes.py
```

### Phase 2: Add Geographical Mapping (Week 1-2)

**Objective**: Link every LADA code to INEGI geographical catalogs

**New fields to add**:
```typescript
interface CodigoLADA {
  lada: string;
  ciudad: string;
  estado: string;

  // NEW FIELDS:
  cve_entidad: string;        // "01" to "32" (INEGI state code)
  cve_municipio?: string;     // "001" to "570" (INEGI municipality code)
  cvegeo?: string;            // "01001xxxx" (optional locality link)
  nom_entidad: string;        // "Aguascalientes" (canonical state name)
  nom_municipio?: string;     // "Aguascalientes" (canonical municipality name)

  tipo: string;
  region: string;
}
```

**Mapping strategy**:
1. **Estado → cve_entidad**: Use INEGI states catalog for exact mapping
2. **Ciudad → Municipality**: Fuzzy match ciudad name to INEGI municipalities
3. **Manual review**: For ambiguous cases (e.g., multiple municipalities with same name)

**Scripts to create**:
```bash
scripts/ift/map_lada_to_inegi_states.py
scripts/ift/map_lada_to_inegi_municipalities.py
scripts/ift/validate_geographical_mapping.py
```

### Phase 3: Python Implementation (Week 2)

**Objective**: Create Python `CodigosLADACatalog` matching TypeScript

**File**: `packages/python/catalogmx/catalogs/ift/codigos_lada.py`

**API to implement** (matching TypeScript):
```python
class CodigosLADACatalog:
    @classmethod
    def get_all() -> list[dict]: ...

    @classmethod
    def buscar_por_lada(lada: str) -> dict | None: ...

    @classmethod
    def buscar_por_ciudad(ciudad: str) -> list[dict]: ...

    @classmethod
    def get_por_estado(estado: str) -> list[dict]: ...

    @classmethod
    def get_por_tipo(tipo: str) -> list[dict]: ...

    @classmethod
    def get_por_region(region: str) -> list[dict]: ...

    @classmethod
    def validar_numero(numero: str) -> dict: ...

    @classmethod
    def formatear_numero(numero: str) -> str: ...

    @classmethod
    def get_info_numero(numero: str) -> dict | None: ...

    # NEW METHODS with geographical integration:
    @classmethod
    def get_por_cve_entidad(cve_entidad: str) -> list[dict]: ...

    @classmethod
    def get_por_municipio(cve_municipio: str) -> list[dict]: ...

    @classmethod
    def link_to_inegi_state(lada: str) -> dict | None:
        """Get INEGI state data for a LADA code"""
        ...

    @classmethod
    def link_to_inegi_municipality(lada: str) -> dict | None:
        """Get INEGI municipality data for a LADA code"""
        ...
```

**Also create**:
- `packages/python/catalogmx/catalogs/ift/operadores_moviles.py`

**Tests to add**:
- `packages/python/tests/test_ift_catalogs.py`

### Phase 4: Update TypeScript with Geo Mapping (Week 2)

**File**: `packages/typescript/src/catalogs/ift/codigos-lada.ts`

**New methods to add**:
```typescript
class CodigosLADA {
  // Existing methods...

  // NEW:
  static getPorCveEntidad(cveEntidad: string): CodigoLADA[]
  static getPorMunicipio(cveMunicipio: string): CodigoLADA[]
  static linkToINEGIState(lada: string): EstadoINEGI | null
  static linkToINEGIMunicipio(lada: string): MunicipioINEGI | null
}
```

**Update types**:
```typescript
// packages/typescript/src/types/index.ts
export interface CodigoLADA {
  lada: string;
  ciudad: string;
  estado: string;
  cve_entidad: string;        // NEW
  cve_municipio?: string;     // NEW
  cvegeo?: string;            // NEW
  nom_entidad: string;        // NEW
  nom_municipio?: string;     // NEW
  tipo: 'metropolitana' | 'fronteriza' | 'turistica' | 'normal';
  region: string;
}
```

### Phase 5: Documentation & Examples (Week 3)

**Documentation to create**:
1. `docs/catalogs/ift.md` - Complete IFT catalogs documentation
2. `docs/guides/lada-geographical-mapping.md` - Guide on using LADA→INEGI links
3. Update `README.md` with IFT catalog examples

**Examples to add**:
```python
# Example: Get all LADA codes in Jalisco
from catalogmx.catalogs.ift import CodigosLADACatalog
from catalogmx.catalogs.inegi import EstadosCatalog

# By state name
ladas_jalisco = CodigosLADACatalog.get_por_estado("Jalisco")
print(f"Jalisco has {len(ladas_jalisco)} LADA codes")

# By INEGI state code
ladas_jalisco_inegi = CodigosLADACatalog.get_por_cve_entidad("14")

# Link LADA to INEGI municipality
lada_info = CodigosLADACatalog.buscar_por_lada("33")  # Guadalajara
municipio = CodigosLADACatalog.link_to_inegi_municipality("33")
print(f"LADA 33 → {municipio['nom_municipio']}, {municipio['nom_entidad']}")

# Validate phone number with geographical context
info = CodigosLADACatalog.get_info_numero("3312345678")
print(f"Número de {info['ciudad']}, {info['estado']}")
print(f"Municipio INEGI: {info['cve_municipio']}")
```

---

## 📊 Success Metrics

### Data Completeness
- ✅ All ~397 LADA codes captured
- ✅ 100% of LADA codes mapped to INEGI `cve_entidad`
- ✅ 95%+ of LADA codes mapped to INEGI `cve_municipio`
- ✅ Mobile operators catalog verified complete

### Implementation
- ✅ Python IFT catalogs with 100% parity to TypeScript
- ✅ 15+ methods in CodigosLADACatalog
- ✅ 10+ methods in OperadoresMovilesCatalog
- ✅ Full test coverage (50+ tests)

### Integration
- ✅ Seamless linkage between IFT and INEGI catalogs
- ✅ Helper methods for cross-catalog queries
- ✅ Documentation with 10+ examples
- ✅ Type safety in both languages

---

## 🔗 Official Sources

### IFT (Instituto Federal de Telecomunicaciones)
- **Plan de Numeración**: https://www.ift.org.mx/industria/numeracion-y-operacion
- **Registro de Operadores**: https://www.ift.org.mx/industria/operadores-registrados
- **Portal de Datos Abiertos**: https://datos.ift.org.mx/

### Alternative Sources
- **PROFECO**: Consumer protection database may have complete LADA listings
- **CFE**: Electrical company databases often have complete city/LADA mappings
- **INEGI**: Economic census may include LADA codes

---

## 📅 Timeline

| Week | Tasks | Owner | Status |
|------|-------|-------|--------|
| **Week 1** | Source IFT data + complete 166 missing LADAs | TBD | ⏳ Pending |
| **Week 1-2** | Add geographical mapping (INEGI linkage) | TBD | ⏳ Pending |
| **Week 2** | Python implementation (CodigosLADA + Operadores) | TBD | ⏳ Pending |
| **Week 2** | TypeScript updates with geo methods | TBD | ⏳ Pending |
| **Week 3** | Documentation, examples, tests | TBD | ⏳ Pending |
| **Week 3** | QA, validation, release | TBD | ⏳ Pending |

**Target completion**: End of Week 3 (v0.4.0 milestone)

---

## 🎯 Priority Justification

**Why CRITICAL for v0.4.0?**

1. **User requirement**: Explicit request for complete LADA→Geography mapping
2. **Data integrity**: 42% missing data is unacceptable for production
3. **Cross-catalog value**: IFT+INEGI integration unlocks powerful queries
4. **Competitive advantage**: Few libraries have complete Mexican telecom data
5. **Foundation for future**: Required for telecoms validators (planned v0.5.0)

**Use cases enabled**:
- Phone number geographical routing
- Area code-based business analytics
- Telecom compliance systems
- CRM systems with Mexican address validation
- Call center routing by region
- Fraud detection (phone/location mismatch)

---

**Document Status**: DRAFT
**Last Updated**: 2025-11-10
**Next Review**: Post-v0.4.0 planning
