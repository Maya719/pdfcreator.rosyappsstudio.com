import os
import uuid
import asyncio
import base64
from fastapi import HTTPException
from playwright.sync_api import sync_playwright
from config.paths import PRIVATE_DISK, ROOT_DIR
from app.helpers.pdf_utils import _make_output_dir, APP_URL

class DocxToPdfConverter:
    @staticmethod
    async def convert(content: bytes, filename: str):
        output_dir = _make_output_dir()
        output_path = output_dir / filename

        # Path to the specialized browser renderer template
        template_path = os.path.join(ROOT_DIR, "app", "resources", "templates", "docx_renderer.html")
        if not os.path.exists(template_path):
            raise HTTPException(status_code=500, detail="DOCX Renderer template missing.")

        def perform_browser_conversion():
            with sync_playwright() as p:
                # Launch Chromium with high-fidelity settings
                browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
                context = browser.new_context(
                    viewport={'width': 800, 'height': 1000},
                    device_scale_factor=2
                )
                page = context.new_page()

                # Load the local renderer template
                # Use file:// protocol for local access
                page.goto(f"file:///{template_path.replace(os.sep, '/')}")

                # Encode DOCX as base64 for injection
                base64_docx = base64.b64encode(content).decode('utf-8')

                # Execute the JS rendering engine
                page.evaluate(f"renderDocx('{base64_docx}')")

                # Wait for the JS engine to finish (Pixel-Perfect Render)
                # We wait until the RENDER_COMPLETE flag is set by docx-preview.js
                try:
                    page.wait_for_function("window.RENDER_COMPLETE === true || window.RENDER_ERROR", timeout=30000)
                except Exception:
                    raise Exception("Rendering timeout: The document was too complex or the engine failed.")

                # Check for JS errors
                error = page.evaluate("window.RENDER_ERROR")
                if error:
                    raise Exception(f"JS Rendering Error: {error}")

                # Give images/fonts an extra half-second to stabilize
                page.wait_for_timeout(500)

                # PIN POINT PDF CAPTURE
                page.pdf(
                    path=str(output_path),
                    format="A4",
                    print_background=True,
                    margin={"top": "0cm", "right": "0cm", "bottom": "0cm", "left": "0cm"},
                    prefer_css_page_size=True
                )

                browser.close()
            return True

        try:
            await asyncio.to_thread(perform_browser_conversion)

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("PDF was not created or is empty")

            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pin Point Browser conversion failed: {str(e)}")

