import importlib
from config.providers import PROVIDERS

class ProviderBootstrapper:
    def __init__(self, app):
        self.app = app

    def register(self):
        instances = []

        for path in PROVIDERS:
            module = importlib.import_module(path)

            provider_class = None

            for item in module.__dict__.values():
                if (isinstance(item, type) and 
                    item.__name__.endswith("Provider") and 
                    item.__name__ != "ServiceProvider"):
                    provider_class = item
                    break

            if provider_class is None:
                raise ImportError(f"No provider class found in {path}")

            instance = provider_class()

            instance.register(self.app)

            instances.append(instance)

        return instances

    def boot(self, instances):
        for instance in instances:
            instance.boot(self.app)