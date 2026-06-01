import os
import uuid
import time
from typing import List, Optional, Union
from fastapi import HTTPException, UploadFile

from app.helpers.pdf_utils import (
    _validate_file_not_protected, _get_safe_filename
)
from app.http.controller.converters.topdf.docx2pdf import DocxToPdfConverter
from app.http.controller.converters.topdf.html2pdf import HtmlToPdfConverter
from app.http.controller.converters.topdf.image2pdf import ImageToPdfConverter
from app.http.controller.converters.topdf.office2pdf import OfficeToPdfConverter
from app.http.controller.converters.topdf.text2pdf import TextToPdfConverter
from app.http.controller.converters.frompdf.pdf2word import PdfToWordConverter

class UniversalConverterController:

    @staticmethod
    async def convert(
        file: Union[UploadFile, List[UploadFile]],
        target_format: str = "pdf",
        filename: Optional[str] = None,
    ):
        if filename:
            filename = _get_safe_filename(filename)

        target_format = target_format.lower().lstrip(".")

        # Normalise single-item list
        if isinstance(file, list) and len(file) == 1:
            file = file[0]

        if isinstance(file, list):
            return await ImageToPdfConverter.convert_multiple(file, filename)

        ext = os.path.splitext(file.filename)[1].lower()

        # ---- Images ----
        if ext in (".jpg", ".jpeg", ".png", ".bmp", ".gif"):
            return await ImageToPdfConverter.convert_single(file, target_format, filename)

        # ---- HTML ----
        if ext in (".html", ".htm"):
            return await HtmlToPdfConverter.convert_file(file, filename)

        # ---- PDF → Word ----
        if ext == ".pdf" and target_format in ("docx", "doc"):
            base = filename or f"doc_{int(time.time())}_{uuid.uuid4().hex[:8]}.{target_format}"
            if not base.endswith(f".{target_format}"):
                base += f".{target_format}"
            return await PdfToWordConverter.convert(file, base)

        # ---- PDF → PDF (passthrough / unsupported) ----
        if ext == ".pdf":
            raise HTTPException(status_code=400, detail="PDF to PDF conversion is not supported.")

        # ---- Unsupported legacy binary formats ----
        if ext in (".doc", ".ppt", ".odp"):
            friendly = {".doc": ".docx", ".ppt": ".pptx", ".odp": ".odp"}
            target = friendly.get(ext, ".docx")
            raise HTTPException(
                status_code=400,
                detail=(
                    f"The '{ext}' format is not supported. "
                    f"Please convert your file to '{target}' and try again."
                ),
            )

        # ---- Office / text formats → PDF ----
        fn = filename or f"doc_{int(time.time())}_{uuid.uuid4().hex[:8]}.pdf"
        if not fn.endswith(".pdf"):
            fn += ".pdf"

        await file.seek(0)
        content = await file.read()
        await file.close()

        _validate_file_not_protected(content, ext)

        if ext == ".docx":
            return await DocxToPdfConverter.convert(content, fn)
        if ext == ".txt":
            return await TextToPdfConverter.convert_txt(content, fn)
        if ext == ".rtf":
            return await TextToPdfConverter.convert_rtf(content, fn)
        if ext == ".csv":
            return await OfficeToPdfConverter.convert_csv(content, fn)
        if ext == ".xlsx":
            return await OfficeToPdfConverter.convert_xlsx(content, fn)
        if ext == ".pptx":
            return await OfficeToPdfConverter.convert_pptx(content, fn)

        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")

    @staticmethod
    async def convert_html_code(html_code: str, filename: str = None):
        if filename:
            filename = _get_safe_filename(filename)
        return await HtmlToPdfConverter.convert_code(html_code, filename)

    @staticmethod
    async def convert_html_link(url: str, filename: str = None):
        if filename:
            filename = _get_safe_filename(filename)
        return await HtmlToPdfConverter.convert_link(url, filename)
