#!/bin/bash
# 等待 Cursor Hook 连接到中央 Server

echo "⏳ 等待 Cursor Hook 连接..."
echo "   请现在重启 Cursor (Cmd+Q 然后重新启动)"
echo ""

# 清空旧日志
> /tmp/cursor_ortensia.log

for i in {1..60}; do
    sleep 2
    
    # 检查日志中是否有连接成功的标记
    if grep -q "已连接到中央Server" /tmp/cursor_ortensia.log 2>/dev/null; then
        echo ""
        echo "✅ Cursor Hook 已连接到中央 Server！"
        echo ""
        
        # 提取 Cursor ID
        CURSOR_ID=$(grep "Cursor ID:" /tmp/cursor_ortensia.log | tail -1 | awk '{print $NF}')
        
        if [ -n "$CURSOR_ID" ]; then
            echo "🔑 Cursor Hook ID: $CURSOR_ID"
            echo "$CURSOR_ID" > /tmp/ortensia_cursor_id.txt
            echo ""
            echo "已保存到 /tmp/ortensia_cursor_id.txt"
            echo ""
        fi
        
        echo "现在可以运行测试:"
        echo "  cd cursor-injector"
        echo "  python3 test_central_server.py"
        echo ""
        
        exit 0
    fi
    
    # 每 10 秒显示一次进度
    if [ $((i % 5)) -eq 0 ]; then
        echo "  等待中... (${i}秒)"
    fi
done

echo ""
echo "❌ 超时：2 分钟内未检测到连接"
echo ""
echo "请检查:"
echo "  1. Cursor 是否已重启"
echo "  2. 查看日志: cat /tmp/cursor_ortensia.log"
echo ""







