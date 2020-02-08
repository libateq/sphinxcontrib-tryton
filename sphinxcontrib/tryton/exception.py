# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.


class ClientError(Exception):
    pass


class ClientLoginError(ClientError):
    pass


class ClientTimeoutError(ClientError):
    pass


class ClientWebDriverError(ClientError):
    pass


class TrytondError(Exception):
    pass


class DatabaseAlreadyExistsError(TrytondError):
    pass


class DatabaseInitialisationFailedError(TrytondError):
    pass


class RecordNotFoundError(TrytondError):
    pass
