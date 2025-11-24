# catalogmx Package Information

Quick reference for all package URLs, installation commands, and project metadata.

---

## Package Registry URLs

| Platform | Package URL | Status |
|----------|-------------|--------|
| **PyPI** | https://pypi.org/project/catalogmx/ | ![PyPI](https://img.shields.io/pypi/v/catalogmx) |
| **NPM** | https://www.npmjs.com/package/catalogmx | ![NPM](https://img.shields.io/npm/v/catalogmx) |
| **pub.dev** | https://pub.dev/packages/catalogmx | ![pub.dev](https://img.shields.io/pub/v/catalogmx) |

---

## Installation Commands

### Python
```bash
# Recommended (using uv - 10-100x faster)
uv pip install catalogmx

# Using pip
pip install catalogmx

# Development install
cd packages/python && uv pip install -e ".[dev]"
```

### TypeScript / JavaScript
```bash
# NPM
npm install catalogmx

# Yarn
yarn add catalogmx

# pnpm
pnpm add catalogmx
```

### Dart / Flutter
```bash
# Add to pubspec.yaml
flutter pub add catalogmx

# Or for Dart only
dart pub add catalogmx

# Or manually add to pubspec.yaml:
# dependencies:
#   catalogmx: ^0.4.0
```

---

## Repository URLs

| Resource | URL |
|----------|-----|
| **GitHub Repository** | https://github.com/openbancor/catalogmx |
| **Issues** | https://github.com/openbancor/catalogmx/issues |
| **Pull Requests** | https://github.com/openbancor/catalogmx/pulls |
| **Releases** | https://github.com/openbancor/catalogmx/releases |
| **Actions (CI/CD)** | https://github.com/openbancor/catalogmx/actions |

---

## Documentation URLs

| Document | Location |
|----------|----------|
| **Main README** | [README.md](README.md) |
| **Publishing Guide** | [docs/PUBLISHING.md](docs/PUBLISHING.md) |
| **API Reference** | [docs/api/](docs/api/) |
| **Dart Catalogs** | [packages/dart/CATALOGS.md](packages/dart/CATALOGS.md) |
| **Developer Guide** | [docs/guides/developers-guide.md](docs/guides/developers-guide.md) |

---

## Version Information

Current version across all packages: **0.4.0**

| Package | Version | Min Runtime |
|---------|---------|-------------|
| Python | 0.4.0 | Python 3.10+ |
| TypeScript | 0.4.0 | Node.js 18+ |
| Dart | 0.4.0 | Dart 3.0+ / Flutter 3.10+ |

---

## Test Coverage

| Package | Tests | Coverage | Status |
|---------|-------|----------|--------|
| **Python** | 926 | 93.78% | Production Ready |
| **TypeScript** | 221 | ~90% | Production Ready |
| **Dart** | 59 | ~85% | Production Ready |
| **Total** | 1,206 | - | - |

---

## Badge Markdown

Use these badges in your README or documentation:

### Version Badges
```markdown
[![PyPI Version](https://img.shields.io/pypi/v/catalogmx)](https://pypi.org/project/catalogmx/)
[![NPM Version](https://img.shields.io/npm/v/catalogmx)](https://www.npmjs.com/package/catalogmx)
[![pub.dev Version](https://img.shields.io/pub/v/catalogmx)](https://pub.dev/packages/catalogmx)
```

### Python Badges
```markdown
[![Python Version](https://img.shields.io/pypi/pyversions/catalogmx)](https://pypi.org/project/catalogmx/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/catalogmx)](https://pypi.org/project/catalogmx/)
```

### Quality Badges
```markdown
[![Test Coverage](https://img.shields.io/badge/coverage-93.78%25-brightgreen)](https://github.com/openbancor/catalogmx)
[![Tests](https://img.shields.io/badge/tests-1206%20passing-brightgreen)](https://github.com/openbancor/catalogmx)
[![License](https://img.shields.io/badge/license-BSD--2--Clause-blue.svg)](LICENSE)
```

---

## Quick Import Examples

### Python
```python
from catalogmx.validators import rfc, curp, clabe, nss
from catalogmx.catalogs.sat.cfdi_4 import RegimenFiscalCatalog
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import MunicipiosCatalog
```

### TypeScript
```typescript
import { validateRFC, validateCURP, validateCLABE, validateNSS } from 'catalogmx';
import { SatCatalogs, SepomexCatalogs, InegiCatalogs } from 'catalogmx';
```

### Dart
```dart
import 'package:catalogmx/catalogmx.dart';

// Validators
validateRFC('GODE561231GR8');
validateCURP('GORS561231HVZNNL00');
validateCLABE('002010077777777771');
validateNSS('12345678903');

// Catalogs
InegStates.getAll();
InegMunicipios.getByClave('09001');
SepomexCodigosPostales.getByCP('06600');
```

---

## Environment Variables

For CI/CD and publishing:

```bash
# PyPI
TWINE_USERNAME=__token__
TWINE_PASSWORD=pypi-xxx

# NPM
NPM_TOKEN=npm_xxx

# pub.dev (OAuth credentials)
PUB_CREDENTIALS={"accessToken":"...","refreshToken":"..."}
```

---

## Maintainer Information

| Role | Name | Contact |
|------|------|---------|
| **Author** | Luis Fernando Barrera | luisfernando@informind.com |
| **GitHub** | @openbancor | https://github.com/openbancor |
| **License** | BSD-2-Clause | [LICENSE](LICENSE) |

---

## Related Links

### Official Data Sources
- [SAT (Tax Administration)](https://www.sat.gob.mx/)
- [INEGI (Statistics)](https://www.inegi.org.mx/)
- [SEPOMEX (Postal Service)](https://www.gob.mx/correosdemexico)
- [Banxico (Central Bank)](https://www.banxico.org.mx/)
- [RENAPO (Population Registry)](https://www.gob.mx/segob/renapo)
- [IFT (Telecommunications)](https://www.ift.org.mx/)

---

**Last Updated**: November 2024
