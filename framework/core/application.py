from fastapi import FastAPI
from framework.providers.bootstrapper import ProviderBootstrapper


class Application:
    def __init__(self):
        self.app = FastAPI()
        self.state = {}
        self.providers = []
        self.bootstrapper = ProviderBootstrapper(self)

    def register_providers(self):
        self.providers = self.bootstrapper.register()
        return self

    def boot_providers(self):
        self.bootstrapper.boot(self.providers)
        return self

    def bootstrap(self):
        self.register_providers()
        self.boot_providers()

        self.app.state.app_instance = self

        return self.app
