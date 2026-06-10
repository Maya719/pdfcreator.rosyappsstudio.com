from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.controllers.converter_controller import ConverterController
from app.jobs.job_manager import JobManager, UPLOADS_DIR

router = APIRouter()
job_manager = JobManager()


@router.get("/")
async def home():
    return ConverterController.home()


@router.post("/convert")
async def convert(
    file: UploadFile = File(...),
    target_format: str = Form(...)
):
    return await ConverterController.convert(
        file=file,
        target_format=target_format
    )


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"success": False, "error": "Job not found"})
    return JSONResponse(content={"success": True, "job": job})


@router.post("/word-to-pdf")
async def word_to_pdf(file: UploadFile = File(...)):
    try:
        original_filename = file.filename or "document"
        job_id = job_manager.create_job(original_filename)

        ext = "." + original_filename.rsplit(".", 1)[-1] if "." in original_filename else ".docx"
        upload_path = UPLOADS_DIR / f"{job_id}{ext}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())

        job_manager.enqueue(job_id, str(upload_path), "pdf")

        return JSONResponse(content={"success": True, "job_id": job_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/merge-pdf")
async def merge_pdf():
    return ConverterController.merge_pdf()

@router.post("/split-pdf")
async def split_pdf():
    return ConverterController.split_pdf()

@router.post("/compress-pdf")
async def compress_pdf():
    return ConverterController.compress_pdf()

@router.post("/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...)):
    try:
        original_filename = file.filename or "document"
        job_id = job_manager.create_job(original_filename)
        ext = "." + original_filename.rsplit(".", 1)[-1] if "." in original_filename else ".pdf"
        upload_path = UPLOADS_DIR / f"{job_id}{ext}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())
        job_manager.enqueue(job_id, str(upload_path), "docx")
        return JSONResponse(content={"success": True, "job_id": job_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/pdf-to-ppt")
async def pdf_to_ppt(file: UploadFile = File(...)):
    try:
        original_filename = file.filename or "document"
        job_id = job_manager.create_job(original_filename)
        ext = "." + original_filename.rsplit(".", 1)[-1] if "." in original_filename else ".pdf"
        upload_path = UPLOADS_DIR / f"{job_id}{ext}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())
        job_manager.enqueue(job_id, str(upload_path), "pptx")
        return JSONResponse(content={"success": True, "job_id": job_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/pdf-to-excel")
async def pdf_to_excel(file: UploadFile = File(...)):
    try:
        original_filename = file.filename or "document"
        job_id = job_manager.create_job(original_filename)
        ext = "." + original_filename.rsplit(".", 1)[-1] if "." in original_filename else ".pdf"
        upload_path = UPLOADS_DIR / f"{job_id}{ext}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())
        job_manager.enqueue(job_id, str(upload_path), "xlsx")
        return JSONResponse(content={"success": True, "job_id": job_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/redact-pdf")
async def redact_pdf():
    return ConverterController.redact_pdf()

@router.post("/sign-pdf")
async def sign_pdf():
    return ConverterController.sign_pdf()

@router.post("/watermark")
async def watermark():
    return ConverterController.watermark()

@router.post("/protect-pdf")
async def protect_pdf():
    return ConverterController.protect_pdf()

@router.post("/unlock-pdf")
async def unlock_pdf():
    return ConverterController.unlock_pdf()

@router.post("/ai-summerizer")
async def ai_summerizer():
    return ConverterController.ai_summerizer()

@router.post("/page-number")
async def page_number():
    return ConverterController.page_number()

@router.post("/ppt-to-pdf")
async def ppt_to_pdf(file: UploadFile = File(...)):
    try:
        original_filename = file.filename or "document"
        job_id = job_manager.create_job(original_filename)
        ext = "." + original_filename.rsplit(".", 1)[-1] if "." in original_filename else ".pptx"
        upload_path = UPLOADS_DIR / f"{job_id}{ext}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())
        job_manager.enqueue(job_id, str(upload_path), "pdf")
        return JSONResponse(content={"success": True, "job_id": job_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/excel-to-pdf")
async def excel_to_pdf(file: UploadFile = File(...)):
    try:
        original_filename = file.filename or "document"
        job_id = job_manager.create_job(original_filename)
        ext = "." + original_filename.rsplit(".", 1)[-1] if "." in original_filename else ".xlsx"
        upload_path = UPLOADS_DIR / f"{job_id}{ext}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())
        job_manager.enqueue(job_id, str(upload_path), "pdf")
        return JSONResponse(content={"success": True, "job_id": job_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/jpg-to-pdf")
async def jpg_to_pdf(file: UploadFile = File(...)):
    try:
        original_filename = file.filename or "document"
        job_id = job_manager.create_job(original_filename)
        ext = (
            "." + original_filename.rsplit(".", 1)[-1]
            if "." in original_filename
            else ".pdf"
        )
        upload_path = UPLOADS_DIR / f"{job_id}{ext}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())
        job_manager.enqueue(job_id, str(upload_path), "pdf")
        return JSONResponse(content={"success": True, "job_id": job_id})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )

@router.post("/pdf-to-jpg")
async def pdf_to_jpg(file: UploadFile = File(...)):
    try:
        original_filename = file.filename or "document"
        job_id = job_manager.create_job(original_filename)
        ext = "." + original_filename.rsplit(".", 1)[-1] if "." in original_filename else ".jpg"
        upload_path = UPLOADS_DIR / f"{job_id}{ext}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())
        job_manager.enqueue(job_id, str(upload_path), "jpg")
        return JSONResponse(content={"success": True, "job_id": job_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/rotate-pdf")
async def rotate_pdf():
    return ConverterController.rotate_pdf()

@router.post("/scan-pdf")
async def scan_pdf():
    return ConverterController.scan_pdf()

@router.post("/ocr-pdf")
async def ocr_pdf():
    return ConverterController.ocr_pdf()

@router.post("/crop-pdf")
async def crop_pdf():
    return ConverterController.crop_pdf()

@router.post("/edit-pdf")
async def edit_pdf():
    return ConverterController.edit_pdf()

@router.post("/compare-pdf")
async def compare_pdf():
    return ConverterController.compare_pdf()

@router.post("/organize-pdf")
async def organize_pdf():
    return ConverterController.organize_pdf()
