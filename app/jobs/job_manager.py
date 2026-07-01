import json
import uuid
import threading
import time
from pathlib import Path
from datetime import datetime, timezone
from config.paths import BASE_DIR, PRIVATE_DIR
from config.redis import redis

JOBS_DIR = BASE_DIR / "storage" / "jobs"
UPLOADS_DIR = PRIVATE_DIR / "job_uploads"
MAX_JOB_TIME = 600
WATCHDOG_INTERVAL = 30
REDIS_JOB_PREFIX = "job:"
REDIS_QUEUE_KEY = "job:queue"
REDIS_ACTIVE_KEY = "active:jobs"


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
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()
        self._watchdog = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._watchdog.start()

    def _job_key(self, job_id):
        return f"{REDIS_JOB_PREFIX}{job_id}"

    def create_job(self, original_filename):
        job_id = "job" + uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc).isoformat()
        job = {
            "id": job_id,
            "status": "pending",
            "original_filename": original_filename,
            "result_filename": "",
            "result_url": "",
            "error": "",
            "created_at": now,
            "completed_at": "",
        }
        redis.hset(self._job_key(job_id), mapping=job)
        return job_id

    def get_job(self, job_id):
        data = redis.hgetall(self._job_key(job_id))
        if not data:
            return None
        if "file_order" in data:
            try:
                data["file_order"] = json.loads(data["file_order"])
            except (json.JSONDecodeError, TypeError):
                data["file_order"] = []
        return data

    def update_job(self, job_id, **kwargs):
        key = self._job_key(job_id)
        if not redis.exists(key):
            return
        mapping = {}
        for k, v in kwargs.items():
            if not isinstance(v, str):
                mapping[k] = json.dumps(v, ensure_ascii=False)
            else:
                mapping[k] = v
        if mapping:
            redis.hset(key, mapping=mapping)

    def enqueue(self, job_id, input_path, target_format):
        payload = json.dumps([job_id, input_path, target_format], ensure_ascii=False)
        redis.rpush(REDIS_QUEUE_KEY, payload)

    def _worker_loop(self):
        while True:
            try:
                result = redis.blpop(REDIS_QUEUE_KEY, timeout=1)
                if result is None:
                    continue
                _, payload = result
                job_id, input_path, target_format = json.loads(payload)
                self._process_job(job_id, input_path, target_format)
            except Exception as e:
                print(f"[Worker] Unexpected error: {e}")

    def _process_job(self, job_id, input_path, target_format):
        self.update_job(job_id, status="processing")
        redis.hset(REDIS_ACTIVE_KEY, job_id, str(time.time()))
        try:
            if target_format == "merge":
                from app.services.merge_pdf_service import merge_pdfs

                job_data = self.get_job(job_id)
                file_paths = [
                    item["path"] for item in (job_data.get("file_order") or [])
                ]
                public_filename, url = merge_pdfs(file_paths)
            else:
                from app.services.converters.libreoffice import LibreOffice

                job_data = self.get_job(job_id)
                original_filename = job_data.get("original_filename", "")
                public_filename, url = LibreOffice.run_conversion(
                    input_path, target_format, original_filename
                )
            self.update_job(
                job_id,
                status="completed",
                result_filename=public_filename,
                result_url=url,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            self.update_job(
                job_id,
                status="failed",
                error=str(e),
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
        finally:
            redis.hdel(REDIS_ACTIVE_KEY, job_id)

    def _watchdog_loop(self):
        while True:
            time.sleep(WATCHDOG_INTERVAL)
            now = time.time()
            try:
                active = redis.hgetall(REDIS_ACTIVE_KEY)
                for jid, start_str in active.items():
                    try:
                        start = float(start_str)
                    except (ValueError, TypeError):
                        continue
                    if now - start > MAX_JOB_TIME:
                        print(
                            f"[Watchdog] Job {jid} exceeded {MAX_JOB_TIME}s — marking as failed"
                        )
                        self.update_job(
                            jid,
                            status="failed",
                            error=f"Conversion timed out after {MAX_JOB_TIME // 60} minutes",
                            completed_at=datetime.now(timezone.utc).isoformat(),
                        )
                        redis.hdel(REDIS_ACTIVE_KEY, jid)
            except Exception as e:
                print(f"[Watchdog] Error: {e}")
