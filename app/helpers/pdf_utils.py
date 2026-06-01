import os
import uuid
import time
import asyncio
from pathlib import Path
from io import BytesIO
from playwright.sync_api import sync_playwright
from config.paths import PUBLIC_DISK
from config.app import APP_URL

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Preformatted

def _make_output_dir():
    out = PUBLIC_DISK / "converted"
    out.mkdir(parents=True, exist_ok=True)
    return out

async def _html_to_pdf_bytes(html: str, output_path, base_url: str = None):
    """Convert an HTML string to a PDF file with high precision and asset support."""
    def convert():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=[
                "--disable-web-security",
                "--font-render-hinting=none",
                "--no-sandbox"
            ])
            context = browser.new_context(
                viewport={'width': 1280, 'height': 800},
                device_scale_factor=2
            )
            page = context.new_page()
            page.set_content(html, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(1500)
            page.emulate_media(media="screen")
            page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={"top": "0.4in", "right": "0.4in", "bottom": "0.4in", "left": "0.4in"},
                display_header_footer=False,
                prefer_css_page_size=False
            )
            browser.close()
        return True

    try:
        await asyncio.to_thread(convert)
        return True
    except Exception as e:
        raise e

def _build_html_table(headers: list, rows: list, sheet_name: str = None) -> str:
    """Build a minimal HTML table string from headers + rows."""
    head = f"<h2>{sheet_name}</h2>" if sheet_name else ""
    th = "".join(f"<th>{h}</th>" for h in headers)
    body_rows = ""
    for row in rows:
        tds = "".join(f"<td>{v}</td>" for v in row)
        body_rows += f"<tr>{tds}</tr>"
    return f"""{head}
<table>
  <thead><tr>{th}</tr></thead>
  <tbody>{body_rows}</tbody>
</table>"""

def _wrap_html(body: str) -> str:
    return f"""<!DOCTYPE html>
<html><head>
<meta charset='utf-8'>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
  body {{ 
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
    font-size: 12px; 
    line-height: 1.5;
    margin: 40px; 
    color: #333;
  }}
  h2 {{ color: #111; font-size: 18px; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 20px; table-layout: fixed; word-wrap: break-word; }}
  th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
  th {{ background-color: #f8f9fa; font-weight: 700; }}
  tr:nth-child(even) {{ background-color: #fafafa; }}
  @media print {{
    body {{ margin: 0; }}
    table {{ page-break-inside: auto; }}
    tr {{ page-break-inside: avoid; page-break-after: auto; }}
    thead {{ display: table-header-group; }}
  }}
</style>
</head><body>{body}</body></html>"""

def _rl_text_to_pdf(text: str, output_path, title: str = "Document"):
    """Render plain text to a PDF using reportlab."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    pre_style = ParagraphStyle(
        "pre",
        fontName="Courier",
        fontSize=9,
        leading=13,
        wordWrap="LTR",
        alignment=TA_LEFT,
    )
    story = [Preformatted(text or "(empty document)", pre_style)]
    doc.build(story)

def _extract_odf_text(odf_doc) -> str:
    """Extract all text from an ODF document as plain text."""
    from odf import text as odf_text
    lines = []
    def recurse(element):
        if hasattr(element, "childNodes"):
            for child in element.childNodes:
                if child.nodeType == 3:  # Text node
                    lines.append(child.data)
                else:
                    recurse(child)
    recurse(odf_doc.body)
    return "\n".join(lines)

import zipfile
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def _validate_file_not_protected(file_bytes: bytes, ext: str):
    """Checks if a file is password protected using its raw bytes."""
    if ext in (".docx", ".xlsx", ".pptx", ".ods", ".odt"):
        bio = BytesIO(file_bytes)
        if not zipfile.is_zipfile(bio):
            # Check for OLE2 header (encrypted office docs)
            if file_bytes[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
                raise Exception("The file is password-protected and cannot be converted.")
        else:
            try:
                with zipfile.ZipFile(BytesIO(file_bytes)) as zf:
                    for info in zf.infolist():
                        if info.flag_bits & 0x1:
                            raise Exception("The file contains encrypted content and cannot be converted.")
            except Exception as e:
                if "password" in str(e).lower() or "encrypted" in str(e).lower():
                    raise e
    
    if ext == ".pdf" and fitz:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            is_enc = doc.is_encrypted
            doc.close()
            if is_enc:
                raise Exception("The PDF file is password-protected and cannot be converted.")
        except Exception as e:
            if "password" in str(e).lower():
                raise Exception("The PDF file is password-protected and cannot be converted.")

def _get_safe_filename(filename: str) -> str:
    if not filename:
        return None
    return os.path.basename(filename).replace(" ", "_")
