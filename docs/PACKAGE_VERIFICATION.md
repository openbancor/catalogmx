# Package Verification Guide

## Python Package (PyPI)

### Package Information

- **Name**: catalogmx
- **Version**: 0.3.0
- **PyPI**: https://pypi.org/project/catalogmx/
- **Build System**: setuptools with pyproject.toml
- **Python Versions**: 3.10, 3.11, 3.12, 3.13

### Verify Package Build

```bash
cd packages/python

# Install build tools
pip install build twine

# Build package
python -m build

# Check package
python -m twine check dist/*
```

Expected output:
```
Checking dist/catalogmx-0.3.0-py3-none-any.whl: PASSED
Checking dist/catalogmx-0.3.0.tar.gz: PASSED
```

### Verify Package Contents

```bash
# List files in wheel
unzip -l dist/catalogmx-0.3.0-py3-none-any.whl

# List files in tarball
tar -tzf dist/catalogmx-0.3.0.tar.gz
```

### Test Installation

```bash
# Create virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from built package
pip install dist/catalogmx-0.3.0-py3-none-any.whl

# Test import
python -c "from catalogmx.validators import rfc; print(rfc.validate_rfc('GODE561231GR8'))"

# Deactivate
deactivate
```

### PyPI Metadata Check

```bash
# View package info
pip show catalogmx

# Expected output:
# Name: catalogmx
# Version: 0.3.0
# Summary: Comprehensive Mexican data validators and official catalogs library
# Home-page: https://github.com/openbancor/catalogmx
# Author: Luis Fernando Barrera
# License: BSD-2-Clause
# Requires: click, unidecode
# Required-by:
```

## TypeScript Package (npm)

### Package Information

- **Name**: catalogmx
- **Version**: 0.3.0
- **npm**: https://www.npmjs.com/package/catalogmx
- **Build System**: TypeScript compiler
- **Node Versions**: >=18.0.0

### Verify Package Build

```bash
cd packages/typescript

# Install dependencies
npm ci

# Build
npm run build

# Check dist folder
ls -la dist/
```

Expected files:
```
dist/
├── index.js
├── index.d.ts
├── validators/
├── catalogs/
└── ... (all compiled files)
```

### Verify Package Contents

```bash
# Dry run publish
npm publish --dry-run

# Expected output:
# package: catalogmx@0.3.0
# dist files included:
#   - dist/**
#   - README.md
```

### Test Installation

```bash
# Pack locally
npm pack

# Install from tarball
npm install catalogmx-0.3.0.tgz

# Test import
node -e "const {validateRFC} = require('catalogmx'); console.log(validateRFC('GODE561231GR8'));"
```

### npm Metadata Check

```bash
# View package info
npm info catalogmx

# Expected output:
# catalogmx@0.3.0 | BSD-2-Clause | deps: 2 | versions: X
# Comprehensive Mexican Data Validators and Official Catalogs
# https://github.com/openbancor/catalogmx
```

## Package Size Analysis

### Python Package

```bash
cd packages/python
python -m build
ls -lh dist/
```

Typical sizes:
- **Wheel (.whl)**: ~50-100 KB (without data files)
- **Source (.tar.gz)**: ~60-120 KB

### TypeScript Package

```bash
cd packages/typescript
npm pack
ls -lh catalogmx-0.3.0.tgz
```

Typical size:
- **Tarball**: ~100-200 KB

## Dependencies Verification

### Python Dependencies

```bash
cd packages/python

# List runtime dependencies
python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies'])"
```

Expected:
```python
['unidecode>=1.4.0', 'click>=8.0.0']
```

### TypeScript Dependencies

```bash
cd packages/typescript

# List dependencies
npm list --depth=0
```

Expected:
```
catalogmx@0.3.0
├── better-sqlite3@12.4.1
└── sql.js@1.13.0
```

## Publishing Checklist

### Pre-Publish (Python)

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.rst
- [ ] Run tests: `pytest tests/`
- [ ] Build package: `python -m build`
- [ ] Check package: `twine check dist/*`
- [ ] Test install locally
- [ ] Update README badges

### Pre-Publish (TypeScript)

- [ ] Update version in `package.json`
- [ ] Update CHANGELOG
- [ ] Run tests: `npm test`
- [ ] Build: `npm run build`
- [ ] Check package: `npm publish --dry-run`
- [ ] Test install locally
- [ ] Update README badges

### Publishing

```bash
# Python to PyPI
cd packages/python
python -m twine upload dist/*

# TypeScript to npm
cd packages/typescript
npm publish
```

## Automated Publishing

Use GitHub Actions (see `.github/workflows/publish.yml`):

1. Create a new release on GitHub
2. Workflows automatically:
   - Build both packages
   - Run all tests
   - Publish to PyPI and npm
   - Update documentation

## Package URLs

### Python (PyPI)
- **Package**: https://pypi.org/project/catalogmx/
- **Stats**: https://pepy.tech/project/catalogmx
- **Install**: `pip install catalogmx`

### TypeScript (npm)
- **Package**: https://www.npmjs.com/package/catalogmx
- **Stats**: https://npm-stat.com/charts.html?package=catalogmx
- **Install**: `npm install catalogmx`

## Troubleshooting

### Package Build Fails

```bash
# Clean and rebuild
rm -rf dist build *.egg-info
python -m build
```

### Import Errors After Install

```bash
# Verify package is installed
pip show catalogmx  # or npm list catalogmx

# Reinstall
pip install --force-reinstall catalogmx
```

### Version Mismatch

Ensure versions match across:
- `pyproject.toml`
- `package.json`
- `README.md`
- `__init__.py` (if version is defined there)
