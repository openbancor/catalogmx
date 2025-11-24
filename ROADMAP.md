# catalogmx Product Roadmap

## Executive Summary

This roadmap outlines the strategic development plan for catalogmx, an enterprise-grade Mexican data validation and catalog library. The roadmap prioritizes features that deliver maximum business value while maintaining code quality and regulatory compliance.

**Current Status**: Version 0.3.0 (Production Ready)  
**Coverage**: 93.78% with 926 passing tests  
**Next Release**: Version 0.4.0 (Q1 2025)

---

## Version 0.3.0 - Current Release (Production)

### Delivered Capabilities

**Validators (4):**
- RFC (Registro Federal de Contribuyentes) - Tax identification
- CURP (Clave Única de Registro de Población) - National ID
- CLABE (Clave Bancaria Estandarizada) - Bank accounts
- NSS (Número de Seguridad Social) - Social security

**Official Catalogs (58):**
- SAT: 31 catalogs (CFDI 4.0, Comercio Exterior, Carta Porte, Nómina)
- INEGI: 4 catalogs (States, Municipalities, Localities with GPS)
- SEPOMEX: 2 catalogs (157,252 postal codes)
- Banxico: 5 catalogs (Banks, UDI, Financial institutions, Currencies, Plaza codes)
- IFT: 1 catalog (Operadores móviles)
- Mexico National: 4 catalogs (Salaries, UMA, Traffic, License plates)

**Data Volume:**
- 170,505+ validated records
- 157,252 postal codes
- 10,635 GPS-enabled localities
- 52,896 product/service codes (SQLite FTS5)

**Quality Metrics:**
- 93.78% test coverage
- 926 Python tests + 221 TypeScript tests
- 50+ modules at 100% coverage
- Zero critical bugs

---

## Version 0.4.0 - Q1 2025 (Performance & Integration)

### Objectives

1. **Optimize Large Catalog Performance**
2. **Enable Geographic Services**
3. **Enhance Developer Experience**
4. **Complete Missing SAT Catalogs**

### Planned Features

#### 1. SQLite Migration for Large Catalogs (Priority: Critical)

**Business Value**: 40% size reduction, 100x faster queries, reduced memory consumption

**Implementation:**
- Convert SEPOMEX (157K records) to SQLite: 43MB → 25MB
- Add spatial indexing for geographic queries
- Implement FTS5 full-text search
- Maintain backward compatibility with JSON API

**Deliverables:**
```python
from catalogmx.catalogs.sepomex import CodigosPostalesSQLite

# High-performance postal code lookup
codes = CodigosPostalesSQLite.query_by_location(
    lat=19.4326,
    lon=-99.1332,
    radius_km=10
)
```

**Timeline**: 3-4 weeks  
**Effort**: Medium

#### 2. Postal Code Geocoding (Priority: High)

**Business Value**: Enable location-based services, shipping optimization, geographic analysis

**Implementation:**
- Add latitude/longitude to all 157,252 postal codes
- Data source: Google Geocoding API or OpenStreetMap
- Batch processing strategy (500-1000 codes/day)
- Quality validation and error handling

**Deliverables:**
```python
# Enhanced postal code with coordinates
postal_data = CodigosPostales.get_by_cp("06700")
# Returns: {
#     'cp': '06700',
#     'asentamiento': 'Roma Norte',
#     'latitude': 19.4194,
#     'longitude': -99.1625,
#     ...
# }
```

**Timeline**: 6-8 weeks (including data acquisition)  
**Effort**: High  
**Cost Consideration**: API fees for 157K requests

#### 3. CP ↔ Locality Linkage Table (Priority: High)

**Business Value**: Precise address validation, improved data quality

**Implementation:**
- Pre-calculated correspondence table
- Matching algorithm: Geographic proximity + name similarity
- Expected accuracy: 75-85%

**Methodology:**
1. Match by municipality code (exact match)
2. Calculate geographic distance (<5km threshold)
3. Compare name similarity (>70% threshold)
4. Manual verification for edge cases

**Deliverables:**
```python
from catalogmx.links import CPLocalityLinker

# Get locality for postal code
locality = CPLocalityLinker.get_locality_for_cp("06700")
# Returns INEGI locality with full data

# Get all postal codes in locality
cps = CPLocalityLinker.get_cps_for_locality("090150001")
```

**Timeline**: 4 weeks  
**Effort**: Medium

#### 4. Complete Missing SAT Catalogs (Priority: Medium)

**Catalogs to Add:**
- c_TipoOperacion (Operation types)
- c_NumPedimentoAduana (Customs document numbers)
- c_EstacionFFCC (Railway stations)
- c_ContenedorMaritimo (Maritime container types)
- c_OrigenRecurso (Resource origin for payroll)

**Timeline**: 2-3 weeks  
**Effort**: Low-Medium

#### 5. Developer Experience Improvements (Priority: High)

**REST API Examples:**
- FastAPI implementation with async support
- Express.js/Node.js implementation
- Flask minimal implementation
- GraphQL API example

**Documentation:**
- Interactive API documentation (Swagger/OpenAPI)
- Integration guides for popular frameworks
- Performance optimization guide
- Deployment best practices

**Timeline**: 2 weeks  
**Effort**: Low

---

## Version 0.5.0 - Q2-Q3 2025 (Expansion)

### Strategic Initiatives

#### 1. New Validators

**Vehicle License Plates:**
- Format validation by state
- NOM-001-SCT-2-2016 compliance
- Diplomatic and federal plate support
- Historical format support

**Passport MRZ (Machine Readable Zone):**
- Parse MRZ from Mexican passports
- Extract personal data
- Validate check digits
- Integration with CURP

**Driver's License:**
- Format validation by state
- Expiration date validation
- State-specific rules

#### 2. Additional Government Catalogs

**IMSS (Social Security Institute):**
- Subdelegations: 250+ IMSS offices
- Medical facilities: 1,500+ clinics and hospitals
- Disease catalog: ICD-10 codes
- Medicine catalog: Registered medications

**TIGIE (Customs Tariff Schedule):**
- Tariff codes: ~10,000 fractions
- Import/export regulations
- Tax rates by fraction
- Unit of measure requirements
- SQLite implementation required (large dataset)

**PROFECO (Consumer Protection):**
- Certified providers
- Adhesion contracts
- Consumer complaint records (anonymized)

**SCIAN (Industrial Classification):**
- Economic activity codes
- Business classification system
- Integration with DENUE (business directory)

#### 3. Advanced Features

**Machine Learning Integration:**
- Address normalization
- Fuzzy matching for names
- Automatic error correction
- Confidence scoring

**WebAssembly Compilation:**
- Browser-optimized validators
- 10x performance improvement
- Zero-dependency browser usage
- Offline-first capability

**Caching Layer:**
- Redis integration for high-traffic deployments
- Configurable TTL per catalog
- Distributed cache support

#### 4. Historical Data

**Version Control for Catalogs:**
- Track catalog changes over time
- Access historical versions
- Audit trail for compliance
- Diff utilities

**Data APIs:**
- `/catalogs/{name}/versions` - List available versions
- `/catalogs/{name}/changes` - Changelog
- `/catalogs/{name}/diff/{v1}/{v2}` - Compare versions

---

## Gap Analysis - Missing Catalogs

### Currently Not Available (Identified Opportunities)

#### Government Catalogs

**CONAGUA (Water Commission):**
- Water quality indicators
- Watershed management zones
- Water rights and concessions
- *Business Value*: Environmental compliance, agriculture

**SEMARNAT (Environment Ministry):**
- Environmental impact zones
- Protected areas
- Emissions regulations
- *Business Value*: Environmental compliance, construction

**COFEPRIS (Health Regulation):**
- Registered medications
- Medical devices
- Sanitary permits
- *Business Value*: Healthcare, pharmaceutical

**SE (Economy Ministry):**
- Business permits
- Industrial norms (NOMs)
- Foreign investment registry
- *Business Value*: Business compliance, legal

#### Economic & Business

**SCIAN (Economic Classification):**
- ~1,000 economic activity codes
- Business classification
- *Business Value*: Business intelligence, tax compliance

**DENUE (Business Directory):**
- Millions of registered businesses
- Location and size data
- *Note*: Very large dataset, requires special handling

**CompraNet (Government Contracts):**
- Public procurement data
- Government suppliers
- Contract values
- *Business Value*: Business intelligence, transparency

#### Transportation

**REPUVE (Vehicle Registry):**
- Vehicle identification numbers (VIN/NIV)
- Stolen vehicle database (public API)
- *Business Value*: Used car transactions, security

**SCT (Communications & Transport):**
- Additional highway catalogs
- Transport concessions
- Aviation regulations
- *Business Value*: Logistics, transportation

---

## Implementation Priorities

### High Priority (Version 0.4.0)

| Feature | Business Impact | Technical Complexity | Timeline |
|---------|----------------|---------------------|----------|
| SEPOMEX SQLite | Very High | Medium | 3-4 weeks |
| Geocoding | Very High | High | 6-8 weeks |
| CP ↔ Locality Link | High | Medium | 4 weeks |
| REST API Examples | High | Low | 2 weeks |
| Missing SAT Catalogs | Medium | Low | 2-3 weeks |

### Medium Priority (Version 0.5.0)

| Feature | Business Impact | Technical Complexity | Timeline |
|---------|----------------|---------------------|----------|
| Vehicle Plates Validator | Medium | Medium | 3 weeks |
| IMSS Catalogs | Medium | Low | 2 weeks |
| TIGIE Tariff Schedule | High | High | 6-8 weeks |
| Historical Data | Medium | Medium | 4 weeks |
| WebAssembly | Low | High | 8 weeks |

### Low Priority (Version 0.6.0+)

| Feature | Business Impact | Technical Complexity | Timeline |
|---------|----------------|---------------------|----------|
| ML Normalization | Low | Very High | 12+ weeks |
| Additional Validators (MRZ, etc.) | Low | Medium | 4 weeks each |
| COFEPRIS Catalogs | Low | Medium | 3 weeks |
| SCIAN/DENUE | Medium | Very High | 12+ weeks |

---

## Success Metrics

### Version 0.4.0 Goals

- **Performance**: Query time <10ms for 95% of operations
- **Coverage**: Maintain >90% test coverage
- **Size**: Reduce package size by 30% with SQLite
- **Geocoding**: 100% of postal codes with coordinates
- **Documentation**: 5+ integration examples

### Version 0.5.0 Goals

- **Catalogs**: Add 10+ new government catalogs
- **Validators**: Add 3+ new validators
- **Performance**: 10x improvement with WebAssembly
- **Adoption**: 1,000+ downloads/month

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Geocoding API costs | High | Use open datasets or cached data |
| Large dataset performance | Medium | SQLite with proper indexing |
| Government API changes | High | Version control, update monitoring |
| Breaking API changes | High | Semantic versioning, deprecation notices |

### Resource Requirements

**Version 0.4.0:**
- Development time: 12-16 weeks
- External API costs: $100-500 (geocoding)
- Testing resources: Automated CI/CD

**Version 0.5.0:**
- Development time: 20-24 weeks
- Data acquisition: Government sources (free)
- Infrastructure: Increased storage for historical data

---

## Contribution Opportunities

### Open for Community Contributions

1. **Geocoding Support**: Help with batch geocoding postal codes
2. **TypeScript Parity**: Implement missing catalog methods
3. **Examples**: Create integration examples for popular frameworks
4. **Documentation**: Translate guides, write tutorials
5. **Testing**: Add edge case tests
6. **Catalog Updates**: Monitor and update government catalogs

See [CONTRIBUTING.rst](CONTRIBUTING.rst) for contribution guidelines.

---

## Changelog

### Version 0.3.0 (Current)
- 58 official catalogs implemented
- 93.78% test coverage achieved
- Modern packaging (pyproject.toml)
- SQLite hybrid architecture for large catalogs
- Comprehensive documentation

### Version 0.2.0 (Previous)
- Initial public release
- Core validators (RFC, CURP, CLABE, NSS)
- Basic SAT and INEGI catalogs
- TypeScript support

---

## Contact & Support

- **Issues**: https://github.com/openbancor/catalogmx/issues
- **Email**: luisfernando@informind.com
- **Documentation**: [docs/](docs/)

---

**Last Updated**: November 2024  
**Current Version**: 0.3.0  
**Next Release**: 0.4.0 (Q1 2025)

---

This roadmap is subject to change based on community feedback and business requirements.
