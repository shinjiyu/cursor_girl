#!/bin/bash
# Agent Hook 包装脚本
# 用于避免路径中空格导致的权限问题

# Hook 脚本路径
HOOK_SCRIPT="$1"
shift || true

# 解释器优先级：
# 1) $HOME/.cursor-agent/venv（由 deploy.sh 创建）
# 2) 环境变量 CURSOR_AGENT_PYTHON（允许自定义）
# 3) python3（系统默认）
VENV_PYTHON="${HOME}/.cursor-agent/venv/bin/python"

if [ -x "$VENV_PYTHON" ]; then
  PYTHON_BIN="$VENV_PYTHON"
elif [ -n "${CURSOR_AGENT_PYTHON:-}" ]; then
  PYTHON_BIN="$CURSOR_AGENT_PYTHON"
else
  PYTHON_BIN="python3"
fi

exec "$PYTHON_BIN" "$HOOK_SCRIPT" "$@"

