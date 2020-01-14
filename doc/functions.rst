Functions
---------

The *sphinxcontrib-tryton* extension provides a few useful functions that are
intended to help when creating Tryton documentation.

.. py:function:: sphinxcontrib.tryton.inherit_modules(app, config)

    Returns a list of names of activated modules from a ``trytond`` server.
    The module names are returned in dependency order.  This means that a
    module will always appear in the list after all the modules that it
    depends upon.  This function can be imported as the *inherit_modules*
    option for the sphinxcontrib-inherit_ extension.

    .. code:: python3

        import from sphinxcontrib.tryton import inherit_modules

.. py:function:: sphinxcontrib.tryton.inherit_installed_modules(app, config)

    Returns a list of names of all the modules installed on a ``trytond``
    server. The module names are returned in dependency order.  This means
    that a module will always appear in the list after all the modules that it
    depends upon.  This function can be imported as the *inherit_modules*
    option for the sphinxcontrib-inherit_ extension.

    .. code:: python3

        import from sphinxcontrib.tryton import inherit_installed_modules as inherit_modules

.. _sphinxcontrib-inherit: https://bitbucket.org/libateq/sphinxcontrib-inherit
