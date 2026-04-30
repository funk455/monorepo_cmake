#!/usr/bin/env python3
"""
CMake Workspace UI — web dashboard for monorepo-cmake-sample.
No external dependencies required (Python 3.7+).

Usage:
  python ui.py [--port 8080] [--host 127.0.0.1]
  Then open http://localhost:8080
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
