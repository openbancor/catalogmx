# Claude AI Agent Rules for catalogmx

## Project Overview

**catalogmx** is a production-ready, enterprise-grade Mexican data validation and catalog library with:
- **93.78% test coverage** (1,250+ tests passing across all platforms)
- **50+ modules at 100%** coverage
- **Multi-platform support**: Python 3.10+, TypeScript 5.0+, and Dart/Flutter 3.0+
- Modern packaging with `pyproject.toml`, `package.json`, and `pubspec.yaml`

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
│   ├── dart/
│   │   ├── lib/             # Dart source code
│   │   ├── test/            # Dart test files
│   │   ├── pubspec.yaml     # Dart package config
│   │   └── analysis_options.yaml  # Dart linter rules
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

## Linting and Static Analysis

### IMPORTANT: Always Run Before Committing

All code MUST pass linting and static analysis checks before committing.

### Python

```bash
cd packages/python

# Format code (required)
black catalogmx/

# Lint code (required)
ruff check catalogmx/
ruff check catalogmx/ --fix  # Auto-fix issues

# Type checking (recommended)
mypy catalogmx/

# All checks in one command
black catalogmx/ && ruff check catalogmx/ && mypy catalogmx/
```

**Configuration**: `pyproject.toml` contains all Black, Ruff, and mypy settings.

### TypeScript

```bash
cd packages/typescript

# Lint code (required)
npm run lint
npm run lint:fix  # Auto-fix issues

# Format code (required)
npm run format:check
npm run format  # Auto-format

# Type checking (required)
npm run typecheck

# All checks in one command
npm run lint && npm run format:check && npm run typecheck
```

**Configuration**: `.eslintrc.js`, `tsconfig.json`, `.prettierrc`

### Dart/Flutter

```bash
cd packages/dart

# Analyze code (required) - catches errors and warnings
dart analyze

# Format code (required)
dart format .
dart format --set-exit-if-changed .  # Check only (CI mode)

# Run tests
dart test

# Dry-run pub.dev publish (validates package)
dart pub publish --dry-run

# All checks in one command
dart analyze && dart format --set-exit-if-changed . && dart test
```

**Configuration**: `analysis_options.yaml` contains all Dart analyzer and linter rules.

### CI Enforcement

All linting checks are enforced in GitHub Actions CI:
- **Python**: Black format check, Ruff lint, mypy type check
- **TypeScript**: ESLint, Prettier format check, TypeScript strict mode
- **Dart**: dart analyze, dart format check

Code that fails any check will NOT be merged.

### Pre-commit Checklist (MANDATORY)

**CRITICAL: Run these commands before EVERY commit to avoid CI failures:**

```bash
# Quick format all (run from repo root)
(cd packages/python && black catalogmx/) && \
(cd packages/typescript && npm run format 2>/dev/null || true) && \
(cd packages/dart && dart format .) && \
echo "✅ All formatted"
```

**Full pre-commit validation:**

```bash
# Python (REQUIRED)
cd packages/python
black catalogmx/ && ruff check catalogmx/ && pytest tests/ -x -q

# TypeScript (REQUIRED if modified)
cd packages/typescript
npm run lint && npm run format:check && npm run typecheck && npm test

# Dart (REQUIRED)
cd packages/dart
dart format . && dart analyze && dart test

# YAML (REQUIRED for workflow changes)
yamllint -d "{extends: relaxed, rules: {line-length: {max: 200}, truthy: disable}}" .github/workflows/
```

**One-liner from repo root (formats + lints all platforms):**

```bash
(cd packages/python && black catalogmx/ && ruff check catalogmx/) && \
(cd packages/typescript && npm run lint && npm run format:check) && \
(cd packages/dart && dart format . && dart analyze) && \
echo "✅ All checks passed"
```

### Common CI Failures and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `black would reformat` | Python not formatted | `black catalogmx/` |
| `dart format --set-exit-if-changed` | Dart not formatted | `dart format .` |
| `ruff check` failures | Lint errors | `ruff check --fix catalogmx/` |
| `yamllint` errors | YAML syntax/trailing spaces | Remove trailing spaces |
| `npm run lint` failures | ESLint errors | `npm run lint:fix` |
| `npm run format:check` failures | Prettier errors | `npm run format` |
| `tsc` type errors | TypeScript errors | Fix type issues manually |
| `pytest` failures | Python test errors | Run `pytest tests/ -x` to find failing test |
| `npm test` failures | TypeScript test errors | Run `npm test` to see details |
| `dart test` failures | Dart test errors | Run `dart test` to see details |
| Circular import | Module imports in wrong order | Use lazy imports in affected modules |

---

## Quality Standards & CI/CD Pipeline

### Overview

catalogmx enforces **strict quality standards** through automated CI/CD pipelines on every push and pull request. All quality checks MUST pass before code can be merged.

### CI Pipeline Structure

The CI pipeline (`.github/workflows/ci.yml`) runs comprehensive quality gates across all three platforms:

#### **Python Quality Gates** (Python 3.10-3.14)

```bash
# 1. Linting (REQUIRED - Must Pass)
ruff check catalogmx/

# 2. Code Formatting (REQUIRED - Must Pass)
black --check catalogmx/

# 3. Type Checking (RECOMMENDED - Warning only)
mypy catalogmx/

# 4. Test Suite (REQUIRED - Must Pass)
pytest tests/ -v --cov=catalogmx --cov-report=xml --cov-report=term-missing --cov-branch

# 5. Coverage Threshold (TARGET - Warning only)
coverage report --fail-under=100  # Target: 100%, Minimum: 90%
```

**Quality Standards:**
- ✅ **Linting**: Zero ruff violations
- ✅ **Format**: 100% Black-compliant code
- ⚠️ **Type Check**: mypy warnings (continue-on-error)
- ✅ **Tests**: 100% passing (0 failures)
- 🎯 **Coverage**: 90% minimum (current: 93.78%, target: 100%)

#### **TypeScript Quality Gates** (Node 18, 20, 22)

```bash
# 1. Linting (REQUIRED - Must Pass)
npm run lint

# 2. Code Formatting (REQUIRED - Must Pass)
npm run format:check

# 3. Type Checking (REQUIRED - Must Pass)
npm run typecheck

# 4. Test Suite with Coverage (REQUIRED - Must Pass)
npm run test:coverage

# 5. Coverage Metrics Check (TARGET - Warning only)
# Checks: lines, statements, functions, branches all at 100%
```

**Quality Standards:**
- ✅ **ESLint**: Zero violations
- ✅ **Prettier**: 100% formatted code
- ✅ **TypeScript**: Strict mode, zero type errors
- ✅ **Tests**: 100% passing (0 failures)
- 🎯 **Coverage**: 90% minimum (target: 100% all metrics)

#### **Dart/Flutter Quality Gates** (Stable & Beta)

```bash
# 1. Dependency Verification (REQUIRED - Must Pass)
dart pub get
dart pub deps

# 2. Static Analysis (REQUIRED - Must Pass)
dart analyze

# 3. Code Formatting (REQUIRED - Must Pass)
dart format --set-exit-if-changed .

# 4. Test Suite with Coverage (REQUIRED - Must Pass)
dart test --coverage=coverage

# 5. Package Validation (REQUIRED - Must Pass)
dart pub publish --dry-run
```

**Quality Standards:**
- ✅ **Analyzer**: Zero errors/warnings (67 lint rules enforced)
- ✅ **Format**: 100% dart-formatted code
- ✅ **Tests**: 100% passing (0 failures)
- ✅ **Package**: Valid pub.dev package structure
- 🎯 **Coverage**: LCOV report generated

### Coverage Reporting

Separate coverage workflow (`.github/workflows/coverage-report.yml`) provides:

1. **Codecov Integration**: Automated coverage uploads
2. **PR Comments**: Coverage diff on pull requests
   - 🟢 Green threshold: ≥90%
   - 🟠 Orange threshold: ≥80%
   - 🔴 Red: <80%
3. **GitHub Pages**: HTML coverage reports
   - Python: `https://[org].github.io/catalogmx/coverage/python/`
   - TypeScript: `https://[org].github.io/catalogmx/coverage/typescript/`

### Quality Gate Matrix

| Platform   | Lint | Format | Types | Tests | Coverage | Min Coverage |
|------------|------|--------|-------|-------|----------|--------------|
| Python     | ✅   | ✅     | ⚠️    | ✅    | 🎯       | 90%          |
| TypeScript | ✅   | ✅     | ✅    | ✅    | 🎯       | 90%          |
| Dart       | ✅   | ✅     | ✅    | ✅    | 🎯       | 90%          |

**Legend:**
- ✅ **REQUIRED**: Must pass or CI fails
- ⚠️ **WARNING**: Continues on error (soft requirement)
- 🎯 **TARGET**: 100% goal, 90% minimum enforced with warnings

### Pre-Commit Quality Checklist

Before committing ANY code, run this full quality check:

#### Python
```bash
cd packages/python

# Full quality suite
black catalogmx/ && \
ruff check catalogmx/ && \
mypy catalogmx/ && \
pytest tests/ --cov=catalogmx --cov-branch --cov-report=term-missing

# Check results:
# ✅ Black: "reformatted" or "left unchanged"
# ✅ Ruff: "All checks passed!"
# ✅ Mypy: "Success: no issues found"
# ✅ Pytest: "passed" (0 failed)
# ✅ Coverage: ≥90% (target: 100%)
```

#### TypeScript
```bash
cd packages/typescript

# Full quality suite
npm run lint && \
npm run format:check && \
npm run typecheck && \
npm run test:coverage

# Check results:
# ✅ ESLint: No errors
# ✅ Prettier: All files formatted
# ✅ TSC: Compiled successfully
# ✅ Jest: All tests passed
# ✅ Coverage: ≥90% lines/statements/functions/branches
```

#### Dart
```bash
cd packages/dart

# Full quality suite
dart analyze && \
dart format --set-exit-if-changed . && \
dart test --coverage=coverage && \
dart pub publish --dry-run

# Check results:
# ✅ Analyzer: No issues found
# ✅ Format: No formatting changes needed
# ✅ Tests: All tests passed!
# ✅ Pub: Package has 0 warnings
```

### CI/CD Workflow Triggers

**Workflows run on:**
- **Push** to: `main`, `master`, `develop` branches
- **Pull Request** targeting: `main`, `master`, `develop` branches

**Other CI Workflows:**
- `publish.yml` - Automated package publishing to PyPI/npm/pub.dev
- `sqlite-assets.yml` - Builds SQLite databases from JSON catalogs
- `update-dynamic-data.yml` - Updates currency/inflation data from APIs
- `webapp-pages.yml` - Deploys webapp to GitHub Pages

### Enforcement Rules

**BLOCKING (CI will FAIL):**
- ❌ Linting errors (ruff, eslint, dart analyze)
- ❌ Format violations (black, prettier, dart format)
- ❌ TypeScript type errors
- ❌ Test failures
- ❌ Build failures
- ❌ Invalid package structure (dart pub publish --dry-run)

**NON-BLOCKING (Warnings only):**
- ⚠️ Python mypy type errors (continue-on-error: true)
- ⚠️ Coverage below 100% (target) but above 90% (minimum)
- ⚠️ Codecov upload failures

### Success Criteria Summary

For **ANY** code change to be merge-ready:

1. ✅ **All linters pass** (ruff, eslint, dart analyze)
2. ✅ **All formatters pass** (black, prettier, dart format)
3. ✅ **All tests pass** (pytest, jest, dart test)
4. ✅ **Coverage ≥90%** (current: 93.78%, target: 100%)
5. ✅ **Build succeeds** (tsc, dart pub)
6. ✅ **Package validates** (twine check, dart pub publish --dry-run)
7. ⚠️ **Type checking** (mypy warning-only, TSC required, dart analyze required)

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

For any change to be acceptable, all quality gates must pass (see **Quality Standards & CI/CD Pipeline** section):

1. ✅ **All linters pass** (ruff, eslint, dart analyze) - ZERO violations
2. ✅ **All formatters pass** (black, prettier, dart format) - 100% compliant
3. ✅ **All tests pass** (pytest, jest, dart test) - 0 failures across all platforms
4. ✅ **Coverage ≥90%** (current: 93.78%, target: 100%)
5. ✅ **All builds succeed** (python -m build, tsc, dart pub)
6. ✅ **Package validation** (twine check, dart pub publish --dry-run)
7. ⚠️ **Type checking** (mypy warning-only, tsc strict mode required)
8. ✅ **CI pipeline passes** (all GitHub Actions workflows green)
9. ✅ **Documentation updated** (if applicable)

**Quick Validation:**
```bash
# Python
cd packages/python && black catalogmx/ && ruff check catalogmx/ && mypy catalogmx/ && pytest tests/ --cov=catalogmx --cov-branch

# TypeScript
cd packages/typescript && npm run lint && npm run format:check && npm run typecheck && npm run test:coverage

# Dart
cd packages/dart && dart analyze && dart format --set-exit-if-changed . && dart test && dart pub publish --dry-run
```

---

## Project Status: ✅ Production Ready

- **Coverage**: 93.78% (exceeds 90% minimum requirement)
- **Tests**: 1,250+ passing (0 failures across all platforms)
- **Packaging**: Modern (pyproject.toml, package.json, pubspec.yaml)
- **Documentation**: Comprehensive and organized
- **Quality**: Enterprise-grade with automated CI/CD enforcement
- **Platforms**: Python 3.10-3.14, TypeScript/Node 18-22, Dart Stable & Beta
- **CI/CD**: 6 automated workflows (tests, coverage, publish, assets, data updates, webapp)

**Last Updated**: January 2026
**Maintained By**: Luis Fernando Barrera
**License**: BSD-2-Clause

