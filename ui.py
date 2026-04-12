#!/usr/bin/env python3
"""
CMake Workspace UI — web dashboard for monorepo-cmake-sample.
No external dependencies required (Python 3.7+).

Usage:
  python ui.py [--port 8080] [--host 127.0.0.1]
  Then open http://localhost:8080
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    from http.server import ThreadingHTTPServer
except ImportError:
    import socketserver
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
        daemon_threads = True

ROOT = Path(__file__).resolve().parent

# ─── Job registry ─────────────────────────────────────────────────────────────

class Job:
    def __init__(self, cmd):
        self.id = uuid.uuid4().hex[:8]
        self.cmd = cmd
        self.output = []
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


def start_job(cmd) -> str:
    cmd = _preprocess_cmd(cmd)
    job = Job(cmd)
    with _jobs_lock:
        _jobs[job.id] = job
    threading.Thread(target=job.run, daemon=True).start()
    return job.id


def get_job(job_id):
    with _jobs_lock:
        return _jobs.get(job_id)


def _preprocess_cmd(cmd):
    """Replace 'python'/'python3' with sys.executable."""
    if isinstance(cmd, list) and cmd and cmd[0] in ("python", "python3"):
        return [sys.executable] + cmd[1:]
    return cmd


# ─── Discovery helpers ────────────────────────────────────────────────────────

def list_projects():
    projects_dir = ROOT / "projects"
    if not projects_dir.exists():
        return []
    result = []
    for proj in sorted(projects_dir.iterdir()):
        if not proj.is_dir():
            continue
        modules = []
        for mod in sorted(proj.iterdir()):
            if mod.is_dir() and (mod / "CMakeLists.txt").exists():
                modules.append(mod.name)
        result.append({
            "name": proj.name,
            "modules": modules,
            "path": str(proj.relative_to(ROOT)).replace("\\", "/"),
        })
    return result


def list_build_dirs():
    result = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir():
            continue
        n = d.name
        if n == "build" or n.startswith("build-") or n.startswith("build_"):
            result.append({
                "name": n,
                "configured": (d / "CMakeCache.txt").exists(),
                "path": str(d.relative_to(ROOT)).replace("\\", "/"),
            })
    return result


def list_reports():
    result = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir():
            continue
        rdir = d / "reports"
        if rdir.exists():
            for f in sorted(rdir.iterdir()):
                if f.is_file():
                    result.append({
                        "name": f.name,
                        "build_dir": d.name,
                        "path": str(f.relative_to(ROOT)).replace("\\", "/"),
                    })
    return result


# ─── HTTP Handler ─────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress access log

    def send_json(self, data, status=200):
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

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path)
        qs = parse_qs(p.query)
        route = p.path

        if route == "/":
            self.send_html(HTML)
        elif route == "/api/projects":
            self.send_json(list_projects())
        elif route == "/api/build-dirs":
            self.send_json(list_build_dirs())
        elif route == "/api/reports":
            self.send_json(list_reports())
        elif route == "/api/report":
            rel = qs.get("path", [None])[0]
            if rel:
                fp = (ROOT / rel).resolve()
                if fp.exists() and fp.is_file() and str(fp).startswith(str(ROOT)):
                    self.send_json({"content": fp.read_text(encoding="utf-8", errors="replace")})
                else:
                    self.send_json({"error": "not found"}, 404)
            else:
                self.send_json({"error": "missing path"}, 400)
        elif route == "/api/stream":
            job_id = qs.get("job", [None])[0]
            if job_id:
                self._stream_sse(job_id)
            else:
                self.send_json({"error": "missing job"}, 400)
        else:
            self.send_json({"error": "not found"}, 404)

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
            job_id = start_job(cmd)
            self.send_json({"job_id": job_id})

        elif route == "/api/new-project":
            try:
                spec = importlib.util.spec_from_file_location(
                    "cli", str(ROOT / "cmake" / "cli.py")
                )
                cli = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cli)
                cli.generate_from_config(ROOT, data, force=data.get("force", False))
                self.send_json({"ok": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        elif route == "/api/delete":
            import shutil
            kind = data.get("kind")
            path = data.get("path", "").strip().replace("\\", "/")
            if not kind or not path:
                self.send_json({"error": "missing kind or path"}, 400)
                return
            target = (ROOT / path).resolve()
            root_s = str(ROOT.resolve())
            # Safety: target must be strictly inside ROOT
            if not str(target).startswith(root_s + os.sep) or target.resolve() == ROOT.resolve():
                self.send_json({"error": "invalid path"}, 400)
                return
            try:
                rel_parts = target.relative_to(ROOT).parts
            except ValueError:
                self.send_json({"error": "invalid path"}, 400)
                return
            if kind == "module":
                # Must be projects/<project>/<module>  (3 parts)
                if len(rel_parts) != 3 or rel_parts[0] != "projects":
                    self.send_json({"error": "invalid module path"}, 400)
                    return
            elif kind == "build":
                # Must be a top-level build dir
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

        else:
            self.send_json({"error": "not found"}, 404)

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
                        msg = f"event: line\ndata: {json.dumps(line)}\n\n"
                        self.wfile.write(msg.encode())
                    offset += len(new_lines)
                    self.wfile.flush()

                if job.done and offset >= len(job.output):
                    msg = f"event: done\ndata: {json.dumps(str(job.returncode))}\n\n"
                    self.wfile.write(msg.encode())
                    self.wfile.flush()
                    break

                if not job.done:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    time.sleep(0.15)

        except (BrokenPipeError, ConnectionResetError, OSError):
            pass


# ─── Embedded HTML ────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CMake Workspace UI</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  *{box-sizing:border-box}
  body{font-family:system-ui,sans-serif}
  .log{font-family:'Cascadia Code','Courier New',monospace;font-size:12px;line-height:1.6}
  input,select,textarea{background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:0.375rem}
  input:focus,select:focus,textarea:focus{outline:none;border-color:#3b82f6;box-shadow:0 0 0 1px #3b82f6}
  ::-webkit-scrollbar{width:5px;height:5px}
  ::-webkit-scrollbar-track{background:#0f172a}
  ::-webkit-scrollbar-thumb{background:#334155;border-radius:3px}
  .nav-item{display:flex;align-items:center;gap:0.5rem;width:100%;text-align:left;padding:0.45rem 0.75rem;border-radius:0.375rem;font-size:0.875rem;color:#94a3b8;transition:all 0.15s;cursor:pointer;border:none;background:none}
  .nav-item:hover{background:#1e293b;color:#e2e8f0}
  .nav-item.active{background:#1e3a5f;color:#60a5fa;font-weight:500}
  .btn{padding:0.4rem 1rem;border-radius:0.375rem;font-size:0.875rem;font-weight:500;cursor:pointer;border:none;transition:all 0.15s}
  .btn:disabled{opacity:0.5;cursor:not-allowed}
  .btn-blue{background:#1d4ed8;color:#fff}.btn-blue:hover:not(:disabled){background:#1e40af}
  .btn-slate{background:#334155;color:#cbd5e1}.btn-slate:hover:not(:disabled){background:#475569}
  .btn-red{background:#7f1d1d;color:#fca5a5}.btn-red:hover:not(:disabled){background:#991b1b}
  .btn-green{background:#14532d;color:#86efac}.btn-green:hover:not(:disabled){background:#166534}
  .card{background:#0f172a;border:1px solid #1e293b;border-radius:0.5rem;padding:1rem}
  .section-title{font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:#64748b;margin-bottom:0.75rem}
  .tag{display:inline-block;padding:0.1rem 0.5rem;border-radius:9999px;font-size:0.7rem;font-weight:500}
  .tag-green{background:#14532d;color:#86efac}
  .tag-gray{background:#1e293b;color:#94a3b8}
</style>
</head>
<body class="bg-gray-950 text-gray-200 flex h-screen overflow-hidden">

<!-- Sidebar -->
<aside class="w-48 bg-gray-900 border-r border-gray-800 flex flex-col shrink-0">
  <div class="p-4 border-b border-gray-800">
    <div class="text-xs text-gray-500 tracking-widest uppercase mb-1">Workspace</div>
    <div class="text-sm font-mono text-green-400 font-semibold truncate">monorepo-cmake</div>
  </div>
  <nav class="flex-1 p-2 space-y-0.5 overflow-y-auto">
    <button class="nav-item active" data-page="dashboard" onclick="navigate('dashboard')">
      <span>⊞</span> Dashboard
    </button>
    <button class="nav-item" data-page="build" onclick="navigate('build')">
      <span>⚙</span> Build
    </button>
    <button class="nav-item" data-page="new-project" onclick="navigate('new-project')">
      <span>＋</span> New Project
    </button>
    <button class="nav-item" data-page="watch" onclick="navigate('watch')">
      <span>◉</span> Watch Mode
    </button>
    <button class="nav-item" data-page="reports" onclick="navigate('reports')">
      <span>▤</span> Reports
    </button>
  </nav>
  <div class="p-3 border-t border-gray-800 text-xs text-gray-600">CMake UI · Python</div>
</aside>

<!-- Main -->
<main class="flex-1 overflow-hidden flex flex-col min-w-0">

<!-- ── Dashboard ── -->
<div id="page-dashboard" class="page flex-1 overflow-auto p-6 space-y-6">
  <div class="flex items-center justify-between">
    <h1 class="text-lg font-semibold">Dashboard</h1>
    <button class="btn btn-slate text-xs" onclick="loadDashboard()">↻ Refresh</button>
  </div>
  <div>
    <div class="section-title">Projects</div>
    <div id="dash-projects" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3"></div>
  </div>
  <div>
    <div class="section-title">Build Directories</div>
    <div id="dash-builds" class="space-y-2"></div>
  </div>
</div>

<!-- ── Build ── -->
<div id="page-build" class="page hidden flex-1 overflow-hidden flex flex-col">
  <div class="p-6 pb-4 border-b border-gray-800">
    <h1 class="text-lg font-semibold mb-4">Build</h1>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
      <label class="block">
        <div class="text-xs text-gray-400 mb-1">Build Dir</div>
        <input id="b-dir" type="text" value="build" class="w-full px-2.5 py-1.5 text-sm">
      </label>
      <label class="block">
        <div class="text-xs text-gray-400 mb-1">Generator</div>
        <select id="b-gen" class="w-full px-2.5 py-1.5 text-sm">
          <option value="">(default)</option>
          <option>Ninja</option>
          <option>Unix Makefiles</option>
          <option>Visual Studio 17 2022</option>
          <option>Visual Studio 16 2019</option>
        </select>
      </label>
      <label class="block">
        <div class="text-xs text-gray-400 mb-1">Build Type</div>
        <select id="b-type" class="w-full px-2.5 py-1.5 text-sm">
          <option>Release</option>
          <option>Debug</option>
          <option>RelWithDebInfo</option>
          <option>MinSizeRel</option>
        </select>
      </label>
      <label class="block">
        <div class="text-xs text-gray-400 mb-1">Config (multi-gen)</div>
        <select id="b-config" class="w-full px-2.5 py-1.5 text-sm">
          <option value="">—</option>
          <option>Release</option>
          <option>Debug</option>
        </select>
      </label>
    </div>
    <div class="flex items-end gap-3 mb-3">
      <label class="block flex-1">
        <div class="text-xs text-gray-400 mb-1">Extra CMake Flags</div>
        <input id="b-extra" type="text" placeholder="-DFOO=bar" class="w-full px-2.5 py-1.5 text-sm">
      </label>
    </div>
    <div class="flex flex-wrap gap-2 items-center">
      <button class="btn btn-blue" onclick="runBuildAction('configure')">Configure</button>
      <button class="btn btn-blue" onclick="runBuildAction('build')">Build</button>
      <button class="btn btn-blue" onclick="runBuildAction('test')">Test</button>
      <button class="btn btn-slate" onclick="runBuildAction('report-all')">Report</button>
      <button class="btn btn-slate" onclick="runBuildAction('install')">Install</button>
      <button class="btn btn-red" onclick="runBuildAction('uninstall')">Uninstall</button>
      <button class="btn btn-slate ml-auto text-xs" onclick="document.getElementById('build-log').textContent=''">Clear log</button>
    </div>
    <div id="build-status" class="mt-2 text-sm hidden"></div>
  </div>
  <div class="flex-1 overflow-hidden p-6 pt-4">
    <div id="build-log" class="log h-full bg-gray-950 border border-gray-800 rounded p-3 overflow-auto whitespace-pre-wrap text-green-300"></div>
  </div>
</div>

<!-- ── New Project ── -->
<div id="page-new-project" class="page hidden flex-1 overflow-auto p-6">
  <h1 class="text-lg font-semibold mb-5">New Project</h1>
  <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
    <div class="space-y-4">
      <div class="card space-y-3">
        <div class="section-title">Project Info</div>
        <label class="block">
          <div class="text-xs text-gray-400 mb-1">Project Name <span class="text-red-400">*</span></div>
          <input id="np-name" type="text" placeholder="myproject" class="w-full px-2.5 py-1.5 text-sm" oninput="updatePreview()">
        </label>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <div class="text-xs text-gray-400 mb-1">Version</div>
            <input id="np-ver" type="text" value="0.1.0" class="w-full px-2.5 py-1.5 text-sm">
          </label>
          <label class="block">
            <div class="text-xs text-gray-400 mb-1">Namespace</div>
            <input id="np-ns" type="text" placeholder="(= name)" class="w-full px-2.5 py-1.5 text-sm" oninput="updatePreview()">
          </label>
        </div>
      </div>

      <div class="card space-y-3">
        <div class="section-title">Modules</div>
        <!-- Library -->
        <div>
          <label class="flex items-center gap-2 cursor-pointer mb-2">
            <input id="np-lib" type="checkbox" checked class="w-4 h-4 accent-blue-500" onchange="toggleSection('lib'); updatePreview()">
            <span class="text-sm font-medium">Library target</span>
          </label>
          <div id="np-lib-fields" class="ml-6 grid grid-cols-2 gap-2">
            <label class="block">
              <div class="text-xs text-gray-400 mb-1">Dir name</div>
              <input id="np-lib-dir" type="text" placeholder="(= name)" class="w-full px-2.5 py-1.5 text-xs" oninput="updatePreview()">
            </label>
            <label class="block">
              <div class="text-xs text-gray-400 mb-1">Target name</div>
              <input id="np-lib-target" type="text" placeholder="(= name)" class="w-full px-2.5 py-1.5 text-xs" oninput="updatePreview()">
            </label>
          </div>
        </div>
        <!-- App -->
        <div>
          <label class="flex items-center gap-2 cursor-pointer mb-2">
            <input id="np-app" type="checkbox" checked class="w-4 h-4 accent-blue-500" onchange="toggleSection('app'); updatePreview()">
            <span class="text-sm font-medium">Application target</span>
          </label>
          <div id="np-app-fields" class="ml-6 grid grid-cols-2 gap-2">
            <label class="block">
              <div class="text-xs text-gray-400 mb-1">Dir name</div>
              <input id="np-app-dir" type="text" value="app" class="w-full px-2.5 py-1.5 text-xs" oninput="updatePreview()">
            </label>
            <label class="block">
              <div class="text-xs text-gray-400 mb-1">Target name</div>
              <input id="np-app-target" type="text" placeholder="(= name_app)" class="w-full px-2.5 py-1.5 text-xs" oninput="updatePreview()">
            </label>
          </div>
        </div>
        <!-- Tests -->
        <div>
          <label class="flex items-center gap-2 cursor-pointer mb-2">
            <input id="np-test" type="checkbox" checked class="w-4 h-4 accent-blue-500" onchange="toggleSection('test'); updatePreview()">
            <span class="text-sm font-medium">Test target</span>
          </label>
          <div id="np-test-fields" class="ml-6 grid grid-cols-2 gap-2">
            <label class="block">
              <div class="text-xs text-gray-400 mb-1">Dir name</div>
              <input id="np-test-dir" type="text" value="tests/smoke" class="w-full px-2.5 py-1.5 text-xs" oninput="updatePreview()">
            </label>
            <label class="block">
              <div class="text-xs text-gray-400 mb-1">Target name</div>
              <input id="np-test-target" type="text" placeholder="(= name_smoke)" class="w-full px-2.5 py-1.5 text-xs" oninput="updatePreview()">
            </label>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button class="btn btn-blue" onclick="submitNewProject()">Generate Project</button>
        <label class="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
          <input id="np-force" type="checkbox" class="w-4 h-4 accent-yellow-500">
          Force overwrite
        </label>
      </div>
      <div id="np-status" class="text-sm hidden"></div>
    </div>

    <div>
      <div class="section-title">Generated Structure Preview</div>
      <div id="np-preview" class="log card text-xs text-blue-300 min-h-48 whitespace-pre overflow-auto"></div>
    </div>
  </div>
</div>

<!-- ── Watch ── -->
<div id="page-watch" class="page hidden flex-1 overflow-hidden flex flex-col">
  <div class="p-6 pb-4 border-b border-gray-800">
    <h1 class="text-lg font-semibold mb-4">Watch Mode</h1>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
      <label class="block">
        <div class="text-xs text-gray-400 mb-1">Build Dir</div>
        <input id="w-dir" type="text" value="build" class="w-full px-2.5 py-1.5 text-sm">
      </label>
      <label class="block">
        <div class="text-xs text-gray-400 mb-1">Generator</div>
        <select id="w-gen" class="w-full px-2.5 py-1.5 text-sm">
          <option value="">(default)</option>
          <option>Ninja</option>
          <option>Unix Makefiles</option>
        </select>
      </label>
      <label class="block">
        <div class="text-xs text-gray-400 mb-1">Build Type</div>
        <select id="w-type" class="w-full px-2.5 py-1.5 text-sm">
          <option>Release</option>
          <option>Debug</option>
        </select>
      </label>
      <label class="block">
        <div class="text-xs text-gray-400 mb-1">Interval (s)</div>
        <input id="w-interval" type="number" value="1" min="0.5" step="0.5" class="w-full px-2.5 py-1.5 text-sm">
      </label>
    </div>
    <div class="flex gap-2 items-center">
      <button id="w-start-btn" class="btn btn-green" onclick="startWatch()">▶ Start Watching</button>
      <button id="w-stop-btn" class="btn btn-red hidden" onclick="stopWatch()">■ Stop</button>
      <span id="w-status" class="text-sm text-gray-400 ml-2"></span>
      <button class="btn btn-slate ml-auto text-xs" onclick="document.getElementById('watch-log').textContent=''">Clear</button>
    </div>
  </div>
  <div class="flex-1 overflow-hidden p-6 pt-4">
    <div id="watch-log" class="log h-full bg-gray-950 border border-gray-800 rounded p-3 overflow-auto whitespace-pre-wrap text-yellow-200"></div>
  </div>
</div>

<!-- ── Reports ── -->
<div id="page-reports" class="page hidden flex-1 overflow-hidden flex">
  <div class="w-56 border-r border-gray-800 flex flex-col shrink-0">
    <div class="p-4 border-b border-gray-800 flex items-center justify-between">
      <span class="section-title mb-0">Reports</span>
      <button class="text-xs text-gray-500 hover:text-gray-300" onclick="loadReports()">↻</button>
    </div>
    <div id="reports-list" class="flex-1 overflow-auto p-2 space-y-1"></div>
  </div>
  <div class="flex-1 overflow-auto p-6">
    <div id="report-viewer" class="text-gray-500 text-sm">Select a report to view.</div>
  </div>
</div>

</main>

<script>
// ─── Router ───────────────────────────────────────────────────────────────────
function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  const el = document.getElementById('page-' + page);
  if (el) { el.classList.remove('hidden'); el.style.display = ''; }
  const btn = document.querySelector('[data-page="' + page + '"]');
  if (btn) btn.classList.add('active');
  if (page === 'dashboard') loadDashboard();
  if (page === 'reports') loadReports();
  if (page === 'new-project') updatePreview();
}

// ─── API ──────────────────────────────────────────────────────────────────────
async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.body = JSON.stringify(body);
    opts.headers['Content-Type'] = 'application/json';
  }
  const r = await fetch(path, opts);
  return r.json();
}

// ─── SSE streaming ────────────────────────────────────────────────────────────
let _activeSource = null;

function streamJob(jobId, logEl, onDone) {
  if (_activeSource) { _activeSource.close(); _activeSource = null; }
  const es = new EventSource('/api/stream?job=' + jobId);
  _activeSource = es;
  es.addEventListener('line', e => {
    logEl.textContent += JSON.parse(e.data) + '\n';
    logEl.scrollTop = logEl.scrollHeight;
  });
  es.addEventListener('done', e => {
    const code = JSON.parse(e.data);
    const ok = code === '0';
    logEl.textContent += '\n[Exit ' + code + ']' + (ok ? ' ✓' : ' ✗') + '\n';
    logEl.scrollTop = logEl.scrollHeight;
    es.close(); _activeSource = null;
    if (onDone) onDone(ok);
  });
  es.onerror = () => { es.close(); _activeSource = null; if (onDone) onDone(false); };
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
async function loadDashboard() {
  const [projects, buildDirs] = await Promise.all([
    api('GET', '/api/projects'), api('GET', '/api/build-dirs')
  ]);
  const pEl = document.getElementById('dash-projects');
  if (!projects.length) {
    pEl.innerHTML = '<p class="text-gray-500 text-sm">No projects found.</p>';
  } else {
    pEl.innerHTML = projects.map(p => `
      <div class="card hover:border-gray-700 transition-colors">
        <div class="flex items-start justify-between mb-2">
          <div>
            <div class="font-semibold text-sm">${esc(p.name)}</div>
            <div class="text-xs text-gray-500 font-mono mt-0.5">${esc(p.path)}</div>
          </div>
          <span class="tag tag-gray">${p.modules.length} mod</span>
        </div>
        <div class="space-y-0.5">
          ${p.modules.map(m => `
            <div class="text-xs text-blue-300 font-mono flex items-center gap-1.5 group">
              <span class="text-gray-600">├─</span>
              <span class="flex-1">${esc(m)}</span>
              <button class="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-400 transition-opacity px-1"
                title="删除模块"
                onclick="deleteModule('${esc(p.path)}','${esc(m)}')">✕</button>
            </div>`).join('')}
        </div>
      </div>
    `).join('');
  }

  const bEl = document.getElementById('dash-builds');
  if (!buildDirs.length) {
    bEl.innerHTML = '<p class="text-gray-500 text-sm">No build directories found yet.</p>';
  } else {
    bEl.innerHTML = buildDirs.map(d => `
      <div class="flex items-center gap-3 card py-2 px-4">
        <span class="w-2 h-2 rounded-full flex-shrink-0 ${d.configured ? 'bg-green-500' : 'bg-gray-600'}"></span>
        <span class="font-mono text-sm">${esc(d.name)}</span>
        <span class="tag ${d.configured ? 'tag-green' : 'tag-gray'} ml-2">${d.configured ? 'configured' : 'unconfigured'}</span>
        <div class="ml-auto flex gap-2">
          <button class="text-xs text-blue-400 hover:text-blue-300" onclick="quickAction('${esc(d.name)}','build')">Build →</button>
          <button class="text-xs text-gray-500 hover:text-gray-300" onclick="quickAction('${esc(d.name)}','test')">Test →</button>
          <button class="text-xs text-red-500 hover:text-red-400" onclick="deleteBuildDir('${esc(d.name)}')">删除</button>
        </div>
      </div>
    `).join('');
  }
}

function quickAction(dir, action) {
  document.getElementById('b-dir').value = dir;
  navigate('build');
  setTimeout(() => runBuildAction(action), 100);
}

async function deleteModule(projPath, modName) {
  if (!confirm(`确认删除模块 "${modName}"？\n路径：${projPath}/${modName}\n此操作不可恢复。`)) return;
  const res = await api('POST', '/api/delete', { kind: 'module', path: projPath + '/' + modName });
  if (res.error) { alert('删除失败：' + res.error); return; }
  loadDashboard();
}

async function deleteBuildDir(name) {
  if (!confirm(`确认删除构建目录 "${name}"？\n此操作不可恢复。`)) return;
  const res = await api('POST', '/api/delete', { kind: 'build', path: name });
  if (res.error) { alert('删除失败：' + res.error); return; }
  loadDashboard();
}

// ─── Build ────────────────────────────────────────────────────────────────────
async function runBuildAction(action) {
  const dir = document.getElementById('b-dir').value.trim() || 'build';
  const gen = document.getElementById('b-gen').value;
  const btype = document.getElementById('b-type').value;
  const config = document.getElementById('b-config').value;
  const extra = document.getElementById('b-extra').value.trim();
  const logEl = document.getElementById('build-log');
  const statusEl = document.getElementById('build-status');

  let cmd;
  if (action === 'configure') {
    cmd = ['cmake', '-S', '.', '-B', dir];
    if (gen) cmd.push('-G', gen);
    if (btype) cmd.push('-DCMAKE_BUILD_TYPE=' + btype);
    if (extra) extra.split(/\s+/).forEach(f => f && cmd.push(f));
  } else if (action === 'build') {
    cmd = ['cmake', '--build', dir];
    if (config) cmd.push('--config', config);
  } else if (action === 'test') {
    cmd = ['ctest', '--test-dir', dir, '--output-on-failure'];
    if (config) cmd.push('-C', config);
  } else if (action === 'report-all') {
    cmd = ['cmake', '--build', dir, '--target', 'report-all'];
    if (config) cmd.push('--config', config);
  } else if (action === 'install') {
    cmd = ['cmake', '--install', dir];
    if (config) cmd.push('--config', config);
  } else if (action === 'uninstall') {
    cmd = ['cmake', '--build', dir, '--target', 'uninstall'];
  }

  logEl.textContent += '\n$ ' + cmd.join(' ') + '\n';
  logEl.scrollTop = logEl.scrollHeight;

  statusEl.className = 'mt-2 text-sm text-yellow-400';
  statusEl.textContent = 'Running ' + action + '...';
  statusEl.classList.remove('hidden');

  const res = await api('POST', '/api/run', { cmd });
  if (res.error) {
    statusEl.className = 'mt-2 text-sm text-red-400';
    statusEl.textContent = 'Error: ' + res.error;
    return;
  }
  streamJob(res.job_id, logEl, ok => {
    statusEl.className = 'mt-2 text-sm ' + (ok ? 'text-green-400' : 'text-red-400');
    statusEl.textContent = action + (ok ? ' succeeded ✓' : ' failed ✗');
  });
}

// ─── New Project ──────────────────────────────────────────────────────────────
function toggleSection(id) {
  const checked = document.getElementById('np-' + id).checked;
  document.getElementById('np-' + id + '-fields').style.display = checked ? '' : 'none';
}

function updatePreview() {
  const name = document.getElementById('np-name').value.trim();
  const el = document.getElementById('np-preview');
  if (!name) { el.textContent = '(enter a project name to preview)'; return; }
  const lines = ['projects/' + name + '/  ← workspace_dir', '  CMakeLists.txt'];
  if (document.getElementById('np-lib').checked) {
    const d = document.getElementById('np-lib-dir').value.trim() || name;
    const t = document.getElementById('np-lib-target').value.trim() || name;
    lines.push('  ' + d + '/');
    lines.push('    CMakeLists.txt');
    lines.push('    ' + t + '.cpp');
    lines.push('    ' + t + '.h');
  }
  if (document.getElementById('np-app').checked) {
    const d = document.getElementById('np-app-dir').value.trim() || 'app';
    lines.push('  ' + d + '/');
    lines.push('    CMakeLists.txt');
    lines.push('    main.cpp');
  }
  if (document.getElementById('np-test').checked) {
    const d = document.getElementById('np-test-dir').value.trim() || 'tests/smoke';
    const testSrc = d.split('/').filter(Boolean).pop() || 'smoke';
    lines.push('  ' + d + '/');
    lines.push('    CMakeLists.txt');
    lines.push('    ' + testSrc + '.cpp');
  }
  el.textContent = lines.join('\n');
}

async function submitNewProject() {
  const name = document.getElementById('np-name').value.trim();
  const statusEl = document.getElementById('np-status');
  if (!name) {
    statusEl.className = 'text-sm text-red-400'; statusEl.textContent = 'Project name is required.';
    statusEl.classList.remove('hidden'); return;
  }
  const ver = document.getElementById('np-ver').value.trim() || '0.1.0';
  const ns = document.getElementById('np-ns').value.trim() || name;
  const inclLib = document.getElementById('np-lib').checked;
  const inclApp = document.getElementById('np-app').checked;
  const inclTest = document.getElementById('np-test').checked;
  const targets = [], modules = [];

  if (inclLib) {
    const ld = document.getElementById('np-lib-dir').value.trim() || name;
    const lt = document.getElementById('np-lib-target').value.trim() || name;
    targets.push({ dir: ld, name: lt, type: 'LIBRARY', kind: 'lib',
      alias_prefix: ns, enable_install: true, sources: [lt+'.cpp'], headers: [lt+'.h'] });
    modules.push(ld);
  }
  if (inclApp) {
    const ad = document.getElementById('np-app-dir').value.trim() || 'app';
    const at = document.getElementById('np-app-target').value.trim() || name + '_app';
    const libT = targets.find(t => t.kind === 'lib');
    targets.push({ dir: ad, name: at, type: 'EXECUTABLE', kind: 'app',
      private_deps: libT ? [ns + '::' + libT.name] : [],
      enable_install: true, sources: ['main.cpp'] });
    modules.push(ad);
  }
  // CMake reserved target names when CTest is enabled
  const CMAKE_RESERVED = ['test', 'install', 'package', 'package_source', 'edit_cache',
    'rebuild_cache', 'clean', 'all', 'ALL_BUILD', 'ZERO_CHECK'];
  if (inclTest) {
    const td = document.getElementById('np-test-dir').value.trim() || 'tests/smoke';
    const tt = document.getElementById('np-test-target').value.trim() || name + '_smoke';
    if (CMAKE_RESERVED.includes(tt)) {
      statusEl.className = 'text-sm text-red-400';
      statusEl.textContent = `目标名 "${tt}" 是 CMake 保留名称，启用 CTest 后不可使用。请改用如 "${name}_smoke" 等名称。`;
      statusEl.classList.remove('hidden'); return;
    }
    const libT = targets.find(t => t.kind === 'lib');
    const testSrc = td.split('/').filter(Boolean).pop() || 'smoke';
    targets.push({ dir: td, name: tt, type: 'EXECUTABLE', kind: 'test',
      private_deps: libT ? [ns + '::' + libT.name] : [],
      sources: [testSrc + '.cpp'] });
  }

  const cfg = {
    project_name: name, project_version: ver, project_namespace: ns,
    workspace_dir: 'projects/' + name,
    modules, include_tests: inclTest, targets,
    force: document.getElementById('np-force').checked,
  };

  statusEl.className = 'text-sm text-yellow-400';
  statusEl.textContent = 'Generating...';
  statusEl.classList.remove('hidden');

  const res = await api('POST', '/api/new-project', cfg);
  if (res.ok) {
    statusEl.className = 'text-sm text-green-400';
    statusEl.textContent = '✓ Created projects/' + name + '  —  run Configure + Build to compile.';
  } else {
    statusEl.className = 'text-sm text-red-400';
    statusEl.textContent = 'Error: ' + res.error;
  }
}

// ─── Watch ────────────────────────────────────────────────────────────────────
async function startWatch() {
  const dir = document.getElementById('w-dir').value.trim() || 'build';
  const gen = document.getElementById('w-gen').value;
  const btype = document.getElementById('w-type').value;
  const interval = document.getElementById('w-interval').value;
  const logEl = document.getElementById('watch-log');

  const cmd = ['python', 'cmake/watch_build.py', '--build', dir,
    '--build-type', btype, '--interval', String(interval)];
  if (gen) { cmd.push('--generator'); cmd.push(gen); }

  logEl.textContent += '\n$ ' + cmd.join(' ') + '\n';
  const res = await api('POST', '/api/run', { cmd });
  if (res.error) {
    document.getElementById('w-status').textContent = 'Error: ' + res.error;
    return;
  }
  document.getElementById('w-start-btn').classList.add('hidden');
  document.getElementById('w-stop-btn').classList.remove('hidden');
  document.getElementById('w-status').textContent = 'Watching…';

  streamJob(res.job_id, logEl, () => {
    document.getElementById('w-start-btn').classList.remove('hidden');
    document.getElementById('w-stop-btn').classList.add('hidden');
    document.getElementById('w-status').textContent = 'Stopped.';
  });
}

function stopWatch() {
  if (_activeSource) { _activeSource.close(); _activeSource = null; }
  document.getElementById('w-start-btn').classList.remove('hidden');
  document.getElementById('w-stop-btn').classList.add('hidden');
  document.getElementById('w-status').textContent = 'Stream closed (background process may persist).';
}

// ─── Reports ──────────────────────────────────────────────────────────────────
async function loadReports() {
  const list = await api('GET', '/api/reports');
  const el = document.getElementById('reports-list');
  if (!list.length) {
    el.innerHTML = '<p class="text-gray-500 text-xs p-2">No reports found.<br>Run a build then<br>click Report.</p>';
    return;
  }
  el.innerHTML = list.map(r => `
    <button class="w-full text-left rounded px-3 py-2 hover:bg-gray-800 transition-colors"
            onclick="viewReport('${esc(r.path)}')">
      <div class="text-xs font-mono text-gray-200">${esc(r.name)}</div>
      <div class="text-xs text-gray-500 mt-0.5">${esc(r.build_dir)}</div>
    </button>
  `).join('');
}

async function viewReport(path) {
  const viewer = document.getElementById('report-viewer');
  viewer.innerHTML = '<div class="text-gray-400 text-sm">Loading…</div>';
  const res = await api('GET', '/api/report?path=' + encodeURIComponent(path));
  if (res.error) { viewer.innerHTML = '<div class="text-red-400 text-sm">' + esc(res.error) + '</div>'; return; }
  const name = path.split('/').pop();
  const header = '<div class="text-xs text-gray-500 font-mono mb-4">' + esc(path) + '</div>';
  if (name.endsWith('.json')) {
    try {
      const obj = JSON.parse(res.content);
      viewer.innerHTML = header + '<table class="w-full text-xs">' +
        Object.entries(obj).map(([k, v]) => {
          const val = typeof v === 'object' ? JSON.stringify(v, null, 2) : String(v);
          return '<tr class="border-b border-gray-800"><td class="py-2 pr-4 text-gray-400 font-mono align-top w-40">'
            + esc(k) + '</td><td class="py-2 text-gray-200 align-top"><pre class="whitespace-pre-wrap font-mono">'
            + esc(val) + '</pre></td></tr>';
        }).join('') + '</table>';
      return;
    } catch(e) {}
  }
  viewer.innerHTML = header + '<pre class="log text-xs text-gray-200 whitespace-pre-wrap">' + esc(res.content) + '</pre>';
}

// ─── Utilities ────────────────────────────────────────────────────────────────
function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ─── Init ─────────────────────────────────────────────────────────────────────
navigate('dashboard');
</script>
</body>
</html>
"""


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CMake Workspace UI")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    print(f"CMake Workspace UI  →  {url}")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
