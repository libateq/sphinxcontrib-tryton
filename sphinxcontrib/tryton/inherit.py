# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from sphinx.util import logging, progress_message

from .trytond import initialise_trytond

logger = logging.getLogger(__name__)


def inherit_modules(app, config, state='activated'):
    assert state in ('activated', 'installed')

    message = 'finding {state} tryton modules'.format(state=state)
    domain = []
    if state == 'activated':
        domain.append(('state', '=', state))

    try:
        with progress_message(message):
            initialise_trytond(app, config)
            modules = app.trytond.get_modules(domain)
    except Exception as err:
        modules = []
        logger.warning(
            "could not find {state} tryton modules: {err}".format(
                state=state, err=repr(err)))

    return modules


def inherit_installed_modules(app, config):
    return inherit_modules(app, config, 'installed')
