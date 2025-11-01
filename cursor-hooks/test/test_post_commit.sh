#!/bin/bash
# 测试 post-commit hook

echo "🧪 测试 post-commit Hook"
echo "======================================"

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOOK_SCRIPT="${HOOKS_ROOT}/.cursor/hooks/post-commit"

# 检查 hook 脚本是否存在
if [ ! -f "$HOOK_SCRIPT" ]; then
    echo "❌ Hook 脚本不存在: ${HOOK_SCRIPT}"
    exit 1
fi

# 确保可执行
chmod +x "$HOOK_SCRIPT"

# 检查是否在 Git 仓库中
cd "$HOOKS_ROOT"
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "⚠️  当前不在 Git 仓库中，初始化临时仓库..."
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"
    
    # 创建初始提交
    echo "测试文件" > test_file.txt
    git add test_file.txt
    git commit -m "Initial commit" > /dev/null
fi

# 创建测试文件并提交
echo "📝 创建测试 commit..."
TEST_FILE="test_commit_$(date +%s).txt"
echo "测试内容 $(date)" > "$TEST_FILE"
git add "$TEST_FILE"
git commit -m "test: 测试 post-commit hook" > /dev/null

echo ""
echo "🔧 模拟 Cursor 调用 post-commit hook..."
echo ""

"$HOOK_SCRIPT"
RESULT=$?

echo ""
echo "======================================"

if [ $RESULT -eq 0 ]; then
    echo "✅ post-commit hook 测试通过"
    echo ""
    echo "📋 查看日志:"
    echo "   tail -30 /tmp/cursor-hooks.log"
    echo ""
    echo "🎯 预期结果:"
    echo "   オルテンシア 应该收到 Git commit 事件"
    echo "   并说: \"太棒了！代码提交成功~\" 🎉"
else
    echo "❌ post-commit hook 测试失败 (exit code: ${RESULT})"
    echo ""
    echo "📋 查看错误日志:"
    echo "   tail -50 /tmp/cursor-hooks.log"
fi

echo ""
exit $RESULT

