from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from helix.templates import templates
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from app.models.User import User
# pyrefly: ignore [missing-import]
from passlib.hash import argon2


class DashboardController:
    @staticmethod
    async def dashboard(request: Request):
        user = request.session.get("user")
        if not user:
            return RedirectResponse(url="/admin/auth/login", status_code=302)
        return templates.TemplateResponse(
            request=request,
            name="dashboard/dashboard.html",
            context={
                "title": "PDF Creator | Dashboard",
                "user": user,
            },
        )
