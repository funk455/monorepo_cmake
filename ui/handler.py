"""HTTP request handler — routing, GET/POST, SSE streaming."""

import importlib.util
import json
import os
import shutil
import time
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .jobs import start_job, get_job
from .parsers import (
    list_projects, list_build_dirs, list_reports,
    parse_target_graph, parse_test_results,
    list_toolchains, read_toolchain, save_toolchain, delete_toolchain,
)

ROOT = Path(__file__).resolve().parent.parent
_HTML_PATH = Path(__file__).resolve().parent / "static" / "index.html"


def _load_html() -> str:
    return _HTML_PATH.read_text(encoding="utf-8")


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # suppress access log

    # ── Response helpers ──────────────────────────────────────────────────────

    def send_json(self, data, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html: str):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self) -> str:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode() if n else ""

    # ── CORS preflight ────────────────────────────────────────────────────────

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── GET ───────────────────────────────────────────────────────────────────

    def do_GET(self):
        p = urlparse(self.path)
        qs = parse_qs(p.query)
        route = p.path

        if route == "/":
            self.send_html(_load_html())

        elif route == "/api/projects":
            self.send_json(list_projects())

        elif route == "/api/build-dirs":
            self.send_json(list_build_dirs())

        elif route == "/api/reports":
            self.send_json(list_reports())

        elif route == "/api/report":
            rel = qs.get("path", [None])[0]
            if not rel:
                self.send_json({"error": "missing path"}, 400)
                return
            fp = (ROOT / rel).resolve()
            if fp.exists() and fp.is_file() and str(fp).startswith(str(ROOT)):
                self.send_json({"content": fp.read_text(encoding="utf-8", errors="replace")})
            else:
                self.send_json({"error": "not found"}, 404)

        elif route == "/api/target-graph":
            try:
                self.send_json(parse_target_graph())
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        elif route == "/api/preset":
            preset_path = ROOT / "preset.json"
            if preset_path.exists():
                try:
                    self.send_json(json.loads(preset_path.read_text(encoding="utf-8")))
                except Exception as e:
                    self.send_json({"error": str(e)}, 500)
            else:
                self.send_json({})

        elif route == "/api/test-results":
            build = qs.get("build", [None])[0]
            if not build:
                self.send_json({"error": "missing build"}, 400)
                return
            build_path = (ROOT / build).resolve()
            if not str(build_path).startswith(str(ROOT.resolve())):
                self.send_json({"error": "invalid path"}, 400)
                return
            result = parse_test_results(build_path)
            self.send_json(result if result is not None else {})

        elif route == "/api/toolchains":
            self.send_json(list_toolchains())

        elif route == "/api/toolchain":
            name = qs.get("name", [None])[0]
            if not name:
                self.send_json({"error": "missing name"}, 400)
                return
            self.send_json(read_toolchain(name))

        elif route == "/api/stream":
            job_id = qs.get("job", [None])[0]
            if job_id:
                self._stream_sse(job_id)
            else:
                self.send_json({"error": "missing job"}, 400)

        else:
            self.send_json({"error": "not found"}, 404)

    # ── POST ──────────────────────────────────────────────────────────────────

    def do_POST(self):
        route = urlparse(self.path).path
        body = self.read_body()
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json({"error": "invalid JSON"}, 400)
            return

        if route == "/api/run":
            cmd = data.get("cmd")
            if not cmd:
                self.send_json({"error": "missing cmd"}, 400)
                return
            self.send_json({"job_id": start_job(cmd)})

        elif route == "/api/new-project":
            self._handle_new_project(data)

        elif route == "/api/delete":
            self._handle_delete(data)

        elif route == "/api/toolchain":
            name = data.get("name", "").strip()
            content = data.get("content", "")
            if not name:
                self.send_json({"error": "missing name"}, 400)
                return
            self.send_json(save_toolchain(name, content))

        elif route == "/api/toolchain/delete":
            name = data.get("name", "").strip()
            if not name:
                self.send_json({"error": "missing name"}, 400)
                return
            self.send_json(delete_toolchain(name))

        else:
            self.send_json({"error": "not found"}, 404)

    # ── Route handlers ────────────────────────────────────────────────────────

    def _handle_new_project(self, data: dict):
        try:
            spec = importlib.util.spec_from_file_location(
                "cli", str(ROOT / "cmake" / "cli.py")
            )
            cli = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cli)
            cli.generate_from_config(ROOT, data, force=data.get("force", False))
            if data.get("save_preset", False):
                save_data = {k: v for k, v in data.items()
                             if k not in ("force", "save_preset")}
                (ROOT / "preset.json").write_text(
                    json.dumps(save_data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            self.send_json({"ok": True})
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def _handle_delete(self, data: dict):
        kind = data.get("kind")
        path = data.get("path", "").strip().replace("\\", "/")
        if not kind or not path:
            self.send_json({"error": "missing kind or path"}, 400)
            return

        target = (ROOT / path).resolve()
        root_s = str(ROOT.resolve())
        if not str(target).startswith(root_s + os.sep) or target == ROOT.resolve():
            self.send_json({"error": "invalid path"}, 400)
            return

        try:
            rel_parts = target.relative_to(ROOT).parts
        except ValueError:
            self.send_json({"error": "invalid path"}, 400)
            return

        if kind == "project":
            if len(rel_parts) != 2 or rel_parts[0] != "projects":
                self.send_json({"error": "invalid project path"}, 400)
                return
        elif kind == "module":
            if len(rel_parts) != 3 or rel_parts[0] != "projects":
                self.send_json({"error": "invalid module path"}, 400)
                return
        elif kind == "build":
            if len(rel_parts) != 1 or not (
                rel_parts[0] == "build"
                or rel_parts[0].startswith("build-")
                or rel_parts[0].startswith("build_")
            ):
                self.send_json({"error": "invalid build dir"}, 400)
                return
        else:
            self.send_json({"error": "unknown kind"}, 400)
            return

        if not target.exists():
            self.send_json({"error": "path not found"}, 404)
            return

        try:
            shutil.rmtree(str(target))
            self.send_json({"ok": True})
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    # ── SSE streaming ─────────────────────────────────────────────────────────

    def _stream_sse(self, job_id: str):
        job = get_job(job_id)
        if not job:
            self.send_json({"error": "job not found"}, 404)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        offset = 0
        try:
            while True:
                new_lines = job.output[offset:]
                if new_lines:
                    for line in new_lines:
                        self.wfile.write(
                            f"event: line\ndata: {json.dumps(line)}\n\n".encode()
                        )
                    offset += len(new_lines)
                    self.wfile.flush()

                if job.done and offset >= len(job.output):
                    self.wfile.write(
                        f"event: done\ndata: {json.dumps(str(job.returncode))}\n\n".encode()
                    )
                    self.wfile.flush()
                    break

                if not job.done:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    time.sleep(0.15)

        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
