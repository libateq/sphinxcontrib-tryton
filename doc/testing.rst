Testing
=======

The full test suite can be run from the top level of the package by executing:

.. code-block:: bash

    python3 setup.py test

Alternatively just some of the tests can be run by using unittest, for example:

.. code-block:: bash

    python3 -m unittest test.test_sao


Client Tests
------------

The client tests, in addition to the requirements for running the client, also
require a running server to be able to work.

For the tests the client options should be specified in environment variables.
These environment variables should be named ``TEST_SPHINXCONTRIB_`` followed by
the option name in uppercase, for example:
``TEST_SPHINXCONTRIB_SAO_BROWSER``.
