Configuration
-------------

To use the *sphinxcontrib-tryton* extension it needs to be enabled in your
project's ``conf.py`` file.  This is done by adding it to the list of enabled
extensions.

.. code-block:: python3

    extensions = ['sphinxcontrib.tryton']

Options
^^^^^^^

The *sphinxcontrib-tryton* extension adds some new configuration options that
need to setup correctly to allow the extension to use the Tryton clients and
server so you can get the most out of it's features.

If you have ``trytond`` installed on the local computer then this extension
can be configured to connect directly to it.  It is also possible to configure
this extension to connect to a remote ``trytond`` server using XMLRPC.  You
should only provide connection settings for one of these connection types.

To generate screenshots from the Tryton desktop client you will need the client
installed.  Screenshots from the Tryton web client can also be taken, for this
you will need a web browser supported by Selenium_, and an appropriate
webdriver_ installed.  Connection settings for each client can be specified
separately to those for the server, but the server connection settings will be
used by default.

.. _Selenium: https://docs.seleniumhq.org/
.. _webdriver: https://docs.seleniumhq.org/download/#thirdPartyDrivers

Common Server Connection Options
""""""""""""""""""""""""""""""""

These configuration options are common to both local and remote server
connections.

**trytond_connection_type**
    The type of connection to make to the tryton server.  This must be either
    ``trytond`` for local connections or ``xmlrpc`` for remote connections.
    The default value for this option is ``trytond``.

.. _trytond-user:

**trytond_database**
    The name of the database to connect to on the Tryton server.
    This defaults to ``tryton`` for remote connections and ``:memory:`` for
    local connections.

**trytond_user**
    The login name for the user to connect as, this defaults to '``admin``'.

Local Server Connection Options
"""""""""""""""""""""""""""""""

These connection options are only used when connecting to local trytond
servers.

**trytond_config_file**
    The configuration file that contains the local ``trytond`` server's
    configuration options.  If a value for this option is not provided then
    connection will fallback to using the value from the ``TRYTOND_CONFIG``
    environment variable instead.

    .. note::

        As normal with the Tryton server, the configuration values can be set
        using environment variables instead.  See the `Tryton Documentation`_
        for more details.

        .. _`Tryton Documentation`: https://docs.tryton.org/projects/server/en/latest/topics/configuration.html

**trytond_activate_modules**
    A list of modules that should be activated in a new database.  If this
    option is provided then the database (which must already exist) is
    initialised, and the modules in this list are activated.  No module
    activation will be attempted on databases that were already initialised
    before running Sphinx, so as not to corrupt existing installations.
    Use ``[]`` to initialise a database with no modules.  The default value
    is ``None`` which does not attempt any module activation or database
    initialisation.

Remote Server Connection Options
""""""""""""""""""""""""""""""""

These connection options are only used when connecting to a remote trytond
server.

**trytond_host**
    The hostname of the server that is running the Tryton server.  This value
    is required for remote connections.

**trytond_password**
    The password for the user to connect as.  This value is required for
    remote connections.

**trytond_port**
    The port on which the remote Tryton server can be reached.  This value
    is required for remote connections.

**trytond_ssl_context**
    This is an optional `ssl context`_ that may be required in order to connect
    to the server successfully.

.. _`ssl context`: https://docs.python.org/3/library/ssl.html#ssl-contexts

Desktop Client Options
""""""""""""""""""""""

These are the options that are available for configuring the Tryton desktop
client.

**tryton_database**
    The name of the database that the client should connect to on the Tryton
    server.  If this value is not set then it defaults to the value specified
    by the ``trytond_database`` option.

**tryton_default_size**
    The default size of any images that are captured of the full window.  This
    should be a tuple containing the default width and height in pixels.  The
    default value for this option is ``(1920, 1080)``.

**tryton_force_update**
    A boolean that specifies whether the images in the tryton figure directives
    should be replaced with new screenshots when the documentation is built.
    If this option is not set then if an existing image is available it will be
    used.

**tryton_host**
    The hostname of the server that the client should connect to.  If this
    value is not set then it defaults to the value specified by the
    ``trytond_host`` option.

**tryton_password**
    The password for the user to connect as.  If this value is not set then
    it defaults to the value specified by the ``trytond_password`` option.

**tryton_port**
    The port on the server that the client should connect to.  If this
    value is not set then it defaults to the value specified by the
    ``trytond_port`` option.

**tryton_timeout**
    The amount of time in seconds that must pass before operations on the
    client are assumed to have failed, and so time out.  This defaults to
    ``60`` seconds.

**tryton_user**
    The login name for the user to connect as.  If this value is not set then
    it defaults to the value specified by the ``trytond_user`` option.

Web Client Options
""""""""""""""""""

These are the options that are available for configuring the web browser
based client called Sao.

**sao_browser**
    The name of the browser that is used to run the Sao client.  See the
    ``sphinxcontrib/tryton/sao.py`` file for a list of supported browsers.

**sao_database**
    The name of the database that Sao should connect to on the Tryton server.
    If this value is not set then it defaults to the value specified by the
    ``trytond_database`` option.

**sao_default_size**
    The default size of any images that are captured of the full window.  This
    should be a tuple containing the default width and height in pixels.  The
    default value for this option is ``(1920, 1080)``.

**sao_force_update**
    A boolean that specifies whether the images in the tryton figure directives
    should be replaced with new screenshots when the documentation is built.
    If this option is not set then if an existing image is available it will be
    used.

**sao_host**
    The hostname of the server that Sao is on.  If this value is not set then
    it defaults to the value specified by the ``trytond_host`` option.

**sao_password**
    The password for the user to connect as.  If this value is not set then
    it defaults to the value specified by the ``trytond_password`` option.

**sao_port**
    The port on the server that Sao is on.  If this value is not set then it
    defaults to the value specified by the ``trytond_port`` option.

**sao_protocol**
    The protocol to use to connect to the server with.  Should be one of
    either ``http`` or ``https``.  The default value for this option is
    ``https``.

**sao_timeout**
    The amount of time in seconds that must pass before operations on the
    client are assumed to have failed, and so time out.  This defaults to
    ``60`` seconds.

**sao_user**
    The login name for the user to connect as.  If this value is not set then
    it defaults to the value specified by the ``trytond_user`` option.
