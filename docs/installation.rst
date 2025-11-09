Installation
============

Requirements
------------

Python
~~~~~~

* Python 3.10 or higher
* pip package manager

TypeScript/JavaScript
~~~~~~~~~~~~~~~~~~~~~

* Node.js 16 or higher
* npm, yarn, or pnpm

Installing catalogmx
--------------------

Python Installation
~~~~~~~~~~~~~~~~~~~

From PyPI (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^

The easiest way to install catalogmx is via pip:

.. code-block:: bash

   pip install catalogmx

From Source
^^^^^^^^^^^

For development or to get the latest changes:

.. code-block:: bash

   git clone https://github.com/openbancor/catalogmx.git
   cd catalogmx/packages/python
   pip install -e .

With Development Tools
^^^^^^^^^^^^^^^^^^^^^^

To install with development dependencies (pytest, black, ruff, mypy):

.. code-block:: bash

   pip install -e ".[dev]"

With Documentation Tools
^^^^^^^^^^^^^^^^^^^^^^^^

To install with documentation dependencies (sphinx):

.. code-block:: bash

   pip install -e ".[docs]"

All Optional Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install -e ".[all]"

TypeScript Installation
~~~~~~~~~~~~~~~~~~~~~~~

From NPM
^^^^^^^^

.. code-block:: bash

   npm install catalogmx

From Yarn
^^^^^^^^^

.. code-block:: bash

   yarn add catalogmx

From PNPM
^^^^^^^^^

.. code-block:: bash

   pnpm add catalogmx

Verifying Installation
----------------------

Python
~~~~~~

.. code-block:: python

   import catalogmx
   print(catalogmx.__version__)  # Should print "0.3.0"
   
   from catalogmx.validators import rfc
   print(rfc.validate_rfc("XAXX010101000"))  # Should print True

TypeScript
~~~~~~~~~~

.. code-block:: typescript

   import { validateRFC } from 'catalogmx';
   console.log(validateRFC('XAXX010101000'));  // Should print true

Troubleshooting
---------------

Python Version Issues
~~~~~~~~~~~~~~~~~~~~~

If you encounter errors about Python version:

.. code-block:: bash

   # Check your Python version
   python --version  # Should be 3.10 or higher
   
   # If you have multiple Python versions
   python3.10 -m pip install catalogmx
   python3.11 -m pip install catalogmx

Missing Dependencies
~~~~~~~~~~~~~~~~~~~~

If you encounter import errors:

.. code-block:: bash

   # Reinstall with dependencies
   pip install --upgrade --force-reinstall catalogmx

Node.js Version Issues
~~~~~~~~~~~~~~~~~~~~~~

If you encounter errors about Node.js version:

.. code-block:: bash

   # Check your Node.js version
   node --version  # Should be 16 or higher
   
   # Update Node.js via nvm
   nvm install 18
   nvm use 18

Next Steps
----------

* :doc:`quickstart` - Get started with catalogmx
* :doc:`usage` - Detailed usage examples
* :doc:`api/validators` - Validator API reference
* :doc:`api/catalogs-sat` - SAT catalogs API reference
