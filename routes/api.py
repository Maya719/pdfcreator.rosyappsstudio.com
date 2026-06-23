from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.jobs.job_manager import JobManager, UPLOADS_DIR

router = APIRouter()
job_manager = JobManager()


@router.post("/convert")
async def convert(file: UploadFile = File(...), target_format: str = Form(...)):
    try:
        original_filename = file.filename or "document"
        job_id = job_manager.create_job(original_filename)

        ext = (
            "." + original_filename.rsplit(".", 1)[-1]
            if "." in original_filename
            else ""
        )
        upload_path = UPLOADS_DIR / f"{job_id}{ext}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())

        job_manager.enqueue(job_id, str(upload_path), target_format)

        return JSONResponse(content={"success": True, "job_id": job_id})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        return JSONResponse(
            status_code=404, content={"success": False, "error": "Job not found"}
        )
    return JSONResponse(content={"success": True, "job": job})
