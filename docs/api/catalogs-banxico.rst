Banxico Catalogs API Reference
===============================

Module: ``catalogmx.catalogs.banxico``

Overview
--------

Banxico (Banco de México) provides the official catalog of financial institutions operating in Mexico.

**Statistics**:
  * Total institutions: 110
  * SPEI participants: ~90
  * Updated: 2025

BankCatalog
-----------

Catalog of Mexican financial institutions participating in SPEI (Sistema de Pagos Electrónicos Interbancarios).

Methods
~~~~~~~

get_all_banks()
^^^^^^^^^^^^^^^

Get all financial institutions.

**Returns**:
  * list[dict] - List of all 110 banks

**Example**:

.. code-block:: python

   from catalogmx.catalogs.banxico import BankCatalog
   
   all_banks = BankCatalog.get_all_banks()
   print(f"Total institutions: {len(all_banks)}")  # 110

get_bank_by_code(code)
^^^^^^^^^^^^^^^^^^^^^^

Get bank information by code.

**Parameters**:
  * ``code`` (str) - Bank code (3 digits)

**Returns**:
  * dict or None - Bank information or None if not found

**Example**:

.. code-block:: python

   bank = BankCatalog.get_bank_by_code("012")
   print(f"Bank: {bank['name']}")  # "BBVA"
   print(f"SPEI: {bank['spei_participant']}")  # True

get_bank_by_name(name)
^^^^^^^^^^^^^^^^^^^^^^

Get bank information by name.

**Parameters**:
  * ``name`` (str) - Bank name (case-insensitive)

**Returns**:
  * dict or None - Bank information or None if not found

**Example**:

.. code-block:: python

   bank = BankCatalog.get_bank_by_name("BBVA")
   print(f"Code: {bank['code']}")  # "012"

is_spei_participant(code)
^^^^^^^^^^^^^^^^^^^^^^^^^

Check if a bank participates in SPEI.

**Parameters**:
  * ``code`` (str) - Bank code (3 digits)

**Returns**:
  * bool - True if participates in SPEI, False otherwise

**Example**:

.. code-block:: python

   participates = BankCatalog.is_spei_participant("012")
   print(participates)  # True

get_spei_banks()
^^^^^^^^^^^^^^^^

Get all banks that participate in SPEI.

**Returns**:
  * list[dict] - List of SPEI participant banks

**Example**:

.. code-block:: python

   spei_banks = BankCatalog.get_spei_banks()
   print(f"{len(spei_banks)} banks participate in SPEI")

validate_bank_code(code)
^^^^^^^^^^^^^^^^^^^^^^^^

Validate that a bank code exists.

**Parameters**:
  * ``code`` (str) - Bank code (3 digits)

**Returns**:
  * bool - True if valid, False otherwise

**Example**:

.. code-block:: python

   is_valid = BankCatalog.validate_bank_code("012")
   print(is_valid)  # True

Data Structure
~~~~~~~~~~~~~~

Bank Record Format
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   {
       'code': '012',                    # Bank code (3 digits)
       'name': 'BBVA',                   # Bank name
       'short_name': 'BBVA',             # Short name
       'spei_participant': True,         # SPEI participation
       'institution_type': 'BANCA'       # Institution type
   }

Integration with CLABE Validator
---------------------------------

The BankCatalog integrates seamlessly with the CLABE validator:

.. code-block:: python

   from catalogmx.validators import clabe
   from catalogmx.catalogs.banxico import BankCatalog
   
   def validate_clabe_with_bank_info(clabe_code):
       """Validate CLABE and get bank information"""
       
       # Validate CLABE
       if not clabe.validate_clabe(clabe_code):
           return False, "Invalid CLABE"
       
       # Extract bank code
       bank_code = clabe.get_bank_code(clabe_code)
       
       # Get bank information
       bank = BankCatalog.get_bank_by_code(bank_code)
       if not bank:
           return False, f"Unknown bank code: {bank_code}"
       
       # Check SPEI participation
       if not bank['spei_participant']:
           return True, {
               'valid': True,
               'bank': bank['name'],
               'warning': 'Bank does not participate in SPEI'
           }
       
       return True, {
           'valid': True,
           'bank': bank['name'],
           'bank_code': bank_code,
           'branch_code': clabe.get_branch_code(clabe_code),
           'account': clabe.get_account_number(clabe_code),
           'spei_enabled': True
       }
   
   # Usage
   valid, result = validate_clabe_with_bank_info("002010077777777771")
   if valid:
       print(f"Bank: {result['bank']}")
       print(f"SPEI: {'Yes' if result.get('spei_enabled') else 'No'}")

Examples
--------

List All Banks
~~~~~~~~~~~~~~

.. code-block:: python

   from catalogmx.catalogs.banxico import BankCatalog
   
   banks = BankCatalog.get_all_banks()
   
   for bank in banks:
       spei_status = "SPEI" if bank['spei_participant'] else "No SPEI"
       print(f"{bank['code']}: {bank['name']} [{spei_status}]")

Find SPEI-Compatible Banks
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   spei_banks = BankCatalog.get_spei_banks()
   
   print(f"Banks with SPEI support: {len(spei_banks)}")
   
   for bank in spei_banks[:10]:
       print(f"  {bank['name']} (code: {bank['code']})")

Validate Bank Before Transfer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def can_transfer_spei(clabe_code):
       """Check if a CLABE can receive SPEI transfers"""
       
       if not clabe.validate_clabe(clabe_code):
           return False, "Invalid CLABE"
       
       bank_code = clabe.get_bank_code(clabe_code)
       
       if not BankCatalog.is_spei_participant(bank_code):
           bank = BankCatalog.get_bank_by_code(bank_code)
           return False, f"{bank['name']} does not participate in SPEI"
       
       return True, "Can receive SPEI transfers"
   
   # Usage
   can_transfer, message = can_transfer_spei("002010077777777771")
   print(message)

See Also
--------

* :doc:`validators` - CLABE validator documentation
* :doc:`catalogs-sat` - SAT tax catalogs
* :doc:`catalogs-inegi` - INEGI geographic catalogs
* :doc:`../usage` - More usage examples

