Domain
------

The *sphinxcontrib-tryton* extension adds a new domain called ``tryton`` for
use when documenting Tryton objects.  This domain contains directives and roles
that can be used to describe models, fields, and other data from a Tryton
system and add screenshots of the Tryton clients to the documentation.

Directives
^^^^^^^^^^

This extension adds several new directives that are intended to help document
various parts of a Tryton system.  All the directives accept the ``:noindex:``
option to leave the directive out of the index, and make it so it cannot be
targeted by references.

**.. tryton:button::** *model.name.button_name*
    The ``tryton:button`` directive is used to document a Tryton button.

**.. tryton:data::** *module_name.xml_id*
    The ``tryton:data`` directive is used to document XML data that is inserted
    into a Tryton system when a module is activated.

**.. tryton:field::** *model.name.field_name*
    The ``tryton:field`` directive is used for documenting a field from a
    Tryton model.

**.. tryton:figure::** *image_uri*
    The ``tryton:figure`` directive is used to insert a screenshot of a Tryton
    client into the document.  It works in a similar way to the `docutils
    figure directive`_, and supports all the options provided by the standard
    figure directive as well as some additional options.

    .. _`docutils figure directive`: http://docutils.sourceforge.net/docs/ref/rst/directives.html#figure

    *image_url*
        The ``image_uri`` argument to the directive is not required, unlike the
        standard figure directive.  If the ``image_uri`` is provided, then if
        there is an image at this location it will be used, otherwise it will
        be created (unless the ``force_update`` option is set for the client,
        in which case existing images will be replaced with new screenshots).
        If no ``image_uri`` is given then a screenshot will be taken each time
        the documentation is built.

    *:client: client_name*
        The client that should be used for the screenshot, if this is not given
        then the first configured client is used.

    *:view: module_name.xml_id*
        The ``module_name.xml_id`` of the view that should be open in the
        client when the screenshot is taken.

    *:fields: field_name [field_name ...]*
        A list of field_names around which the screenshot will be cropped.
        The first field in the list will also be focused in the client.

        .. note::
            If you want to focus a field, but still capture the whole view,
            then specify the field to focus using this option, then set a large
            ``padding`` so everything in the window is then captured.

    *:domain: tryton_domain*
        The Tryton domain to use in order to filter the records displayed in
        the view by the client.

    *:menuitem: module_name.xml_id*
        The ``module_name.xml_id`` of the main menu item that should be
        selected and displayed in the screenshot.  If this option is not given
        then the main menu will be hidden in the screenshot.

    *:padding: num_pixels*
        The number of extra pixels around the edge of cropped parts of the
        screenshot that should be included in the image.  The padding will not
        make the screenshot extend beyond the edges of the client window.

**.. tryton:menu::** *module_name.xml_id*
    The ``tryton:menu`` directive is used to document a menu item that appears
    in the main Tryton menu.

**.. tryton:model::** *model.name*
    The ``tryton:model`` directive is used to document a Tryton model.

**.. tryton:option::** *model.name.field_name.option*
    The ``tryton:model`` directive is used to document an option from a Tryton
    selection field.

**.. tryton:view::** *module_name.xml_id* *image_uri*
    The ``tryton:view`` directive is used to insert a screenshot of a Tryton
    view into the document.  It works in exactly the same way, and has the same
    options, as the ``tryton:figure`` directive, with one exception.  Instead
    of providing the view's ``module_name.xml_id`` in an option it must be
    given as the first argument.

**.. tryton:wizard::** *wizard.wiz_name*
    The ``tryton:wizard`` directive is used to document a Tryton wizard.

Roles
^^^^^

The roles provided by the ``tryton`` domain allow you to refer to Tryton
objects, such as models, fields or data.  If there is a matching directive they
will also generate a link to it.

Cross Referencing Syntax
""""""""""""""""""""""""

In general the ``tryton`` roles follow the normal Sphinx `cross referencing
syntax`_, by writing ``:tryton:role:`target``` a link will be created to the
target, if the target has been defined.  By default the title for the target
will be the name of the object translated into the language of the
:ref:`trytond user <trytond-user>`, if the object can be found in the Tryton
system and a translation for it is available.

The cross referencing syntax also enables the following features:

* You may supply an explicit title, like in reST direct hyperlinks:
  ``:tryton:role:`title <target>``` will refer to *target* but the link text
  will be *title*.
* You can set the title of the link to a different property of the object
  instead of the object name.  This is done by appending a pipe symbol ``|``
  and the property name to the target.  For example the help text for a field
  can be set as the title with: ``:tryton:field:`model.name.field|help```.
* Prefixing the content with an exclamation mark ``!`` will mean that no
  reference or hyperlink will be created.
* Prefixing the target with a tilde ``~`` will still create a link, but if
  the target is an object name then it will only include the last component of
  the target.  If the target is not an object name, then any leading or
  trailing full stops are ``.`` removed.

.. _`cross referencing syntax`: http://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#xref-syntax

**:tryton:button:**\`model.name.button_name\`
    Reference to a Tryton button.

**:tryton:data:**\`module_name.xml_id\`
    Reference to some XML data that gets inserted into a Tryton system when a
    module is activated.

**:tryton:field:**\`model.name.field_name\`
    Reference to a field in a Tryton model.

**:tryton:menu:**\`module_name.xml_id\`
    Reference to a menu item that appears in the main Tryton menu.

**:tryton:model:**\`model.name\`
    Reference to a Tryton model.

**:tryton:option:**\`model.name.field_name.option\`
    Reference to a Tryton selection field option.

**:tryton:toolbar:**\`button_name\`
    Reference to a toolbar button that appears in the Tryton client.

**:tryton:wizard:**\`wizard.wiz_name\`
    Reference to a Tryton wizard.
