from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = ROOT_DIR / "resources" / "views"
STORAGE_DIR = ROOT_DIR / "storage"
PUBLIC_DISK = STORAGE_DIR / "public"
PRIVATE_DISK = STORAGE_DIR / "private"
