import uuid
import time
import os
import shutil
import subprocess
import requests
import docx
import zipfile
import asyncio
import tempfile
import pathlib
try:
    import fitz # PyMuPDF
except ImportError:
    fitz = None
from io import BytesIO
from typing import List, Optional, Union
from fastapi import HTTPException, UploadFile
# pyrefly: ignore [missing-import]
from PIL import Image
# pyrefly: ignore [missing-import]
from xhtml2pdf import pisa
from pdf2docx import Converter
from config.paths import PRIVATE_DISK, PUBLIC_DISK
from config.app import APP_URL



class UniversalConverterController:

    @staticmethod
    def _validate_file_not_protected(file_path: str, ext: str):
        """
        Definitively checks if a file is password protected without guessing.
        """
        # OOXML formats (.docx, .xlsx, .pptx) are ZIP files. 
        # If they are encrypted, they are OLE2 containers and NOT ZIP files.
        if ext in (".docx", ".xlsx", ".pptx", ".ods", ".odt"):
            if not zipfile.is_zipfile(file_path):
                # Check for OLE2 header (common for encrypted office docs)
                with open(file_path, "rb") as f:
                    header = f.read(8)
                    if header == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
                        raise Exception("The file is password-protected and cannot be converted.")
            else:
                # Even if it's a zip, check if any entry is encrypted
                try:
                    with zipfile.ZipFile(file_path) as zf:
                        for info in zf.infolist():
                            if info.flag_bits & 0x1:
                                raise Exception("The file contains encrypted content and cannot be converted.")
                except Exception:
                    # If it's a ZIP but we can't read it, it might be corrupted or protected
                    pass

        # PDF check using fitz
        if ext == ".pdf" and fitz:
            try:
                doc = fitz.open(file_path)
                is_encrypted = doc.is_encrypted
                doc.close()
                if is_encrypted:
                    raise Exception("The PDF file is password-protected and cannot be converted.")
            except Exception as e:
                if "password" in str(e).lower():
                    raise Exception("The PDF file is password-protected and cannot be converted.")

    @staticmethod
    def _get_safe_filename(filename: str) -> str:
        if not filename:
            return None
        # Use os.path.basename to prevent directory traversal and replace spaces
        return os.path.basename(filename).replace(" ", "_")

    @staticmethod
    async def convert(
        file: Union[UploadFile, List[UploadFile]],
        target_format: str = "pdf",
        filename: Optional[str] = None,
    ):
        # Sanitize filename if provided
        if filename:
            filename = UniversalConverterController._get_safe_filename(filename)

        # Normalize target_format (remove leading dot if present)
        target_format = target_format.lower().lstrip(".")

        # If it's a list with only one file, treat it as a single file for better routing
        if isinstance(file, list) and len(file) == 1:
            file = file[0]

        if isinstance(file, list):
            # Handle multiple files (currently only supported for images to PDF)
            return await UniversalConverterController._handle_multiple_images(
                file, filename
            )

        # Now 'file' is a single UploadFile
        ext = os.path.splitext(file.filename)[1].lower()

        # Image to PDF
        if ext in (".jpg", ".jpeg", ".png", ".bmp", ".gif"):
            return await UniversalConverterController._handle_single_image(
                file, target_format, filename
            )

        # HTML to PDF
        if ext in (".html", ".htm"):
            return await UniversalConverterController._handle_html(file, filename)

        # Office Documents and PDFs to target_format
        office_extensions = (
            ".docx",
            ".doc",
            ".rtf",
            ".odt",
            ".txt",
            ".xlsx",
            ".xls",
            ".ods",
            ".csv",
            ".pptx",
            ".ppt",
            ".odp",
            ".pdf",
        )

        if ext in office_extensions:
            return await UniversalConverterController._handle_office_doc(
                file, target_format, filename
            )

        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")

    @staticmethod
    async def _handle_single_image(
        file: UploadFile, target_format: str, filename: str = None
    ):
        if not filename:
            filename = f"img_{int(time.time())}_{uuid.uuid4().hex[:8]}.{target_format}"

        if not filename.endswith(f".{target_format}"):
            filename += f".{target_format}"

        try:
            await file.seek(0)
            content = await file.read()
            if not content:
                raise Exception("Uploaded file is empty")

            try:
                img = Image.open(BytesIO(content))
            except Exception as e:
                raise Exception(
                    f"PIL could not identify image {file.filename}: {str(e)}"
                )

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            output_dir = PUBLIC_DISK / "converted"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename
            img.save(
                output_path,
                target_format.upper() if target_format.lower() != "pdf" else "PDF",
            )

            if not output_path.exists():
                raise Exception("Output file was not saved successfully")

            return {
                "status": "success",
                "file_url": f"{APP_URL}/storage/converted/{filename}",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Image conversion failed: {str(e)}"
            )
        finally:
            await file.close()

    @staticmethod
    async def _handle_multiple_images(files: List[UploadFile], filename: str = None):
        if not filename:
            filename = f"images_{int(time.time())}_{uuid.uuid4().hex[:8]}.pdf"

        try:
            images = []
            for file in files:
                await file.seek(0)
                content = await file.read()
                if not content:
                    continue

                try:
                    img = Image.open(BytesIO(content))
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    elif img.mode != "RGB":
                        img = img.convert("RGB")
                    images.append(img)
                except Exception as e:
                    raise Exception(
                        f"PIL could not identify image {file.filename} in the list: {str(e)}"
                    )

            if not images:
                raise HTTPException(
                    status_code=400,
                    detail="No valid images were provided or identified",
                )

            output_dir = PUBLIC_DISK / "converted"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename
            images[0].save(
                output_path,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=images[1:],
            )

            if not output_path.exists():
                raise Exception("Combined PDF was not saved successfully")

            return {
                "status": "success",
                "file_url": f"{APP_URL}/storage/converted/{filename}",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Images to PDF failed: {str(e)}"
            )
        finally:
            for file in files:
                await file.close()

    @staticmethod
    async def _handle_html(file: UploadFile, filename: str = None):
        if not filename:
            filename = f"html_{int(time.time())}_{uuid.uuid4().hex[:8]}.pdf"

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        output_dir = PUBLIC_DISK / "converted"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        try:
            await file.seek(0)
            content = await file.read()
            html_content = content.decode("utf-8")

            def generate_pdf():
                with open(output_path, "wb") as f:
                    pisa_status = pisa.CreatePDF(html_content, dest=f)
                return pisa_status

            pisa_status = await asyncio.to_thread(generate_pdf)

            if pisa_status.err:
                raise Exception(f"xhtml2pdf conversion error code: {pisa_status.err}")

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("PDF file was not created or is empty")

            return {
                "status": "success",
                "file_url": f"{APP_URL}/storage/converted/{filename}",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"HTML conversion failed: {str(e)}"
            )
        finally:
            await file.close()

    @staticmethod
    async def _handle_pdf_to_word(
        file: UploadFile, target_format: str, filename: str = None
    ):
        temp_upload_dir = PRIVATE_DISK / "uploads"
        temp_upload_dir.mkdir(parents=True, exist_ok=True)

        # Use UUID for temp file to avoid issues with special characters in original filename
        ext = os.path.splitext(file.filename)[1].lower()
        temp_input_path = temp_upload_dir / f"{uuid.uuid4().hex}{ext}"

        outdir = PUBLIC_DISK / "converted"
        outdir.mkdir(parents=True, exist_ok=True)
        output_path = outdir / filename

        try:
            await file.seek(0)
            content = await file.read()
            with open(temp_input_path, "wb") as buffer:
                buffer.write(content)

            # pdf2docx conversion
            def perform_conversion():
                cv = Converter(str(temp_input_path))
                cv.convert(str(output_path), start=0, end=None)
                cv.close()

            await asyncio.to_thread(perform_conversion)

            if not output_path.exists():
                raise Exception("Word file was not created by the converter")

            return {
                "status": "success",
                "file_url": f"{APP_URL}/storage/converted/{filename}",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"PDF to Word conversion failed: {str(e)}"
            )
        finally:
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            await file.close()

    @staticmethod
    async def _handle_office_doc(
        file: UploadFile, target_format: str, filename: str = None
    ):
        if not filename:
            filename = f"doc_{int(time.time())}_{uuid.uuid4().hex[:8]}.{target_format}"

        if not filename.endswith(f".{target_format}"):
            filename += f".{target_format}"

        ext = os.path.splitext(file.filename)[1].lower()

        # Special case: PDF to Word using pdf2docx
        if ext == ".pdf" and target_format.lower() in ("docx", "doc"):
            return await UniversalConverterController._handle_pdf_to_word(
                file, target_format, filename
            )

        temp_upload_dir = PRIVATE_DISK / "uploads"
        temp_upload_dir.mkdir(parents=True, exist_ok=True)

        # Use UUID for temp file to avoid issues with special characters in original filename
        temp_input_path = temp_upload_dir / f"{uuid.uuid4().hex}{ext}"

        # Setup a temp directory for LibreOffice UserInstallation
        temp_profile_dir = tempfile.mkdtemp(prefix="soffice_profile_")
        profile_uri = pathlib.Path(temp_profile_dir).as_uri()

        try:
            await file.seek(0)
            content = await file.read()
            with open(temp_input_path, "wb") as buffer:
                buffer.write(content)

            # Definitive check for password protection
            UniversalConverterController._validate_file_not_protected(str(temp_input_path), ext)

            outdir = PUBLIC_DISK / "converted"
            outdir.mkdir(parents=True, exist_ok=True)

            soffice_path = os.getenv("LIBREOFFICE_PATH", "soffice")

            soffice_args = [
                soffice_path,
                f"-env:UserInstallation={profile_uri}",
                "--headless",
                "--nologo",
                "--nodefault",
                "--nofirststartwizard",
                "--nolockcheck",
                "--convert-to",
                target_format,
                "--outdir",
                str(outdir),
                str(temp_input_path),
            ]

            def run_soffice():
                return subprocess.run(
                    soffice_args,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

            result = await asyncio.to_thread(run_soffice)

            # Check for specific error patterns in stdout or stderr
            combined_output = (result.stdout or "") + (result.stderr or "")

            if result.returncode != 0:
                raise Exception(f"LibreOffice error (Exit Code {result.returncode}): {combined_output}")

            generated_name = os.path.splitext(os.path.basename(temp_input_path))[0] + f".{target_format}"
            generated_path = outdir / generated_name
            final_path = outdir / filename

            if not generated_path.exists():
                raise Exception(f"Conversion failed. LibreOffice output: {combined_output.strip() or 'No output from converter'}")

            if final_path.exists():
                os.remove(final_path)
            
            os.rename(generated_path, final_path)

            if not final_path.exists():
                raise Exception("Failed to move the converted file to the final destination")

            return {
                "status": "success",
                "file_url": f"{APP_URL}/storage/converted/{filename}",
            }

        except subprocess.TimeoutExpired as e:
            stdout_str = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            stderr_str = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
            raise HTTPException(
                status_code=500,
                detail=f"LibreOffice conversion timed out. STDOUT: {stdout_str.strip()} | STDERR: {stderr_str.strip()}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            # Clean up the temp profile directory
            if os.path.exists(temp_profile_dir):
                try:
                    shutil.rmtree(temp_profile_dir)
                except Exception:
                    pass
            await file.close()

    @staticmethod
    async def convert_html_code(html_code: str, filename: str = None):
        # Sanitize filename if provided
        if filename:
            filename = UniversalConverterController._get_safe_filename(filename)

        if not filename:
            filename = f"html_code_{int(time.time())}_{uuid.uuid4().hex[:8]}.pdf"

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        output_dir = PUBLIC_DISK / "converted"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        try:
            def generate_pdf():
                with open(output_path, "wb") as f:
                    pisa_status = pisa.CreatePDF(html_code, dest=f)
                return pisa_status

            pisa_status = await asyncio.to_thread(generate_pdf)

            if pisa_status.err:
                raise Exception(f"xhtml2pdf conversion error code: {pisa_status.err}")

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("PDF file was not created or is empty")

            return {
                "status": "success",
                "file_url": f"{APP_URL}/storage/converted/{filename}",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"HTML Code conversion failed: {str(e)}"
            )

    @staticmethod
    async def convert_html_link(url: str, filename: str = None):
        # Sanitize filename if provided
        if filename:
            filename = UniversalConverterController._get_safe_filename(filename)

        if not filename:
            filename = f"html_link_{int(time.time())}_{uuid.uuid4().hex[:8]}.pdf"

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        output_dir = PUBLIC_DISK / "converted"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        try:
            def fetch_and_generate():
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                html_content = response.text
                with open(output_path, "wb") as f:
                    pisa_status = pisa.CreatePDF(html_content, dest=f)
                return pisa_status

            pisa_status = await asyncio.to_thread(fetch_and_generate)

            if pisa_status.err:
                raise Exception(f"xhtml2pdf conversion error code: {pisa_status.err}")

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("PDF file was not created or is empty")

            return {
                "status": "success",
                "file_url": f"{APP_URL}/storage/converted/{filename}",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"HTML Link conversion failed: {str(e)}"
            )
