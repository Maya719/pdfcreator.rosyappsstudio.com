from fastapi import APIRouter, Request
from app.http.controller.HomeController import HomeController

router = APIRouter()

@router.get("/")
async def home(request: Request):
    return await HomeController.index(request)

@router.get("/word-to-pdf")
async def word_to_pdf(request: Request):
    return await HomeController.word_to_pdf(request)

@router.get("/excel-to-pdf")
async def excel_to_pdf(request: Request):
    return await HomeController.excel_to_pdf(request)

@router.get("/ppt-to-pdf")
async def ppt_to_pdf(request: Request):
    return await HomeController.ppt_to_pdf(request)

@router.get("/jpg-to-pdf")
async def jpg_to_pdf(request: Request):
    return await HomeController.jpg_to_pdf(request)

@router.get("/html-to-pdf")
async def html_to_pdf(request: Request):
    return await HomeController.html_to_pdf(request)

@router.get("/api-docs")
async def api_docs(request: Request):
    return await HomeController.api_docs(request)
