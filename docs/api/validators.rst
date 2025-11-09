Validators API Reference
========================

This page documents the API for all validators included in catalogmx.

RFC Validator
-------------

Module: ``catalogmx.validators.rfc``

Functions
~~~~~~~~~

validate_rfc(rfc_code)
^^^^^^^^^^^^^^^^^^^^^^

Validates an RFC code (Registro Federal de Contribuyentes).

**Parameters**:
  * ``rfc_code`` (str) - The RFC code to validate (12 or 13 characters)

**Returns**:
  * bool - True if valid, False otherwise

**Example**:

.. code-block:: python

   from catalogmx.validators import rfc
   
   result = rfc.validate_rfc("XAXX010101000")
   # Returns: True

generate_rfc_persona_fisica(nombre, apellido_paterno, apellido_materno, fecha_nacimiento)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generates RFC for a natural person (Persona Física).

**Parameters**:
  * ``nombre`` (str) - First name
  * ``apellido_paterno`` (str) - Paternal surname
  * ``apellido_materno`` (str) - Maternal surname  
  * ``fecha_nacimiento`` (str or date) - Birth date in format "YYYY-MM-DD"

**Returns**:
  * str - Generated RFC code (13 characters)

**Example**:

.. code-block:: python

   rfc_code = rfc.generate_rfc_persona_fisica(
       nombre="Juan",
       apellido_paterno="Pérez",
       apellido_materno="López",
       fecha_nacimiento="1990-01-15"
   )
   # Returns: "PELJ900115XXX"

generate_rfc_persona_moral(razon_social, fecha_constitucion)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generates RFC for a legal entity (Persona Moral).

**Parameters**:
  * ``razon_social`` (str) - Company legal name
  * ``fecha_constitucion`` (str or date) - Constitution date in format "YYYY-MM-DD"

**Returns**:
  * str - Generated RFC code (12 characters)

**Example**:

.. code-block:: python

   rfc_code = rfc.generate_rfc_persona_moral(
       razon_social="Tecnología Avanzada S.A. de C.V.",
       fecha_constitucion="2020-03-15"
   )
   # Returns: "TAV200315XXX"

get_rfc_info(rfc_code)
^^^^^^^^^^^^^^^^^^^^^^

Extracts information from an RFC code.

**Parameters**:
  * ``rfc_code`` (str) - The RFC code

**Returns**:
  * dict or None - Dictionary with RFC information or None if invalid

**Example**:

.. code-block:: python

   info = rfc.get_rfc_info("PELJ900115XXX")
   # Returns: {
   #   'tipo': 'FISICA',
   #   'fecha_nacimiento': '1990-01-15',
   #   'homoclave': 'XXX'
   # }

detect_rfc_type(rfc_code)
^^^^^^^^^^^^^^^^^^^^^^^^^

Detects if RFC is for Persona Física or Persona Moral.

**Parameters**:
  * ``rfc_code`` (str) - The RFC code

**Returns**:
  * str - "FISICA" or "MORAL" or None if invalid

**Example**:

.. code-block:: python

   tipo = rfc.detect_rfc_type("XAXX010101000")
   # Returns: "FISICA" or "MORAL"

---

CURP Validator
--------------

Module: ``catalogmx.validators.curp``

Functions
~~~~~~~~~

generate_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado, differentiator=None)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generates a CURP code (Clave Única de Registro de Población) from personal information.

**Parameters**:
  * ``nombre`` (str) - First name(s)
  * ``apellido_paterno`` (str) - Father's surname
  * ``apellido_materno`` (str or None) - Mother's surname (can be None or empty string)
  * ``fecha_nacimiento`` (str or date) - Birth date in format "YYYY-MM-DD" or datetime.date object
  * ``sexo`` (str) - Gender: "H" for male (Hombre), "M" for female (Mujer)
  * ``estado`` (str) - Birth state (full name like "Jalisco" or 2-letter code like "JC")
  * ``differentiator`` (str, optional) - Custom homonymy differentiator (position 17)

**Returns**:
  * str - Generated 18-character CURP code

**Example**:

.. code-block:: python

   from catalogmx.validators import curp
   
   curp_code = curp.generate_curp(
       nombre="Juan",
       apellido_paterno="Pérez",
       apellido_materno="García",
       fecha_nacimiento="1990-05-15",
       sexo="H",
       estado="Jalisco"
   )
   # Returns: "PEGJ900515HJCRRN09"

**Supported States**:

All 32 Mexican states are supported, plus "NE" for foreign-born:

.. code-block:: python

   # By full name
   curp.generate_curp(..., estado="Jalisco")
   curp.generate_curp(..., estado="Ciudad de México")
   curp.generate_curp(..., estado="Nuevo León")
   
   # By 2-letter code
   curp.generate_curp(..., estado="JC")  # Jalisco
   curp.generate_curp(..., estado="DF")  # Ciudad de México
   curp.generate_curp(..., estado="NL")  # Nuevo León
   
   # Foreign-born
   curp.generate_curp(..., estado="Nacido en el Extranjero")
   curp.generate_curp(..., estado="NE")

validate_curp(curp_code, check_digit=True)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Validates a CURP code (Clave Única de Registro de Población).

**Parameters**:
  * ``curp_code`` (str) - The CURP code to validate (18 characters)
  * ``check_digit`` (bool, optional) - Whether to validate the check digit (default: True)

**Returns**:
  * bool - True if valid, False otherwise

**Example**:

.. code-block:: python

   from catalogmx.validators import curp
   
   result = curp.validate_curp("PEGJ900515HJCRRN09")
   # Returns: True
   
   # Without check digit validation (faster)
   result = curp.validate_curp("PEGJ900515HJCRRN09", check_digit=False)

get_curp_info(curp_code)
^^^^^^^^^^^^^^^^^^^^^^^^

Extracts information from a CURP code.

**Parameters**:
  * ``curp_code`` (str) - The CURP code (18 characters)

**Returns**:
  * dict - Dictionary with extracted information

**Example**:

.. code-block:: python

   info = curp.get_curp_info("PEGJ900515HJCRRN09")
   # Returns: {
   #   'fecha_nacimiento': '1990-05-15',
   #   'sexo': 'H',
   #   'estado': 'Jalisco',
   #   'valido': True
   # }

is_valid_curp(curp_code)
^^^^^^^^^^^^^^^^^^^^^^^^

Alias for ``validate_curp`` with check digit validation enabled.

**Parameters**:
  * ``curp_code`` (str) - The CURP code to validate

**Returns**:
  * bool - True if valid, False otherwise

---

CLABE Validator
---------------

Module: ``catalogmx.validators.clabe``

Functions
~~~~~~~~~

validate_clabe(clabe_code)
^^^^^^^^^^^^^^^^^^^^^^^^^^

Validates a CLABE code (Clave Bancaria Estandarizada).

**Parameters**:
  * ``clabe_code`` (str) - The CLABE code to validate (18 digits)

**Returns**:
  * bool - True if valid, False otherwise

**Example**:

.. code-block:: python

   from catalogmx.validators import clabe
   
   result = clabe.validate_clabe("002010077777777771")
   # Returns: True

get_bank_code(clabe_code)
^^^^^^^^^^^^^^^^^^^^^^^^^

Extracts the bank code from a CLABE.

**Parameters**:
  * ``clabe_code`` (str) - The CLABE code (18 digits)

**Returns**:
  * str - Bank code (3 digits)

**Example**:

.. code-block:: python

   bank_code = clabe.get_bank_code("002010077777777771")
   # Returns: "002"

get_branch_code(clabe_code)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extracts the branch code from a CLABE.

**Parameters**:
  * ``clabe_code`` (str) - The CLABE code (18 digits)

**Returns**:
  * str - Branch code (3 digits)

**Example**:

.. code-block:: python

   branch = clabe.get_branch_code("002010077777777771")
   # Returns: "010"

get_account_number(clabe_code)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extracts the account number from a CLABE.

**Parameters**:
  * ``clabe_code`` (str) - The CLABE code (18 digits)

**Returns**:
  * str - Account number (11 digits)

**Example**:

.. code-block:: python

   account = clabe.get_account_number("002010077777777771")
   # Returns: "07777777777"

---

NSS Validator
-------------

Module: ``catalogmx.validators.nss``

Functions
~~~~~~~~~

validate_nss(nss_code)
^^^^^^^^^^^^^^^^^^^^^^

Validates an NSS code (Número de Seguridad Social).

**Parameters**:
  * ``nss_code`` (str) - The NSS code to validate (11 digits)

**Returns**:
  * bool - True if valid, False otherwise

**Example**:

.. code-block:: python

   from catalogmx.validators import nss
   
   result = nss.validate_nss("12345678901")
   # Returns: True or False

get_nss_info(nss_code)
^^^^^^^^^^^^^^^^^^^^^^

Extracts information from an NSS code.

**Parameters**:
  * ``nss_code`` (str) - The NSS code (11 digits)

**Returns**:
  * dict - Dictionary with extracted components

**Example**:

.. code-block:: python

   info = nss.get_nss_info("12345678901")
   # Returns: {
   #   'subdelegacion': '12345',
   #   'año': '67',
   #   'serie': '8901'
   # }

---

Error Handling
--------------

All validators handle invalid input gracefully:

.. code-block:: python

   from catalogmx.validators import rfc
   
   # Invalid input returns False, not exception
   result = rfc.validate_rfc("INVALID")
   print(result)  # False
   
   # Empty string
   result = rfc.validate_rfc("")
   print(result)  # False
   
   # None
   result = rfc.validate_rfc(None)
   print(result)  # False

For functions that extract information, invalid input returns None:

.. code-block:: python

   info = rfc.get_rfc_info("INVALID")
   print(info)  # None

Type Hints
----------

All validators include complete type hints for static type checking:

.. code-block:: python

   from catalogmx.validators import rfc
   
   def process_rfc(code: str) -> bool:
       return rfc.validate_rfc(code)
   
   # mypy and IDEs will validate types automatically

See Also
--------

* :doc:`catalogs-sat` - SAT catalog API reference
* :doc:`catalogs-inegi` - INEGI catalog API reference
* :doc:`catalogs-sepomex` - SEPOMEX catalog API reference
* :doc:`../usage` - Usage examples

