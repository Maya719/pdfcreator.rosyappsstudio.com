import os
import sys
import asyncio
from dotenv import load_dotenv
import uvicorn
from config.app import APP_HOST, APP_PORT

load_dotenv()

# Playwright on Windows requires ProactorEventLoop to launch browsers
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if __name__ == "__main__":
    uvicorn.run(
        "public.app:app",
        host=APP_HOST,
        port=int(APP_PORT),
        proxy_headers=True,
        reload=os.getenv("DEBUG", "True").lower() == "true",
    )
