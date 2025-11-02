#!/bin/bash
# 启动 Cursor（带调试端口）并运行 DOM Inspector

echo "=========================================="
echo "  🚀 Cursor DOM Inspector"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

CURSOR_PATH="/Applications/Cursor.app/Contents/MacOS/Cursor"
DEBUG_PORT=9222

# 检查 Cursor 是否已经在运行
if lsof -Pi :$DEBUG_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Cursor is already running with debug port $DEBUG_PORT"
else
    echo "🚀 Starting Cursor with debug port $DEBUG_PORT..."
    echo ""
    echo "💡 Command:"
    echo "   $CURSOR_PATH --remote-debugging-port=$DEBUG_PORT"
    echo ""
    
    # 在后台启动 Cursor
    "$CURSOR_PATH" --remote-debugging-port=$DEBUG_PORT &
    CURSOR_PID=$!
    
    echo "✅ Cursor started (PID: $CURSOR_PID)"
    echo ""
    echo "⏳ Waiting 5 seconds for Cursor to initialize..."
    sleep 5
fi

echo ""
echo "=========================================="
echo "  🔍 Running DOM Inspector"
echo "=========================================="
echo ""

# 运行检查器
node cursor-dom-inspector-cdp.js

echo ""
echo "=========================================="
echo "  ✅ Done!"
echo "=========================================="
echo ""
echo "💡 Cursor is still running. To close it:"
echo "   - Close Cursor manually, or"
echo "   - Run: pkill -f 'Cursor --remote-debugging-port'"
echo ""

