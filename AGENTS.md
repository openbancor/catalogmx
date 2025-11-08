# 🤖 AGENTS.md - Instructions for AI Agents

This document provides instructions for AI agents (Claude, GPT-4, etc.) working on the catalogmx project.

---

## 📋 Project Overview

**catalogmx** is a comprehensive Mexican data validators and official catalogs library.

**Key Components**:
- Validators: RFC, CURP, CLABE, NSS
- SAT Catalogs: CFDI 4.0, Comercio Exterior, Carta Porte, Nómina
- Geographic: INEGI, SEPOMEX
- Banking: Banxico

**Tech Stack**:
- Python 3.10+
- Modern type hints (PEP 604 union syntax with `|`)
- Lazy loading architecture
- JSON-based catalog data
- pytest for testing

---

## 🏗️ Architecture Principles

### 1. Lazy Loading Pattern

All catalogs use lazy loading to minimize memory usage:

```python
class ExampleCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent / '...' / 'data.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['items']
            cls._by_code = {item['code']: item for item in cls._data}
```

**Rules**:
- Always check `if cls._data is None` before loading
- Load JSON only once per catalog class
- Create indices (by_code, by_name, etc.) during first load
- Use class variables, not instance variables

### 2. File Structure

```
packages/
├── shared-data/           # JSON catalog data
│   ├── sat/
│   │   ├── cfdi_4.0/     # One JSON file per catalog
│   │   ├── comercio_exterior/
│   │   ├── carta_porte_3/
│   │   └── nomina_1.2/
│   ├── inegi/
│   ├── sepomex/
│   └── banxico/
└── python/
    └── catalogmx/
        ├── validators/    # RFC, CURP, CLABE, NSS
        └── catalogs/      # Catalog classes
            ├── sat/
            ├── inegi/
            ├── sepomex/
            └── banxico/
```

**Rules**:
- Each catalog = 1 JSON file + 1 Python class
- JSON files in `shared-data/`
- Python classes in `catalogmx/catalogs/`
- Maintain parallel structure

### 3. JSON Catalog Format

**Standard structure**:
```json
{
  "metadata": {
    "catalog": "catalog_name",
    "version": "2025",
    "source": "Official source",
    "description": "Description",
    "last_updated": "2025-11-08",
    "total_records": 100,
    "notes": "Additional notes"
  },
  "items_key": [
    {
      "code": "001",
      "name": "Item name",
      "field1": "value1"
    }
  ]
}
```

**Rules**:
- Always include metadata section
- Main data key varies: `municipios`, `codigos_postales`, `aeropuertos`, etc.
- Use consistent field names: `code`, `name`, `description`
- Include `total_records` in metadata
- Use UTF-8 encoding, `ensure_ascii=False` when writing JSON

### 4. Python Catalog Class Template

```python
"""Catalog description"""
import json
from pathlib import Path

class CatalogName:
    """Catalog description in Spanish"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo si aún no han sido cargados"""
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'path' / 'file.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['items']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_item(cls, code: str) -> dict | None:
        """Get item by code"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Check if code is valid"""
        return cls.get_item(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Get all items"""
        cls._load_data()
        return cls._data.copy()
```

**Rules**:
- Use class methods, not instance methods
- Always call `cls._load_data()` before accessing data
- Return copies of lists (`cls._data.copy()`)
- Type hints on all methods using Python 3.10+ syntax (no `typing` imports)
- Docstrings for public methods
- Use `list[dict]` instead of `List[Dict]`
- Use `dict | None` instead of `Optional[Dict]`
- Add `-> None` return type to `_load_data()` methods

### 5. Naming Conventions

**Files**:
- JSON: snake_case.json (`regimen_fiscal.json`)
- Python: snake_case.py (`regimen_fiscal.py`)
- Classes: PascalCase (`RegimenFiscalCatalog`)

**Methods**:
- `get_<item>()` - Get single item by primary key
- `get_by_<field>()` - Get items by secondary field
- `is_valid()` - Check if code/key is valid
- `get_all()` - Get all items
- `search_<field>()` - Search with partial matching

**Variables**:
- Class variables: `_data`, `_by_code`, `_by_name`
- Use underscore prefix for internal/private
- No instance variables

---

## 🔧 Common Tasks

### Adding a New Catalog

1. **Create JSON file** in `packages/shared-data/`:
```bash
packages/shared-data/sat/cfdi_4.0/new_catalog.json
```

2. **Create Python class** in `packages/python/catalogmx/catalogs/`:
```bash
packages/python/catalogmx/catalogs/sat/cfdi_4/new_catalog.py
```

3. **Update `__init__.py`** to export new class:
```python
from .new_catalog import NewCatalogClass

__all__ = [..., 'NewCatalogClass']
```

4. **Add tests** in `tests/`:
```python
def test_new_catalog():
    item = NewCatalogClass.get_item('001')
    assert item is not None
```

5. **Update README** with new catalog information

### Updating an Existing Catalog

1. **Update JSON file** with new data
2. **Update metadata.total_records** to match
3. **Update metadata.last_updated** to current date
4. **Test** that Python class still works
5. **Document changes** in CHANGELOG or commit message

### Converting External Data to catalogmx Format

Use the conversion scripts:

**For SEPOMEX**:
```bash
python scripts/csv_to_catalogmx.py input.csv
```

**For INEGI**:
```bash
python scripts/process_inegi_data.py input.txt
```

**For custom formats**, create a new script following this pattern:
1. Read input file (CSV, Excel, JSON, etc.)
2. Parse and transform data
3. Create catalogmx JSON structure with metadata
4. Write to `packages/shared-data/`

---

## 🧪 Testing Guidelines

### Test Structure

```python
def test_catalog_load():
    """Test catalog loads without errors"""
    items = CatalogClass.get_all()
    assert len(items) > 0

def test_catalog_get_item():
    """Test getting single item"""
    item = CatalogClass.get_item('known_code')
    assert item is not None
    assert item['code'] == 'known_code'

def test_catalog_is_valid():
    """Test validation"""
    assert CatalogClass.is_valid('known_code') == True
    assert CatalogClass.is_valid('invalid_code') == False

def test_catalog_indices():
    """Test secondary indices"""
    items = CatalogClass.get_by_type('type_value')
    assert len(items) > 0
```

**Rules**:
- Test all public methods
- Test with known good data
- Test with invalid data
- Test edge cases (empty strings, None, etc.)
- Use descriptive test names

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_catalogs.py

# Specific test
pytest tests/test_catalogs.py::test_catalog_load

# With coverage
pytest --cov=catalogmx --cov-report=html
```

---

## 📝 Documentation Standards

### Code Comments

**When to comment**:
- Complex algorithms (RFC homoclave, CURP check digit)
- Non-obvious business rules
- SAT/RENAPO specification references
- Validation rules

**When not to comment**:
- Obvious code (`# Load data` before loading data)
- Self-documenting code with good naming

### Docstrings

**Required for**:
- All public methods
- All classes
- Complex private methods

**Format**:
```python
def get_item(cls, code: str) -> Optional[Dict]:
    """
    Get catalog item by code.

    Args:
        code: The item code to search for

    Returns:
        Dictionary with item data, or None if not found

    Example:
        >>> item = Catalog.get_item('001')
        >>> print(item['name'])
    """
```

### README Updates

When adding features, update:
1. Feature list in main README
2. Usage examples
3. Statistics (catalog counts)
4. Quick links if applicable

---

## 🚨 Common Pitfalls

### ❌ Don't Do This

```python
# DON'T: Load data multiple times
def get_item(cls, code: str):
    with open(file) as f:  # ❌ Loads every time
        data = json.load(f)
    return data.get(code)

# DON'T: Return references to class data
def get_all(cls):
    return cls._data  # ❌ Allows external modification

# DON'T: Use instance variables
def __init__(self):
    self.data = []  # ❌ Should be class variable

# DON'T: Hardcode paths
path = "/absolute/path/to/file.json"  # ❌
```

### ✅ Do This Instead

```python
# DO: Lazy load with class variables
def get_item(cls, code: str) -> dict | None:
    cls._load_data()  # ✅ Loads once
    return cls._by_code.get(code)

# DO: Return copies
def get_all(cls) -> list[dict]:
    return cls._data.copy()  # ✅ Safe

# DO: Use class variables with modern type hints
class Catalog:
    _data: list[dict] | None = None  # ✅

# DO: Use relative paths
path = Path(__file__).parent / 'data.json'  # ✅
```

---

## 🔍 Code Review Checklist

Before committing:

- [ ] JSON files have complete metadata
- [ ] JSON `total_records` matches actual count
- [ ] Python classes use lazy loading
- [ ] All public methods have docstrings
- [ ] Type hints on all methods
- [ ] Tests added for new features
- [ ] All tests passing (`pytest`)
- [ ] README updated if adding features
- [ ] No hardcoded paths
- [ ] Proper encoding (UTF-8)
- [ ] Consistent naming conventions
- [ ] No instance variables in catalog classes

---

## 🎯 Quick Reference

### Important Files

- `README.md` - Main documentation
- `README_CATALOGMX.md` - Detailed catalog docs
- `DESCARGA_RAPIDA.md` - Quick download guide
- `CATALOG_UPDATES.md` - Update procedures
- `CLAUDE.md` - Architecture details

### Official Sources

- **SAT**: https://www.sat.gob.mx/consulta/55405/catalogo-de-catalogos
- **INEGI**: https://www.inegi.org.mx/app/ageeml/
- **SEPOMEX**: https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/
- **Banxico**: https://www.banxico.org.mx/

### Key Commands

```bash
# Development
pip install -e packages/python/
pytest
python -m catalogmx.validators.rfc

# Add catalog
1. Create JSON in shared-data/
2. Create Python class in catalogmx/catalogs/
3. Update __init__.py
4. Add tests
5. Update README

# Convert data
python scripts/csv_to_catalogmx.py file.csv
python scripts/process_inegi_data.py file.txt
```

---

## 💡 Tips for AI Agents

1. **Always preserve existing patterns** - The codebase has consistent patterns, maintain them
2. **Check existing catalogs** - Look at similar catalogs for reference
3. **Test before committing** - Run pytest to ensure changes work
4. **Update documentation** - Keep README current with changes
5. **Use type hints** - They help catch errors and improve IDE support
6. **Think about memory** - Large datasets should use lazy loading
7. **Validate official sources** - Double-check data against SAT/INEGI sources
8. **Be consistent** - Follow the established naming and structure conventions

---

## 📞 Questions?

If implementing a new feature:
1. Check existing similar features
2. Review this AGENTS.md guide
3. Review CLAUDE.md for architecture details
4. Look at test files for examples
5. Follow the patterns established in the codebase

The codebase is designed to be consistent and predictable. When in doubt, follow existing patterns.
