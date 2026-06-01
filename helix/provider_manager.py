import importlib
from fastapi import FastAPI
from config.providers import Providers

class ProviderManager:
    @staticmethod
    def boot(app: FastAPI):
        for provider_path in Providers:
            class_name = provider_path.split(".")[-1]
            module = importlib.import_module(provider_path)
            provider_class = getattr(module, class_name)
            if hasattr(provider_class, "boot"):
                provider_class.boot(app)
