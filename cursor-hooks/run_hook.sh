#!/bin/bash
# Agent Hook 包装脚本
# 用于避免路径中空格导致的权限问题

# 虚拟环境 Python 路径
VENV_PYTHON="/Users/user/Documents/ cursorgirl/bridge/venv/bin/python"

# Hook 脚本路径
HOOK_SCRIPT="$1"

# 执行 Hook
"$VENV_PYTHON" "$HOOK_SCRIPT"

