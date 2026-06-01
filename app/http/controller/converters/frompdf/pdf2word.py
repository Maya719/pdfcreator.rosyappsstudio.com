import os
import uuid
import asyncio
from fastapi import UploadFile, HTTPException
from pdf2docx import Converter
from config.paths import PRIVATE_DISK
from app.helpers.pdf_utils import _make_output_dir, APP_URL

class PdfToWordConverter:
    @staticmethod
    async def convert(file: UploadFile, filename: str):
        temp_upload_dir = PRIVATE_DISK / "uploads"
        temp_upload_dir.mkdir(parents=True, exist_ok=True)

        ext = os.path.splitext(file.filename)[1].lower()
        temp_input_path = temp_upload_dir / f"{uuid.uuid4().hex}{ext}"
        output_dir = _make_output_dir()
        output_path = output_dir / filename

        try:
            await file.seek(0)
            content = await file.read()
            with open(temp_input_path, "wb") as buf:
                buf.write(content)

            def perform_conversion():
                cv = Converter(str(temp_input_path))
                cv.convert(str(output_path), start=0, end=None)
                cv.close()

            await asyncio.to_thread(perform_conversion)

            if not output_path.exists():
                raise Exception("Word file was not created by the converter")

            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF to Word conversion failed: {str(e)}")
        finally:
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            await file.close()
