# Claude AI Agent Rules for catalogmx

## Project Overview

**catalogmx** is a production-ready, enterprise-grade Mexican data validation and catalog library with:
- **93.78% test coverage** (926 tests passing)
- **50+ modules at 100%** coverage
- Dual-language support (Python 3.10+ and TypeScript 5.0+)
- Modern packaging with `pyproject.toml`

---

## Core Principles

### 1. **Quality First**
- ✅ Maintain **minimum 90% test coverage** (currently 93.78%)
- ✅ All tests must pass before committing
- ✅ Write tests for new features (TDD preferred)
- ✅ No decrease in coverage allowed

### 2. **Modern Python Standards**
- ✅ Use `pyproject.toml` as single source of truth
- ✅ No `setup.py`, `setup.cfg`, or `requirements.txt`
- ✅ Recommend `uv` for package installation (10-100x faster)
- ✅ Python 3.10+ only (use modern type hints: PEP 604)
- ✅ Use `ruff` and `black` for code formatting

### 3. **Code Organization**
- ✅ Keep validators independent (no external dependencies except unidecode/click)
- ✅ Lazy load catalogs (don't load all data at once)
- ✅ Use TypedDict for structured data
- ✅ Maintain identical APIs across Python and TypeScript

### 4. **Testing**
- ✅ Test files in `packages/python/tests/`
- ✅ Use pytest with coverage: `pytest tests/ --cov=catalogmx --cov-branch`
- ✅ Minimum 90% coverage required
- ✅ Cover error paths and edge cases
- ✅ Test both success and failure scenarios

---

## Project Structure

```
catalogmx/
├── .github/workflows/        # CI/CD automation
├── docs/                     # ALL documentation here
│   ├── api/                 # API references
│   ├── guides/              # User guides
│   ├── archive/             # Old/irrelevant docs
│   └── *.md                 # New documentation
├── packages/
│   ├── python/
│   │   ├── catalogmx/       # Source code
│   │   ├── tests/           # 34 test files
│   │   └── pyproject.toml   # Single config file
│   ├── typescript/
│   │   ├── src/
│   │   ├── tests/
│   │   └── package.json
│   └── shared-data/         # JSON catalogs & SQLite DBs
├── README.md                 # Main documentation
├── CLAUDE.md                 # This file (AI agent rules)
├── AGENTS.md                 # Symlink to CLAUDE.md
└── LICENSE                   # BSD-2-Clause
```

---

## Coding Rules

### Python

```python
# ✅ DO: Use modern type hints
def validate_rfc(rfc: str | None) -> bool:
    """Validate RFC with proper typing"""
    
# ❌ DON'T: Use old Union syntax
from typing import Union, Optional
def validate_rfc(rfc: Optional[Union[str, None]]) -> bool:

# ✅ DO: Use lazy loading
class Catalog:
    _data: list[dict] | None = None
    
    @classmethod
    def _load_data(cls):
        if cls._data is None:
            cls._data = load_json()

# ❌ DON'T: Load data at module level
DATA = load_json()  # Loads immediately!

# ✅ DO: Handle both JSON formats
with open(path) as f:
    data = json.load(f)
    cls._data = data if isinstance(data, list) else data.get("items", data)

# ✅ DO: Use descriptive test names
def test_validate_rfc_with_invalid_homoclave():
    """Test RFC validation when homoclave has invalid characters"""
    
# ❌ DON'T: Use vague test names
def test_1():
```

### Testing

```python
# ✅ DO: Test both success and failure
def test_valid_clabe():
    assert validate_clabe("002010077777777771") is True

def test_invalid_clabe():
    assert validate_clabe("invalid") is False

# ✅ DO: Test error paths
def test_clabe_with_invalid_length():
    with pytest.raises(CLABELengthError):
        CLABEValidator("short").validate()

# ✅ DO: Test edge cases
def test_curp_with_special_characters_in_name():
    gen = CURPGenerator(..., nombre="José María")
    assert len(gen.curp) == 18
```

---

## File Naming Conventions

### Source Files
- `catalogmx/catalogs/<source>/<catalog_name>.py` - Catalog modules
- `catalogmx/validators/<validator>.py` - Validator modules
- `catalogmx/utils/<utility>.py` - Utility modules

### Test Files
- `tests/test_<module>.py` - Direct module tests
- `tests/test_<module>_complete.py` - Comprehensive tests
- `tests/test_<feature>_all.py` - Feature tests

### Documentation
- `docs/` - All documentation
- `docs/guides/` - User/developer guides
- `docs/api/` - API references
- `docs/archive/` - Old/irrelevant docs
- Root: Only `README.md`, `CLAUDE.md`, `AGENTS.md`, `LICENSE`

---

## Git Workflow

### Commits

```bash
# ✅ Good commit messages
git commit -m "feat: add CLABE validator with 100% coverage"
git commit -m "fix: handle both JSON list and dict formats in catalogs"
git commit -m "docs: add testing and coverage guide"
git commit -m "test: achieve 93.78% coverage with 926 tests"

# ❌ Bad commit messages
git commit -m "updates"
git commit -m "fix"
```

### Before Committing

```bash
# 1. Run tests
pytest tests/ --cov=catalogmx --cov-branch

# 2. Check coverage (must be >= 90%)
# Coverage: 93.78% ✅

# 3. Format code
black catalogmx/
ruff check catalogmx/

# 4. Type check
mypy catalogmx/
```

---

## When Adding New Features

### 1. **Write Tests First (TDD)**
```python
# tests/test_new_feature.py
def test_new_validator_valid():
    assert validate_new("valid_input") is True

def test_new_validator_invalid():
    assert validate_new("invalid") is False
```

### 2. **Implement Feature**
```python
# catalogmx/validators/new.py
def validate_new(value: str | None) -> bool:
    """Validate new Mexican identifier"""
    if not value:
        return False
    # Implementation
    return True
```

### 3. **Ensure Coverage**
```bash
pytest tests/test_new_feature.py --cov=catalogmx/validators/new.py --cov-report=term-missing
# Must show 100% or close to it
```

### 4. **Update Documentation**
- Add to README.md features section
- Create guide in `docs/guides/` if needed
- Update API documentation

---

## Catalog Guidelines

### JSON Handling
```python
# ✅ Always handle both formats
with open(path) as f:
    data = json.load(f)
    # Handle both list and dict
    cls._data = data if isinstance(data, list) else data.get("key", data)
```

### Catalog Methods Pattern
```python
class MyCatalog:
    _data: list[dict] | None = None
    
    @classmethod
    def _load_data(cls):
        """Lazy load data"""
        if cls._data is None:
            # Load from JSON
            cls._data = ...
    
    @classmethod
    def get_all(cls) -> list[dict]:
        """Get all items"""
        cls._load_data()
        return cls._data.copy()
    
    @classmethod
    def get_by_code(cls, code: str) -> dict | None:
        """Get item by code"""
        cls._load_data()
        return cls._by_code.get(code)
    
    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Validate code exists"""
        return cls.get_by_code(code) is not None
```

---

## Dependencies

### Python Runtime (Minimal)
- `unidecode>=1.4.0` - For RFC/CURP generation (accent removal)
- `click>=8.0.0` - For CLI interface

### Python Development
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `black>=23.0.0` - Code formatting
- `ruff>=0.1.0` - Linting
- `mypy>=1.7.0` - Type checking

### Keep It Light!
- ❌ No pandas, numpy, or heavy dependencies
- ❌ No external API calls in core functionality
- ✅ Validators work offline
- ✅ Catalogs are local JSON/SQLite files

---

## Common Tasks

### Run Tests
```bash
cd packages/python
pytest tests/ -v
```

### Check Coverage
```bash
pytest tests/ --cov=catalogmx --cov-report=term-missing --cov-branch
```

### Build Package
```bash
python -m build
```

### Install Locally
```bash
uv pip install -e ".[dev]"
```

### Format Code
```bash
black catalogmx/
ruff check --fix catalogmx/
```

---

## Coverage Rules

### Minimum Requirements
- **Overall**: 90% minimum (currently 93.78%)
- **New modules**: Aim for 100%
- **Critical validators**: Must be 100% (CLABE, NSS are 100%)
- **Catalogs**: 90%+ preferred

### What Can Be Uncovered
- Optional utility methods (< 5% of module)
- Defensive error handling (already tested indirectly)
- Legacy compatibility code (if marked as deprecated)

### What Must Be Covered
- ✅ All validator logic paths
- ✅ All public methods
- ✅ Error handling in critical paths
- ✅ Catalog loading mechanisms

---

## Documentation Rules

### Keep in Root
- ✅ `README.md` - Main documentation (essential)
- ✅ `CLAUDE.md` - AI agent rules (this file)
- ✅ `AGENTS.md` - Symlink to CLAUDE.md
- ✅ `LICENSE` - Legal (essential)
- ✅ `CONTRIBUTING.rst` - Contribution guide (if exists)
- ✅ `CHANGELOG.rst` - Version history (if exists)

### Move to docs/
- 📦 All other `.md` files go in `docs/`
- 📦 Technical documentation → `docs/`
- 📦 Old documentation → `docs/archive/`
- 📦 Guides → `docs/guides/`

---

## Don'ts

### Code
- ❌ Don't add external API dependencies
- ❌ Don't use deprecated Python syntax (Union, Optional)
- ❌ Don't create setup.py (use pyproject.toml)
- ❌ Don't hardcode paths (use pathlib)
- ❌ Don't load all catalog data at import time

### Tests
- ❌ Don't skip tests
- ❌ Don't lower coverage threshold below 90%
- ❌ Don't commit failing tests
- ❌ Don't write tests without assertions

### Documentation
- ❌ Don't scatter MD files in root
- ❌ Don't duplicate documentation
- ❌ Don't create outdated documentation

---

## Quick Reference

### Test Coverage Check
```bash
pytest tests/ --cov=catalogmx --cov-branch -q
# Required: >= 90% (currently 93.78% ✅)
```

### Package Build Check
```bash
cd packages/python
python -m build && python -m twine check dist/*
# Must see: PASSED ✅
```

### TypeScript Build Check
```bash
cd packages/typescript
npm run build
# Must complete without errors ✅
```

---

## Success Criteria

For any change to be acceptable:

1. ✅ All 926 tests must pass
2. ✅ Coverage must be >= 90%
3. ✅ Code must be formatted (black + ruff)
4. ✅ Package must build successfully
5. ✅ Documentation must be updated

---

## Project Status: ✅ Production Ready

- **Coverage**: 93.78% (exceeds 90% requirement)
- **Tests**: 926 passing (0 failures)
- **Packaging**: Modern pyproject.toml
- **Documentation**: Comprehensive and organized
- **Quality**: Enterprise-grade

**Last Updated**: November 2024
**Maintained By**: Luis Fernando Barrera
**License**: BSD-2-Clause

