catalogmx Documentation
=======================

**Comprehensive Mexican Data Validators and Official Catalogs Library**

catalogmx is a production-ready, multi-language library (Python 3.10+ | TypeScript 5.0+) for validating Mexican identifiers and accessing official catalogs from government agencies.

.. image:: https://img.shields.io/badge/python-3.10+-blue.svg
   :target: https://python.org
   :alt: Python 3.10+

.. image:: https://img.shields.io/badge/typescript-5.0+-blue.svg
   :target: https://www.typescriptlang.org
   :alt: TypeScript 5.0+

.. image:: https://img.shields.io/badge/license-BSD--2--Clause-blue.svg
   :target: LICENSE
   :alt: BSD 2-Clause License

Overview
--------

**Key Features**:

* **4 Validators**: RFC, CURP, CLABE, NSS with complete official algorithms
* **43 Official Catalogs**: SAT, INEGI, SEPOMEX, Banxico
* **170,505+ Records**: Complete databases with 157K postal codes, 2.4K municipalities, 10K+ localities
* **GPS Coordinates**: Geographic search for 10,635 localities
* **Type-Safe**: Full type hints (PEP 604) and TypeScript declarations
* **Zero Dependencies**: Validators require no external packages
* **Production Ready**: Tested and documented

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install catalogmx

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from catalogmx.validators import rfc
   from catalogmx.catalogs.sepomex import CodigosPostales
   
   # Validate RFC
   is_valid = rfc.validate_rfc("XAXX010101000")
   
   # Search postal codes
   results = CodigosPostales.get_by_cp("06700")
   print(results[0]['asentamiento'])  # "Roma Norte"

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   
   installation
   quickstart
   usage

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/validators
   api/catalogs-sat
   api/catalogs-inegi
   api/catalogs-sepomex
   api/catalogs-banxico

.. toctree::
   :maxdepth: 2
   :caption: Guides
   
   guides/architecture
   guides/developers-guide
   guides/catalog-updates
   guides/cp-locality-linking

.. toctree::
   :maxdepth: 1
   :caption: Catalogs Documentation
   
   catalogs/overview
   catalogs/sepomex
   catalogs/inegi
   catalogs/sat

.. toctree::
   :maxdepth: 1
   :caption: Project
   
   roadmap
   changelog
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
