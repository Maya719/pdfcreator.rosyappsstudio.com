from bootstrap import app
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

class MountProvider:
    @staticmethod
    def boot(app: FastAPI):
        print("Booting Mounts...")
        # Static files
        os.makedirs("public/assets", exist_ok=True)
        os.makedirs("public/build", exist_ok=True)
        app.mount("/assets", StaticFiles(directory="public/assets"), name="assets")
        app.mount("/build", StaticFiles(directory="public/build"), name="build")
        app.mount("/storage", StaticFiles(directory="storage/public"), name="storage")

