"""Job registry — run subprocess commands and stream their output."""

import subprocess
import sys
import threading
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Job:
    def __init__(self, cmd: list):
        self.id = uuid.uuid4().hex[:8]
        self.cmd = cmd
        self.output: list[str] = []
        self.done = False
        self.returncode = None

    def run(self):
        try:
            proc = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=str(ROOT),
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            for line in proc.stdout:
                self.output.append(line.rstrip())
            proc.wait()
            self.returncode = proc.returncode
        except Exception as e:
            self.output.append(f"[ERROR] {e}")
            self.returncode = 1
        finally:
            self.done = True


_jobs: dict = {}
_jobs_lock = threading.Lock()


def _preprocess_cmd(cmd: list) -> list:
    """Replace 'python'/'python3' with sys.executable."""
    if isinstance(cmd, list) and cmd and cmd[0] in ("python", "python3"):
        return [sys.executable] + cmd[1:]
    return cmd


def start_job(cmd: list) -> str:
    cmd = _preprocess_cmd(cmd)
    job = Job(cmd)
    with _jobs_lock:
        _jobs[job.id] = job
    threading.Thread(target=job.run, daemon=True).start()
    return job.id


def get_job(job_id: str):
    with _jobs_lock:
        return _jobs.get(job_id)
