#!/bin/bash
# Cursor Hooks 配置文件

# WebSocket 服务器地址
WS_SERVER="ws://localhost:8000/ws"

# オルテンシア Bridge 路径
BRIDGE_PATH="/Users/user/Documents/ cursorgirl/bridge"

# Python 虚拟环境路径
VENV_PATH="${BRIDGE_PATH}/venv"

# 日志文件路径
LOG_FILE="/tmp/cursor-hooks.log"

# 是否启用调试模式
DEBUG=true

# 是否启用 WebSocket 发送
ENABLE_WEBSOCKET=true

# Hook 超时时间（秒）
HOOK_TIMEOUT=5

