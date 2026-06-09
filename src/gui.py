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
import urllib.request
import urllib.error
import json

import uvicorn
import webview

# Ensure imports resolve when run from the repo root
sys.path.insert(0, os.path.dirname(__file__))
from app import app as fastapi_app

PORT = 8765
URL = f"http://localhost:{PORT}/static/jobs.html"
_HEALTH_URL = f"http://127.0.0.1:{PORT}/jobs/stats"


def _our_server_ready() -> bool:
    """Return True only when /jobs/stats responds with our expected payload."""
    try:
        with urllib.request.urlopen(_HEALTH_URL, timeout=1) as resp:
            data = json.loads(resp.read())
            return "total" in data
    except Exception:
        return False


def _start_server() -> None:
    uvicorn.run(fastapi_app, host="127.0.0.1", port=PORT, log_level="warning")


def main() -> None:
    # Start FastAPI in a daemon thread so it dies with the window
    server_thread = threading.Thread(target=_start_server, daemon=True)
    server_thread.start()

    # Poll /jobs/stats — confirms it's *our* app, not an unrelated service
    deadline = time.time() + 5
    while not _our_server_ready():
        if time.time() > deadline:
            print("ERROR: job-apply server did not start in time", file=sys.stderr)
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
