SAT Catalogs API Reference
===========================

Module: ``catalogmx.catalogs.sat``

Overview
--------

SAT (Servicio de Administración Tributaria) catalog collection includes:

* **CFDI 4.0**: 9 core catalogs for electronic invoicing
* **Comercio Exterior 2.0**: 8 catalogs for foreign trade
* **Carta Porte 3.0**: 7 catalogs for transportation
* **Nómina 1.2**: 7 catalogs for payroll

CFDI 4.0 Catalogs
-----------------

RegimenFiscalCatalog
~~~~~~~~~~~~~~~~~~~~

Tax regimes catalog (c_RegimenFiscal).

**Statistics**: 26 tax regimes

.. code-block:: python

   from catalogmx.catalogs.sat.cfdi_4 import RegimenFiscalCatalog
   
   # Get specific regime
   regimen = RegimenFiscalCatalog.get_regimen("605")
   print(regimen['description'])
   # "Sueldos y Salarios e Ingresos Asimilados a Salarios"
   
   # Filter by person type
   regimenes_fisica = RegimenFiscalCatalog.get_all_persona_fisica()
   regimenes_moral = RegimenFiscalCatalog.get_all_persona_moral()
   
   # Validate
   is_valid = RegimenFiscalCatalog.is_valid("605")

UsoCFDICatalog
~~~~~~~~~~~~~~

CFDI use codes catalog (c_UsoCFDI).

**Statistics**: 25 CFDI uses

.. code-block:: python

   from catalogmx.catalogs.sat.cfdi_4 import UsoCFDICatalog
   
   uso = UsoCFDICatalog.get_uso("G03")
   print(uso['description'])  # "Gastos en general"
   
   is_valid = UsoCFDICatalog.is_valid("G03")

FormaPagoCatalog
~~~~~~~~~~~~~~~~

Payment method catalog (c_FormaPago).

**Statistics**: 18 payment methods

.. code-block:: python

   from catalogmx.catalogs.sat.cfdi_4 import FormaPagoCatalog
   
   forma = FormaPagoCatalog.get_forma("03")
   print(forma['description'])  # "Transferencia electrónica de fondos"

MetodoPagoCatalog
~~~~~~~~~~~~~~~~~

Payment type catalog (c_MetodoPago).

**Statistics**: 2 payment types (PUE, PPD)

.. code-block:: python

   from catalogmx.catalogs.sat.cfdi_4 import MetodoPagoCatalog
   
   metodo = MetodoPagoCatalog.get_metodo("PUE")
   print(metodo['description'])  # "Pago en una sola exhibición"

TipoComprobanteCatalog
~~~~~~~~~~~~~~~~~~~~~~

Receipt type catalog (c_TipoComprobante).

**Statistics**: 5 receipt types

ImpuestoCatalog
~~~~~~~~~~~~~~~

Tax type catalog (c_Impuesto).

**Statistics**: 4 tax types

ExportacionCatalog
~~~~~~~~~~~~~~~~~~

Export codes catalog (c_Exportacion).

**Statistics**: 4 export keys

TipoRelacionCatalog
~~~~~~~~~~~~~~~~~~~

CFDI relationship types catalog (c_TipoRelacion).

**Statistics**: 9 relationship types

ObjetoImpCatalog
~~~~~~~~~~~~~~~~

Tax object codes catalog (c_ObjetoImp).

**Statistics**: 8 tax object codes

Comercio Exterior Catalogs
---------------------------

IncotermsCatalog
~~~~~~~~~~~~~~~~

Incoterms 2020 catalog.

**Statistics**: 11 Incoterms

.. code-block:: python

   from catalogmx.catalogs.sat.comercio_exterior import IncotermsCatalog
   
   incoterm = IncotermsCatalog.get_incoterm("FOB")
   print(incoterm['description'])
   print(f"Valid for: {', '.join(incoterm['valid_transport'])}")

MonedasCatalog
~~~~~~~~~~~~~~

ISO 4217 currency catalog.

**Statistics**: 150 currencies

.. code-block:: python

   from catalogmx.catalogs.sat.comercio_exterior import MonedasCatalog
   
   moneda = MonedasCatalog.get_moneda("USD")
   print(f"{moneda['description']}: {moneda['decimals']} decimals")

PaisesCatalog
~~~~~~~~~~~~~

ISO 3166-1 country catalog.

**Statistics**: 249 countries

ClavePedimentoCatalog
~~~~~~~~~~~~~~~~~~~~~

Customs document keys catalog.

**Statistics**: 42 keys

Carta Porte Catalogs
--------------------

AeropuertosCatalog
~~~~~~~~~~~~~~~~~~

Airport catalog with IATA/ICAO codes.

**Statistics**: 76 airports

.. code-block:: python

   from catalogmx.catalogs.sat.carta_porte import AeropuertosCatalog
   
   airport = AeropuertosCatalog.get_aeropuerto("MEX")
   print(f"{airport['nombre']}")
   print(f"ICAO: {airport['codigo_icao']}")

PuertosMarit imosCatalog
~~~~~~~~~~~~~~~~~~~~~~~~~

Seaport catalog.

**Statistics**: 100 seaports across 4 coasts

CarreterasCatalog
~~~~~~~~~~~~~~~~~

Federal highway catalog (SCT).

**Statistics**: 200 highways

MaterialPeligrosoCatalog
~~~~~~~~~~~~~~~~~~~~~~~~

UN dangerous goods catalog.

**Statistics**: 3,000 materials

Nómina Catalogs
---------------

TipoContratoCatalog
~~~~~~~~~~~~~~~~~~~

Labor contract types catalog.

**Statistics**: 10 contract types

TipoJornadaCatalog
~~~~~~~~~~~~~~~~~~

Work shift types catalog.

**Statistics**: 8 shift types

PeriodicidadPagoCatalog
~~~~~~~~~~~~~~~~~~~~~~~

Payment frequency catalog.

**Statistics**: 10 frequencies

.. code-block:: python

   from catalogmx.catalogs.sat.nomina import PeriodicidadPagoCatalog
   
   periodicidad = PeriodicidadPagoCatalog.get_periodicidad("04")
   print(periodicidad['description'])  # "Semanal"
   print(f"Days: {periodicidad.get('days', 'N/A')}")

RiesgoPuestoCatalog
~~~~~~~~~~~~~~~~~~~

IMSS risk level catalog.

**Statistics**: 5 risk levels (I-V)

.. code-block:: python

   from catalogmx.catalogs.sat.nomina import RiesgoPuestoCatalog
   
   riesgo = RiesgoPuestoCatalog.get_riesgo("I")
   print(f"Risk level {riesgo['code']}: {riesgo['description']}")

Common Patterns
---------------

All SAT catalogs follow a consistent pattern:

.. code-block:: python

   from catalogmx.catalogs.sat.cfdi_4 import SomeCatalog
   
   # Get specific item by code
   item = SomeCatalog.get_item(code)
   
   # Validate code exists
   is_valid = SomeCatalog.is_valid(code)
   
   # Get all items
   all_items = SomeCatalog.get_all()

Complete CFDI Validation Example
---------------------------------

.. code-block:: python

   from catalogmx.validators import rfc
   from catalogmx.catalogs.sat.cfdi_4 import (
       RegimenFiscalCatalog,
       UsoCFDICatalog,
       FormaPagoCatalog,
       MetodoPagoCatalog,
       TipoComprobanteCatalog
   )
   
   def validate_cfdi_complete(cfdi_data):
       """Validate all CFDI fields against catalogs"""
       
       errors = []
       warnings = []
       
       # Validate RFCs
       if not rfc.validate_rfc(cfdi_data['rfc_emisor']):
           errors.append("Invalid issuer RFC")
       
       if not rfc.validate_rfc(cfdi_data['rfc_receptor']):
           errors.append("Invalid receiver RFC")
       
       # Validate against catalogs
       if not RegimenFiscalCatalog.is_valid(cfdi_data['regimen_fiscal']):
           errors.append(f"Invalid tax regime: {cfdi_data['regimen_fiscal']}")
       
       if not UsoCFDICatalog.is_valid(cfdi_data['uso_cfdi']):
           errors.append(f"Invalid CFDI use: {cfdi_data['uso_cfdi']}")
       
       if not FormaPagoCatalog.is_valid(cfdi_data['forma_pago']):
           errors.append(f"Invalid payment method: {cfdi_data['forma_pago']}")
       
       if not MetodoPagoCatalog.is_valid(cfdi_data['metodo_pago']):
           errors.append(f"Invalid payment type: {cfdi_data['metodo_pago']}")
       
       if not TipoComprobanteCatalog.is_valid(cfdi_data['tipo_comprobante']):
           errors.append(f"Invalid receipt type: {cfdi_data['tipo_comprobante']}")
       
       # Cross-validate regime and use
       regimen = RegimenFiscalCatalog.get_regimen(cfdi_data['regimen_fiscal'])
       if regimen:
           rfc_type = rfc.detect_rfc_type(cfdi_data['rfc_emisor'])
           if rfc_type == 'FISICA' and not regimen.get('fisica', False):
               warnings.append(f"Regime {cfdi_data['regimen_fiscal']} not valid for Persona Física")
           elif rfc_type == 'MORAL' and not regimen.get('moral', False):
               warnings.append(f"Regime {cfdi_data['regimen_fiscal']} not valid for Persona Moral")
       
       return {
           'valid': len(errors) == 0,
           'errors': errors,
           'warnings': warnings
       }

See Also
--------

* :doc:`validators` - Validator API reference
* :doc:`catalogs-inegi` - INEGI catalogs API
* :doc:`catalogs-sepomex` - SEPOMEX catalogs API
* :doc:`catalogs-banxico` - Banxico catalogs API

