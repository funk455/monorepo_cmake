#!/usr/bin/env python3
"""
CMake Workspace UI — web dashboard for monorepo-cmake-sample.
No external dependencies required (Python 3.7+).

Usage:
  python ui.py [--port 8080] [--host 127.0.0.1] [--root <workspace>]
  Then open http://localhost:8080

  --root manages another repository that references this framework
  (e.g. as a git submodule); defaults to this repository.
"""

import argparse
from http.server import HTTPServer
from pathlib import Path

try:
    from http.server import ThreadingHTTPServer
except ImportError:
    import socketserver
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
        daemon_threads = True

from ui.handler import Handler
from ui.paths import set_workspace, is_external_workspace, FRAMEWORK_DIR


def main():
    parser = argparse.ArgumentParser(description="CMake Workspace UI")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--root", help="workspace root to manage (default: this framework repo)")
    args = parser.parse_args()

    if args.root:
        ws = set_workspace(args.root)
        if not (ws / "CMakeLists.txt").exists() and not (ws / "projects").exists():
            print(f"note: {ws} has no CMakeLists.txt or projects/ yet; "
                  "creating a project from the UI will scaffold them.")

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    print(f"CMake Workspace UI  →  {url}")
    if is_external_workspace():
        from ui.paths import workspace
        print(f"Workspace: {workspace()}")
        print(f"Framework: {FRAMEWORK_DIR}")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
