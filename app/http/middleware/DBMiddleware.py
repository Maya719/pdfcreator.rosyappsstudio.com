from starlette.middleware.base import BaseHTTPMiddleware
from database.connection.db import db


class DBMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.db = db.session()

        try:
            response = await call_next(request)
        finally:
            request.state.db.close()

        return response
