from fastapi import FastAPI
from routes.web import router as web_router
from routes.api import router as api_router
from routes.admin import router as admin_router


class RouteProvider:
    @staticmethod
    def boot(app: FastAPI):
        print("Booting routes...")
        app.include_router(web_router)
        app.include_router(api_router, prefix="/api")
        app.include_router(admin_router, prefix="/admin")
