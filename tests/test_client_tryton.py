# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from os import environ
from pathlib import Path
from shutil import rmtree
from sphinx.util.logging import skip_warningiserror
from sys import exc_info
from tempfile import mkdtemp
from threading import Event
from unittest import SkipTest, TestCase

from sphinxcontrib.tryton.client_tryton import ClientTryton


def skipIfClientNotAvailable(func):
    def _skipIfClientNotAvailable(self, **kwargs):
        if not self.tryton.is_available:
            raise SkipTest("Tryton client is not available.")
        return func(self, **kwargs)
    return _skipIfClientNotAvailable


class TestClientTryton(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = mkdtemp()
        config = dict(ClientTryton.config_options)
        for key in config:
            env_name = 'TEST_SPHINXCONTRIB_{}_{}'.format(
                ClientTryton.config_prefix.upper(), key.upper())
            if env_name in environ:
                config[key] = environ[env_name]
        cls.tryton = ClientTryton(**config)
        with skip_warningiserror():
            cls.tryton.start()

    @classmethod
    def tearDownClass(cls):
        with skip_warningiserror():
            cls.tryton.stop()
        rmtree(cls.temp_dir, ignore_errors=True)

    def assertApplyInGtkThread(self, func):
        from gi.repository import GLib

        def testAssert(tryton, check_complete):
            self.exc_info = None
            try:
                func(tryton)
            except Exception:
                self.exc_info = exc_info()
            finally:
                check_complete.set()

        check_complete = Event()
        GLib.idle_add(testAssert, self.tryton.client, check_complete)

        if not check_complete.wait(timeout=self.tryton.timeout):
            raise AssertionError("assertion timed out for func '{}'".format(
                func.__name__))

        if self.exc_info:
            raise self.exc_info[1].with_traceback(self.exc_info[2])

    @skipIfClientNotAvailable
    def test_resize_window(self):
        "Test resizing the window."
        window_size = (512, 480)
        self.tryton.resize_window(*window_size)

        def check_window_size(tryton):
            actual_size = tryton.get_window_size()
            self.assertEqual(actual_size, window_size)

        self.assertApplyInGtkThread(check_window_size)

    @skipIfClientNotAvailable
    def test_open_view(self):
        "Test opening a view"
        page_name = "Test"
        self.tryton.open_view('ir.model', page_name, record_id=1)

        def check_view_open(tryton):
            self.assertIn(page_name, [p.name for p in tryton.main.pages])

        self.assertApplyInGtkThread(check_view_open)

    @skipIfClientNotAvailable
    def test_select_field(self):
        "Test selecting a field"
        self.tryton.open_view('ir.model', "Test", record_id=1)
        self.tryton.select_field('name')

        def check_field_is_selected(tryton):
            name_hbox = tryton.page_view.widgets['name'][0].widget
            name_entry = name_hbox.get_children()[0]
            focused_widget = tryton.main.window.get_focus()
            self.assertEqual(focused_widget, name_entry)

        self.assertApplyInGtkThread(check_field_is_selected)

    @skipIfClientNotAvailable
    def test_close_windows(self):
        "Test closing the windows"
        self.tryton.open_view('ir.model', "Test")
        self.tryton.close_windows()

        def check_windows_closed(tryton):
            self.assertEqual(len(tryton.main.pages), 0)

        self.assertApplyInGtkThread(check_windows_closed)

    @skipIfClientNotAvailable
    def test_select_main_menu_item(self):
        "Test selecting a main menu item"
        current_view = self.tryton.client.main.menu_screen.current_view
        menu_item = current_view.treeview.get_model().group[0].id

        self.tryton.select_main_menu_item([menu_item])

        def check_main_menu_item_selected(tryton):
            self.assertEqual(
                menu_item,
                tryton.main.menu_screen.current_record.id)

        self.assertApplyInGtkThread(check_main_menu_item_selected)

    @skipIfClientNotAvailable
    def test_collapse_main_menu_items(self):
        "Test collapsing the main menu items"
        self.tryton.collapse_main_menu_items()

        def check_main_menu_items_are_collapsed(tryton):
            current_view = tryton.main.menu_screen.current_view
            expanded_paths = current_view.get_expanded_paths()
            self.assertEqual(expanded_paths, [])

        self.assertApplyInGtkThread(check_main_menu_items_are_collapsed)

    @skipIfClientNotAvailable
    def test_hide_main_menu(self):
        "Test hiding the main menu"
        self.tryton.hide_main_menu()

        def check_menu_hidden(tryton):
            self.assertFalse(tryton.main.menu.get_visible())

        self.assertApplyInGtkThread(check_menu_hidden)

    @skipIfClientNotAvailable
    def test_capture_image(self):
        "Test capturing an image"
        area = (0, 0, 512, 480)
        filename = Path(self.temp_dir) / 'test-capture-image.png'

        self.tryton.capture_image(str(filename), *area)

        self.assertTrue(filename.exists())
