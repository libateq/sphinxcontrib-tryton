# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from functools import lru_cache
from os import environ
from proteus import Model, Wizard, config as proteus_config
from sphinx.util import logging
from urllib.parse import urlparse, quote

logger = logging.getLogger(__name__)


class Trytond(object):

    def __init__(self, connection_type, **kwargs):
        method = getattr(self, '_init_{}_connection'.format(connection_type))
        try:
            method(**kwargs)
        except Exception as err:
            logger.warning(
                "could not connect to Trytond server: {err}".format(
                    err=repr(err)))

    def _init_trytond_connection(self, user, database_uri, config_file,
                                 modules=None, **kwargs):
        if modules is not None:
            database_name = self._get_database_name(database_uri)

            environ['DB_NAME'] = database_name
            from trytond.tests.test_tryton import db_exist, create_db

            if db_exist(database_name):
                modules = None
                logger.warning(
                    "database already exists - skipping module activation")
            else:
                create_db(database_name)

        proteus_config.set_trytond(
            database=database_uri,
            user=user,
            config_file=config_file)

        if modules:
            Module = Model.get('ir.module')
            records = Module.find([('name', 'in', modules)])

            missing_modules = set(modules) - set([r.name for r in records])
            if missing_modules:
                logger.warning(
                    "some trytond modules are not available for "
                    "activation: {missing_modules}".format(
                        missing_modules=missing_modules))

            for record in records:
                record.click('activate')
            Wizard('ir.module.activate_upgrade').execute('upgrade')

    def _init_xmlrpc_connection(self, host, user, password, database,
                                ssl_context=None, port=8000, modules=None,
                                **kwargs):
        if modules is not None:
            raise ValueError(
                "cannot create a database and activate modules over an "
                "xmlrpc connection: {modules}".format(modules=modules))
        proteus_config.set_xmlrpc(
            url='http://{user}:{password}@{host}:{port}/{database}/'.format(
                user=quote(user), password=quote(password), host=host,
                port=int(port), database=quote(database)),
            context=ssl_context)

    def get_modules(self, domain):
        Module = Model.get('ir.module')
        modules = Module.find(domain)

        def walk_graph(graph):
            roots = ['ir', 'res']
            while roots:
                for root in roots:
                    for node in graph:
                        graph[node].discard(root)
                    del graph[root]
                    yield root
                roots = sorted([n for n, p in graph.items() if not p])
            assert not graph, "module graph is disconnected"

        graph = {m.name: set(p.name for p in m.parents) for m in modules}

        return list(walk_graph(graph))

    @lru_cache(maxsize=1024)
    def get_property(self, type_, name, property=None):
        method = getattr(self, '_get_property_{}'.format(type_))
        args = [name]
        if property:
            args.append(property)
        return method(*args)

    def get_record(self, model_name, domain=None, id=None):
        try:
            RecordModel = Model.get(model_name)
        except Exception as err:
            raise ValueError(
                "model '{model}' not found: {err}".format(
                    model=model_name, err=repr(err)))

        if id is not None:
            return RecordModel(id)

        if domain is not None:
            records = RecordModel.find(domain, limit=1)
            if records:
                return records[0]

    def get_data_record(self, xml_id, domain=None):
        module_name, fs_id = xml_id.split('.', 1)

        record = self.get_record('ir.model.data', domain=[
            ('module', '=', module_name),
            ('fs_id', '=', fs_id)] +
            (domain or []))
        if record is None:
            return

        return self.get_record(record.model, id=record.db_id)

    def get_main_menu_item_path(self, xml_id):
        menuitem = self.get_data_record(xml_id)
        path = [menuitem.id]
        while menuitem.parent:
            menuitem = menuitem.parent
            path.append(menuitem.id)
        path.reverse()
        return path

    def get_view(self, xml_id):
        view = self.get_data_record(xml_id)
        action = self.get_record('ir.action.act_window', domain=[
            ('res_model', '=', view.model)])
        return {
            'view_id': view.id,
            'model': view.model,
            'title': action.name,
            }

    def _get_property_button(self, button_name, property='string'):
        model_name, button_name = button_name.rsplit('.', 1)
        model = self.get_record('ir.model', domain=[
            ('model', '=', model_name)])
        if model:
            button = self.get_record('ir.model.button', domain=[
                ('model', '=', model.id),
                ('name', '=', button_name)])
            return getattr(button, property, None)

    def _get_property_data(self, xml_id, property='name'):
        data = self.get_data_record(xml_id)
        return getattr(data, property, None)

    def _get_property_field(self, field_name, property='field_description'):
        model_name, field_name = field_name.rsplit('.', 1)

        model = self.get_record('ir.model', domain=[
            ('model', '=', model_name)])
        field = self.get_record('ir.model.field', domain=[
            ('model', '=', model.id if model else -1),
            ('name', '=', field_name)])
        if field is None:
            return

        field_str = getattr(field, property)

        if property == 'field_description':
            model_str = self.get_property('model', model_name)
            return '{model}.{field}'.format(model=model_str, field=field_str)

        return field_str

    def _get_property_menu(self, xml_id, property='complete_name'):
        menu = self.get_data_record(xml_id, [('model', '=', 'ir.ui.menu')])
        return getattr(menu, property, None)

    def _get_property_model(self, model_name, property='name'):
        model = self.get_record('ir.model', domain=[
            ('model', '=', model_name)])
        return getattr(model, property, None)

    def _get_property_option(self, option, property='name'):
        model_name, field_name, option_name = option.rsplit('.', 2)

        try:
            RecordModel = Model.get(model_name)
            selection = RecordModel._fields[field_name]['selection']
        except Exception as err:
            raise ValueError(
                "field '{model}.{field}' not found: {err}".format(
                    model=model_name, field=field_name, err=repr(err)))
        field = self._get_property_field(
            '{model}.{field}'.format(model=model_name, field=field_name))

        for option, name in selection:
            if option == option_name:
                return '{field}.{option}'.format(field=field, option=name)

    def _get_property_wizard(self, wiz_name, property='name'):
        wizard = self.get_record('ir.action.wizard', [
            ('wiz_name', '=', wiz_name)])
        return getattr(wizard, property, None)

    @staticmethod
    def _get_database_name(database_uri):
        if not database_uri:
            database_uri = environ.get('TRYTOND_DATABASE_URI')

        database_name = None
        if database_uri:
            uri = urlparse(database_uri)
            database_name = uri.path.strip('/')

        if not database_name:
            database_name = environ['DB_NAME']

        return database_name


_config_options = [
    ('connection_type', 'trytond'),
    ('config_file', None),
    ('database_uri', 'sqlite:///:memory:'),
    ('database', None),
    ('host', None),
    ('modules', None),
    ('password', None),
    ('port', 8000),
    ('ssl_context', None),
    ('user', 'admin'),
    ]


def trytond_add_config_values(app):
    for name, default in _config_options:
        app.add_config_value('trytond_{opt}'.format(opt=name), default, 'env')


def trytond_config_values(config):
    return {
        n: getattr(config, 'trytond_{opt}'.format(opt=n), v)
        for n, v in _config_options}


def initialise_trytond(app, env, docnames):
    env.trytond = Trytond(**trytond_config_values(app.config))
