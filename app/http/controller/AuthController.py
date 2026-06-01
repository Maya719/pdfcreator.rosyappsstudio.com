from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from helix.templates import templates
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from app.models.User import User
# pyrefly: ignore [missing-import]
from passlib.hash import argon2


class AuthController:
    @staticmethod
    async def login(request: Request):
        if request.session.get("user"):
            return RedirectResponse(url="/admin", status_code=302)
        return templates.TemplateResponse(
            request=request,
            name="dashboard/auth/login.html",
            context={"title": "PDF Creator"},
        )

    @staticmethod
    async def do_login(
        request: Request, username: str = Form(...), password: str = Form(...)
    ):
        session: Session = request.state.db

        user = session.query(User).filter(User.username == username).first()

        if not user:
            return templates.TemplateResponse(
                "dashboard/auth/login.html",
                {"request": request, "error": "Invalid credentials"},
            )

        if not argon2.verify(password, user.password):
            return templates.TemplateResponse(
                "dashboard/auth/login.html",
                {"request": request, "error": "Invalid credentials"},
            )

        request.session["user"] = {"id": user.id, "username": user.username}

        return RedirectResponse("/admin", status_code=302)

    @staticmethod
    async def logout(request: Request):
        request.session.clear()
        return RedirectResponse(url="/admin/auth/login", status_code=302)
