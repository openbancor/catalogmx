Contributing Guide
==================

Thank you for your interest in contributing to catalogmx!

Getting Started
---------------

Development Setup
~~~~~~~~~~~~~~~~~

1. **Fork and Clone**

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/catalogmx.git
      cd catalogmx

2. **Python Setup**

   .. code-block:: bash

      cd packages/python
      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      pip install -e ".[dev]"

3. **TypeScript Setup**

   .. code-block:: bash

      cd packages/typescript
      npm install

4. **Run Tests**

   .. code-block:: bash

      # Python
      pytest
      
      # TypeScript
      npm test

Code Standards
--------------

Python
~~~~~~

We use modern Python 3.10+ with PEP 604 type hints:

.. code-block:: python

   # Correct - Python 3.10+ syntax
   def get_item(code: str) -> dict | None:
       pass
   
   _data: list[dict] | None = None
   
   # Incorrect - Old syntax
   from typing import Optional, List, Dict
   def get_item(code: str) -> Optional[Dict]:
       pass

**Tools**:
  * **black**: Code formatting (line length: 100)
  * **ruff**: Linting and import sorting
  * **mypy**: Type checking
  * **pytest**: Testing

Run before committing:

.. code-block:: bash

   black catalogmx/
   ruff check catalogmx/
   mypy catalogmx/
   pytest

TypeScript
~~~~~~~~~~

We use TypeScript 5.0+ with strict mode:

.. code-block:: typescript

   // Correct
   export function validateRFC(code: string): boolean {
       // ...
   }
   
   export interface PostalCode {
       cp: string;
       asentamiento: string;
       municipio: string;
   }

**Tools**:
  * **prettier**: Code formatting
  * **eslint**: Linting
  * **jest**: Testing

Run before committing:

.. code-block:: bash

   npm run lint
   npm run format
   npm test

Adding New Catalogs
-------------------

1. **Create JSON File**

   Place in ``packages/shared-data/SOURCE/CATEGORY/``:

   .. code-block:: json

      {
        "metadata": {
          "catalog": "CatalogName",
          "version": "2025",
          "source": "Official Source",
          "description": "Catalog description",
          "last_updated": "2025-11-08",
          "total_records": 100
        },
        "items": [
          {
            "code": "001",
            "description": "Item description"
          }
        ]
      }

2. **Create Python Class**

   In ``packages/python/catalogmx/catalogs/SOURCE/``:

   .. code-block:: python

      """Catalog description"""
      import json
      from pathlib import Path
      
      class CatalogNameCatalog:
          """Catalog description in Spanish for official data"""
          
          _data: list[dict] | None = None
          _by_code: dict[str, dict] | None = None
          
          @classmethod
          def _load_data(cls) -> None:
              if cls._data is None:
                  path = Path(__file__).parent.parent.parent.parent.parent / \
                         'shared-data' / 'source' / 'file.json'
                  with open(path, 'r', encoding='utf-8') as f:
                      data = json.load(f)
                      cls._data = data['items']
                  cls._by_code = {item['code']: item for item in cls._data}
          
          @classmethod
          def get_item(cls, code: str) -> dict | None:
              cls._load_data()
              return cls._by_code.get(code)
          
          @classmethod
          def is_valid(cls, code: str) -> bool:
              return cls.get_item(code) is not None
          
          @classmethod
          def get_all(cls) -> list[dict]:
              cls._load_data()
              return cls._data.copy()

3. **Add Tests**

   In ``packages/python/tests/``:

   .. code-block:: python

      def test_catalog_load():
          items = CatalogNameCatalog.get_all()
          assert len(items) > 0
      
      def test_catalog_get_item():
          item = CatalogNameCatalog.get_item('001')
          assert item is not None
          assert item['code'] == '001'
      
      def test_catalog_is_valid():
          assert CatalogNameCatalog.is_valid('001') == True
          assert CatalogNameCatalog.is_valid('999') == False

4. **Update Documentation**

   Add to ``docs/api/catalogs-SOURCE.rst``

5. **Update Exports**

   In ``catalogmx/catalogs/SOURCE/__init__.py``:

   .. code-block:: python

      from .catalog_name import CatalogNameCatalog
      
      __all__ = [..., 'CatalogNameCatalog']

Pull Request Process
--------------------

1. **Create Feature Branch**

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make Changes**

   * Write code
   * Add tests
   * Update documentation

3. **Run Tests and Linters**

   .. code-block:: bash

      # Python
      pytest
      black catalogmx/
      ruff check catalogmx/
      mypy catalogmx/
      
      # TypeScript
      npm test
      npm run lint

4. **Commit**

   Use conventional commits:

   .. code-block:: bash

      git commit -m "feat: add new catalog XYZ"
      git commit -m "fix: correct path in SEPOMEX catalog"
      git commit -m "docs: update API reference for validators"

5. **Push and Create PR**

   .. code-block:: bash

      git push origin feature/your-feature-name

   Then create a Pull Request on GitHub.

Commit Message Format
---------------------

We use Conventional Commits:

* ``feat:``: New feature
* ``fix:``: Bug fix
* ``docs:``: Documentation changes
* ``test:``: Adding or updating tests
* ``refactor:``: Code refactoring
* ``perf:``: Performance improvements
* ``chore:``: Maintenance tasks

Examples:

.. code-block:: text

   feat: add LocalidadesCatalog with GPS search
   fix: correct CLABE check digit calculation
   docs: add API reference for SEPOMEX catalogs
   test: add tests for geographic search
   refactor: modernize type hints to PEP 604

Documentation Guidelines
------------------------

Code Documentation
~~~~~~~~~~~~~~~~~~

All public functions and classes must have docstrings:

.. code-block:: python

   def validate_rfc(rfc_code: str) -> bool:
       """
       Validate RFC code (Registro Federal de Contribuyentes).
       
       Args:
           rfc_code: The RFC code to validate (12 or 13 characters)
       
       Returns:
           True if valid, False otherwise
       
       Example:
           >>> validate_rfc("XAXX010101000")
           True
       """
       pass

Language Strategy
~~~~~~~~~~~~~~~~~

* **Code**: 100% English (variables, functions, classes)
* **Docstrings**: English (for IDEs and international developers)
* **Official Data**: Spanish (SAT descriptions, INEGI names - official)
* **README**: Bilingual (README.md + README.es.md)
* **Technical Guides**: Spanish (docs/guides/)

Catalog Update Process
----------------------

1. **Download Official Data**

   .. code-block:: bash

      python scripts/download_sepomex_complete.py
      python scripts/download_inegi_complete.py

2. **Process Data**

   .. code-block:: bash

      python scripts/process_sepomex_file.py
      python scripts/process_inegi_municipios.py

3. **Verify Data**

   Check that:
   * JSON is valid
   * ``metadata.total_records`` matches actual count
   * No encoding issues (UTF-8)
   * All required fields present

4. **Update Tests**

   Ensure existing tests still pass with new data

5. **Document Changes**

   Update ``docs/changelog-catalogs.md``

Testing Guidelines
------------------

Test Coverage
~~~~~~~~~~~~~

Aim for >80% code coverage:

.. code-block:: bash

   pytest --cov=catalogmx --cov-report=html
   # Open htmlcov/index.html

Types of Tests
~~~~~~~~~~~~~~

**Unit Tests**: Test individual functions

.. code-block:: python

   def test_validate_rfc_valid():
       assert validate_rfc("XAXX010101000") == True
   
   def test_validate_rfc_invalid():
       assert validate_rfc("INVALID") == False

**Integration Tests**: Test catalog loading

.. code-block:: python

   def test_catalog_loads():
       items = SomeCatalog.get_all()
       assert len(items) > 0

**Edge Cases**: Test boundary conditions

.. code-block:: python

   def test_validate_empty_string():
       assert validate_rfc("") == False
   
   def test_validate_none():
       assert validate_rfc(None) == False

Release Process
---------------

1. **Update Version**

   In ``packages/python/pyproject.toml``:

   .. code-block:: toml

      [project]
      version = "0.4.0"

2. **Update Changelog**

   In ``CHANGELOG.rst``

3. **Run Full Test Suite**

   .. code-block:: bash

      pytest
      npm test

4. **Build Documentation**

   .. code-block:: bash

      cd docs
      make html

5. **Build Packages**

   .. code-block:: bash

      # Python
      cd packages/python
      python -m build
      
      # TypeScript
      cd packages/typescript
      npm run build

6. **Create Git Tag**

   .. code-block:: bash

      git tag v0.4.0
      git push origin v0.4.0

7. **Publish**

   .. code-block:: bash

      # PyPI
      twine upload dist/*
      
      # NPM
      npm publish

Questions or Issues?
--------------------

* **Bug Reports**: `GitHub Issues <https://github.com/openbancor/catalogmx/issues>`_
* **Feature Requests**: `GitHub Discussions <https://github.com/openbancor/catalogmx/discussions>`_
* **Email**: luisfernando@informind.com

Code of Conduct
---------------

This project follows the Python Community Code of Conduct. Please be respectful and professional in all interactions.

License
-------

All contributions will be licensed under the BSD 2-Clause License.

Thank You!
----------

Your contributions make catalogmx better for the entire Mexican developer community.
