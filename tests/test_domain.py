# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from sphinx_testing import with_app
from unittest import TestCase
from unittest.mock import patch

from sphinxcontrib.tryton.trytond import Trytond


def with_basic_app(warnings=''):
    return with_app(
        srcdir='tests/doc/basic/',
        warningiserror=(warnings != 'allow-warnings'),
        write_docstring=True)


class MockTrytond(object):
    def __init__(self, **kwargs):
        pass

    @classmethod
    def get_config(cls, config):
        return Trytond.get_config(config)

    def get_property(self, type_, name, property=None):
        return (property or name).title()


class TestTrytonDomain(TestCase):

    def setUp(self):
        trytond_patcher = patch(
            'sphinxcontrib.tryton.trytond.Trytond', MockTrytond)
        self.MockTrytond = trytond_patcher.start()
        self.addCleanup(trytond_patcher.stop)

    @with_basic_app()
    def test_directive_button(self, app, status, warning):
        ".. tryton:button:: model.name.button_name"
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<dl class="button">\s*'
            r'<dt id="model.name.button_name">\s*'
            r'<code class="[^"]*descname[^"]*">Model.Name.Button_Name')

    @with_basic_app()
    def test_directive_data(self, app, status, warning):
        ".. tryton:data:: module.xml_id"
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<dl class="data">\s*'
            r'<dt id="module.xml_id">\s*'
            r'<code class="[^"]*descname[^"]*">Module.Xml_Id')

    @with_basic_app()
    def test_directive_field(self, app, status, warning):
        ".. tryton:field:: model.name.field_name"
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<dl class="field">\s*'
            r'<dt id="model.name.field_name">\s*'
            r'<code class="[^"]*descname[^"]*">Model.Name.Field_Name')

    @with_basic_app('allow-warnings')
    def test_directive_figure(self, app, status, warning):
        """
        .. tryton:figure::
        """
        app.builder.build_all()
        self.assertRegex(
            warning.getvalue(),
            r'WARNING: client \'NoneType\' is not available - '
            r'image could not be created')
        self.assertRegex(
            warning.getvalue(),
            r'WARNING: image file not readable:')

    @with_basic_app()
    def test_directive_menu(self, app, status, warning):
        ".. tryton:menu:: module.xml_id"
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<dl class="menu">\s*'
            r'<dt id="module.xml_id">\s*'
            r'<code class="[^"]*descname[^"]*">Module.Xml_Id')

    @with_basic_app()
    def test_directive_model(self, app, status, warning):
        ".. tryton:model:: model.name"
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<dl class="model">\s*'
            r'<dt id="model.name">\s*'
            r'<code class="[^"]*descname[^"]*">Model.Name')

    @with_basic_app()
    def test_directive_option(self, app, status, warning):
        ".. tryton:option:: model.name.field_name.option_name"
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<dl class="option">\s*'
            r'<dt id="model.name.field_name.option_name">\s*'
            r'<code class="[^"]*descname[^"]*">'
            r'Model.Name.Field_Name.Option_Name')

    @with_basic_app('allow-warnings')
    def test_directive_view(self, app, status, warning):
        """
        .. tryton:view:: module_name.xml_id
        """
        app.builder.build_all()
        self.assertRegex(
            warning.getvalue(),
            r'WARNING: client \'NoneType\' is not available - '
            r'image could not be created')
        self.assertRegex(
            warning.getvalue(),
            r'WARNING: image file not readable:')

    @with_basic_app()
    def test_directive_wizard(self, app, status, warning):
        ".. tryton:wizard:: wizard.wiz_name"
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<dl class="wizard">\s*'
            r'<dt id="wizard.wiz_name">\s*'
            r'<code class="[^"]*descname[^"]*">Wizard.Wiz_Name')

    @with_basic_app()
    def test_role_button(self, app, status, warning):
        "Tryton button :tryton:button:`model.name.button_name`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-button[^"]*">'
            r'<span class="pre">Model.Name.Button_Name</span>'
            r'</code>.')

    @with_basic_app()
    def test_role_data(self, app, status, warning):
        "Tryton data :tryton:data:`module.xml_id`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-data[^"]*">'
            r'<span class="pre">Module.Xml_Id</span>'
            r'</code>.')

    @with_basic_app()
    def test_role_field(self, app, status, warning):
        "Tryton field :tryton:field:`model.name.field_name`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-field[^"]*">'
            r'<span class="pre">Model.Name.Field_Name</span>'
            r'</code>.')

    @with_basic_app()
    def test_role_menu(self, app, status, warning):
        "Tryton data :tryton:menu:`module.xml_id`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-menu[^"]*">'
            r'<span class="pre">Module.Xml_Id</span>'
            r'</code>.')

    @with_basic_app()
    def test_role_model(self, app, status, warning):
        "Tryton model :tryton:model:`model.name`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-model[^"]*">'
            r'<span class="pre">Model.Name</span>'
            r'</code>.')

    @with_basic_app()
    def test_role_option(self, app, status, warning):
        "Tryton option :tryton:option:`model.name.field_name.option_name`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-option[^"]*">'
            r'<span class="pre">Model.Name.Field_Name.Option_Name</span>'
            r'</code>.')

    @with_basic_app()
    def test_role_toolbar(self, app, status, warning):
        "Tryton toolbar :tryton:toolbar:`new`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'Tryton toolbar <(em|code[^>]*)>New</(em|code)>.')

    @with_basic_app()
    def test_role_wizard(self, app, status, warning):
        "Tryton wizard :tryton:wizard:`wizard.wiz_name`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-wizard[^"]*">'
            r'<span class="pre">Wizard.Wiz_Name</span>'
            r'</code>.')

    @with_basic_app()
    def test_role_explicit_title(self, app, status, warning):
        "Tryton model :tryton:model:`Explicit Title <model.name>`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-model[^"]*">'
            r'<span class="pre">Explicit</span> <span class="pre">Title</span>'
            r'</code>.')

    @with_basic_app()
    def test_role_alternate_property(self, app, status, warning):
        "Tryton model :tryton:model:`model.name|different_property`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-model[^"]*">'
            r'<span class="pre">Different_Property</span>'
            r'</code>.')

    @with_basic_app()
    def test_role_last_component_only(self, app, status, warning):
        "Tryton field :tryton:field:`~model.name.field_name`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<code class="xref tryton tryton-field[^"]*">'
            r'<span class="pre">Field_Name</span>'
            r'</code>.')

    @with_basic_app()
    def test_reference_model(self, app, status, warning):
        """
        .. tryton:model:: model.name

        Tryton model :tryton:model:`model.name`.
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<a class="headerlink" href="#model.name" title="[^"]*">')
        self.assertRegex(
            source,
            r'<a class="reference internal" href="#model.name"'
            r' title="model.name">')

    @with_basic_app()
    def test_reference_field(self, app, status, warning):
        """
        .. tryton:field:: model.name.field_name

        Tryton field :tryton:field:`model.name.field_name`.
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<a class="headerlink" href="#model.name.field_name"'
            r' title="[^"]*">')
        self.assertRegex(
            source,
            r'<a class="reference internal" href="#model.name.field_name"'
            r' title="model.name.field_name">')

    @with_basic_app()
    def test_reference_data(self, app, status, warning):
        """
        .. tryton:data:: module.xml_id

        Tryton data :tryton:data:`module.xml_id`.
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<a class="headerlink" href="#module.xml_id" title="[^"]*">')
        self.assertRegex(
            source,
            r'<a class="reference internal" href="#module.xml_id"'
            r' title="module.xml_id">')

    @with_basic_app()
    def test_reference_menu(self, app, status, warning):
        """
        .. tryton:menu:: module.xml_id

        Tryton data :tryton:menu:`module.xml_id`.
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            r'<a class="headerlink" href="#module.xml_id" title="[^"]*">')
        self.assertRegex(
            source,
            r'<a class="reference internal" href="#module.xml_id"'
            r' title="module.xml_id">')
