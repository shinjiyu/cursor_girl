#!/usr/bin/env python3
"""
Cross-platform Cursor Agent Hook runner.

Why:
- Windows cannot run `run_hook.sh`
- The existing `run_hook.sh` was hard-coded to a macOS venv path

Usage:
  python run_hook.py <hook_script.py>

Notes:
- We forward stdin/stdout/stderr so Cursor can communicate with the hook.
- You can override the python interpreter via env var:
    CURSOR_AGENT_PYTHON=C:\\Path\\to\\python.exe
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _pick_python() -> str:
    override = os.environ.get("CURSOR_AGENT_PYTHON") or os.environ.get("VENV_PYTHON")
    if override:
        return str(Path(override).expanduser())
    return sys.executable


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: run_hook.py <hook_script.py>", file=sys.stderr)
        return 2

    hook_script = Path(argv[1]).expanduser()
    if not hook_script.exists():
        print(f"run_hook.py: hook script not found: {hook_script}", file=sys.stderr)
        return 2

    py = _pick_python()
    cmd = [py, str(hook_script)]

    try:
        # Important: forward streams unchanged for Cursor hooks protocol.
        completed = subprocess.run(
            cmd,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            check=False,
        )
        return int(completed.returncode or 0)
    except FileNotFoundError:
        print(f"run_hook.py: python interpreter not found: {py}", file=sys.stderr)
        return 127
    except Exception as e:
        print(f"run_hook.py: failed to execute hook: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

