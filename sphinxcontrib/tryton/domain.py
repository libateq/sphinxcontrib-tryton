# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from collections import OrderedDict
from docutils.parsers.rst.directives import positive_int, unchanged, uri
from docutils.parsers.rst.directives.images import Figure
from hashlib import sha1
from pathlib import Path
from shutil import rmtree
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.locale import _
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.docutils import SphinxRole
from sphinx.util.nodes import make_refnode
from tempfile import mkdtemp
from time import sleep

from .client import Area, Client

logger = logging.getLogger(__name__)


def tryton_field_list(argument):
    return argument.strip().split(' ')


class TrytonObject(ObjectDescription):
    "Description of a Tryton object."

    def handle_signature(self, sig, signode):
        internal_name = sig
        type_ = self.name.split(':')[-1]

        name = self.env.trytond.get_property(type_, internal_name)
        if not name:
            logger.warning(
                "{type_} {internal_name} not found in Tryton.".format(
                    type_=type_, internal_name=internal_name),
                location=(self.env.docname, self.lineno))
            raise ValueError

        signode += addnodes.desc_name(name, name)

        return name

    def add_target_and_index(self, name, sig, signode):
        internal_name = sig

        if internal_name not in self.state.document.ids:
            signode['names'].append(internal_name)
            signode['ids'].append(internal_name)
            signode['first'] = not(self.names)
            self.state.document.note_explicit_target(signode)

            objects = self.env.domaindata['tryton']['objects']
            if internal_name in objects:
                logger.warning(
                    "duplicate tryton object description of {object}, "
                    "other found in {document}".format(
                        object=internal_name,
                        document=self.env.doc2path(objects[internal_name][0])),
                    location=(self.env.docname, self.lineno))
            objects[internal_name] = (self.env.docname, self.objtype)

        indextext = '{} ({})'.format(name, internal_name)
        if indextext:
            self.indexnode['entries'].append(
                ('single', indextext, internal_name, '', None))


class TrytonXRefRole(XRefRole):
    "Cross reference role to a Tryton object."

    def _get_title(self, type_, text):
        property = None
        target = text.lstrip('!~')
        if '|' in target:
            target, property = target.split('|', 1)

        try:
            title = self.env.trytond.get_property(type_, target, property)
        except ValueError:
            title = None
        if not title:
            title = text
            logger.warning(
                "no value for {type_} {text} found in Tryton.".format(
                    type_=type_, text=text),
                location=self.env.docname)

        strip_title = '~' in text[0:2]
        if strip_title:
            if property:
                title = title.strip('.')
            else:
                title = title.rsplit('.', 1)[-1]

        if text.startswith('!'):
            title = '!' + title

        return title

    def create_non_xref_node(self):
        self.text = self._get_title(self.reftype, self.text)
        return super().create_non_xref_node()

    def process_link(self, env, refnode, has_explicit_title, title, target):
        if not has_explicit_title:
            title = self._get_title(refnode['reftype'], target)

        target = target.lstrip('~')
        target = target.split('|', 1)[0]

        return title, target


class TrytonUIRole(SphinxRole):
    "Sphinx role that refers to a Tryton Client UI element."

    def run(self):
        return [addnodes.desc_name(self.text, self.text.title())], []


class TrytonFigure(Figure):
    required_arguments = 0
    optional_arguments = 1
    option_spec = Figure.option_spec.copy()
    option_spec.update({
        'client': unchanged,
        'view': unchanged,
        'fields': tryton_field_list,
        'domain': unchanged,
        'menuitem': unchanged,
        'padding': positive_int,
        })

    @classmethod
    def get_temp_dir(cls, env):
        if not getattr(env, 'tryton_figure_temp_dir', None):
            env.tryton_figure_temp_dir = mkdtemp(
                dir=env.srcdir, prefix='tmp-images-')
        return Path(env.tryton_figure_temp_dir)

    @classmethod
    def remove_temp_dir(cls, env):
        if hasattr(env, 'tryton_figure_temp_dir'):
            rmtree(env.tryton_figure_temp_dir, ignore_errors=True)

    @property
    def clients(self):
        global _tryton_clients_in_use
        if '_tryton_clients_in_use' not in globals():
            _tryton_clients_in_use = OrderedDict()
        return _tryton_clients_in_use

    @property
    def config(self):
        return self.env.config

    @property
    def env(self):
        return self.state.document.settings.env

    def get_client(self, client=None):
        if client is None:
            if self.clients:
                client = next(iter(self.clients))
            else:
                for TrytonClient in Client.__subclasses__():
                    if TrytonClient.is_configured(self.config):
                        client = TrytonClient.__name__.lower()
                        break

        if client not in self.clients:
            for TrytonClient in Client.__subclasses__():
                name = TrytonClient.__name__.lower()
                if name == client:
                    config = TrytonClient.get_config(self.config)
                    self.clients[name] = TrytonClient(**config)

        if client in self.clients:
            return self.clients[client]

    def start_client(self, client):
        if not client:
            return
        if not client.is_available:
            client.start()
        return client.is_available

    def temp_filename(self, client):
        dir = self.get_temp_dir(self.env)
        option_hash = sha1(str(self.options).encode('utf-8')).digest().hex()
        filename = '-'.join([
            self.name.replace('tryton:', ''),
            client.__class__.__name__,
            option_hash]) + '.png'

        return str(dir / filename)

    def create_image(self, client, filename):
        if not self.start_client(client):
            logger.warning(
                "client '{client}' is not available - "
                "image could not be created".format(
                    client=client.__class__.__name__))
            return

        area = Area(
            0, 0,
            self.options.get('width', client.default_size[0]),
            self.options.get('height', client.default_size[1]))

        client.close_windows()
        client.collapse_main_menu_items()
        client.hide_main_menu()

        client.resize_window(*area[2:])

        menu_item = self.options.get('menuitem', None)
        if menu_item:
            menu_item_path = self.env.trytond.get_main_menu_item_path(
                menu_item)
            client.select_main_menu_item(menu_item_path)

        view = self.options.get('view', None)
        if view:
            params = self.env.trytond.get_view(view)
            params['domain'] = self.options.get('domain', None)
            client.open_view(**params)

            fields = self.options.get('fields', None)
            if fields:
                client.select_field(fields[0])
                area = client.calculate_area(
                    fields,
                    self.options.get('padding', 0))
                self.options['width'] = area.width
                self.options['height'] = area.height

        # Pause to let things settle down,
        sleep(1)

        client.capture_image(str(filename), *area)

    def run(self):
        client = self.get_client(self.options.get('client', None))

        if not self.arguments:
            self.arguments.append(self.temp_filename(client))
        image_file = Path(self.env.relfn2path(
            uri(self.arguments[0]), self.env.docname)[1])

        if not image_file.exists() or (client and client.force_update):
            self.create_image(client, image_file)

        return super().run()


class TrytonView(TrytonFigure):
    required_arguments = 1
    optional_arguments = 1
    option_spec = TrytonFigure.option_spec.copy()
    option_spec.pop('view')

    def run(self):
        self.options['view'] = self.arguments[0]
        self.arguments.pop(0)
        return super().run()


class TrytonDomain(Domain):
    "Tryton domain."
    name = 'tryton'
    label = 'Tryton'
    object_types = {
        'button': ObjType(_('button'), 'button'),
        'data': ObjType(_('data'), 'data'),
        'field': ObjType(_('field'), 'field'),
        'figure': ObjType(_('figure'), 'figure'),
        'menu': ObjType(_('menu'), 'menu'),
        'model': ObjType(_('model'), 'model'),
        'option': ObjType(_('option'), 'option'),
        'view': ObjType(_('view'), 'view'),
        'wizard': ObjType(_('wizard'), 'wizard'),
        }
    directives = {
        'button': TrytonObject,
        'data': TrytonObject,
        'field': TrytonObject,
        'figure': TrytonFigure,
        'menu': TrytonObject,
        'model': TrytonObject,
        'option': TrytonObject,
        'view': TrytonView,
        'wizard': TrytonObject,
        }
    roles = {
        'button': TrytonXRefRole(),
        'data': TrytonXRefRole(),
        'field': TrytonXRefRole(),
        'menu': TrytonXRefRole(),
        'model': TrytonXRefRole(),
        'option': TrytonXRefRole(),
        'toolbar': TrytonUIRole(),
        'wizard': TrytonXRefRole(),
        }
    initial_data = {
        'objects': {},
        }

    def clear_doc(self, docname):
        for fullname, (objdoc, objtype) in list(self.data['objects'].items()):
            if objdoc == docname:
                del self.data['objects'][fullname]

    def merge_domaindata(self, docnames, otherdata):
        for fullname, (objdoc, objtype) in otherdata['objects'].items():
            if objdoc in docnames:
                self.data['objects'][fullname] = (objdoc, objtype)

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        if target not in self.data['objects']:
            return None
        obj = self.data['objects'][target]
        return make_refnode(
            builder, fromdocname, obj[0], target, contnode, target)

    def resolve_any_xref(self, env, fromdocname, builder, target,
                         node, contnode):
        if target not in self.data['objects']:
            return []
        obj = self.data['objects'][target]
        return [(
            'tryton:' + self.role_for_objtype(obj[1]),
            make_refnode(
                builder, fromdocname, obj[0], target, contnode, target))]

    def get_objects(self):
        for refname, (docname, type) in list(self.data['objects'].items()):
            yield (refname, refname, type, docname, refname, 1)


def cleanup_temp_figures(app, exception):
    TrytonFigure.remove_temp_dir(app.env)


def cleanup_stop_clients(app, exception):
    global _tryton_clients_in_use
    if '_tryton_clients_in_use' in globals():
        for client in _tryton_clients_in_use.values():
            client.stop()
