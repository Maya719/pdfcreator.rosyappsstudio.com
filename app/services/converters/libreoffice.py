import os
import uuid
import shutil
import logging
import subprocess
import json

from pathlib import Path

from config.supported_formats import SUPPORTED_FORMATS
from config.paths import PRIVATE_DIR, PUBLIC_DIR, LIBREOFFICE_BIN
from config.app import APP_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LibreOffice:

    # Font substitution table — maps Windows fonts to metric-compatible Linux fonts
    # Carlito ≈ Calibri, Caladea ≈ Cambria, Liberation ≈ Arial/Times/Courier
    FONT_SUBS_XCU = '''<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry"
           xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <item oor:path="/org.openoffice.VCL/FontSubstitution">
    <prop oor:name="FontSubstituteTable" oor:op="fuse">
      <value>
        <it><prop oor:name="SubstituteFont"><value>Carlito</value></prop><prop oor:name="OriginalFont"><value>Calibri</value></prop></it>
        <it><prop oor:name="SubstituteFont"><value>Caladea</value></prop><prop oor:name="OriginalFont"><value>Cambria</value></prop></it>
        <it><prop oor:name="SubstituteFont"><value>Liberation Sans</value></prop><prop oor:name="OriginalFont"><value>Arial</value></prop></it>
        <it><prop oor:name="SubstituteFont"><value>Liberation Serif</value></prop><prop oor:name="OriginalFont"><value>Times New Roman</value></prop></it>
        <it><prop oor:name="SubstituteFont"><value>Liberation Mono</value></prop><prop oor:name="OriginalFont"><value>Courier New</value></prop></it>
        <it><prop oor:name="SubstituteFont"><value>DejaVu Sans</value></prop><prop oor:name="OriginalFont"><value>Verdana</value></prop></it>
        <it><prop oor:name="SubstituteFont"><value>DejaVu Sans</value></prop><prop oor:name="OriginalFont"><value>Tahoma</value></prop></it>
        <it><prop oor:name="SubstituteFont"><value>DejaVu Sans</value></prop><prop oor:name="OriginalFont"><value>Segoe UI</value></prop></it>
      </value>
    </prop>
  </item>
</oor:items>'''

    @staticmethod
    def _prepare_environment(private_dir, profile_dir):
        """Builds a clean environment for LibreOffice subprocess"""
        env = os.environ.copy()

        # Prevent app's Python from leaking into LibreOffice's embedded Python
        for var in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONNOUSERSITE']:
            env.pop(var, None)

        env['HOME'] = str(private_dir.resolve())

        # Headless rendering
        env['SAL_USE_VCLPLUGIN'] = 'svp'
        if os.name != 'nt':
            env['DISPLAY'] = ':99'

        env['OOO_DISABLE_RECOVERY'] = '1'
    
        return env

    @staticmethod
    def kill_soffice_processes():
        try:
            if os.name == "nt":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = subprocess.SW_HIDE

                for p in ["soffice.exe", "soffice.bin"]:
                    try:
                        subprocess.run(
                            ["taskkill", "/F", "/T", "/IM", p],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=10,
                            startupinfo=si,
                        )
                    except Exception:
                        pass
            else:
                for cmd in (
                    ["pkill", "-9", "-f", "soffice"],
                    ["killall", "-9", "soffice"],
                    ["killall", "-9", "soffice.bin"],
                ):
                    try:
                        subprocess.run(
                            cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=10,
                        )
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"cleanup error: {e}")

    @staticmethod
    def run_conversion(input_path_str, target_format):
        target_format = target_format.lower().strip()

        if target_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported target format: {target_format}")

        libreoffice_path = Path(LIBREOFFICE_BIN)

        if not libreoffice_path.exists():
            raise RuntimeError(f"LibreOffice not found: {LIBREOFFICE_BIN}")

        session_id = uuid.uuid4().hex

        private_dir = PRIVATE_DIR / session_id
        profile_dir = private_dir / "profile"

        private_dir.mkdir(parents=True, exist_ok=True)
        profile_dir.mkdir(parents=True, exist_ok=True)
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

        # Write font substitution table so LibreOffice maps Calibri→Carlito etc.
        user_dir = profile_dir / "user"
        user_dir.mkdir(parents=True, exist_ok=True)
        with open(user_dir / "registrymodifications.xcu", "w", encoding="utf-8") as f:
            f.write(LibreOffice.FONT_SUBS_XCU)

        process = None

        try:
            input_path = Path(input_path_str)

            if not input_path.exists():
                raise FileNotFoundError(str(input_path))

            logger.info(f"Processing {input_path.name}")

            env = LibreOffice._prepare_environment(private_dir, profile_dir)

            if target_format == "pdf":
                export_filter = (
                    'pdf:writer_pdf_Export:'
                    '{"SelectPdfVersion":1,"EmbedStandardFonts":true,'
                    '"FontEmbedding":true,"Quality":100,"ReduceImageResolution":false,'
                    '"MaxImageResolution":600,"JPEGQuality":100}'
                )
            else:
                export_filter = target_format

            profile_url = profile_dir.resolve().as_uri()

            cmd = [
                str(libreoffice_path),
                f"-env:UserInstallation={profile_url}",
                "--headless",
                "--invisible",
                "--norestore",
                "--nolockcheck",
                "--nofirststartwizard",
                "--convert-to",
                export_filter,
                "--outdir",
                str(private_dir),
                str(input_path.resolve()),
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                cwd=str(private_dir),
            )

            try:
                stdout, stderr = process.communicate(timeout=600)

            except subprocess.TimeoutExpired:
                process.kill()
                LibreOffice.kill_soffice_processes()
                raise TimeoutError("Conversion timeout")

            if process.returncode != 0:
                raise RuntimeError(stderr or stdout)

            converted_files = list(private_dir.glob(f"*.{target_format}"))

            if not converted_files:
                raise RuntimeError("Output file not found")

            converted_file = converted_files[0]

            public_filename = f"{session_id}.{target_format}"
            public_path = PUBLIC_DIR / public_filename

            shutil.move(str(converted_file), str(public_path))

            return public_filename, f"{APP_URL}/storage/{public_filename}"

        finally:
            try:
                if process and process.poll() is None:
                    process.kill()
            except Exception:
                pass

            LibreOffice.kill_soffice_processes()
            shutil.rmtree(private_dir, ignore_errors=True)
