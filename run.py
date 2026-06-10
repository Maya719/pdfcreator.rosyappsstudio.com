import uvicorn
from public.app import app

if __name__ == "__main__":
    uvicorn.run("public.app:app", host="127.0.0.1", port=5000, reload=True)
