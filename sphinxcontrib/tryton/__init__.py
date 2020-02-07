# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from .client_sao import ClientSao
from .client_tryton import ClientTryton
from .domain import TrytonDomain, cleanup_stop_clients, cleanup_temp_figures
from .trytond import Trytond, setup_env, initialise_trytond

version = '0.1.1'


def setup(app):
    ClientSao.add_config_values(app)
    ClientTryton.add_config_values(app)
    Trytond.add_config_values(app)

    app.connect('config-inited', initialise_trytond)
    app.connect('env-before-read-docs', setup_env)
    app.connect('build-finished', cleanup_stop_clients)
    app.connect('build-finished', cleanup_temp_figures)

    app.add_domain(TrytonDomain)

    return {
        'version': version,
        'env_version': 1,
        }
