"""
Desktop GUI launcher for the Indeed Auto Job Apply app.

Starts the FastAPI server in a background thread, then opens a native
OS window (via pywebview) showing the job board — no browser required.

Usage:
    python src/gui.py
"""

import threading
import time
import sys
import os
import socket

import uvicorn
import webview

# Ensure imports resolve when run from the repo root
sys.path.insert(0, os.path.dirname(__file__))
from app import app as fastapi_app

PORT = 8765
URL = f"http://localhost:{PORT}/static/jobs.html"


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def _start_server() -> None:
    uvicorn.run(fastapi_app, host="127.0.0.1", port=PORT, log_level="warning")


def main() -> None:
    # Start FastAPI in a daemon thread so it dies with the window
    server_thread = threading.Thread(target=_start_server, daemon=True)
    server_thread.start()

    # Wait up to 5 s for the server to accept connections
    deadline = time.time() + 5
    while not _port_open(PORT):
        if time.time() > deadline:
            print("ERROR: server did not start in time", file=sys.stderr)
            sys.exit(1)
        time.sleep(0.1)

    # Open the native window
    window = webview.create_window(
        title="Indeed Auto Job Apply — Thomas Hopkinson",
        url=URL,
        width=1100,
        height=750,
        min_size=(800, 600),
        resizable=True,
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
