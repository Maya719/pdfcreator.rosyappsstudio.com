from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):

        path = request.url.path
        print(f"DEBUG: Middleware path={path}, session={request.session.get('user')}")

        if path.startswith("/admin") and path != "/admin/auth/login":

            print(f"DEBUG: Checking admin path: {path}")
            if "session" not in request.scope:
                print("DEBUG: session not in scope for admin path. Redirecting.")
                return RedirectResponse("/admin/auth/login")

            user = request.session.get("user")
            if not user:
                print("DEBUG: user not in session for admin path. Redirecting.")
                return RedirectResponse("/admin/auth/login")
            else:
                print(f"DEBUG: User {user.get('username')} found in session for admin path.")

        return await call_next(request)
