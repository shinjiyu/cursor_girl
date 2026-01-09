#!/usr/bin/env bash
# Agent Hook wrapper (Unix/macOS)
# - Avoid hard-coded venv paths
# - Allow selecting Python via env var CURSOR_AGENT_PYTHON / VENV_PYTHON

set -euo pipefail

HOOK_SCRIPT="${1:-}"
if [ -z "$HOOK_SCRIPT" ]; then
  echo "Usage: run_hook.sh <hook_script.py>" >&2
  exit 2
fi

PY="${CURSOR_AGENT_PYTHON:-${VENV_PYTHON:-}}"
if [ -z "$PY" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PY="python3"
  else
    PY="python"
  fi
fi

exec "$PY" "$HOOK_SCRIPT"

