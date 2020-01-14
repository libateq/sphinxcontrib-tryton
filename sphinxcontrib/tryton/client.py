# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from collections import namedtuple
from inspect import getmembers, isfunction


Area = namedtuple('Area', ('x', 'y', 'width', 'height'))
Size = namedtuple('Size', ('width', 'height'))


class Client(object):

    config_options = [
        ('database', None),
        ('default_size', (1920, 1080)),
        ('force_update', False),
        ('host', None),
        ('password', None),
        ('port', None),
        ('timeout', 60),
        ('user', None),
        ]
    config_prefix = ''
    config_required_options = [
        'database',
        'host',
        'user',
        ]

    def __init__(self, host, user, password, database, port, timeout,
                 default_size, force_update, **kwargs):
        self.database = database
        self.host = host
        self.user = user
        self.password = password
        self.port = port

        self.timeout = timeout
        self.default_size = Size(*default_size)
        self.force_update = force_update

        self.client_apply_method = ClientApplyMethod

        self.client = None

    def __getattr__(self, name):
        if name in AsyncClient.get_methods():
            if not self.is_available:
                raise AttributeError(
                    "method not available - client not running")
            return self.client_apply_method(
                name=name, client=self.client, timeout=self.timeout)
        raise AttributeError

    @property
    def is_available(self):
        return self.client is not None

    @classmethod
    def add_config_values(cls, app):
        for name, default in cls.config_options:
            app.add_config_value(
                '{prefix}_{name}'.format(prefix=cls.config_prefix, name=name),
                default, 'env')

    @classmethod
    def get_config(cls, config):
        result = {}
        client_template = cls.config_prefix + '_{option}'
        trytond_template = 'trytond_{option}'

        for option, _ in cls.config_options:
            client_opt = client_template.format(option=option)
            trytond_opt = trytond_template.format(option=option)

            if client_opt in config and config[client_opt] is not None:
                result[option] = config[client_opt]
            elif trytond_opt in config and config[trytond_opt] is not None:
                result[option] = config[trytond_opt]

        return result

    @classmethod
    def is_configured(cls, config):
        client_template = cls.config_prefix + '_{option}'
        trytond_template = 'trytond_{option}'

        for option in cls.config_required_options:
            client_opt = client_template.format(option=option)
            trytond_opt = trytond_template.format(option=option)

            if client_opt not in config or config[client_opt] is None:
                if trytond_opt not in config or config[trytond_opt] is None:
                    return False

        return True

    def start(self):
        pass

    def stop(self):
        pass


class ClientApplyMethod(object):

    def __init__(self, name, client, timeout):
        self.name = name
        self.client = client
        self.timeout = timeout

    def __call__(self, *args, **kwargs):
        return self.apply_method(self.name, *args, **kwargs)

    def apply_method(self, name, *args, **kwargs):
        self.client.apply_method(name, self, args, kwargs)
        return self.value


class AsyncClient(object):

    @classmethod
    def get_methods(cls):
        return [n for n, _ in getmembers(cls, predicate=isfunction)]

    def apply_method(self, name, result, args, kwargs):
        method = getattr(self, name)
        return_value = method(*args, **kwargs)
        if result:
            result.value = return_value

    def get_base_url(self):
        raise NotImplementedError

    def get_view_url(self, model, title, view_id=None, record_id=None,
                     domain=None):
        raise NotImplementedError

    def calculate_area(self, fields, padding):
        areas = self.get_fields_areas(fields)

        top = min(a.y for a in areas)
        bottom = max(a.y + a.height for a in areas)
        left = min(a.x for a in areas)
        right = max(a.x + a.width for a in areas)

        result = Area(left, top, right - left, bottom - top)

        if padding:
            max_width, max_height = self.get_window_size()
            result = Area(
                max(result[0] - padding, 0),
                max(result[1] - padding, 0),
                min(result[2] + padding * 2, max_width),
                min(result[3] + padding * 2, max_height))

        return result

    def get_fields_areas(self, fields):
        raise NotImplementedError

    def get_window_size(self):
        raise NotImplementedError

    def resize_window(self, width, height):
        raise NotImplementedError

    def capture_image(self, filename, x, y, width, height):
        raise NotImplementedError

    def open_view(self, model, title, view_id=None, record_id=None,
                  domain=None):
        raise NotImplementedError

    def select_field(self, name):
        raise NotImplementedError

    def close_windows(self):
        raise NotImplementedError

    def select_main_menu_item(self, menu_item_path):
        raise NotImplementedError

    def collapse_main_menu_items(self):
        raise NotImplementedError

    def hide_main_menu(self):
        raise NotImplementedError

    def quit(self):
        raise NotImplementedError
