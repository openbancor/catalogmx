Quick Start Guide
=================

This guide will help you get started with catalogmx in 5 minutes.

Installation
------------

.. code-block:: bash

   pip install catalogmx

Basic Usage
-----------

Validating Identifiers
~~~~~~~~~~~~~~~~~~~~~~~

RFC Validation
^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.validators import rfc
   
   # Validate existing RFC
   is_valid = rfc.validate_rfc("XAXX010101000")
   print(is_valid)  # True
   
   # Generate RFC for Persona Física
   generated_rfc = rfc.generate_rfc_persona_fisica(
       nombre="Juan",
       apellido_paterno="Pérez",
       apellido_materno="López",
       fecha_nacimiento="1990-01-15"
   )
   print(generated_rfc)  # "PELJ900115XXX"

CURP Generation and Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.validators import curp
   
   # Generate CURP
   curp_code = curp.generate_curp(
       nombre="Juan",
       apellido_paterno="Pérez",
       apellido_materno="García",
       fecha_nacimiento="1990-05-15",
       sexo="H",              # H=Male, M=Female
       estado="Jalisco"       # State name or 2-letter code
   )
   print(curp_code)  # "PEGJ900515HJCRRN09"
   
   # Validate CURP
   is_valid = curp.validate_curp("PEGJ900515HJCRRN09")
   print(is_valid)  # True
   
   # Extract information
   info = curp.get_curp_info("PEGJ900515HJCRRN09")
   print(info['fecha_nacimiento'])  # "1990-05-15"
   print(info['sexo'])              # "H"
   print(info['estado'])            # "Jalisco"

CLABE Validation
^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.validators import clabe
   
   # Validate bank account
   is_valid = clabe.validate_clabe("002010077777777771")
   print(is_valid)  # True
   
   # Extract bank code
   bank_code = clabe.get_bank_code("002010077777777771")
   print(bank_code)  # "002"

Working with Catalogs
~~~~~~~~~~~~~~~~~~~~~

Postal Codes (SEPOMEX)
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.sepomex import CodigosPostales
   
   # Search by postal code
   results = CodigosPostales.get_by_cp("06700")
   for cp in results:
       print(f"{cp['asentamiento']}, {cp['municipio']}")
       # Output: "Roma Norte, Cuauhtémoc"
   
   # Validate postal code
   is_valid = CodigosPostales.is_valid("06700")
   print(is_valid)  # True
   
   # Get all postal codes for a state
   jalisco_codes = CodigosPostales.get_by_estado("Jalisco")
   print(f"{len(jalisco_codes):,} postal codes")  # 6,412 postal codes

Municipalities (INEGI)
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.inegi import MunicipiosCatalog
   
   # Get municipality by code
   municipio = MunicipiosCatalog.get_municipio("09015")
   print(municipio['nom_municipio'])      # "Cuauhtémoc"
   print(municipio['poblacion_total'])    # 545,884
   
   # Get all municipalities in a state
   jalisco_muns = MunicipiosCatalog.get_by_entidad("14")
   print(f"{len(jalisco_muns)} municipalities")  # 125 municipalities

Localities with GPS (INEGI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.inegi import LocalidadesCatalog
   
   # Search by coordinates (geographic search)
   nearby = LocalidadesCatalog.get_by_coordinates(
       lat=19.4326,      # Mexico City latitude
       lon=-99.1332,     # Mexico City longitude
       radio_km=50       # 50 km radius
   )
   
   for locality in nearby[:5]:
       print(f"{locality['nom_localidad']}: {locality['distancia_km']} km away")
       print(f"  Population: {locality['poblacion_total']:,}")
   
   # Search by population
   large_cities = LocalidadesCatalog.get_by_population_range(min_pob=100000)
   print(f"{len(large_cities)} cities with 100K+ inhabitants")  # 145

SAT Tax Catalogs (CFDI 4.0)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.sat.cfdi_4 import (
       RegimenFiscalCatalog,
       UsoCFDICatalog,
       FormaPagoCatalog
   )
   
   # Get tax regime
   regimen = RegimenFiscalCatalog.get_regimen("605")
   print(regimen['description'])
   # "Sueldos y Salarios e Ingresos Asimilados a Salarios"
   
   # Validate CFDI use
   is_valid = UsoCFDICatalog.is_valid("G03")
   print(is_valid)  # True
   
   # Get all payment methods
   payment_methods = FormaPagoCatalog.get_all()
   print(f"{len(payment_methods)} payment methods")

Complete Example: Address Validation
-------------------------------------

Here's a complete example that validates a Mexican address:

.. code-block:: python

   from catalogmx.catalogs.sepomex import CodigosPostales
   from catalogmx.catalogs.inegi import MunicipiosCatalog, LocalidadesCatalog
   
   def validate_complete_address(postal_code, municipality, locality=None):
       """
       Validate a complete Mexican address.
       
       Args:
           postal_code: 5-digit postal code
           municipality: Municipality name
           locality: Optional locality name
       
       Returns:
           tuple: (is_valid, details or error_message)
       """
       # Step 1: Validate postal code exists
       if not CodigosPostales.is_valid(postal_code):
           return False, f"Invalid postal code: {postal_code}"
       
       # Step 2: Get postal code information
       cp_data = CodigosPostales.get_by_cp(postal_code)
       if not cp_data:
           return False, f"Postal code not found: {postal_code}"
       
       cp_info = cp_data[0]
       
       # Step 3: Verify municipality matches
       if municipality.lower() not in cp_info['municipio'].lower():
           return False, (
               f"Postal code {postal_code} belongs to {cp_info['municipio']}, "
               f"not {municipality}"
           )
       
       # Step 4: Optional locality verification
       if locality:
           localities = LocalidadesCatalog.search_by_name(locality)
           if not localities:
               return False, f"Locality not found: {locality}"
       
       # Return validated address information
       return True, {
           'postal_code': cp_info['cp'],
           'settlement': cp_info['asentamiento'],
           'municipality': cp_info['municipio'],
           'state': cp_info['estado']
       }
   
   # Usage
   valid, result = validate_complete_address("06700", "Cuauhtémoc")
   if valid:
       print("Valid address:")
       print(f"  {result['settlement']}")
       print(f"  {result['municipality']}, {result['state']}")
       print(f"  CP: {result['postal_code']}")
   else:
       print(f"Invalid address: {result}")

Next Steps
----------

* :doc:`usage` - Detailed usage examples
* :doc:`api/validators` - Complete validator API reference
* :doc:`api/catalogs-sat` - SAT catalogs API reference
* :doc:`api/catalogs-inegi` - INEGI catalogs API reference
* :doc:`guides/developers-guide` - Contributing and development

