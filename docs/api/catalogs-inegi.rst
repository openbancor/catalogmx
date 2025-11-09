INEGI Catalogs API Reference
=============================

Module: ``catalogmx.catalogs.inegi``

Overview
--------

INEGI (Instituto Nacional de Estadística y Geografía) provides official geographic and demographic data for Mexico.

catalogmx includes three INEGI catalogs:
  * **MunicipiosCatalog**: 2,478 municipalities with population data
  * **LocalidadesCatalog**: 10,635 localities with GPS coordinates (1,000+ inhabitants)
  * **StatesCatalog**: 32 Mexican states

MunicipiosCatalog
-----------------

Complete catalog of Mexican municipalities with Census 2020 data.

**Statistics**:
  * Total records: 2,478
  * Population: 126,014,024 (100% coverage)
  * Size: 0.98 MB
  * Updated: October 2025

Methods
~~~~~~~

get_municipio(cve_completa)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get municipality by complete code.

**Parameters**:
  * ``cve_completa`` (str) - Complete municipality code (5 digits: state+municipality)

**Returns**:
  * dict or None - Municipality data or None if not found

**Example**:

.. code-block:: python

   from catalogmx.catalogs.inegi import MunicipiosCatalog
   
   municipio = MunicipiosCatalog.get_municipio("09015")
   print(municipio)
   # Returns: {
   #   'cve_entidad': '09',
   #   'nom_entidad': 'Ciudad de México',
   #   'cve_municipio': '015',
   #   'nom_municipio': 'Cuauhtémoc',
   #   'cve_completa': '09015',
   #   'poblacion_total': 545884,
   #   'viviendas_habitadas': 161915
   # }

get_by_entidad(cve_entidad)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get all municipalities in a state.

**Parameters**:
  * ``cve_entidad`` (str) - State code (2 digits)

**Returns**:
  * list[dict] - List of municipalities in the state

**Example**:

.. code-block:: python

   jalisco_muns = MunicipiosCatalog.get_by_entidad("14")
   print(f"{len(jalisco_muns)} municipalities")  # 125

is_valid(cve_completa)
^^^^^^^^^^^^^^^^^^^^^^

Check if a municipality code exists.

**Parameters**:
  * ``cve_completa`` (str) - Complete municipality code

**Returns**:
  * bool - True if exists, False otherwise

get_all()
^^^^^^^^^

Get all municipalities.

**Returns**:
  * list[dict] - All 2,478 municipalities

---

LocalidadesCatalog
------------------

Catalog of localities with 1,000+ inhabitants, including GPS coordinates.

**Statistics**:
  * Total records: 10,635
  * Population: 108,739,262 (86% coverage)
  * Urban: 4,454 localities
  * Rural: 6,181 localities
  * Size: 5.22 MB
  * Updated: October 2025

Methods
~~~~~~~

get_localidad(cvegeo)
^^^^^^^^^^^^^^^^^^^^^

Get locality by unique geostatistical code.

**Parameters**:
  * ``cvegeo`` (str) - Geostatistical code (9 digits)

**Returns**:
  * dict or None - Locality data or None if not found

**Example**:

.. code-block:: python

   from catalogmx.catalogs.inegi import LocalidadesCatalog
   
   loc = LocalidadesCatalog.get_localidad("010010001")
   print(f"{loc['nom_localidad']}: {loc['poblacion_total']:,} inhabitants")

get_by_coordinates(lat, lon, radio_km)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Find localities near GPS coordinates (geographic search).

**Parameters**:
  * ``lat`` (float) - Latitude in decimal degrees
  * ``lon`` (float) - Longitude in decimal degrees
  * ``radio_km`` (float) - Search radius in kilometers

**Returns**:
  * list[dict] - Localities within radius, sorted by distance (includes ``distancia_km`` field)

**Example**:

.. code-block:: python

   # Find localities near Mexico City
   nearby = LocalidadesCatalog.get_by_coordinates(
       lat=19.4326,
       lon=-99.1332,
       radio_km=50
   )
   
   for loc in nearby[:5]:
       print(f"{loc['nom_localidad']}: {loc['distancia_km']} km")

get_by_municipio(cve_municipio)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get all localities in a municipality.

**Parameters**:
  * ``cve_municipio`` (str) - Municipality code (3 digits)

**Returns**:
  * list[dict] - Localities in the municipality

get_by_entidad(cve_entidad)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get all localities in a state.

**Parameters**:
  * ``cve_entidad`` (str) - State code (2 digits)

**Returns**:
  * list[dict] - Localities in the state

search_by_name(nombre)
^^^^^^^^^^^^^^^^^^^^^^

Search localities by name (partial, case-insensitive).

**Parameters**:
  * ``nombre`` (str) - Name or partial name to search

**Returns**:
  * list[dict] - Matching localities

**Example**:

.. code-block:: python

   results = LocalidadesCatalog.search_by_name("Guadalajara")
   for loc in results:
       print(f"{loc['nom_localidad']}, {loc['nom_entidad']}")

get_by_population_range(min_pob, max_pob=None)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get localities within a population range.

**Parameters**:
  * ``min_pob`` (int) - Minimum population
  * ``max_pob`` (int, optional) - Maximum population (None for no limit)

**Returns**:
  * list[dict] - Localities in the range

**Example**:

.. code-block:: python

   # Large cities (100K+ inhabitants)
   large = LocalidadesCatalog.get_by_population_range(100000)
   print(f"{len(large)} large cities")  # 145
   
   # Medium cities (10K-100K)
   medium = LocalidadesCatalog.get_by_population_range(10000, 100000)
   print(f"{len(medium)} medium cities")

get_urbanas()
^^^^^^^^^^^^^

Get only urban localities.

**Returns**:
  * list[dict] - Urban localities (4,454 records)

get_rurales()
^^^^^^^^^^^^^

Get only rural localities.

**Returns**:
  * list[dict] - Rural localities (6,181 records)

is_valid(cvegeo)
^^^^^^^^^^^^^^^^

Check if a geostatistical code exists.

**Parameters**:
  * ``cvegeo`` (str) - Geostatistical code

**Returns**:
  * bool - True if exists, False otherwise

get_all()
^^^^^^^^^

Get all localities.

**Returns**:
  * list[dict] - All 10,635 localities

Data Structure
~~~~~~~~~~~~~~

Locality Record Format
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   {
       'cvegeo': '010010001',                # Unique geostatistical code
       'cve_entidad': '01',                  # State code
       'nom_entidad': 'Aguascalientes',      # State name
       'nom_abr_entidad': 'Ags.',           # State abbreviation
       'cve_municipio': '001',               # Municipality code
       'nom_municipio': 'Aguascalientes',    # Municipality name
       'cve_localidad': '0001',              # Locality code
       'nom_localidad': 'Aguascalientes',    # Locality name
       'ambito': 'U',                        # Classification: U=Urban, R=Rural
       'latitud': 21.879822,                 # Latitude (decimal degrees)
       'longitud': -102.296046,              # Longitude (decimal degrees)
       'altitud': 1878,                      # Altitude (meters)
       'poblacion_total': 863893,            # Total population
       'poblacion_masculina': 419168,        # Male population
       'poblacion_femenina': 444725,         # Female population
       'viviendas_habitadas': 246259         # Inhabited dwellings
   }

Performance Notes
~~~~~~~~~~~~~~~~~

**First Access**: ~30-50ms (loads JSON file)

**Subsequent Access**: <1ms for indexed lookups

**Geographic Search**: ~10-50ms depending on radius and result count

**Memory Usage**: ~6 MB when loaded

For geographic queries on very large datasets, consider the SQLite implementation (available in v0.4.0).

Examples
--------

Find Localities Near a Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from catalogmx.catalogs.inegi import LocalidadesCatalog
   
   # Find localities within 20km of Mexico City center
   nearby = LocalidadesCatalog.get_by_coordinates(
       lat=19.4326,
       lon=-99.1332,
       radio_km=20
   )
   
   print(f"Found {len(nearby)} localities")
   
   for loc in nearby[:10]:
       print(f"{loc['nom_localidad']}: {loc['distancia_km']:.1f} km")
       print(f"  Population: {loc['poblacion_total']:,}")
       print(f"  Type: {'Urban' if loc['ambito']=='U' else 'Rural'}")

Demographic Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Analyze population distribution in Jalisco
   jalisco_locs = LocalidadesCatalog.get_by_entidad("14")
   
   total_pop = sum(loc['poblacion_total'] for loc in jalisco_locs)
   urban_locs = [loc for loc in jalisco_locs if loc['ambito'] == 'U']
   urban_pop = sum(loc['poblacion_total'] for loc in urban_locs)
   
   print(f"Total localities: {len(jalisco_locs)}")
   print(f"Total population: {total_pop:,}")
   print(f"Urban population: {urban_pop:,} ({urban_pop/total_pop*100:.1f}%)")

Find Largest Cities
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get top 10 largest cities
   all_locs = LocalidadesCatalog.get_all()
   largest = sorted(all_locs, key=lambda x: x['poblacion_total'], reverse=True)[:10]
   
   for i, loc in enumerate(largest, 1):
       print(f"{i}. {loc['nom_localidad']}, {loc['nom_entidad']}")
       print(f"   Population: {loc['poblacion_total']:,}")

See Also
--------

* :doc:`catalogs-sepomex` - Postal codes API
* :doc:`catalogs-sat` - SAT tax catalogs API
* :doc:`../guides/cp-locality-linking` - Linking strategies
* :doc:`../usage` - More usage examples

