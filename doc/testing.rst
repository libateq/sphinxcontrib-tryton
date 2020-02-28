Testing
=======

To run the test suite you need to have version 1.0.1 or later of
``sphinx-testing`` installed and the ``install_requires`` packages listed in
the ``setup.py`` file.

The full test suite can be run from the top level of the package by executing:

.. code-block:: bash

    python3 -m pytest --verbose tests/

Alternatively just some of the tests can be run by using unittest, for example:

.. code-block:: bash

    python3 -m unittest tests.test_sao


Client Tests
------------

The client tests, in addition to the requirements for running the client, also
require a running server to be able to work.

For the tests the client options should be specified in environment variables.
These environment variables should be named ``TEST_SPHINXCONTRIB_`` followed by
the option name in uppercase, for example:
``TEST_SPHINXCONTRIB_SAO_BROWSER``.
