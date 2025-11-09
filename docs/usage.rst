Usage Guide
===========

This guide provides detailed usage examples for catalogmx.

Validators
----------

RFC (Registro Federal de Contribuyentes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic Validation
^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.validators import rfc
   
   # Validate existing RFC
   result = rfc.validate_rfc("XAXX010101000")
   print(result)  # True or False

Generate RFC for Persona Física
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   rfc_code = rfc.generate_rfc_persona_fisica(
       nombre="María",
       apellido_paterno="García",
       apellido_materno="Martínez",
       fecha_nacimiento="1985-05-20"
   )
   print(rfc_code)  # "GAMM850520XXX"

Generate RFC for Persona Moral
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   rfc_code = rfc.generate_rfc_persona_moral(
       razon_social="Tecnología Avanzada",
       fecha_constitucion="2020-03-15"
   )
   print(rfc_code)  # "TAV200315XXX"

Extract RFC Information
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   info = rfc.get_rfc_info("PELJ900115XXX")
   print(info)
   # {
   #   'tipo': 'FISICA',
   #   'fecha_nacimiento': '1990-01-15',
   #   'homoclave': 'XXX'
   # }

CURP (Clave Única de Registro de Población)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validation
^^^^^^^^^^

.. code-block:: python

   from catalogmx.validators import curp
   
   is_valid = curp.validate_curp("PELJ900115HDFRPN09")
   print(is_valid)  # True

Extract Information
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   info = curp.get_curp_info("PELJ900115HDFRPN09")
   print(info)
   # {
   #   'fecha_nacimiento': '1990-01-15',
   #   'sexo': 'H',
   #   'estado': 'Hidalgo',
   #   'valido': True
   # }

CLABE (Clave Bancaria Estandarizada)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validation
^^^^^^^^^^

.. code-block:: python

   from catalogmx.validators import clabe
   
   is_valid = clabe.validate_clabe("002010077777777771")
   print(is_valid)  # True

Extract Components
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   bank_code = clabe.get_bank_code("002010077777777771")
   print(bank_code)  # "002"
   
   branch_code = clabe.get_branch_code("002010077777777771")
   print(branch_code)  # "010"
   
   account_number = clabe.get_account_number("002010077777777771")
   print(account_number)  # "07777777777"

Integration with Bank Catalog
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.banxico import BankCatalog
   
   bank_code = clabe.get_bank_code("002010077777777771")
   bank = BankCatalog.get_bank_by_code(bank_code)
   print(bank['name'])  # "Banamex"

NSS (Número de Seguridad Social)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validation
^^^^^^^^^^

.. code-block:: python

   from catalogmx.validators import nss
   
   is_valid = nss.validate_nss("12345678901")
   print(is_valid)  # True or False

Catalogs
--------

SEPOMEX - Postal Codes
~~~~~~~~~~~~~~~~~~~~~~~

Search by Postal Code
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.sepomex import CodigosPostales
   
   results = CodigosPostales.get_by_cp("06700")
   for cp in results:
       print(f"Settlement: {cp['asentamiento']}")
       print(f"Type: {cp['tipo_asentamiento']}")
       print(f"Municipality: {cp['municipio']}")
       print(f"State: {cp['estado']}")

Search by State
^^^^^^^^^^^^^^^

.. code-block:: python

   jalisco_cps = CodigosPostales.get_by_estado("Jalisco")
   print(f"Total postal codes in Jalisco: {len(jalisco_cps):,}")  # 6,412

Get Municipality from Postal Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   municipality = CodigosPostales.get_municipio("06700")
   print(municipality)  # "Cuauhtémoc"
   
   state = CodigosPostales.get_estado("06700")
   print(state)  # "Ciudad de México"

INEGI - Municipalities
~~~~~~~~~~~~~~~~~~~~~~~

Get Municipality Data
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.inegi import MunicipiosCatalog
   
   municipio = MunicipiosCatalog.get_municipio("09015")
   print(f"Name: {municipio['nom_municipio']}")
   print(f"State: {municipio['nom_entidad']}")
   print(f"Population: {municipio['poblacion_total']:,}")
   print(f"Households: {municipio['viviendas_habitadas']:,}")

Get All Municipalities in a State
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   jalisco_municipios = MunicipiosCatalog.get_by_entidad("14")
   print(f"Municipalities in Jalisco: {len(jalisco_municipios)}")  # 125
   
   for mun in jalisco_municipios[:5]:
       print(f"  {mun['nom_municipio']}: {mun['poblacion_total']:,} inhabitants")

INEGI - Localities with GPS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Geographic Search
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.inegi import LocalidadesCatalog
   
   # Find localities near Mexico City
   nearby = LocalidadesCatalog.get_by_coordinates(
       lat=19.4326,
       lon=-99.1332,
       radio_km=50
   )
   
   print(f"Found {len(nearby)} localities within 50km")
   
   for loc in nearby[:10]:
       print(f"{loc['nom_localidad']}: {loc['distancia_km']} km")
       print(f"  Population: {loc['poblacion_total']:,}")
       print(f"  GPS: {loc['latitud']}, {loc['longitud']}")

Search by Name
^^^^^^^^^^^^^^

.. code-block:: python

   results = LocalidadesCatalog.search_by_name("Guadalajara")
   for loc in results:
       print(f"{loc['nom_localidad']}, {loc['nom_municipio']}")
       print(f"  Population: {loc['poblacion_total']:,}")

Filter by Population
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Large cities (100K+ inhabitants)
   large_cities = LocalidadesCatalog.get_by_population_range(min_pob=100000)
   print(f"{len(large_cities)} cities with 100K+ inhabitants")  # 145
   
   # Medium cities (10K-100K inhabitants)
   medium_cities = LocalidadesCatalog.get_by_population_range(
       min_pob=10000,
       max_pob=100000
   )
   print(f"{len(medium_cities)} medium-sized cities")

Urban vs Rural Classification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   urban = LocalidadesCatalog.get_urbanas()
   rural = LocalidadesCatalog.get_rurales()
   
   print(f"Urban localities: {len(urban):,}")    # 4,454
   print(f"Rural localities: {len(rural):,}")    # 6,181

SAT - Tax Catalogs
~~~~~~~~~~~~~~~~~~

Tax Regimes (Régimen Fiscal)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.sat.cfdi_4 import RegimenFiscalCatalog
   
   # Get specific regime
   regimen = RegimenFiscalCatalog.get_regimen("605")
   print(regimen['description'])
   # "Sueldos y Salarios e Ingresos Asimilados a Salarios"
   
   # Filter by person type
   regimenes_pf = RegimenFiscalCatalog.get_all_persona_fisica()
   print(f"Tax regimes for individuals: {len(regimenes_pf)}")

CFDI Use Codes
^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.sat.cfdi_4 import UsoCFDICatalog
   
   uso = UsoCFDICatalog.get_uso("G03")
   print(uso['description'])  # "Gastos en general"
   
   # Validate
   is_valid = UsoCFDICatalog.is_valid("G03")
   print(is_valid)  # True

Banxico - Banks
~~~~~~~~~~~~~~~

Get Bank Information
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from catalogmx.catalogs.banxico import BankCatalog
   
   bank = BankCatalog.get_bank_by_code("012")
   print(f"Bank: {bank['name']}")  # "BBVA"
   
   # SPEI participants
   spei_banks = BankCatalog.get_spei_banks()
   print(f"{len(spei_banks)} banks participate in SPEI")

Advanced Examples
-----------------

Complete CFDI Validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from catalogmx.validators import rfc
   from catalogmx.catalogs.sat.cfdi_4 import (
       RegimenFiscalCatalog,
       UsoCFDICatalog,
       FormaPagoCatalog,
       MetodoPagoCatalog
   )
   
   def validate_cfdi_invoice(data):
       """Validate all CFDI fields"""
       errors = []
       
       # Validate RFC
       if not rfc.validate_rfc(data['rfc_emisor']):
           errors.append("Invalid issuer RFC")
       
       if not rfc.validate_rfc(data['rfc_receptor']):
           errors.append("Invalid receiver RFC")
       
       # Validate catalogs
       if not RegimenFiscalCatalog.is_valid(data['regimen_fiscal']):
           errors.append(f"Invalid tax regime: {data['regimen_fiscal']}")
       
       if not UsoCFDICatalog.is_valid(data['uso_cfdi']):
           errors.append(f"Invalid CFDI use: {data['uso_cfdi']}")
       
       if not FormaPagoCatalog.is_valid(data['forma_pago']):
           errors.append(f"Invalid payment method: {data['forma_pago']}")
       
       if not MetodoPagoCatalog.is_valid(data['metodo_pago']):
           errors.append(f"Invalid payment type: {data['metodo_pago']}")
       
       return len(errors) == 0, errors
   
   # Example usage
   invoice_data = {
       'rfc_emisor': 'XAXX010101000',
       'rfc_receptor': 'XEXX010101000',
       'regimen_fiscal': '605',
       'uso_cfdi': 'G03',
       'forma_pago': '03',
       'metodo_pago': 'PUE'
   }
   
   is_valid, errors = validate_cfdi_invoice(invoice_data)
   if is_valid:
       print("Valid CFDI invoice")
   else:
       print("Validation errors:")
       for error in errors:
           print(f"  - {error}")

Geographic Analysis
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from catalogmx.catalogs.inegi import LocalidadesCatalog
   
   def analyze_region(center_lat, center_lon, radius_km):
       """Analyze demographic data for a geographic region"""
       
       localities = LocalidadesCatalog.get_by_coordinates(
           lat=center_lat,
           lon=center_lon,
           radio_km=radius_km
       )
       
       total_population = sum(loc['poblacion_total'] for loc in localities)
       urban_count = sum(1 for loc in localities if loc['ambito'] == 'U')
       rural_count = len(localities) - urban_count
       
       return {
           'total_localities': len(localities),
           'total_population': total_population,
           'urban_localities': urban_count,
           'rural_localities': rural_count,
           'largest_locality': max(localities, key=lambda x: x['poblacion_total'])
       }
   
   # Analyze area around Guadalajara
   analysis = analyze_region(lat=20.6597, lon=-103.3496, radius_km=100)
   
   print(f"Localities: {analysis['total_localities']}")
   print(f"Population: {analysis['total_population']:,}")
   print(f"Urban: {analysis['urban_localities']}, Rural: {analysis['rural_localities']}")
   print(f"Largest: {analysis['largest_locality']['nom_localidad']}")

Next Steps
----------

* :doc:`api/validators` - Complete validator API reference
* :doc:`api/catalogs-sat` - SAT catalogs detailed documentation
* :doc:`api/catalogs-inegi` - INEGI catalogs detailed documentation
* :doc:`guides/developers-guide` - Development and contribution guide
