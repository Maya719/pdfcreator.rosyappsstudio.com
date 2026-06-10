import json
import uuid
import threading
import queue
import time
import signal
import subprocess
import os
from pathlib import Path
from datetime import datetime, timezone
from config.paths import BASE_DIR, PRIVATE_DIR

JOBS_DIR = BASE_DIR / "storage" / "jobs"
UPLOADS_DIR = PRIVATE_DIR / "job_uploads"
MAX_JOB_TIME = 600
WATCHDOG_INTERVAL = 30


def kill_soffice():
    if os.name == 'nt':
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'soffice.exe', '/IM', 'soffice.bin', '/T'],
                           capture_output=True, timeout=10, startupinfo=si)
        except Exception:
            pass
    else:
        for cmd in [['killall', '-9', 'soffice', 'soffice.bin'], ['pkill', '-9', '-f', 'soffice']]:
            try:
                subprocess.run(cmd, capture_output=True, timeout=10)
            except Exception:
                pass


class JobManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        JOBS_DIR.mkdir(parents=True, exist_ok=True)
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        self._queue = queue.Queue()
        self._file_lock = threading.Lock()
        self._active_jobs = {}
        self._active_lock = threading.Lock()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()
        self._watchdog = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._watchdog.start()

    def create_job(self, original_filename):
        job_id = "job" + uuid.uuid4().hex[:8]
        job = {
            "id": job_id,
            "status": "pending",
            "original_filename": original_filename,
            "result_filename": None,
            "result_url": None,
            "error": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        self._save_job(job)
        return job_id

    def get_job(self, job_id):
        job_path = JOBS_DIR / f"{job_id}.json"
        if job_path.exists():
            with self._file_lock:
                with open(job_path, encoding="utf-8") as f:
                    return json.load(f)
        return None

    def update_job(self, job_id, **kwargs):
        job_path = JOBS_DIR / f"{job_id}.json"
        if not job_path.exists():
            return
        with self._file_lock:
            with open(job_path, encoding="utf-8") as f:
                job = json.load(f)
            job.update(kwargs)
            with open(job_path, "w", encoding="utf-8") as f:
                json.dump(job, f, indent=2, ensure_ascii=False)

    def enqueue(self, job_id, input_path, target_format):
        self._queue.put((job_id, input_path, target_format))

    def _save_job(self, job):
        with self._file_lock:
            path = JOBS_DIR / f"{job['id']}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(job, f, indent=2, ensure_ascii=False)

    def _worker_loop(self):
        while True:
            try:
                job_id, input_path, target_format = self._queue.get(timeout=1)
                self._process_job(job_id, input_path, target_format)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Worker] Unexpected error: {e}")

    def _process_job(self, job_id, input_path, target_format):
        self.update_job(job_id, status="processing")
        with self._active_lock:
            self._active_jobs[job_id] = time.time()
        try:
            if target_format == "merge":
                from app.services.merge_pdf_service import merge_pdfs
                job_data = self.get_job(job_id)
                file_order = job_data.get("file_order", [])
                file_paths = [item["path"] for item in file_order]
                public_filename, url = merge_pdfs(file_paths, f"{job_id}.pdf")
            else:
                from app.services.converters.libreoffice import LibreOffice
                public_filename, url = LibreOffice.run_conversion(input_path, target_format)
            self.update_job(
                job_id,
                status="completed",
                result_filename=public_filename,
                result_url=url,
                completed_at=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            self.update_job(
                job_id,
                status="failed",
                error=str(e),
                completed_at=datetime.now(timezone.utc).isoformat()
            )
        finally:
            with self._active_lock:
                self._active_jobs.pop(job_id, None)

    def _watchdog_loop(self):
        while True:
            time.sleep(WATCHDOG_INTERVAL)
            now = time.time()
            with self._active_lock:
                stalled = [
                    jid for jid, start in self._active_jobs.items()
                    if now - start > MAX_JOB_TIME
                ]
            for jid in stalled:
                print(f"[Watchdog] Job {jid} exceeded {MAX_JOB_TIME}s — killing soffice")
                kill_soffice()
                self.update_job(
                    jid,
                    status="failed",
                    error=f"Conversion timed out after {MAX_JOB_TIME // 60} minutes",
                    completed_at=datetime.now(timezone.utc).isoformat()
                )
                with self._active_lock:
                    self._active_jobs.pop(jid, None)
