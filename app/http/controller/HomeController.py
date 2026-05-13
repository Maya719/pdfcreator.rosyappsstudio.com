from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

templates = Jinja2Templates(directory="resources/views")


class HomeController:
    @staticmethod
    async def index(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="welcome.html",
            context={"title": "PDF Creator", "api_key": os.getenv("API_KEY")},
        )

    @staticmethod
    async def word_to_pdf(request: Request):
        return templates.TemplateResponse(request=request, name="conversions/word.html", context={"api_key": os.getenv("API_KEY")})

    @staticmethod
    async def excel_to_pdf(request: Request):
        return templates.TemplateResponse(request=request, name="conversions/excel.html", context={"api_key": os.getenv("API_KEY")})

    @staticmethod
    async def ppt_to_pdf(request: Request):
        return templates.TemplateResponse(request=request, name="conversions/ppt.html", context={"api_key": os.getenv("API_KEY")})

    @staticmethod
    async def jpg_to_pdf(request: Request):
        return templates.TemplateResponse(request=request, name="conversions/image.html", context={"api_key": os.getenv("API_KEY")})

    @staticmethod
    async def html_to_pdf(request: Request):
        return templates.TemplateResponse(request=request, name="conversions/html.html", context={"api_key": os.getenv("API_KEY")})

    @staticmethod
    async def pdf_to_word(request: Request):
        return templates.TemplateResponse(request=request, name="conversions/pdf_to_word.html", context={"api_key": os.getenv("API_KEY")})

    @staticmethod
    async def api_docs(request: Request):
        return templates.TemplateResponse(request=request, name="api-docs.html", context={"api_key": os.getenv("API_KEY")})
