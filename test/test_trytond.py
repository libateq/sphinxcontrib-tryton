# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from unittest import SkipTest, TestCase, skipIf
from unittest.mock import Mock, patch
from sphinx_testing import with_app

from sphinxcontrib.tryton.inherit import inherit_modules
from sphinxcontrib.tryton.trytond import Trytond

try:
    import trytond
except ImportError:
    trytond = None
try:
    from trytond.modules import currency
except ImportError:
    currency = None


def with_trytond_app(modules=[]):
    return with_app(
        confoverrides={'trytond_activate_modules': modules},
        srcdir='test/doc/basic/',
        warningiserror=True,
        write_docstring=True)


class TestTrytondDatabase(TestCase):

    def setUp(self):
        self.addCleanup(self.drop_database)

    def drop_database(self):
        trytond.tests.test_tryton.drop_db()

    @skipIf(trytond is None, "trytond package is not available")
    @with_trytond_app()
    def test_create_database_directive(self, app, status, warning):
        ".. tryton:model:: ir.module"
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            '<dl class="model">\s*'
            '<dt id="ir.module">\s*'
            '<code class="[^"]*descname[^"]*">Module')

    @skipIf(trytond is None, "trytond package is not available")
    @with_trytond_app()
    def test_create_database_role(self, app, status, warning):
        "Tryton field :tryton:field:`ir.module.name`."
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            '<code class="xref tryton tryton-field[^"]*">'
            '<span class="pre">Module.Name</span>'
            '</code>.')

    @skipIf(trytond is None, "trytond package is not available")
    @with_trytond_app()
    def test_create_database_reference(self, app, status, warning):
        """
        .. tryton:data:: ir.menu_modules

        Tryton data :tryton:data:`ir.menu_modules`.
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            '<a class="headerlink" href="#ir.menu_modules" title="[^"]*">')
        self.assertRegex(
            source,
            '<a class="reference internal" href="#ir.menu_modules"'
            ' title="ir.menu_modules">')

    @skipIf(currency is None, "currency module is not available")
    @with_trytond_app(['currency'])
    def test_create_database_with_modules(self, app, status, warning):
        ".. tryton:model:: currency.currency"
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegex(
            source,
            '<dl class="model">\s*'
            '<dt id="currency.currency">\s*'
            '<code class="[^"]*descname[^"]*">Currency')

    @skipIf(trytond is None, "trytond package is not available")
    @with_app(
        srcdir='test/doc/basic/',
        confoverrides={'trytond_activate_modules': [
            'account_credit_limit', 'sale_stock_quantity', 'stock_lot_sled']})
    def test_trytond_inherit_modules(self, app, status, warning):
        "Test the module inheritance list."
        modules = inherit_modules(app, app.config)
        if 'some trytond modules are not available' in warning.getvalue():
            raise SkipTest("some trytond modules are not available")

        self.assertIn('account_credit_limit', modules)
        self.assertIn('sale_stock_quantity', modules)
        self.assertIn('stock_lot_sled', modules)

        trytond = Trytond(**Trytond.get_config(app.config))
        for module in modules:
            record = trytond.get_record('ir.module', [('name', '=', module)])
            module_index = modules.index(module)
            parent_indexes = [modules.index(p.name) for p in record.parents]
            self.assertTrue(module_index > max(parent_indexes, default=-1))


class TestTrytondInit(TestCase):

    def setUp(self):
        proteus_config_patcher = patch(
            'sphinxcontrib.tryton.trytond.proteus_config')
        self.proteus_config = proteus_config_patcher.start()
        self.addCleanup(proteus_config_patcher.stop)

    def test_trytond_config(self):
        "Test proteus.config.set_trytond is called correctly."
        Trytond(
            connection_type='trytond', config_file='config_file',
            database='database', user='user')

        self.proteus_config.set_trytond.assert_called_once_with(
            config_file='config_file', database='database', user='user')

    def test_xmlrpc_config(self):
        "Test proteus.config.set_xmlrpc is called correctly."
        Trytond(
            connection_type='xmlrpc', database='database',
            host='url.to.tryton', port=8000, user='user', password='passwd',
            ssl_context='ssl_context')

        self.proteus_config.set_xmlrpc.assert_called_once_with(
            url='http://user:passwd@url.to.tryton:8000/database/',
            context='ssl_context')


class TestTrytondGetRecord(TestCase):

    def setUp(self):
        with patch('sphinxcontrib.tryton.trytond.proteus_config'):
            self.trytond = Trytond(
                connection_type='trytond', config_file='config_file',
                database='database', user='user')

        trytond_model_patcher = patch('sphinxcontrib.tryton.trytond.Model')
        self.Model = trytond_model_patcher.start()
        self.addCleanup(trytond_model_patcher.stop)

    def test_get_record_domain(self):
        "Test get_record from domain."
        record = Mock(name='record')
        self.Model.get.return_value = Mock(**{'find.return_value': [record]})

        result = self.trytond.get_record(
            'model.name', domain=[('id', '=', '1')])
        self.assertEqual(result, record)

    def test_get_record_id(self):
        "Test get_record from id."
        record = Mock(name='record')
        self.Model.get.return_value = Mock(return_value=record)

        result = self.trytond.get_record('model.name', id=1)
        self.assertEqual(result, record)

    def test_get_data_record(self):
        "Test get_data_record."
        ir_model_data = Mock(name='model_data')
        record = Mock(name='record')
        self.Model.get.return_value = Mock(**{
            'find.return_value': [ir_model_data],
            'return_value': record})

        result = self.trytond.get_data_record('module.xml_id')
        self.assertEqual(result, record)


class TestTrytondGetProperty(TestCase):

    mock_model = Mock(name='Model', id=1)
    mock_field = Mock(name='Field', id=1)
    mock_data = Mock(name='Data', id=1)

    def setUp(self):
        with patch('sphinxcontrib.tryton.trytond.proteus_config'):
            self.trytond = Trytond(
                connection_type='trytond', config_file='config_file',
                database='database', user='user')

        get_record_patcher = patch.object(
            self.trytond, 'get_record', self._get_record)
        self.get_record = get_record_patcher.start()
        self.addCleanup(get_record_patcher.stop)

    @classmethod
    def _get_record(cls, model_name, domain=None, id=None):
        model_domain = [('model', '=', 'model.name')]
        if model_name == 'ir.model' and (model_domain == domain or id == 1):
            return cls.mock_model

        field_domain = [('model', '=', 1), ('name', '=', 'field_name')]
        if model_name == 'ir.model.field' and field_domain == domain:
            return cls.mock_field

        data_domain = [('module', '=', 'module'), ('fs_id', '=', 'xml_id')]
        if model_name == 'ir.model.data' and data_domain == domain:
            return Mock(model='data.model', db_id=1)

        if model_name == 'data.model' and id == 1:
            return cls.mock_data

    def test_get_property_model(self):
        "Test get_property for a model."
        expected = self.mock_model.name
        result = self.trytond.get_property('model', 'model.name')
        self.assertEqual(result, expected)

    def test_get_property_model_alt_property(self):
        "Test get_property for a model with an alternative property name."
        expected = self.mock_model.property
        result = self.trytond.get_property('model', 'model.name', 'property')
        self.assertEqual(result, expected)

    def test_get_property_field(self):
        "Test get_property for a field."
        expected = '{}.{}'.format(
            self.mock_model.name, self.mock_field.field_description)
        result = self.trytond.get_property('field', 'model.name.field_name')
        self.assertEqual(result, expected)

    def test_get_property_field_alt_property(self):
        "Test get_property for a field with an alternative property name."
        expected = self.mock_field.property
        result = self.trytond.get_property(
            'field', 'model.name.field_name', 'property')
        self.assertEqual(result, expected)

    def test_get_property_data(self):
        "Test get_property for some data."
        expected = self.mock_data.name
        result = self.trytond.get_property('data', 'module.xml_id')
        self.assertEqual(result, expected)

    def test_get_property_data_alt_property(self):
        "Test get_property for some data with an alternative property name."
        expected = self.mock_data.property
        result = self.trytond.get_property('data', 'module.xml_id', 'property')
        self.assertEqual(result, expected)


class TestTrytondGetOther(TestCase):

    def setUp(self):
        with patch('sphinxcontrib.tryton.trytond.proteus_config'):
            self.trytond = Trytond(
                connection_type='trytond', config_file='config_file',
                database='database', user='user')

    def test_get_main_menu_item_path(self):
        "Test get_main_menu_item_path returns a list of record ids."
        menu = Mock(name='menu')
        menu.parent.parent.parent = None
        expected = [menu.parent.parent.id, menu.parent.id, menu.id]
        with patch.object(self.trytond, 'get_data_record', return_value=menu):
            result = self.trytond.get_main_menu_item_path('module.menu_xml_id')
        self.assertEqual(result, expected)

    def test_get_view(self):
        "Test get_view returns a dict containing the view information."
        view = Mock(name='view')
        action = Mock(name='action')
        expected = {
            'view_id': view.id,
            'model': view.model,
            'title': action.name,
            }
        with patch.object(self.trytond, 'get_data_record', return_value=view):
            with patch.object(self.trytond, 'get_record', return_value=action):
                result = self.trytond.get_view('module.view_xml_id')
        self.assertEqual(result, expected)
