import asyncio
from fastapi import HTTPException
from app.helpers.pdf_utils import _make_output_dir, _rl_text_to_pdf, APP_URL

try:
    from striprtf.striprtf import rtf_to_text
except ImportError:
    rtf_to_text = None

class TextToPdfConverter:
    @staticmethod
    async def convert_txt(content: bytes, filename: str):
        output_dir = _make_output_dir()
        output_path = output_dir / filename
        try:
            def convert():
                text = content.decode("utf-8", errors="replace")
                _rl_text_to_pdf(text, output_path)
            await asyncio.to_thread(convert)
            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TXT to PDF failed: {str(e)}")

    @staticmethod
    async def convert_rtf(content: bytes, filename: str):
        if not rtf_to_text: raise HTTPException(status_code=500, detail="striprtf not installed")
        output_dir = _make_output_dir()
        output_path = output_dir / filename
        try:
            def convert():
                raw = content.decode("utf-8", errors="replace")
                text = rtf_to_text(raw)
                _rl_text_to_pdf(text, output_path)
            await asyncio.to_thread(convert)
            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RTF to PDF failed: {str(e)}")
