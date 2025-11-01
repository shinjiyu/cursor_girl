#!/bin/bash
# 测试 post-save hook

echo "🧪 测试 post-save Hook"
echo "======================================"

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOOK_SCRIPT="${HOOKS_ROOT}/.cursor/hooks/post-save"

# 检查 hook 脚本是否存在
if [ ! -f "$HOOK_SCRIPT" ]; then
    echo "❌ Hook 脚本不存在: ${HOOK_SCRIPT}"
    exit 1
fi

# 确保可执行
chmod +x "$HOOK_SCRIPT"

# 创建测试文件
TEST_FILE="${HOOKS_ROOT}/test/test_file.txt"
echo "测试内容" > "$TEST_FILE"

echo "📝 创建测试文件: ${TEST_FILE}"
echo ""

# 模拟 Cursor 调用 hook
echo "🔧 模拟 Cursor 保存文件..."
echo "   调用: post-save \"${TEST_FILE}\" \"${HOOKS_ROOT}\""
echo ""

"$HOOK_SCRIPT" "$TEST_FILE" "$HOOKS_ROOT"
RESULT=$?

echo ""
echo "======================================"

if [ $RESULT -eq 0 ]; then
    echo "✅ post-save hook 测试通过"
    echo ""
    echo "📋 查看日志:"
    echo "   tail -20 /tmp/cursor-hooks.log"
    echo ""
    echo "🎯 预期结果:"
    echo "   オルテンシア 应该收到文件保存事件"
    echo "   并说: \"保存成功~\" 😊"
else
    echo "❌ post-save hook 测试失败 (exit code: ${RESULT})"
    echo ""
    echo "📋 查看错误日志:"
    echo "   tail -50 /tmp/cursor-hooks.log"
fi

echo ""
exit $RESULT

