#!/bin/bash
# Cursor Hooks 配置文件

# WebSocket 服务器地址（Ortensia 中央服务器）
WS_SERVER="ws://localhost:8765"

# 自动检测 オルテンシア 项目路径
# 假设 .cursor 在项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# オルテンシア Bridge 路径
BRIDGE_PATH="${PROJECT_ROOT}/bridge"

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

