from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from framework.providers.bootstrapper import ProviderBootstrapper
import os
import json
from config.paths import PUBLIC_DIR


class Application:
    def __init__(self):
        self.app = FastAPI()
        self.state = {}
        self.providers = []
        self.templates = None
        self.bootstrapper = ProviderBootstrapper(self)
        self._manifest = None

        self.app.mount("/build", StaticFiles(directory="public/build"), name="static")
        self.app.mount("/assets", StaticFiles(directory="public/assets"), name="assets")
        self.app.mount(
            "/storage", StaticFiles(directory=str(PUBLIC_DIR)), name="storage"
        )

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

    def _load_manifest(self):
        manifest_path = os.path.join("public", "build", ".vite", "manifest.json")
        if not os.path.exists(manifest_path):
            manifest_path = os.path.join("public", "build", "manifest.json")

        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                self._manifest = json.load(f)
        else:
            self._manifest = {}

    def asset(self, path: str):
        if self._manifest is None:
            self._load_manifest()
        return "/build/" + self._manifest.get(path, {}).get("file", path)

    def get_css_assets(self, path: str):
        if self._manifest is None:
            self._load_manifest()

        entry = self._manifest.get(path)

        if not entry:
            for key, val in self._manifest.items():
                if val.get("src") == path:
                    entry = val
                    break

        if not entry:
            return []

        # If the entry point is a JS file, return its associated CSS chunks
        if "css" in entry:
            return ["/build/" + css for css in entry.get("css", [])]

        # If the entry point is the CSS file itself, return its compiled path
        if path.endswith(".css") and "file" in entry:
            return ["/build/" + entry["file"]]

        return []
