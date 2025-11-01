#!/bin/bash
# 停止所有 オルテンシア 相关服务

echo ""
echo "🛑 正在停止所有服务..."
echo ""

# 停止 Next.js 开发服务器（端口 3000）
if lsof -ti :3000 2>/dev/null | xargs kill -9 2>/dev/null; then
    echo "✅ Next.js 开发服务器已停止"
else
    echo "ℹ️  没有运行的 Next.js 服务器"
fi

# 停止 WebSocket 服务器（端口 8000）
if lsof -ti :8000 2>/dev/null | xargs kill -9 2>/dev/null; then
    echo "✅ WebSocket 服务器已停止"
else
    echo "ℹ️  没有运行的 WebSocket 服务器"
fi

# 额外确保：通过进程名停止 Python WebSocket 服务器
pkill -f "websocket_server.py" 2>/dev/null

# 停止 Electron 进程
if pkill -9 -f "Electron.*aituber-kit" 2>/dev/null; then
    echo "✅ Electron 悬浮窗已停止"
else
    echo "ℹ️  没有运行的 Electron 悬浮窗"
fi

# 停止所有相关的 npm 进程
if pkill -f "npm.*run.*(dev|assistant)" 2>/dev/null; then
    echo "✅ npm 进程已停止"
fi

# 等待进程彻底退出
sleep 1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 验证端口状态："
echo ""

# 检查端口是否真的被释放了
ALL_CLEAR=true
for port in 3000 8000; do
    if lsof -i :$port 2>/dev/null | grep LISTEN > /dev/null; then
        echo "  ⚠️  端口 $port 仍在使用（可能需要手动清理）"
        lsof -i :$port | grep LISTEN
        ALL_CLEAR=false
    else
        echo "  ✅ 端口 $port 已释放"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$ALL_CLEAR" = true ]; then
    echo "✨ 所有服务已停止，端口已释放！"
else
    echo "⚠️  有些端口未能释放，可能需要重启终端或运行："
    echo "   sudo lsof -ti :3000,:8000 | xargs kill -9"
fi

echo ""

