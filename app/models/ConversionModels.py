from pydantic import BaseModel
from typing import Optional

class HTMLToPDFRequest(BaseModel):
    html_content: str
    filename: Optional[str] = "document.pdf"


