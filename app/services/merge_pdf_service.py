import uuid
import shutil
import logging
from pathlib import Path
from pypdf import PdfWriter

from config.paths import PUBLIC_DIR
from config.app import APP_URL

logger = logging.getLogger(__name__)


def merge_pdfs(file_paths, output_filename=None):
    """Merge multiple PDF files into one. file_paths must be ordered correctly."""
    if not file_paths:
        raise ValueError("No files to merge")

    if output_filename is None:
        public_filename = "merged.pdf"
        counter = 1
        while (PUBLIC_DIR / public_filename).exists():
            public_filename = f"merged_{counter}.pdf"
            counter += 1
        output_filename = public_filename

    output_path = PUBLIC_DIR / output_filename
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    writer = PdfWriter()
    for path in file_paths:
        p = Path(path)
        if not p.exists():
            logger.warning(f"File not found, skipping: {p}")
            continue
        try:
            writer.append(str(p))
        except Exception as e:
            logger.warning(f"Failed to append {p}: {e}")
            raise

    writer.write(str(output_path))
    writer.close()

    return output_filename, f"{APP_URL}/storage/{output_filename}"
