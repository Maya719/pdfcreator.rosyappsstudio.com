from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.controllers.home_controller import HomeController
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    app = request.app.state.app_instance
    return HomeController().index(app, request)

@router.get("/merge-pdf", response_class=HTMLResponse)
def merge_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().mergepdf(app, request)

@router.get("/split-pdf", response_class=HTMLResponse)
def split_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().splitpdf(app, request)

@router.get("/compress-pdf", response_class=HTMLResponse)
def compress_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().compresspdf(app, request)

@router.get("/word-to-pdf", response_class=HTMLResponse)
def word_to_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().wordtopdf(app, request)

@router.get("/word-to-pdf/{job_id}", response_class=HTMLResponse)
def word_to_pdf_job(request: Request, job_id: str):
    app = request.app.state.app_instance
    return HomeController().wordtopdf_job(app, request, job_id)

@router.get("/pdf-to-word", response_class=HTMLResponse)
def pdf_to_word(request: Request):
    app = request.app.state.app_instance
    return HomeController().pdftoword(app, request)


@router.get("/pdf-to-word/{job_id}", response_class=HTMLResponse)
def pdf_to_word_job(request: Request, job_id: str):
    app = request.app.state.app_instance
    return HomeController().pdftoword_job(app, request, job_id)


@router.get("/pdf-to-ppt", response_class=HTMLResponse)
def pdf_to_ppt(request: Request):
    app = request.app.state.app_instance
    return HomeController().pdftoppt(app, request)


@router.get("/pdf-to-ppt/{job_id}", response_class=HTMLResponse)
def pdf_to_ppt_job(request: Request, job_id: str):
    app = request.app.state.app_instance
    return HomeController().pdftoppt_job(app, request, job_id)


@router.get("/pdf-to-excel", response_class=HTMLResponse)
def pdf_to_excel(request: Request):
    app = request.app.state.app_instance
    return HomeController().pdftoexcel(app, request)


@router.get("/pdf-to-excel/{job_id}", response_class=HTMLResponse)
def pdf_to_excel_job(request: Request, job_id: str):
    app = request.app.state.app_instance
    return HomeController().pdftoexcel_job(app, request, job_id)


@router.get("/ppt-to-pdf", response_class=HTMLResponse)
def ppt_to_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().ppttopdf(app, request)


@router.get("/ppt-to-pdf/{job_id}", response_class=HTMLResponse)
def ppt_to_pdf_job(request: Request, job_id: str):
    app = request.app.state.app_instance
    return HomeController().ppttopdf_job(app, request, job_id)


@router.get("/excel-to-pdf", response_class=HTMLResponse)
def excel_to_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().exceltopdf(app, request)


@router.get("/excel-to-pdf/{job_id}", response_class=HTMLResponse)
def excel_to_pdf_job(request: Request, job_id: str):
    app = request.app.state.app_instance
    return HomeController().exceltopdf_job(app, request, job_id)


@router.get("/redact-pdf", response_class=HTMLResponse)
def redact_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().redactpdf(app, request)

@router.get("/sign-pdf", response_class=HTMLResponse)
def sign_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().signpdf(app, request)

@router.get("/watermark", response_class=HTMLResponse)
def watermark(request: Request):
    app = request.app.state.app_instance
    return HomeController().watermark(app, request)

@router.get("/protect-pdf", response_class=HTMLResponse)
def protect_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().protectpdf(app, request)

@router.get("/unlock-pdf", response_class=HTMLResponse)
def unlock_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().unlockpdf(app, request)

@router.get("/ai-summerizer", response_class=HTMLResponse)
def ai_summerizer(request: Request):
    app = request.app.state.app_instance
    return HomeController().aisummerizer(app, request)

@router.get("/page-number", response_class=HTMLResponse)
def page_number(request: Request):
    app = request.app.state.app_instance
    return HomeController().pagenumber(app, request)

@router.get("/jpg-to-pdf", response_class=HTMLResponse)
def jpg_to_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().jpgtopdf(app, request)


@router.get("/jpg-to-pdf/{job_id}", response_class=HTMLResponse)
def jpg_to_pdf_job(request: Request, job_id: str):
    app = request.app.state.app_instance
    return HomeController().jpgtopdf_job(app, request, job_id)


@router.get("/pdf-to-jpg", response_class=HTMLResponse)
def pdf_to_jpg(request: Request):
    app = request.app.state.app_instance
    return HomeController().pdftojpg(app, request)


@router.get("/pdf-to-jpg/{job_id}", response_class=HTMLResponse)
def pdf_to_jpg_job(request: Request, job_id: str):
    app = request.app.state.app_instance
    return HomeController().pdftojpg_job(app, request, job_id)


@router.get("/rotate-pdf", response_class=HTMLResponse)
def rotate_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().rotatepdf(app, request)

@router.get("/scan-pdf", response_class=HTMLResponse)
def scan_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().scanpdf(app, request)


@router.get("/ocr-pdf", response_class=HTMLResponse)
def ocr_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().ocrpdf(app, request)

@router.get("/crop-pdf", response_class=HTMLResponse)
def crop_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().croppdf(app, request)

@router.get("/edit-pdf", response_class=HTMLResponse)
def edit_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().editpdf(app, request)


@router.get("/compare-pdf", response_class=HTMLResponse)
def compare_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().comparepdf(app, request)


@router.get("/organize-pdf", response_class=HTMLResponse)
def organize_pdf(request: Request):
    app = request.app.state.app_instance
    return HomeController().organizepdf(app, request)
