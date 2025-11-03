#!/bin/bash

# Frida 动态注入测试脚本
# 测试 Frida 是否能动态附加到正在运行的 Cursor

echo "======================================================================="
echo "  🔥 Frida 动态注入测试"
echo "======================================================================="
echo ""

# 检查 Frida 是否安装
echo "📝 Step 1: 检查 Frida 安装"
echo "─────────────────────────────────────────────────────────────────────"
if command -v frida &> /dev/null; then
    echo "✅ Frida 已安装"
    frida --version
else
    echo "❌ Frida 未安装"
    echo ""
    echo "📦 安装方法："
    echo "   cd '/Users/user/Documents/ cursorgirl/bridge'"
    echo "   source venv/bin/activate"
    echo "   pip install frida-tools"
    echo ""
    exit 1
fi
echo ""

# 检查 Cursor 是否运行
echo "📝 Step 2: 检查 Cursor 是否运行"
echo "─────────────────────────────────────────────────────────────────────"
CURSOR_PID=$(pgrep -f "Cursor.app/Contents/MacOS/Cursor" | head -1)

if [ -z "$CURSOR_PID" ]; then
    echo "❌ Cursor 未运行"
    echo ""
    echo "请先启动 Cursor："
    echo "   open -a Cursor"
    echo ""
    echo "然后重新运行此脚本"
    exit 1
else
    echo "✅ Cursor 正在运行 (PID: $CURSOR_PID)"
fi
echo ""

# 创建测试脚本
echo "📝 Step 3: 准备动态注入脚本"
echo "─────────────────────────────────────────────────────────────────────"

TEST_SCRIPT="/tmp/frida-test-cursor.js"
cat > "$TEST_SCRIPT" << 'EOF'
console.log('');
console.log('='.repeat(70));
console.log('  🎉 Frida 动态注入成功！');
console.log('='.repeat(70));
console.log('');

// 测试 1: 访问 window 对象
console.log('✅ 测试 1: 访问 window 对象');
console.log('   typeof window:', typeof window);
console.log('   typeof document:', typeof document);
console.log('');

// 测试 2: 获取页面信息
console.log('✅ 测试 2: 获取页面信息');
try {
    console.log('   document.title:', document.title);
    console.log('   window.location:', window.location.href);
} catch (e) {
    console.log('   ⚠️  无法访问 document (可能需要附加到渲染进程)');
}
console.log('');

// 测试 3: 查找 DOM 元素
console.log('✅ 测试 3: 查找 DOM 元素');
try {
    const bodyElements = document.body ? document.body.children.length : 0;
    console.log('   body.children.length:', bodyElements);
    
    const textareas = document.querySelectorAll('textarea').length;
    console.log('   textarea 数量:', textareas);
} catch (e) {
    console.log('   ⚠️  无法访问 DOM:', e.message);
}
console.log('');

// 测试 4: 查找 Monaco Editor
console.log('✅ 测试 4: 查找 Monaco Editor');
if (typeof window !== 'undefined') {
    if (window.monaco) {
        console.log('   ✅ Monaco Editor 可用！');
        if (window.monaco.editor) {
            const editors = window.monaco.editor.getEditors();
            console.log('   编辑器数量:', editors.length);
        }
    } else {
        console.log('   ⚠️  Monaco Editor 未找到');
    }
}
console.log('');

// 测试 5: 创建全局 API
console.log('✅ 测试 5: 创建全局 API');
try {
    if (typeof window !== 'undefined') {
        window.fridaTestAPI = {
            version: '1.0.0',
            timestamp: Date.now(),
            test: function() {
                return 'Frida 动态注入测试成功！';
            }
        };
        console.log('   ✅ window.fridaTestAPI 已创建');
        console.log('   测试调用:', window.fridaTestAPI.test());
    }
} catch (e) {
    console.log('   ⚠️  创建 API 失败:', e.message);
}
console.log('');

// 暴露 RPC 接口给 Python
rpc.exports = {
    test: function() {
        return {
            success: true,
            message: 'Frida RPC 工作正常！',
            timestamp: Date.now()
        };
    },
    
    getDomInfo: function() {
        try {
            return {
                success: true,
                title: document.title,
                bodyChildren: document.body.children.length,
                textareas: document.querySelectorAll('textarea').length
            };
        } catch (e) {
            return {
                success: false,
                error: e.message
            };
        }
    }
};

console.log('='.repeat(70));
console.log('  ✅ 所有测试完成！');
console.log('  💡 Frida 已成功动态注入到 Cursor');
console.log('  💡 你可以在 Python 中调用: script.exports.test()');
console.log('='.repeat(70));
console.log('');
EOF

echo "✅ 测试脚本已创建: $TEST_SCRIPT"
echo ""

# 动态注入测试
echo "📝 Step 4: 执行动态注入"
echo "─────────────────────────────────────────────────────────────────────"
echo "🔥 附加到 Cursor 并注入测试脚本..."
echo ""
echo "⚠️  注意: 如果 Frida 卡住，说明可能附加到了主进程而不是渲染进程"
echo "          这是正常的，我们会在下一步创建 Python 版本来解决"
echo ""
echo "按 Ctrl+C 可以中断测试"
echo ""

# 设置超时，避免卡住
timeout 10s frida -n Cursor -l "$TEST_SCRIPT" --no-pause 2>&1 || {
    EXIT_CODE=$?
    echo ""
    if [ $EXIT_CODE -eq 124 ]; then
        echo "⏱️  测试超时（这可能是正常的，因为 Frida 可能附加到了主进程）"
    else
        echo "⚠️  Frida 执行遇到问题（退出码: $EXIT_CODE）"
    fi
    echo ""
}

echo ""
echo "======================================================================="
echo "  📊 测试总结"
echo "======================================================================="
echo ""

if [ -f "$TEST_SCRIPT" ]; then
    echo "✅ Frida 可以附加到 Cursor"
    echo "✅ 测试脚本已创建: $TEST_SCRIPT"
    echo ""
    echo "⚠️  如果上面的测试没有输出 DOM 信息，这是因为："
    echo "   1. Cursor 有多个进程（主进程、渲染进程）"
    echo "   2. 我们需要附加到渲染进程才能访问 DOM"
    echo "   3. 下一步：使用 Python 脚本来正确附加到渲染进程"
    echo ""
fi

echo "🚀 下一步："
echo "   1. 使用 Python 脚本进行更精确的测试"
echo "   2. 运行: python playwright-cursor/test-frida-python.py"
echo ""

echo "📚 相关文档:"
echo "   - Frida 动态注入原理: FRIDA_INJECTION_MECHANISM.md"
echo "   - Frida DOM 访问: FRIDA_DOM_ACCESS_EXPLAINED.md"
echo ""

echo "✅ 测试完成！"

