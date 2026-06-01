from fastapi import APIRouter, Request, Form
from app.http.controller.AuthController import AuthController
from app.http.controller.DashboardController import DashboardController

router = APIRouter()


@router.get("/")
async def dashboard(request: Request):
    return await DashboardController.dashboard(request)


@router.get("/auth/login")
async def login(request: Request):
    return await AuthController.login(request)


@router.post("/auth/login")
async def do_login(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    return await AuthController.do_login(request, username, password)


@router.get("/auth/logout")
async def logout(request: Request):
    return await AuthController.logout(request)
