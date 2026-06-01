import os
import uuid
import asyncio
from fastapi import HTTPException
from config.paths import PRIVATE_DISK
from app.helpers.pdf_utils import _make_output_dir, APP_URL

try:
    from docx2pdf import convert as docx_to_pdf_convert
except ImportError:
    docx_to_pdf_convert = None

class DocxToPdfConverter:
    @staticmethod
    async def convert(content: bytes, filename: str):
        if docx_to_pdf_convert is None:
            raise HTTPException(status_code=500, detail="docx2pdf library is not installed.")

        temp_upload_dir = PRIVATE_DISK / "uploads"
        temp_upload_dir.mkdir(parents=True, exist_ok=True)
        
        temp_input_path = temp_upload_dir / f"temp_{uuid.uuid4().hex}.docx"
        output_dir = _make_output_dir()
        output_path = output_dir / filename

        try:
            # Write bytes to temp docx file
            with open(temp_input_path, "wb") as f:
                f.write(content)

            # Perform exact conversion using Word engine
            def perform_exact_conversion():
                docx_to_pdf_convert(str(temp_input_path), str(output_path))

            await asyncio.to_thread(perform_exact_conversion)

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("PDF was not created or is empty")

            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Exact DOCX to PDF failed: {str(e)}")
        finally:
            if temp_input_path.exists():
                os.remove(temp_input_path)
