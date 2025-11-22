#!/bin/bash
# 运行所有 Cursor Hook 测试

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         🧪 Cursor Hooks 完整测试套件                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 测试计数
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 运行测试函数
run_test() {
    local test_name=$1
    local test_script=$2
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "测试 ${TOTAL_TESTS}: ${test_name}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [ ! -f "$test_script" ]; then
        echo "❌ 测试脚本不存在: ${test_script}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
    
    chmod +x "$test_script"
    
    if "$test_script"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo ""
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo ""
    fi
}

# 清理日志
echo "🧹 清理旧日志..."
> /tmp/cursor-hooks.log
echo ""

# 检查 WebSocket 服务器
echo "🔍 检查 WebSocket 服务器状态..."
if lsof -i :8765 > /dev/null 2>&1; then
    echo "✅ WebSocket 服务器运行中 (端口 8765 - Ortensia 中央服务器)"
else
    echo "⚠️  WebSocket 服务器未运行 (需要启动 bridge/websocket_server.py)"
    echo "   启动方法: cd bridge && python websocket_server.py"
    echo ""
    echo "   继续测试（但オルテンシア 不会收到消息）..."
fi
echo ""

# 运行所有测试
run_test "post-save Hook" "${SCRIPT_DIR}/test_post_save.sh"
sleep 2

run_test "post-commit Hook" "${SCRIPT_DIR}/test_post_commit.sh"
sleep 2

# 测试总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    📊 测试总结                            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "   总测试数: ${TOTAL_TESTS}"
echo "   ✅ 通过: ${PASSED_TESTS}"
echo "   ❌ 失败: ${FAILED_TESTS}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 所有测试通过！Cursor Hooks 工作正常！"
    echo ""
    echo "🚀 下一步:"
    echo "   1. 将 .cursor/ 目录复制到你的项目中"
    echo "   2. 在 Cursor 中测试实际的文件保存和 Git commit"
    echo "   3. 观察オルテンシア的反应 ✨"
else
    echo "⚠️  有 ${FAILED_TESTS} 个测试失败"
    echo ""
    echo "🔍 调试步骤:"
    echo "   1. 查看日志: tail -50 /tmp/cursor-hooks.log"
    echo "   2. 检查 Python 环境: cd bridge && source venv/bin/activate"
    echo "   3. 确保 WebSocket 服务器运行中"
fi

echo ""
echo "📋 完整日志:"
echo "   tail -f /tmp/cursor-hooks.log"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    exit 0
else
    exit 1
fi

