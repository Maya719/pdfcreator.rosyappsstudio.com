from framework.core.application import Application
from framework.providers.bootstrapper import ProviderBootstrapper


def bootstrap():
    app = Application()
    return app.bootstrap()
