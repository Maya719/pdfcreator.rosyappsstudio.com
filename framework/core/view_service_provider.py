from framework.contracts.service_provider import ServiceProvider
from fastapi.templating import Jinja2Templates
import os


class ViewServiceProvider(ServiceProvider):
    def register(self, app):
        # Define the directory for views relative to this file
        views_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resources", "views")
        
        # Initialize Jinja2Templates
        app.templates = Jinja2Templates(directory=views_dir)

        # Add asset helpers to Jinja2 globals
        def asset_global(path: str):
            return app.asset(path)

        app.templates.env.globals['asset'] = asset_global
        app.templates.env.globals['css_asset'] = lambda path: f'<link rel="stylesheet" href="{asset_global(path)}">'
        app.templates.env.globals['js_asset'] = lambda path: f'<script type="module" src="{asset_global(path)}"></script>'