from framework.contracts.service_provider import ServiceProvider
from routes.web import router as web
from routes.api import router as api


class RouteServiceProvider(ServiceProvider):
    def boot(self, app):
        app.app.include_router(web)
        app.app.include_router(api, prefix="/api")
