# Modern Python Packaging with uv

## Overview

catalogmx uses modern Python packaging standards with `pyproject.toml` (PEP 621).

## Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a blazing-fast Python package installer and resolver written in Rust.

### Installation

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# With pip
pip install uv
```

### Development with uv

```bash
# Install package in development mode
cd packages/python
uv pip install -e ".[dev]"

# Install all optional dependencies
uv pip install -e ".[all]"

# Run tests
pytest tests/

# Install specific dependency
uv pip install pytest-cov
```

### Benefits of uv

- ⚡ **10-100x faster** than pip
- 🔒 **Deterministic** dependency resolution
- 🎯 **Compatible** with pip and pyproject.toml
- 🚀 **Production-ready** from Astral (creators of Ruff)

## Package Structure

### pyproject.toml (Modern Standard)

The project uses `pyproject.toml` for all configuration:

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "catalogmx"
version = "0.3.0"
dependencies = [
    "unidecode>=1.4.0",
    "click>=8.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0"
]
```

### Legacy Files Removed

The following legacy files have been removed:
- ❌ `setup.py` - Replaced by pyproject.toml
- ❌ `setup.cfg` - Configuration moved to pyproject.toml
- ❌ `requirements.txt` - Dependencies in pyproject.toml
- ❌ `requirements-dev.txt` - Dev dependencies in pyproject.toml

**Note**: `pyproject.toml` is the single source of truth for all package metadata and dependencies.

## Publishing

### PyPI (Python)

```bash
cd packages/python

# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### npm (TypeScript)

```bash
cd packages/typescript

# Build
npm run build

# Publish
npm publish
```

## GitHub Actions Integration

Add this to `.github/workflows/publish.yml`:

```yaml
name: Publish

on:
  release:
    types: [published]

jobs:
  publish-pypi:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install build twine
      - name: Build package
        run: |
          cd packages/python
          python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: |
          cd packages/python
          python -m twine upload dist/*

  publish-npm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      - name: Install and build
        run: |
          cd packages/typescript
          npm ci
          npm run build
      - name: Publish to npm
        run: |
          cd packages/typescript
          npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Package Verification

### Check PyPI Package

```bash
# Check package metadata
python -m twine check packages/python/dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ catalogmx
```

### Check npm Package

```bash
# Check package contents
cd packages/typescript
npm pack --dry-run

# Verify package
npm publish --dry-run
```

## Best Practices

1. ✅ Use `pyproject.toml` as single source of truth
2. ✅ Use `uv` for faster dependency installation
3. ✅ Pin versions in `pyproject.toml`
4. ✅ Use GitHub Actions for automated publishing
5. ✅ Test packages before publishing
6. ✅ Keep package metadata synchronized (Python & TypeScript)
7. ✅ Use semantic versioning

