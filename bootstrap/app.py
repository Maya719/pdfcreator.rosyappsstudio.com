import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from helix.provider_manager import ProviderManager
from app.http.middleware.SessionMiddleware import SessionMiddleware
from app.http.middleware.DBMiddleware import DBMiddleware
from database.connection.db import db, Base
from starlette.middleware.sessions import SessionMiddleware as StarletteSession


def create_app():
    app = FastAPI(
        title="PDF Creator API",
        description="A powerful API to generate PDF documents from HTML and templates.",
        version="1.0.0",
    )

    ProviderManager.boot(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SessionMiddleware)
    app.add_middleware(StarletteSession, secret_key=os.getenv("APP_KEY"))
    app.add_middleware(DBMiddleware)
    
    # Laravel-like boot lifecycle
    @app.on_event("startup")
    async def startup_event():
        print("Application is starting up...")
        from app.models.User import User
        Base.metadata.create_all(bind=db.engine)
        print("Database tables ready")

    @app.on_event("shutdown")
    async def shutdown_event():
        print("Application is shutting down...")

    return app
