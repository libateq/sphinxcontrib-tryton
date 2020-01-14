# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from functools import partial
from sphinx.util import logging
from urllib.parse import quote

from .client import Area, AsyncClient, Client, Size
from .exception import ClientError

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from selenium import webdriver
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.action_chains import ActionChains
except ImportError:
    webdriver = None

logger = logging.getLogger(__name__)

SUPPORTED_BROWSERS = ['Firefox']


class ClientSao(Client, AsyncClient):

    config_options = Client.config_options.copy()
    config_options += [
        ('browser', None),
        ('protocol', 'https')]
    config_prefix = 'sao'
    config_required_options = Client.config_required_options.copy()
    config_required_options.append('browser')

    def __init__(self, browser, protocol, **kwargs):
        super().__init__(**kwargs)
        self.browser = None
        self.browser_name = browser
        self.protocol = protocol

    def start(self):
        try:
            self.client = self.get_webdriver(self.browser_name)
            self.browser = Browser(self.client, self.timeout)
            self.login()
        except Exception as err:
            logger.warning(
                "sao screenshots disabled: {err}".format(err=repr(err)))
            self.stop()

    def stop(self):
        if self.browser:
            try:
                self.close_windows()
            except Exception as err:
                logger.warning(
                    "error closing windows: {err}".format(err=repr(err)))

            try:
                self.browser.quit()
            except Exception as err:
                logger.warning(
                    "error quitting browser: {err}".format(err=repr(err)))

        self.browser = None
        self.client = None

    def get_webdriver(self, browser):
        if Image is None:
            raise ImportError("pillow not available")

        if webdriver is None:
            raise ImportError("selenium webdriver not available")

        if not browser:
            raise ValueError("no browser specified")

        if browser.title() not in SUPPORTED_BROWSERS:
            raise ValueError(
                "{browser} browser not supported".format(
                    browser=browser.title()))

        WebDriver = getattr(webdriver, browser.title())
        return WebDriver()

    def login(self):
        self.browser.get_url(self.get_base_url())

        database = self.browser.get_database_field()
        if database.get_attribute('readonly') is not None:
            if database.get_attribute('value') != self.database:
                raise ClientError('database not available')
        else:
            Select(database).select_by_visible_text(self.database)

        login = self.browser.get_login_field()
        login.send_keys(self.user)
        login.submit()

        password = self.browser.get_password_field()
        password.send_keys(self.password)
        password.submit()

        self.browser.wait_for_login_to_complete()

    def get_base_url(self):
        standard_ports = [
            ('http', '80'),
            ('https', '443'),
            ]

        port = ':{}'.format(self.port)
        if (self.protocol, self.port) in standard_ports:
            port = ''

        return '{protocol}://{host}{port}/'.format(
            protocol=self.protocol, host=self.host, port=port)

    def get_view_url(self, model, title, view_id=None, record_id=None,
                     domain=None):
        record = '/{}'.format(int(record_id)) if record_id else ''
        params = [
            'domain=' + quote(domain) if domain else None,
            'name="{}"'.format(quote(title)) if title else None,
            'views=[{}]'.format(int(view_id)) if view_id else None,
            ]
        return '#{database}/model/{model}{record};{params}'.format(
            database=quote(self.database),
            model=quote(model), record=record,
            params='&'.join(p for p in params if p))

    def get_fields_areas(self, fields):
        result = []
        for field in fields:
            field_element = self.browser.get_field_element(field)
            result.append(Area(**field_element.rect))

            label_element = self.browser.get_label_element(field)
            if label_element:
                result.append(Area(**label_element.rect))

        return result

    def get_window_size(self):
        window_size = self.browser.get_window_size()
        return Size(window_size['width'], window_size['height'])

    def resize_window(self, width, height):
        self.browser.set_window_size(width, height)

    def capture_image(self, filename, x, y, width, height):
        self.browser.save_screenshot(filename)
        image = Image.open(filename)

        image_width, image_height = image.size
        if x + width > image_width:
            width = image_width - x
        if y + height > image_height:
            height = image_height - y

        image = image.crop((x, y, x + width, y + height))
        image.save(filename)

    def open_view(self, model, title, view_id=None, record_id=None,
                  domain=None):
        url = self.get_view_url(model, title, view_id, record_id, domain)
        self.browser.open_url(url)
        self.browser.wait_for_view_to_open(title)

    def select_field(self, name):
        self.browser.select_field(name)
        self.browser.wait_for_focus_on_field(name)

    def close_windows(self):
        self.browser.close_windows()
        self.browser.wait_for_windows_to_close()

    def select_main_menu_item(self, menu_item_path):
        attribute = 'sphinxcontrib-tryton'
        value = 'selected-menu-item'

        self.browser.add_attribute_to_main_menu_item(
            menu_item_path, attribute, value)
        menu_item = self.browser.get_element_with_attribute(attribute, value)
        self.browser.remove_attribute(menu_item, attribute)
        self.browser.select_element(menu_item)

    def collapse_main_menu_items(self):
        self.browser.collapse_main_menu_items()
        self.browser.wait_for_main_menu_items_to_collapse()

    def hide_main_menu(self):
        self.browser.hide_main_menu()
        self.browser.wait_for_main_menu_to_hide()


class Browser(object):

    def __init__(self, webdriver, timeout):
        self.webdriver = webdriver
        self.timeout = timeout

    def get_url(self, url):
        self.webdriver.get(url)

    @staticmethod
    def element_is_active(element, webdriver):
        return 'active' in element.get_attribute('class')

    @staticmethod
    def element_is_ancestor_of_focus(element, webdriver):
        focus_element = webdriver.switch_to.active_element
        ancestors = focus_element.find_elements_by_xpath('.//ancestor::*')
        return element in ancestors

    @staticmethod
    def find_database_field(webdriver):
        # Should be able to use get_element_by_id but duplicate ids in page
        input = webdriver.find_element_by_xpath(
            '//input[@id="database"]')
        select = webdriver.find_element_by_xpath(
            '//select[@id="database"]')
        if select.is_displayed():
            return select
        if input.is_displayed():
            return input

    @staticmethod
    def find_login_field(webdriver):
        return webdriver.find_element_by_id('login')

    @staticmethod
    def find_password_field(webdriver):
        return webdriver.find_element_by_id('ask-dialog-entry')

    @staticmethod
    def find_element_with_attribute(attribute, value, webdriver):
        return webdriver.find_element_by_xpath(
            '//tr[@{attribute}="{value}"]'.format(
                attribute=attribute, value=value))

    @staticmethod
    def find_windows(webdriver):
        return webdriver.find_element_by_xpath('//*[@id="tablist"]//li'),

    @staticmethod
    def login_complete(webdriver):
        return webdriver.execute_script('''
            try {
                session_loaded = Boolean(
                    Sao.Session.current_session.session);
                main_menu_loaded = Boolean(
                    Sao.main_menu_screen.current_view.rows.length);
                return session_loaded && main_menu_loaded;
            } catch(err) {
                return false;
            }''')

    @staticmethod
    def main_menu_items_collapsed(webdriver):
        return webdriver.execute_script('''
            rows = Sao.main_menu_screen.current_view.rows;
            count = 0;
            for (var i = 0; i < rows.length; i++) {
                count += rows[i].rows.length;
            }
            return count == 0;''')

    @staticmethod
    def view_open(name, webdriver):
        return webdriver.find_element_by_xpath(
            '//*[@id="tablist"]//*[text()="{name}"]'.format(name=name))

    def get_database_field(self):
        return WebDriverWait(self.webdriver, self.timeout).until(
            self.find_database_field,
            "timed out waiting for the database field")

    def get_element_with_attribute(self, attribute, value):
        return WebDriverWait(self.webdriver, self.timeout).until(
            partial(self.find_element_with_attribute, attribute, value),
            "timed out waiting for the element with "
            "{attribute}='{value}'.".format(attribute=attribute, value=value))

    def get_field_element(self, name):
        return self.webdriver.execute_script('''
            return Sao.Tab.tabs.get_current().screen.current_view
                .widgets["{name}"][0].el[0];'''.format(name=name))

    def get_label_element(self, field):
        return self.webdriver.execute_script(
            '''
            state_widgets = Sao.Tab.tabs.get_current().screen.current_view
                .state_widgets;
            for (var i = 0; i < state_widgets.length; i++) {
                if (state_widgets[i].attributes["name"] == arguments[0]) {
                    return state_widgets[i].el[0];
                }
            }''',
            field)

    def get_login_field(self):
        return WebDriverWait(self.webdriver, self.timeout).until(
            self.find_login_field,
            "timed out waiting for the login field")

    def get_password_field(self):
        return WebDriverWait(self.webdriver, self.timeout).until(
            self.find_password_field,
            "timed out waiting for the password field")

    def get_selected_menu_item(self):
        return WebDriverWait(self.webdriver, self.timeout).until(
            self.find_selected_menu_item,
            "timed out waiting for the selected menu item")

    def get_window_size(self):
        return self.webdriver.get_window_size()

    def set_window_size(self, width, height):
        self.webdriver.set_window_size(width, height)

    def add_attribute_to_main_menu_item(self, item_path, attribute, value):
        return self.webdriver.execute_script(
            '''
            function expand_to_id_path(rows, path, mark_selected_item) {
                for (var i = 0; i < rows.length; i++) {
                    if (rows[i].record.id == path[0]) {
                        if (path.length <= 1) {
                            mark_selected_item();
                        } else {
                            rows[i].update_expander(true);
                            rows[i].expand_children().done(
                                expand_to_id_path.bind(
                                    null, rows[i].rows, path.slice(1)));
                        }
                        break;
                    }
                }
            }
            function mark_selected_item(rows, path, attribute, value) {
                for (var i = 0; i < rows.length; i++) {
                    if (rows[i].record.id == path[0]) {
                        if (path.length <= 1) {
                            rows[i].el.attr(attribute, value);
                        } else {
                            mark_selected_item(rows[i].rows, path.slice(1));
                        }
                        break;
                    }
                }
            }
            jQuery("#menu").parent().addClass("active");
            menu_items = Sao.main_menu_screen.current_view.rows;
            mark_item = mark_selected_item.bind(
                null, menu_items, arguments[0], arguments[1], arguments[2]);
            expand_to_id_path(menu_items, arguments[0], mark_item);''',
            item_path, attribute, value)

    def close_windows(self):
        return self.webdriver.execute_script('''
            for (var i = 0; i < Sao.Tab.tabs.length; i++) {
                Sao.Tab.tabs[i].screen.modified = function() {
                    return false;
                };
                Sao.Tab.tabs[i].close();
            }''')

    def collapse_main_menu_items(self):
        return self.webdriver.execute_script('''
            rows = Sao.main_menu_screen.current_view.rows;
            for (var i = 0; i < rows.length; i++) {
                row = rows[i];
                if (row.rows.length > 0) {
                    row.update_expander(false);
                    row.collapse_children();
                }
            };
            rows[0].tree.expanded = {};''')

    def hide_main_menu(self):
        return self.webdriver.execute_script(
            'jQuery("#menu").parent().removeClass("active");')

    def open_url(self, url):
        return self.webdriver.execute_script(
            'Sao.open_url(arguments[0]);',
            url)

    def quit(self):
        self.webdriver.execute_script('window.onbeforeunload = function(e){};')
        self.webdriver.quit()

    def remove_attribute(self, element, attribute):
        self.webdriver.execute_script(
            'arguments[0].removeAttribute(arguments[1]);',
            element, attribute)

    def save_screenshot(self, filename):
        self.webdriver.save_screenshot(filename)

    def select_element(self, element):
        ActionChains(self.webdriver).move_to_element(element).perform()

    def select_field(self, name):
        return self.webdriver.execute_script(
            '''
            current_view = Sao.Tab.tabs.get_current().screen.current_view;
            el = current_view.widgets[arguments[0]][0].el;
            for (var i = 0; i < current_view.notebooks.length; i++) {
                notebook = current_view.notebooks[i];
                pages = notebook.get_n_pages();
                for (var j = 0; j < pages; j++) {
                    child = notebook.get_nth_page(j);
                    is_ancestor = jQuery(el).closest(child).length > 0;
                    if (is_ancestor) {
                        notebook.set_current_page(j);
                        break;
                    }
                }
            }
            for (var i = 0; i < current_view.expandables.length; i++) {
                group = current_view.expandables[i];
                is_ancestor = jQuery(el).closest(group.el).length > 0;
                if (is_ancestor) {
                    group.set_expanded(true);
                }
            }
            jQuery(el).find("input,select,textarea").focus();''',
            name)

    def wait_for_focus_on_field(self, name):
        field = self.get_field_element(name)
        WebDriverWait(self.webdriver, self.timeout).until(
            partial(self.element_is_ancestor_of_focus, field),
            "timed out waiting for the field to be selected")

    def wait_for_login_to_complete(self):
        WebDriverWait(self.webdriver, self.timeout).until(
            self.login_complete,
            "timed out waiting for the login to complete")

    def wait_for_main_menu_items_to_collapse(self):
        WebDriverWait(self.webdriver, self.timeout).until(
            self.main_menu_items_collapsed,
            "timed out waiting for all the main menu items to collapse")

    def wait_for_main_menu_to_hide(self):
        main_menu = self.webdriver.find_element_by_xpath('//*[@id="menu"]/..')
        WebDriverWait(self.webdriver, self.timeout).until_not(
            partial(self.element_is_active, main_menu),
            "timed out waiting for the main menu to be hidden")

    def wait_for_view_to_open(self, name):
        WebDriverWait(self.webdriver, self.timeout).until(
            partial(self.view_open, name),
            "timed out waiting for the view to open")

    def wait_for_windows_to_close(self):
        WebDriverWait(self.webdriver, self.timeout).until_not(
            self.find_windows,
            "timed out waiting for the windows to close")
