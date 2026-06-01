import uuid
import time
from fastapi import UploadFile, HTTPException
from playwright.sync_api import sync_playwright
from app.helpers.pdf_utils import _make_output_dir, _html_to_pdf_bytes, APP_URL
import asyncio

class HtmlToPdfConverter:
    @staticmethod
    async def convert_file(file: UploadFile, filename: str = None):
        if not filename:
            filename = f"html_{int(time.time())}_{uuid.uuid4().hex[:8]}.pdf"
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        output_dir = _make_output_dir()
        output_path = output_dir / filename

        try:
            await file.seek(0)
            content = await file.read()
            html_content = content.decode("utf-8")

            await _html_to_pdf_bytes(html_content, output_path)
            
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("PDF file was not created or is empty")

            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HTML conversion failed: {str(e)}")
        finally:
            await file.close()

    @staticmethod
    async def convert_code(html_code: str, filename: str = None):
        if not filename:
            filename = f"html_code_{int(time.time())}_{uuid.uuid4().hex[:8]}.pdf"
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        output_dir = _make_output_dir()
        output_path = output_dir / filename

        try:
            await _html_to_pdf_bytes(html_code, output_path)
            
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("PDF file was not created or is empty")

            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HTML Code conversion failed: {str(e)}")

    @staticmethod
    async def convert_link(url: str, filename: str = None):
        if not filename:
            filename = f"html_link_{int(time.time())}_{uuid.uuid4().hex[:8]}.pdf"
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        output_dir = _make_output_dir()
        output_path = output_dir / filename

        try:
            def perform_conversion():
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
                    context = browser.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=2)
                    page = browser.new_page()
                    page.goto(url, wait_until="networkidle")
                    page.add_style_tag(content="""
                        img { max-width: 100% !important; height: auto !important; }
                        body { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
                    """)
                    page.emulate_media(media="print")
                    page.pdf(
                        path=str(output_path),
                        format="A4",
                        print_background=True,
                        margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
                        prefer_css_page_size=True
                    )
                    browser.close()
                return True

            await asyncio.to_thread(perform_conversion)

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("PDF file was not created or is empty")

            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HTML Link conversion failed: {str(e)}")
