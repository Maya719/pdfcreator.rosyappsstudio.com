from framework.contracts.service_provider import ServiceProvider
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
import os


class ViewServiceProvider(ServiceProvider):
    def register(self, app):
        # Define the directory for views
        views_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resources", "view")
        
        # Initialize Jinja2Templates
        app.templates = Jinja2Templates(directory=views_dir)

        # Add the asset function to Jinja2 globals
        # This allows calling {{ asset('resources/js/app.js') }} in templates
        def asset_global(path: str):
            return app.asset(path)

        app.templates.env.globals['asset'] = asset_global
        app.templates.env.globals['css_asset'] = lambda path: Markup(
            "".join([f'<link rel="stylesheet" href="{css}">' for css in app.get_css_assets(path)])
        )
        app.templates.env.globals['js_asset'] = lambda path: Markup(f'<script type="module" src="{asset_global(path)}"></script>')