# Testing and Coverage

## Overview

catalogmx has comprehensive test coverage with **926 tests** covering **93.78%** of the codebase.

## Coverage Badge

Add this to your README.md for a live coverage badge:

```markdown
[![Coverage](https://img.shields.io/badge/coverage-93.78%25-brightgreen)](https://github.com/openbancor/catalogmx)
```

## Running Tests

### Python

```bash
cd packages/python

# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=catalogmx --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_clabe.py -v

# Run with branch coverage
pytest tests/ --cov=catalogmx --cov-branch --cov-report=term-missing
```

### TypeScript

```bash
cd packages/typescript

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

## Coverage Reports

### Local HTML Report

```bash
cd packages/python
pytest tests/ --cov=catalogmx --cov-report=html
open htmlcov/index.html
```

### CI/CD Integration

The project uses GitHub Actions for continuous integration. Coverage reports are generated on every push.

#### GitHub Pages Coverage Display

To display coverage on GitHub Pages:

1. **Add GitHub Actions workflow** (`.github/workflows/coverage.yml`):

```yaml
name: Coverage

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  coverage:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd packages/python
        pip install -e ".[dev]"
    
    - name: Run tests with coverage
      run: |
        cd packages/python
        pytest tests/ --cov=catalogmx --cov-report=html --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      with:
        file: ./packages/python/coverage.xml
        flags: python
        name: catalogmx-python
    
    - name: Deploy coverage to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./packages/python/htmlcov
        destination_dir: coverage
```

2. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` / `root`
   - Coverage will be available at: `https://openbancor.github.io/catalogmx/coverage/`

3. **Add Codecov integration** (optional):
   - Sign up at https://codecov.io
   - Add repository
   - Badge will be auto-generated

## Test Coverage Breakdown

### Modules at 100% Coverage (50+)

- ✅ `catalogmx/validators/clabe.py` - CLABE validator
- ✅ `catalogmx/validators/nss.py` - NSS validator
- ✅ `catalogmx/utils/text.py` - Text normalization
- ✅ All SAT CFDI 4.0 core catalogs
- ✅ All Banxico core catalogs  
- ✅ IFT operadores_moviles
- ✅ INEGI municipios
- ✅ And 40+ more modules

### High Coverage Modules (90%+)

- 💎 `catalogmx/validators/curp.py` - **95.02%**
- 💎 `catalogmx/catalogs/inegi/localidades.py` - **98.11%**
- 💎 `catalogmx/catalogs/sat/cfdi_4/clave_prod_serv.py` - **97.37%**
- 💎 `catalogmx/catalogs/mexico/hoy_no_circula.py` - **96.46%**
- 💎 `catalogmx/helpers.py` - **91.15%**
- 💎 `catalogmx/validators/rfc.py` - **90.69%**
- 💎 And 20+ more modules

## Test Statistics

| Metric | Value |
|--------|-------|
| **Total Tests** | 926 |
| **Python Tests** | 926 |
| **TypeScript Tests** | 221 |
| **Overall Coverage** | 93.78% |
| **Modules at 100%** | 50+ |
| **Test Files** | 34 |

## Coverage Threshold

The project requires a minimum of **90% coverage** for CI/CD pipelines to pass.

Current configuration in `pyproject.toml`:

```toml
[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
fail_under = 90
```

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure coverage stays above 90%
3. Run `pytest --cov` before committing
4. Update documentation

## Test Organization

```
packages/python/tests/
├── test_clabe.py              # CLABE validator (140 tests)
├── test_nss.py                # NSS validator (75 tests)
├── test_curp.py               # CURP validator
├── test_rfc.py                # RFC validator
├── test_helpers.py            # Helper functions
├── test_*_catalogs.py         # Catalog tests
└── test_*.py                  # Additional test files
```

## Continuous Integration

The project uses GitHub Actions for:
- ✅ Running tests on Python 3.10, 3.11, 3.12, 3.13
- ✅ Running tests on TypeScript
- ✅ Generating coverage reports
- ✅ Publishing to PyPI and npm
- ✅ Building documentation

See `.github/workflows/` for CI configuration.
