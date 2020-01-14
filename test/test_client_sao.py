# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from collections import OrderedDict
from os import environ
from pathlib import Path
from shutil import rmtree
from sphinx.util.logging import skip_warningiserror
from tempfile import mkdtemp
from unittest import SkipTest, TestCase

from sphinxcontrib.tryton.client_sao import ClientSao


def skipIfClientNotAvailable(func):
    def _skipIfClientNotAvailable(self, **kwargs):
        if not self.sao.is_available:
            raise SkipTest("Sao client is not available.")
        return func(self, **kwargs)
    return _skipIfClientNotAvailable


class TestClientSao(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = mkdtemp()
        config = dict(ClientSao.config_options)
        for key in config:
            env_name = 'TEST_SPHINXCONTRIB_{}_{}'.format(
                ClientSao.config_prefix.upper(), key.upper())
            if env_name in environ:
                config[key] = environ[env_name]
        cls.sao = ClientSao(**config)
        with skip_warningiserror():
            cls.sao.start()

    @classmethod
    def tearDownClass(cls):
        with skip_warningiserror():
            cls.sao.stop()
        rmtree(cls.temp_dir, ignore_errors=True)

    @property
    def webdriver(self):
        return self.sao.browser.webdriver

    @skipIfClientNotAvailable
    def test_resize_window(self):
        "Test resizing the window."
        window_size = OrderedDict([('width', 512), ('height', 480)])
        self.sao.resize_window(*window_size.values())
        self.assertEqual(self.webdriver.get_window_size(), dict(window_size))

    @skipIfClientNotAvailable
    def test_open_view(self):
        "Test opening a view"
        self.sao.open_view('ir.model', "Test", record_id=1)
        self.assertTrue(self.webdriver.find_elements_by_xpath(
            '//*[@id="tablist"]//*[text() = "Test"]'))

    @skipIfClientNotAvailable
    def test_select_field(self):
        "Test selecting a field"
        self.sao.open_view('ir.model', "Test", record_id=1)
        self.sao.select_field('name')

        field = self.webdriver.execute_script(
            'current_view = Sao.Tab.tabs.get_current().screen.current_view;'
            'return current_view.widgets["name"][0].el[0];')
        focus = self.webdriver.switch_to.active_element.find_elements_by_xpath(
            './/ancestor-or-self::*')
        self.assertIn(field, focus)

    @skipIfClientNotAvailable
    def test_close_windows(self):
        "Test closing the windows"
        self.sao.open_view('ir.model', "Test")
        self.sao.close_windows()

        self.assertFalse(self.webdriver.find_elements_by_xpath(
            '//*[@id="tablist"]//li'))

    @skipIfClientNotAvailable
    def test_select_main_menu_item(self):
        "Test selecting a main menu item"
        menu_item = self.webdriver.execute_script(
            'return Sao.main_menu_screen.current_view.rows[0].record.id;')

        self.sao.select_main_menu_item([menu_item])

        main_menu = self.webdriver.find_element_by_xpath('//*[@id="menu"]/..')
        self.assertIn('active', main_menu.get_attribute('class'))

    @skipIfClientNotAvailable
    def test_collapse_main_menu_items(self):
        "Test collapsing the main menu items"
        self.sao.collapse_main_menu_items()

        open_menu_items = self.webdriver.execute_script(
            'rows = Sao.main_menu_screen.current_view.rows;'
            'count = 0;'
            'for (var i = 0; i < rows.length; i++) {'
            '    count += rows[i].rows.length;'
            '}'
            'return count;')
        self.assertEqual(open_menu_items, 0)

    @skipIfClientNotAvailable
    def test_hide_main_menu(self):
        "Test hiding the main menu"
        self.sao.hide_main_menu()

        main_menu = self.webdriver.find_element_by_xpath('//*[@id="menu"]/..')
        self.assertNotIn('active', main_menu.get_attribute('class'))

    @skipIfClientNotAvailable
    def test_capture_image(self):
        "Test capturing an image"
        area = (0, 0, 512, 480)
        filename = Path(self.temp_dir) / 'test-capture-image.png'

        self.sao.capture_image(str(filename), *area)

        self.assertTrue(filename.exists())
