import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes.api import router as api_router
from routes.web import router as web_router


def create_app():
    """
    Create and configure the FastAPI application instance.
    """
    app = FastAPI(
        title="PDF Creator API",
        description="A powerful API to generate PDF documents from HTML and templates.",
        version="1.0.0",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount Static Files
    if not os.path.exists("public/assets"):
        os.makedirs("public/assets", exist_ok=True)

    app.mount("/assets", StaticFiles(directory="public/assets"), name="assets")
    app.mount("/storage", StaticFiles(directory="storage/public"), name="storage")

    # Include Routers
    app.include_router(web_router)
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    async def startup_event():
        print("Application is starting up...")

    @app.on_event("shutdown")
    async def shutdown_event():
        print("Application is shutting down...")

    return app
