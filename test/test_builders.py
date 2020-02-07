# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from sphinx_testing import with_app
from unittest import TestCase
from unittest.mock import patch

from sphinxcontrib.tryton.trytond import Trytond


def with_basic_app(*args, **kwargs):
    kwargs.pop('srcdir', None)
    kwargs.pop('warningiserror', None)
    return with_app(
        srcdir='test/doc/basic/', warningiserror=True, *args, **kwargs)


class MockTrytond(object):
    def __init__(self, **kwargs):
        pass

    @classmethod
    def get_config(cls, config):
        return Trytond.get_config(config)


class TestTrytondBuilders(TestCase):

    def setUp(self):
        trytond_patcher = patch(
            'sphinxcontrib.tryton.trytond.Trytond', MockTrytond)
        self.MockTrytond = trytond_patcher.start()
        self.addCleanup(trytond_patcher.stop)

    @with_basic_app(buildername='epub')
    def test_builder_epub(self, app, status, warning):
        "Test building epub documentation."
        app.builder.build_all()

    @with_basic_app(buildername='html')
    def test_builder_html(self, app, status, warning):
        "Test building html documentation."
        app.builder.build_all()

    @with_basic_app(buildername='latex')
    def test_builder_latex(self, app, status, warning):
        "Test building latex documentation."
        app.builder.build_all()

    @with_basic_app(buildername='man')
    def test_builder_man(self, app, status, warning):
        "Test building man documentation."
        app.builder.build_all()

    @with_basic_app(buildername='texinfo')
    def test_builder_texinfo(self, app, status, warning):
        "Test building texinfo documentation."
        app.builder.build_all()

    @with_basic_app(buildername='text')
    def test_builder_text(self, app, status, warning):
        "Test building text documentation."
        app.builder.build_all()
