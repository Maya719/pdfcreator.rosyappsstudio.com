from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional, Union
from app.models.ConversionModels import HTMLToPDFRequest
from app.http.controller.UniversalConverterController import UniversalConverterController
from app.http.middleware.ApiKeyMiddleware import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/")
async def api_root():
    return {"message": "Welcome to the PDF Creator API", "version": "1.0.0"}


@router.post("/convert")
async def convert(
    file: Union[UploadFile, List[UploadFile]] = File(...),
    target_format: str = Form("pdf"),
    filename: Optional[str] = Form(None)
):
    """
    Unified conversion endpoint.
    Automatically detects input type and converts to target_format.
    """
    return await UniversalConverterController.convert(file, target_format, filename)


@router.post("/html-to-pdf/file")
async def html_to_pdf_file(
    file: UploadFile = File(...), filename: Optional[str] = Form(None)
):
    return await UniversalConverterController.convert(file, "pdf", filename)


@router.post("/html-to-pdf/code")
async def html_to_pdf_code(request: HTMLToPDFRequest):
    return await UniversalConverterController.convert_html_code(
        request.html_content, request.filename
    )


@router.post("/html-to-pdf/link")
async def html_to_pdf_link(
    url: str = Form(...), filename: Optional[str] = Form(None)
):
    return await UniversalConverterController.convert_html_link(url, filename)


@router.post("/jpg-to-pdf")
async def jpg_to_pdf(
    files: List[UploadFile] = File(...), filename: Optional[str] = Form(None)
):
    return await UniversalConverterController.convert(files, "pdf", filename)


@router.post("/word-to-pdf")
async def word_to_pdf(
    file: UploadFile = File(...), filename: Optional[str] = Form(None)
):
    return await UniversalConverterController.convert(file, "pdf", filename)
