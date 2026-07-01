import os
import uuid
import shutil
import logging
import json
import base64
import time
import requests
from pathlib import Path

from config.supported_formats import SUPPORTED_FORMATS
from config.paths import PUBLIC_DIR
from config.app import APP_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LibreOffice:

    @staticmethod
    def run_conversion(input_path_str, target_format, original_filename=None):
        target_format = target_format.lower().strip()

        if target_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported target format: {target_format}")

        runpod_api_key = os.getenv("RUNPOD_API_KEY")
        runpod_endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")

        if not runpod_api_key or not runpod_endpoint_id:
            raise RuntimeError("RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID must be configured in environment variables.")

        session_id = uuid.uuid4().hex
        input_path = Path(input_path_str)

        if not input_path.exists():
            raise FileNotFoundError(str(input_path))

        ext = input_path.suffix
        temp_input_filename = f"temp_{session_id}{ext}"
        temp_input_public_path = PUBLIC_DIR / temp_input_filename

        # Copy the private file to the public directory so Runpod can download it
        shutil.copy2(str(input_path), str(temp_input_public_path))
        file_url = f"{APP_URL}/storage/{temp_input_filename}"

        try:
            logger.info(f"Sending file {input_path.name} to Runpod for conversion via URL: {file_url}")

            # Call the Runpod API
            run_url = f"https://api.runpod.ai/v1/{runpod_endpoint_id}/runsync"
            headers = {
                "Authorization": f"Bearer {runpod_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": {
                    "file": file_url,
                    "target": target_format
                }
            }

            response = requests.post(run_url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            res_data = response.json()

            status = res_data.get("status")
            job_id = res_data.get("id")

            # If not completed immediately, poll for status
            if status in ["IN_QUEUE", "IN_PROGRESS"]:
                logger.info(f"Job {job_id} is in queue/progress, polling status...")
                status_url = f"https://api.runpod.ai/v1/{runpod_endpoint_id}/status/{job_id}"
                while status in ["IN_QUEUE", "IN_PROGRESS"]:
                    time.sleep(1.5)
                    status_resp = requests.get(status_url, headers=headers, timeout=30)
                    status_resp.raise_for_status()
                    res_data = status_resp.json()
                    status = res_data.get("status")

            if status != "COMPLETED":
                error_msg = res_data.get("error") or f"Runpod job failed with status: {status}"
                raise RuntimeError(error_msg)

            output = res_data.get("output", {})
            if isinstance(output, dict) and "error" in output:
                raise RuntimeError(f"Runpod worker error: {output['error']}")

            base64_result = output.get("base64")
            if not base64_result:
                raise RuntimeError("Response from Runpod did not contain 'base64' output.")

            # Decode the base64 output
            converted_bytes = base64.b64decode(base64_result)

            # Generate the final public file name
            if original_filename:
                base_name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
                base_name = base_name.replace(" ", "_")
                public_filename = f"converted_{base_name}.{target_format}"
                counter = 1
                while (PUBLIC_DIR / public_filename).exists():
                    public_filename = f"converted_{base_name}_{counter}.{target_format}"
                    counter += 1
            else:
                public_filename = f"{session_id}.{target_format}"

            public_path = PUBLIC_DIR / public_filename

            # Write the converted file bytes
            with open(public_path, "wb") as f:
                f.write(converted_bytes)

            return public_filename, f"{APP_URL}/storage/{public_filename}"

        finally:
            # Always clean up the temporary public input file
            if temp_input_public_path.exists():
                try:
                    os.remove(temp_input_public_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary public input file: {e}")
