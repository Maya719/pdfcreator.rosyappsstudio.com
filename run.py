import os
from dotenv import load_dotenv
import uvicorn
from config.app import APP_HOST, APP_PORT
import os

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "public.app:app",
        host=APP_HOST,
        port=int(APP_PORT),
        proxy_headers=True,
        reload=os.getenv("DEBUG", "True").lower() == "true",
    )
