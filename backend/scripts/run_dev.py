"""
Quick-start dev server for life-planner.

Usage:
    python scripts/run_dev.py
    python scripts/run_dev.py --port 8765
    python scripts/run_dev.py --no-reload

What it does:
    1. Kills any process on the target port (avoids "address in use")
    2. Prints a "ready" banner
    3. Runs uvicorn in the foreground (Ctrl+C goes to it)

Why this exists:
    Earlier belief that "uvicorn --reload doesn't work" was wrong --
    it works fine with watchfiles 1.2.0 on Windows + sandbox paths
    (verified 2026-07-17). The "didn't reload" symptoms were caused by
    forgetting --reload on the original command. This script makes the
    default explicit and adds port cleanup.

Verified 2026-07-17: --reload detects file changes in <4s on
    life-planner backend routers college.py.

Design note:
    We use subprocess.run() (blocking) with stdio inherit, NOT Popen + reader
    thread. Popen+pipe triggers a reader thread that decodes bytes -> str,
    which on Windows can fail with cp1252 / utf-8 mismatch and crash
    with UnicodeDecodeError. Inheriting stdio avoids that entirely
    (no pipe = no reader thread).
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 8765  # Avoid common conflicts (haolo_desktop uses 8010, 8000)


def kill_port(port: int) -> None:
    """Kill any process listening on the given port (Windows only)."""
    if sys.platform != "win32":
        return
    try:
        out = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        if not out:
            return
        for line in out.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                if pid and pid.isdigit():
                    subprocess.run(
                        ["powershell", "-Command", f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                        capture_output=True, timeout=5,
                    )
                    print(f"[run_dev] killed old PID {pid} on port {port}", flush=True)
                    time.sleep(0.5)
    except Exception as e:
        print(f"[run_dev] kill_port warning: {e}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Start life-planner dev server.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to bind (default: {DEFAULT_PORT}, avoids common conflicts)")
    parser.add_argument("--host", type=str, default="127.0.0.1",
                        help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--no-reload", action="store_true",
                        help="Disable auto-reload (default: enabled)")
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of workers (default: 1, debug only)")
    args = parser.parse_args()

    # Ensure we're in backend dir
    os.chdir(BACKEND_DIR)

    # Step 1: kill stale processes on this port
    kill_port(args.port)

    # Step 2: build uvicorn command
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", args.host,
        "--port", str(args.port),
        "--log-level", "info",
    ]
    if not args.no_reload and args.workers == 1:
        cmd.extend(["--reload", "--reload-dir", "."])
    if args.workers > 1:
        cmd.extend(["--workers", str(args.workers)])

    # Step 3: print banner
    reload_status = "yes" if (not args.no_reload and args.workers == 1) else "no"
    print(f"[run_dev] cwd:    {BACKEND_DIR}", flush=True)
    print(f"[run_dev] port:   {args.port}  host: {args.host}", flush=True)
    print(f"[run_dev] reload: {reload_status}", flush=True)
    print(f"[run_dev] swagger: http://{args.host}:{args.port}/docs", flush=True)
    print(f"[run_dev] cmd:     {' '.join(cmd)}", flush=True)
    print("---", flush=True)

    # Step 4: run uvicorn in foreground with stdio inherit
    # stdio=None means inherit from parent -> no pipe -> no reader thread
    # Ctrl+C goes directly to uvicorn, then propagates back via KeyboardInterrupt
    try:
        return subprocess.call(cmd, stdin=None, stdout=None, stderr=None)
    except FileNotFoundError as e:
        print(f"[run_dev] FAILED: {e}", flush=True)
        print(f"[run_dev] Is uvicorn installed? Try:", flush=True)
        print(f"  {sys.executable} -m pip install uvicorn[standard]", flush=True)
        return 1
    except KeyboardInterrupt:
        print("\n[run_dev] interrupted, exiting", flush=True)
        return 0


if __name__ == "__main__":
    sys.exit(main())
