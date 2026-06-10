import uuid
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from framework.contracts.base_controller import BaseController
from config.supported_formats import SUPPORTED_FORMATS
from config.paths import PRIVATE_DIR
from app.services.converters.libreoffice import LibreOffice

class ConverterController(BaseController):

    @staticmethod
    def home():
        return {"message": "api home"}

    @staticmethod
    def merge_pdf():
        return {"success": True, "message": "Merge PDF successfully", "data": {"merged_file": "merged.pdf"}}

    @staticmethod
    def split_pdf():
        return {"success": True, "message": "Split PDF successfully", "data": {"split_files": ["file1.pdf", "file2.pdf"]}}

    @staticmethod
    def compress_pdf():
        return {"success": True, "message": "Compress PDF successfully", "data": {"compressed_file": "compressed.pdf"}}

    @staticmethod
    def pdf_to_ppt():
        return {"success": True, "message": "PDF to PPT successfully", "data": {"converted_file": "converted.ppt"}}

    @staticmethod
    def pdf_to_excel():
        return {"success": True, "message": "PDF to Excel successfully", "data": {"converted_file": "converted.xlsx"}}

    @staticmethod
    def word_to_pdf():
        return {"success": True, "message": "Word to PDF successfully", "data": {"converted_file": "converted.pdf"}}

    @staticmethod
    def pdf_to_word():
        return {"success": True, "message": "PDF to Word successfully", "data": {"converted_file": "converted.docx"}}

    @staticmethod
    def redact_pdf():
        return {"success": True, "message": "Redact PDF successfully", "data": {"redacted_file": "redacted.pdf"}}

    @staticmethod
    def sign_pdf():
        return {"success": True, "message": "Sign PDF successfully", "data": {"signed_file": "signed.pdf"}}

    @staticmethod
    def watermark():
        return {"success": True, "message": "Watermark added successfully", "data": {"watermarked_file": "watermarked.pdf"}}

    @staticmethod
    def protect_pdf():
        return {"success": True, "message": "PDF protected successfully", "data": {"protected_file": "protected.pdf"}}

    @staticmethod
    def unlock_pdf():
        return {"success": True, "message": "PDF unlocked successfully", "data": {"unlocked_file": "unlocked.pdf"}}

    @staticmethod
    def ai_summerizer():
        return {"success": True, "message": "AI Summarization successfully", "data": {"summary": "This is a summary of the PDF content."}}

    @staticmethod
    def page_number():
        return {"success": True, "message": "Page numbers added successfully", "data": {"page_numbers": [1, 2, 3]}}

    @staticmethod
    def ppt_to_pdf():
        return {"success": True, "message": "PPT to PDF successfully", "data": {"converted_file": "converted.pdf"}}

    @staticmethod
    def excel_to_pdf():
        return {"success": True, "message": "Excel to PDF successfully", "data": {"converted_file": "converted.pdf"}}

    @staticmethod
    def jpg_to_pdf():
        return {"success": True, "message": "JPG to PDF successfully", "data": {"converted_file": "converted.pdf"}}

    @staticmethod
    def pdf_to_jpg():
        return {"success": True, "message": "PDF to JPG successfully", "data": {"converted_file": "converted.jpg"}}

    @staticmethod
    def rotate_pdf():
        return {"success": True, "message": "PDF rotated successfully", "data": {"rotated_file": "rotated.pdf"}}

    @staticmethod
    def edit_pdf():
        return {"success": True, "message": "PDF edited successfully", "data": {"edited_file": "edited.pdf"}}

    @staticmethod
    def compare_pdf():
        return {"success": True, "message": "PDF compared successfully", "data": {"comparison_result": "The PDFs are identical."}}

    @staticmethod
    def organize_pdf():
        return {"success": True, "message": "PDF organized successfully", "data": {"organized_file": "organized.pdf"}}

    @staticmethod
    def scan_pdf():
        return {"success": True, "message": "Scan PDF successfully", "data": {"scanned_file": "scanned.pdf"}}

    @staticmethod
    def ocr_pdf():
        return {"success": True, "message": "OCR PDF successfully", "data": {"ocr_file": "ocr.pdf"}}

    @staticmethod
    def crop_pdf():
        return {"success": True, "message": "Crop PDF successfully", "data": {"cropped_file": "cropped.pdf"}}

    @staticmethod
    async def convert(file, target_format):
        target_format = target_format.lower().strip()

        if target_format not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400, detail=f"Unsupported target format: {target_format}"
            )

        session_id = uuid.uuid4().hex
        temp_dir = PRIVATE_DIR / session_id
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            input_path = temp_dir / (file.filename or "document")

            with open(input_path, "wb") as f:
                f.write(await file.read())

            public_filename, url = LibreOffice.run_conversion(
                str(input_path), target_format
            )

            return JSONResponse(
                status_code=200,
                content={"success": True, "filename": public_filename, "url": url},
            )

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
