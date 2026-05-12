from pydantic import BaseModel
from typing import Optional

class PDFRequest(BaseModel):
    html_content: str
    filename: Optional[str] = "document.pdf"
