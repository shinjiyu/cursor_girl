#!/bin/bash
#
# 使用 ChatTTS 虚拟环境启动 WebSocket 服务器
#

set -e

CHATTTS_VENV="/Users/user/Documents/tts/chattts/venv"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "🎤 使用 ChatTTS 启动 WebSocket 服务器"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "$CHATTTS_VENV" ]; then
    echo "❌ ChatTTS 虚拟环境不存在: $CHATTTS_VENV"
    exit 1
fi

# 激活虚拟环境
source "$CHATTTS_VENV/bin/activate"

# 进入 bridge 目录
cd "$SCRIPT_DIR"

echo "虚拟环境: $CHATTTS_VENV"
echo "工作目录: $SCRIPT_DIR"
echo "配置文件: tts_config.json"
echo ""
echo "启动服务器..."
echo ""

# 启动服务器（后台运行）
nohup python websocket_server.py > /tmp/ws_server.log 2>&1 &
SERVER_PID=$!

sleep 2

# 检查是否启动成功
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ 服务器已启动 (PID: $SERVER_PID)"
    echo "   监听端口: 8765"
    echo "   日志文件: /tmp/ws_server.log"
    echo ""
    echo "查看日志: tail -f /tmp/ws_server.log"
else
    echo "❌ 服务器启动失败"
    echo "查看错误: cat /tmp/ws_server.log"
    exit 1
fi






















