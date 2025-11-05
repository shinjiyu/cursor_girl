#!/bin/bash
# 通过命令行启动 Cursor 并设置环境变量

set -e

echo "========================================================================"
echo "  🌸 启动 Cursor (中央 Server 模式)"
echo "========================================================================"
echo ""

# 1. 确认中央服务器正在运行
if ! ps aux | grep -q "[p]ython.*websocket_server.py"; then
    echo "❌ 中央 Server 未运行！"
    echo "   请先运行: cd bridge && python3 websocket_server.py"
    exit 1
fi
echo "✅ 中央 Server 正在运行"
echo ""

# 2. 关闭现有的 Cursor 进程
echo "📝 关闭现有的 Cursor 进程..."
pkill -f "Cursor.app" || true
sleep 2
echo "✅ Cursor 已关闭"
echo ""

# 3. 设置环境变量并启动 Cursor
echo "📝 启动 Cursor (传递 ORTENSIA_SERVER 环境变量)..."
export ORTENSIA_SERVER=ws://localhost:8765

# 在 macOS 上，需要直接运行可执行文件来传递环境变量
ORTENSIA_SERVER=ws://localhost:8765 /Applications/Cursor.app/Contents/MacOS/Cursor > /dev/null 2>&1 &

echo ""
echo "✅ Cursor 已启动！"
echo ""
echo "========================================================================"
echo "  ⏱️  等待 Cursor Hook 连接到中央 Server..."
echo "========================================================================"
echo ""
echo "执行以下命令查看连接状态:"
echo "  cat /tmp/cursor_ortensia.log | tail -30"
echo ""
echo "连接成功后，运行测试:"
echo "  cd cursor-injector && python3 test_central_server.py"
echo ""
echo "========================================================================"
echo ""

