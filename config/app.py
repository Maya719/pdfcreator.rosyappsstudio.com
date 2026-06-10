from dotenv import load_dotenv
import os

load_dotenv()

APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8000")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
APP_NAME = os.getenv("APP_NAME", "MyApp")
