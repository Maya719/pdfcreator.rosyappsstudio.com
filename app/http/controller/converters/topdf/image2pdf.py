import uuid
import time
from io import BytesIO
from typing import List
from fastapi import UploadFile, HTTPException
from PIL import Image
from fpdf import FPDF
from app.helpers.pdf_utils import _make_output_dir, APP_URL

class ImageToPdfConverter:
    @staticmethod
    async def convert_single(file: UploadFile, target_format: str, filename: str = None):
        if not filename:
            filename = f"img_{int(time.time())}_{uuid.uuid4().hex[:8]}.{target_format}"
        if not filename.endswith(f".{target_format}"):
            filename += f".{target_format}"

        try:
            await file.seek(0)
            content = await file.read()
            if not content:
                raise Exception("Uploaded file is empty")

            output_dir = _make_output_dir()
            output_path = output_dir / filename

            if target_format.lower() == "pdf":
                pdf = FPDF()
                pdf.add_page()
                img = Image.open(BytesIO(content))
                img_width, img_height = img.size
                margin = 10
                max_w = 210 - (2 * margin)
                max_h = 297 - (2 * margin)
                ratio = min(max_w / img_width, max_h / img_height)
                w = img_width * ratio
                h = img_height * ratio
                x = (210 - w) / 2
                y = (297 - h) / 2
                pdf.image(BytesIO(content), x=x, y=y, w=w, h=h)
                pdf.output(str(output_path))
            else:
                img = Image.open(BytesIO(content))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(output_path, target_format.upper())

            if not output_path.exists():
                raise Exception("Output file was not saved successfully")

            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image conversion failed: {str(e)}")
        finally:
            await file.close()

    @staticmethod
    async def convert_multiple(files: List[UploadFile], filename: str = None):
        if not filename:
            filename = f"images_{int(time.time())}_{uuid.uuid4().hex[:8]}.pdf"

        try:
            pdf = FPDF()
            output_dir = _make_output_dir()
            output_path = output_dir / filename

            valid_images = 0
            for f in files:
                await f.seek(0)
                content = await f.read()
                if not content:
                    continue
                try:
                    img = Image.open(BytesIO(content))
                    img_width, img_height = img.size
                    pdf.add_page()
                    margin = 10
                    max_w = 210 - (2 * margin)
                    max_h = 297 - (2 * margin)
                    ratio = min(max_w / img_width, max_h / img_height)
                    w = img_width * ratio
                    h = img_height * ratio
                    x = (210 - w) / 2
                    y = (297 - h) / 2
                    pdf.image(BytesIO(content), x=x, y=y, w=w, h=h)
                    valid_images += 1
                except Exception:
                    continue

            if valid_images == 0:
                raise HTTPException(status_code=400, detail="No valid images were provided")

            pdf.output(str(output_path))
            return {"status": "success", "file_url": f"{APP_URL}/storage/converted/{filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Images to PDF failed: {str(e)}")
        finally:
            for f in files:
                await f.close()
