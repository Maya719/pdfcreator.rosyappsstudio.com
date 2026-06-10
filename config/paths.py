from pathlib import Path
import shutil

import os

BASE_DIR = Path(os.getcwd()).resolve()

PRIVATE_DIR = BASE_DIR / "storage" / "private"
PUBLIC_DIR = BASE_DIR / "storage" / "public"
LIBREOFFICE_BIN = (
    shutil.which("soffice")
    or r"C:\Program Files\LibreOffice\program\soffice.exe"
)
