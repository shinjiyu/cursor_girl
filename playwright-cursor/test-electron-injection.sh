#!/bin/bash
# Electron 注入技术测试脚本

echo "======================================================================="
echo "  🔬 Electron JavaScript 注入技术测试"
echo "======================================================================="
echo ""

CURSOR_PATH="/Applications/Cursor.app/Contents/MacOS/Cursor"
CURSOR_RESOURCES="/Applications/Cursor.app/Contents/Resources"

# 检查 Cursor 是否存在
if [ ! -f "$CURSOR_PATH" ]; then
    echo "❌ Cursor not found at $CURSOR_PATH"
    exit 1
fi

echo "✅ Found Cursor at $CURSOR_PATH"
echo ""

# ==================== 测试 1: ELECTRON_RUN_AS_NODE ====================
echo "======================================================================="
echo "  📝 Test 1: ELECTRON_RUN_AS_NODE Environment Variable"
echo "======================================================================="
echo ""

cat > /tmp/test-node.js << 'EOF'
console.log('Testing Node.js integration...');
try {
  const process = require('process');
  console.log('✅ Node.js is available!');
  console.log('   Node version:', process.version);
  console.log('   Platform:', process.platform);
  console.log('   CWD:', process.cwd());
  
  // 测试文件系统访问
  const fs = require('fs');
  const homeDir = require('os').homedir();
  console.log('✅ Can access filesystem');
  console.log('   Home:', homeDir);
} catch (e) {
  console.log('❌ Node.js integration disabled');
  console.log('   Error:', e.message);
}
EOF

echo "Running with ELECTRON_RUN_AS_NODE=1..."
ELECTRON_RUN_AS_NODE=1 "$CURSOR_PATH" /tmp/test-node.js 2>&1 | head -20
echo ""

# ==================== 测试 2: Chrome Extension Loading ====================
echo "======================================================================="
echo "  📝 Test 2: Chrome Extension Loading"
echo "======================================================================="
echo ""

# 创建简单的 Chrome 扩展
mkdir -p /tmp/cursor-injector
cat > /tmp/cursor-injector/manifest.json << 'EOF'
{
  "name": "Cursor Injector",
  "version": "1.0.0",
  "manifest_version": 3,
  "description": "Inject code into Cursor",
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["inject.js"],
    "run_at": "document_start"
  }]
}
EOF

cat > /tmp/cursor-injector/inject.js << 'EOF'
console.log('🎉 Extension injected into Cursor!');
window.ortensiaInjected = true;
window.ortensiaAPI = {
  version: '1.0.0',
  sendToAI: (prompt) => {
    console.log('📤 Sending to AI:', prompt);
  }
};
EOF

echo "Created test extension at /tmp/cursor-injector"
echo ""
echo "To test manually, run:"
echo "  $CURSOR_PATH --load-extension=/tmp/cursor-injector"
echo ""
echo "Then open DevTools and check for: window.ortensiaInjected"
echo ""

# ==================== 测试 3: 检查 asar 包 ====================
echo "======================================================================="
echo "  📝 Test 3: Check asar Package"
echo "======================================================================="
echo ""

if [ -f "$CURSOR_RESOURCES/app.asar" ]; then
    echo "✅ Found app.asar"
    
    # 检查是否已安装 asar 工具
    if command -v asar &> /dev/null; then
        echo "✅ asar tool is installed"
        echo ""
        echo "📦 asar package info:"
        asar list "$CURSOR_RESOURCES/app.asar" | head -20
        echo "   ... (truncated)"
        echo ""
        echo "💡 To extract and modify:"
        echo "   asar extract $CURSOR_RESOURCES/app.asar /tmp/cursor-extracted"
        echo "   # modify files"
        echo "   asar pack /tmp/cursor-extracted $CURSOR_RESOURCES/app.asar.new"
    else
        echo "⚠️  asar tool not installed"
        echo "   Install with: npm install -g asar"
    fi
else
    echo "⚠️  No app.asar found (might use unpacked format)"
fi
echo ""

# ==================== 测试 4: 检查 userData 目录 ====================
echo "======================================================================="
echo "  📝 Test 4: Check userData Directory"
echo "======================================================================="
echo ""

USERDATA_DIR="$HOME/Library/Application Support/Cursor"

if [ -d "$USERDATA_DIR" ]; then
    echo "✅ Found userData directory:"
    echo "   $USERDATA_DIR"
    echo ""
    echo "📁 Contents:"
    ls -la "$USERDATA_DIR" | head -20
    echo ""
    
    # 检查是否有可注入的配置文件
    if [ -f "$USERDATA_DIR/User/settings.json" ]; then
        echo "✅ Found settings.json"
        echo "📄 Current settings (first 10 lines):"
        head -10 "$USERDATA_DIR/User/settings.json"
    fi
else
    echo "⚠️  userData directory not found"
fi
echo ""

# ==================== 测试 5: 检查命令行参数 ====================
echo "======================================================================="
echo "  📝 Test 5: Available Command Line Flags"
echo "======================================================================="
echo ""

echo "Testing common Electron flags:"
echo ""

# 测试 --help
echo "1. Testing --help:"
timeout 2s "$CURSOR_PATH" --help 2>&1 | head -20
echo ""

# 测试 --version
echo "2. Testing --version:"
timeout 2s "$CURSOR_PATH" --version 2>&1
echo ""

# 常用的 Electron/Chrome 标志
echo "💡 Useful flags to try:"
echo "   --remote-debugging-port=9222"
echo "   --load-extension=/path/to/extension"
echo "   --enable-logging"
echo "   --js-flags=\"--expose-gc\""
echo "   --disable-gpu-sandbox"
echo "   --no-sandbox"
echo ""

# ==================== 测试 6: Frida 检查 ====================
echo "======================================================================="
echo "  📝 Test 6: Frida Dynamic Instrumentation"
echo "======================================================================="
echo ""

if command -v frida &> /dev/null; then
    echo "✅ Frida is installed"
    echo "   Version: $(frida --version)"
    echo ""
    echo "💡 To inject with Frida:"
    echo "   1. Start Cursor normally"
    echo "   2. frida -n Cursor -l inject.js"
    echo ""
else
    echo "⚠️  Frida not installed"
    echo "   Install with: pip install frida-tools"
    echo ""
    echo "💡 Frida is a powerful dynamic instrumentation toolkit"
    echo "   It can inject JavaScript into running processes"
    echo "   Website: https://frida.re"
fi
echo ""

# ==================== 总结 ====================
echo "======================================================================="
echo "  📊 Summary"
echo "======================================================================="
echo ""
echo "✅ Tests completed. Results:"
echo ""
echo "1. ELECTRON_RUN_AS_NODE: See output above"
echo "2. Extension Loading: Test manually with --load-extension"
echo "3. asar Package: $([ -f "$CURSOR_RESOURCES/app.asar" ] && echo "Found" || echo "Not found")"
echo "4. userData Directory: $([ -d "$USERDATA_DIR" ] && echo "Found" || echo "Not found")"
echo "5. Command Line Flags: See output above"
echo "6. Frida: $(command -v frida &> /dev/null && echo "Available" || echo "Not installed")"
echo ""
echo "======================================================================="
echo "  📝 Next Steps"
echo "======================================================================="
echo ""
echo "Based on test results, try these approaches:"
echo ""
echo "1. If ELECTRON_RUN_AS_NODE works:"
echo "   → Use Node.js integration to inject code"
echo ""
echo "2. If extension loading works:"
echo "   → Develop Chrome extension for injection"
echo ""
echo "3. If Frida is available:"
echo "   → Use Frida for dynamic injection (most powerful)"
echo ""
echo "4. If asar is accessible:"
echo "   → Modify app package (requires repackaging)"
echo ""
echo "5. Check userData for injection points:"
echo "   → Look for preload scripts or config files"
echo ""
echo "======================================================================="

