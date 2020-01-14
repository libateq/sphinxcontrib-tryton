# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from os import environ
from sphinx.util import logging
from threading import Event, Thread
from time import sleep
from types import MethodType
from urllib.parse import quote

from .client import Area, AsyncClient, Client, ClientApplyMethod, Size
from .exception import ClientError, ClientTimeoutError

logger = logging.getLogger(__name__)


def wait_for_gtk_main_loop():
    # Pause briefly to allow the GTK main loop to finish its iteration
    sleep(0.1)


class ClientTryton(Client):

    config_prefix = 'tryton'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_apply_method = TrytonApplyMethod
        self.kwargs = kwargs

    def start(self):
        try:
            startup_event = Event()
            self.client = Tryton(startup_event=startup_event, **self.kwargs)
            self.client.start()
            if not startup_event.wait(timeout=self.timeout):
                raise ClientTimeoutError(
                    "timed out waiting for the login to complete")

            wait_for_gtk_main_loop()
            if not self.client.is_alive():
                raise ClientError("login failed")

        except Exception as err:
            logger.warning(
                "tryton screenshots disabled: {err}".format(err=repr(err)))
            self.stop()

    def stop(self):
        try:
            self.client.quit()
        except Exception as err:
            logger.warning("error quitting client: {err}".format(
                err=repr(err)))
        self.client = None

    @property
    def is_available(self):
        return super().is_available and self.client.is_alive()


class TrytonApplyMethod(ClientApplyMethod):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.result = None

    @property
    def value(self):
        if self.result is None:
            return

        if not self.result.wait(self.timeout):
            raise ClientTimeoutError(
                "timed out waiting for {method} to return".format(
                    method=self.name))

        wait_for_gtk_main_loop()
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self.result is not None:
            self.result.set()

    def apply_method(self, name, *args, **kwargs):
        from gi.repository import GLib
        self.result = Event()
        GLib.idle_add(
            self.client.apply_method, name, self, args, kwargs)
        return self.value


class Tryton(Thread, AsyncClient):

    def __init__(self, startup_event, host, port, database, user, password,
                 **kwargs):
        Thread.__init__(self, daemon=True)
        AsyncClient.__init__(self)

        self.tryton = None
        self.startup_event = startup_event

        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.login_parameters = {'password': password}

    @property
    def main(self):
        if not getattr(self, '_main', None):
            self._main = self.tryton.gui.main.Main()
        return self._main

    @property
    def menu_view(self):
        if not getattr(self, '_menu_view', None):
            self._menu_view = self.main.menu_screen.current_view
        return self._menu_view

    @property
    def page_view(self):
        if not getattr(self, '_page_view', None):
            self._page_view = self.main.get_page().screen.current_view
        return self._page_view

    def run(self):
        try:
            import tryton
            import tryton.client
        except ImportError:
            logger.warning("tryton client not available")
            tryton = None
            self.startup_event.set()
            return

        try:
            self.apply_patch_login(tryton)
            self.apply_patch_config(tryton)
            self.apply_patch_error_dialog(tryton)
            self.apply_patch_gui_startup(tryton)
        except Exception as err:
            logger.warning("error patching tryton client: {err}".format(
                err=repr(err)))
            tryton = None

        self.tryton = tryton
        if not self.tryton:
            self.startup_event.set()
            return

        environ['UBUNTU_MENUPROXY'] = '0'
        environ['LIBOVERLAY_SCROLLBAR'] = '0'
        self.tryton.client.main()

    def apply_patch_login(self, tryton):
        tryton_login_parameters = self.login_parameters

        class LoginPatch(object):
            def __init__(self, func=tryton.rpc.login):
                try:
                    func(tryton_login_parameters)
                except Exception as err:
                    raise ValueError(
                        "tryton client login failed: {err}".format(
                            err=repr(err)))

        tryton.common.Login = LoginPatch

    def apply_patch_config(self, tryton):
        tryton_login = self.user
        tryton_url = self.get_base_url()

        def config_load_save_patch(self):
            return True

        def config_parse_patch(self):
            self.arguments = [tryton_url]
            self.options['client.check_version'] = False
            self.options['login.login'] = tryton_login

        CONFIG = tryton.config.CONFIG
        CONFIG.load = MethodType(config_load_save_patch, CONFIG)
        CONFIG.save = MethodType(config_load_save_patch, CONFIG)
        CONFIG.parse = MethodType(config_parse_patch, CONFIG)

    def apply_patch_error_dialog(self, tryton):
        class ErrorDialog(object):
            def __call__(self, title, details):
                logger.error(
                    "ERROR: Tryton {title}: {details}".format(
                        title=title, details=details))

        tryton.common.ErrorDialog = ErrorDialog
        tryton.common.error = ErrorDialog()
        tryton.common.common.ErrorDialog = tryton.common.ErrorDialog
        tryton.common.common.error = tryton.common.error

    def apply_patch_gui_startup(self, tryton):
        tryton_self = self
        tryton_startup_event = self.startup_event

        def application_loaded_patch(self):
            tryton_self.main.window.unmaximize()
            tryton_startup_event.set()
            return True

        CONFIG = tryton.config.CONFIG
        CONFIG.save = MethodType(application_loaded_patch, CONFIG)

    def get_base_url(self):
        port = ':{}'.format(self.port) if str(self.port).isdigit() else ''
        database = quote(self.database) if self.database else ''
        return 'tryton://{host}{port}/{database}'.format(
            host=self.host, port=port, database=database)

    def get_view_url(self, model, title, view_id=None, record_id=None,
                     domain=None):
        params = [
            'domain=' + quote(domain) if domain else None,
            'name="{}"'.format(quote(title)) if title else None,
            'views=[{}]'.format(int(view_id)) if view_id else None,
            ]
        record = '/{}'.format(int(record_id)) if record_id else ''
        return '/model/{model}{record};{params}'.format(
            model=quote(model), record=record,
            params='&'.join(p for p in params if p))

    def get_widget_area(self, widget):
        allocation = widget.get_allocation()
        position = widget.translate_coordinates(
            self.main.window, allocation.x, allocation.y)
        return Area(*position, allocation.width, allocation.height)

    def get_fields_areas(self, fields):
        result = []
        for field in fields:
            widget = self.page_view.widgets[field]
            result.append(self.get_widget_area(widget))

            for state_widget in self.page_view.state_widgets:
                name = getattr(state_widget, 'attrs', {}).get('name', None)
                if name == field:
                    result.append(self.get_widget_area(state_widget))
                    break

        return result

    def get_window_size(self):
        size = self.main.window.get_size()
        return Size(size.width, size.height)

    def resize_window(self, width, height):
        window = self.main.window
        window.resize(width, height)
        if window.is_maximized():
            window.unmaximize()

    def capture_image(self, filename, x, y, width, height):
        from gi.repository import Gdk
        image = Gdk.pixbuf_get_from_window(
            self.main.window.get_window(), x, y, width, height)

        extension = filename[filename.rfind('.')+1:]
        image.savev(filename, extension, [], [])

    def open_view(self, model, title, view_id=None, record_id=None,
                  domain=None):
        self.main._open_url(
            self.get_base_url() + self.get_view_url(
                model, title, view_id, record_id, domain))
        return False

    def find_focusable_child(self, widget):
        if widget.get_can_focus():
            return widget
        if not hasattr(widget, 'get_children'):
            return
        for child in widget.get_children():
            focusable = self.find_focusable_child(child)
            if focusable:
                return focusable

    def select_field(self, name):
        widget = self.page_view.widgets[name][0].widget
        focusable_widget = self.find_focusable_child(widget)
        if not focusable_widget:
            return

        for notebook in self.page_view.notebooks:
            for i in range(notebook.get_n_pages()):
                child = notebook.get_nth_page(i)
                if focusable_widget.is_ancestor(child):
                    notebook.set_current_page(i)

        for group in self.page_view.expandables:
            if focusable_widget.is_ancestor(group):
                group.set_expanded(True)

        focusable_widget.grab_focus()

    def close_windows(self):
        done = False
        while not done:
            window = self.main.get_page()
            if window:
                window.screen.modified = lambda: False
                if not window.sig_close():
                    return
                done = not self.main._win_del()
            else:
                done = True

    def select_main_menu_item(self, menu_item_path):
        nested_path = (
            [menu_item_path] +
            [menu_item_path[:i]
             for i in range(-1, len(menu_item_path)*-1, -1)])
        self.menu_view.expand_nodes(nested_path[1:])
        self.menu_view.select_nodes(nested_path[:1])

    def collapse_main_menu_items(self):
        self.menu_view.treeview.collapse_all()

    def hide_main_menu(self):
        if self.main.menu.get_visible():
            self.main.menu_toggle()

    def quit(self):
        self.close_windows()
        self.main.window.hide()
        self.tryton.rpc.logout()
        self.main.quit()
