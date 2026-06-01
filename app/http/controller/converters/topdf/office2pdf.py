import asyncio
import os
import uuid
import csv as csv_module
from io import BytesIO, StringIO
from fastapi import HTTPException
from config.paths import PRIVATE_DISK
from app.helpers.pdf_utils import (
    _make_output_dir, _html_to_pdf_bytes, _build_html_table, _wrap_html, APP_URL
)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

class OfficeToPdfConverter:
    @staticmethod
    async def convert_csv(content: bytes, filename: str):
        output_dir = _make_output_dir()
        output_path = output_dir / filename
        try:
            text = content.decode("utf-8", errors="replace")
            reader = csv_module.reader(StringIO(text))
            rows = list(reader)
            if not rows: raise Exception("CSV is empty")
            # CSV is better as a clean HTML table than a raw native render
            html = _wrap_html(_build_html_table(rows[0], rows[1:], "CSV Data"))
            await _html_to_pdf_bytes(html, output_path)
            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"CSV to PDF failed: {str(e)}")

    @staticmethod
    async def convert_xlsx(content: bytes, filename: str):
        return await OfficeToPdfConverter._native_convert(content, filename, ".xlsx")

    @staticmethod
    async def convert_pptx(content: bytes, filename: str):
        return await OfficeToPdfConverter._native_convert(content, filename, ".pptx")

    @staticmethod
    async def _native_convert(content: bytes, filename: str, ext: str):
        if fitz is None:
            raise HTTPException(status_code=500, detail="PyMuPDF (fitz) is not installed.")

        temp_upload_dir = PRIVATE_DISK / "uploads"
        temp_upload_dir.mkdir(parents=True, exist_ok=True)
        temp_input_path = temp_upload_dir / f"temp_{uuid.uuid4().hex}{ext}"
        output_dir = _make_output_dir()
        output_path = output_dir / filename

        try:
            with open(temp_input_path, "wb") as f:
                f.write(content)

            def perform_conversion():
                doc = fitz.open(str(temp_input_path))
                pdf_bytes = doc.convert_to_pdf()
                with open(output_path, "wb") as f_pdf:
                    f_pdf.write(pdf_bytes)
                doc.close()

            await asyncio.to_thread(perform_conversion)
            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Native {ext} conversion failed: {str(e)}")
        finally:
            if temp_input_path.exists():
                os.remove(temp_input_path)
