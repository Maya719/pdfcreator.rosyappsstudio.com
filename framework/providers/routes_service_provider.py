from fastapi.staticfiles import StaticFiles
from framework.contracts.service_provider import ServiceProvider
from routes.api import router as api
from routes.web import router as web
from config.paths import PUBLIC_DIR


class RouteServiceProvider(ServiceProvider):
    def boot(self, app):
        app.app.include_router(api, prefix="/api")
        app.app.include_router(web)

        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        app.app.mount("/storage", StaticFiles(directory=str(PUBLIC_DIR)), name="storage")
