SEPOMEX Catalogs API Reference
===============================

Module: ``catalogmx.catalogs.sepomex``

CodigosPostales
---------------

Class for accessing Mexican postal codes (Códigos Postales).

**Statistics**:
  * Total records: 157,252
  * Coverage: 32 states (100%)
  * Size: 43.53 MB
  * Updated: November 2025

Methods
~~~~~~~

get_by_cp(cp)
^^^^^^^^^^^^^

Get all settlements for a postal code.

**Parameters**:
  * ``cp`` (str) - Postal code (5 digits)

**Returns**:
  * list[dict] - List of settlements with this postal code

**Example**:

.. code-block:: python

   from catalogmx.catalogs.sepomex import CodigosPostales
   
   results = CodigosPostales.get_by_cp("06700")
   for item in results:
       print(f"{item['asentamiento']}, {item['municipio']}")
       # Output: "Roma Norte, Cuauhtémoc"

is_valid(cp)
^^^^^^^^^^^^

Check if a postal code exists.

**Parameters**:
  * ``cp`` (str) - Postal code (5 digits)

**Returns**:
  * bool - True if exists, False otherwise

**Example**:

.. code-block:: python

   exists = CodigosPostales.is_valid("06700")
   # Returns: True

get_by_estado(estado)
^^^^^^^^^^^^^^^^^^^^^

Get all postal codes for a state.

**Parameters**:
  * ``estado`` (str) - State name (e.g., "Jalisco", "Ciudad de México")

**Returns**:
  * list[dict] - List of postal code records for the state

**Example**:

.. code-block:: python

   jalisco_cps = CodigosPostales.get_by_estado("Jalisco")
   print(f"{len(jalisco_cps):,} postal codes")
   # Output: "6,412 postal codes"

get_all()
^^^^^^^^^

Get all postal codes.

**Returns**:
  * list[dict] - Complete list of all 157,252 postal codes

**Warning**: This method loads all records into memory (~43 MB). Use with caution.

**Example**:

.. code-block:: python

   all_codes = CodigosPostales.get_all()
   print(f"Total: {len(all_codes):,}")
   # Output: "Total: 157,252"

get_municipio(cp)
^^^^^^^^^^^^^^^^^

Get the municipality name for a postal code.

**Parameters**:
  * ``cp`` (str) - Postal code (5 digits)

**Returns**:
  * str or None - Municipality name or None if not found

**Example**:

.. code-block:: python

   municipality = CodigosPostales.get_municipio("06700")
   # Returns: "Cuauhtémoc"

get_estado(cp)
^^^^^^^^^^^^^^

Get the state name for a postal code.

**Parameters**:
  * ``cp`` (str) - Postal code (5 digits)

**Returns**:
  * str or None - State name or None if not found

**Example**:

.. code-block:: python

   state = CodigosPostales.get_estado("06700")
   # Returns: "Ciudad de México"

Data Structure
~~~~~~~~~~~~~~

Each postal code record contains:

.. code-block:: python

   {
       'cp': '06700',                      # Postal code (5 digits)
       'asentamiento': 'Roma Norte',       # Settlement name
       'tipo_asentamiento': 'Colonia',     # Settlement type
       'municipio': 'Cuauhtémoc',          # Municipality
       'estado': 'Ciudad de México',       # State
       'ciudad': 'Ciudad de México',       # City (optional)
       'codigo_estado': '09',              # State code (2 digits)
       'codigo_municipio': '015',          # Municipality code (3 digits)
       'zona': 'Urbano'                    # Zone: Urbano/Rural
   }

Performance Notes
~~~~~~~~~~~~~~~~~

**First Access**: ~20-50ms (loads JSON file into memory)

**Subsequent Access**: <1ms (data cached in class variable)

**Memory Usage**: ~50 MB when loaded

For better performance with large datasets, consider the SQLite implementation (available in v0.4.0).

Examples
--------

Basic Search
~~~~~~~~~~~~

.. code-block:: python

   from catalogmx.catalogs.sepomex import CodigosPostales
   
   # Search by postal code
   results = CodigosPostales.get_by_cp("06700")
   
   if results:
       cp_data = results[0]
       print(f"Settlement: {cp_data['asentamiento']}")
       print(f"Municipality: {cp_data['municipio']}")
       print(f"State: {cp_data['estado']}")

State-wide Search
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get all postal codes in Jalisco
   jalisco = CodigosPostales.get_by_estado("Jalisco")
   
   # Count by municipality
   by_municipality = {}
   for cp in jalisco:
       mun = cp['municipio']
       by_municipality[mun] = by_municipality.get(mun, 0) + 1
   
   # Show top 5 municipalities
   sorted_muns = sorted(by_municipality.items(), key=lambda x: x[1], reverse=True)
   for mun, count in sorted_muns[:5]:
       print(f"{mun}: {count} postal codes")

Address Validation
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def validate_postal_address(cp, municipality_name):
       """Validate that postal code belongs to municipality"""
       
       if not CodigosPostales.is_valid(cp):
           return False, "Invalid postal code"
       
       cp_data = CodigosPostales.get_by_cp(cp)[0]
       
       if municipality_name.lower() not in cp_data['municipio'].lower():
           return False, f"CP {cp} does not belong to {municipality_name}"
       
       return True, cp_data
   
   # Usage
   valid, result = validate_postal_address("06700", "Cuauhtémoc")
   if valid:
       print(f"Valid address in {result['estado']}")

See Also
--------

* :doc:`catalogs-inegi` - INEGI catalogs (municipalities, localities)
* :doc:`catalogs-sat` - SAT tax catalogs
* :doc:`../usage` - More usage examples
* :doc:`../guides/cp-locality-linking` - Linking postal codes with localities

