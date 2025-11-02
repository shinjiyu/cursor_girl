# Electron JavaScript 注入技术完整指南

**目标**: 从 Electron 层面注入 JavaScript 到 Cursor，实现自动化控制

---

## 🎯 方案总览

| 方案 | 难度 | 侵入性 | 稳定性 | 推荐度 |
|-----|------|--------|--------|--------|
| Frida 动态注入 | 🟡 中 | 🟢 低 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| ELECTRON_RUN_AS_NODE | 🟢 低 | 🟢 低 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Chrome Extension | 🟢 低 | 🟢 低 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| userData 注入 | 🟢 低 | 🟡 中 | ⭐⭐⭐ | ⭐⭐⭐ |
| asar 修改 | 🔴 高 | 🔴 高 | ⭐⭐ | ⭐⭐ |

---

## 🥇 方案 1: Frida 动态注入（最推荐）

### 原理

Frida 是一个动态代码注入工具，可以在运行时注入 JavaScript 到任何进程。

### 优势

- ✅ **无需修改应用** - 不破坏 Cursor
- ✅ **动态注入** - 随时附加/分离
- ✅ **功能强大** - 可以 hook 任何函数
- ✅ **跨平台** - Windows/macOS/Linux
- ✅ **实时调试** - 可以实时修改行为

### 安装

```bash
# 安装 Frida
pip install frida-tools

# 验证安装
frida --version
```

### 使用步骤

#### 1. 启动 Cursor

```bash
# 正常启动 Cursor
open -a Cursor
```

#### 2. 附加 Frida

```bash
# 方法 A: 通过进程名
frida -n Cursor -l frida-inject-cursor.js

# 方法 B: 通过 PID
PID=$(pgrep -f "Cursor.app/Contents/MacOS/Cursor")
frida -p $PID -l frida-inject-cursor.js
```

#### 3. 使用 Python 控制

```python
from frida_cursor_controller import FridaCursorController

# 创建控制器
controller = FridaCursorController()

# 附加到 Cursor
controller.attach()

# 加载注入脚本
controller.load_script('frida-inject-cursor.js')

# 执行 JavaScript
controller.execute_js('''
    console.log("Hello from Frida!");
    window.ortensiaAPI.sendToAI("Fix the error");
''')
```

### 注入能力

```javascript
// 在 Cursor 中可以做的事情：

// 1. 访问 window 对象
window.ortensiaAPI = { /* ... */ };

// 2. 查找 Monaco Editor
const editor = window.monaco.editor.getEditors()[0];
editor.getValue();  // 获取代码
editor.setValue('new code');  // 设置代码

// 3. Hook 函数
const originalFetch = window.fetch;
window.fetch = function(...args) {
    console.log('Fetch called:', args);
    return originalFetch.apply(this, args);
};

// 4. 监听 DOM 变化
const observer = new MutationObserver((mutations) => {
    // 检测 AI 界面变化
});
observer.observe(document.body, {
    childList: true,
    subtree: true
});

// 5. 查找 Cursor AI API
Object.keys(window).filter(key => 
    key.includes('cursor') || 
    key.includes('ai')
);
```

### 限制

- ⚠️ 需要安装 Frida
- ⚠️ 需要进程正在运行
- ⚠️ 可能被安全软件阻止

---

## 🥈 方案 2: ELECTRON_RUN_AS_NODE

### 原理

通过环境变量启用 Node.js 集成，可以在 Electron 中使用 `require()`。

### 测试

```bash
# 创建测试脚本
cat > /tmp/test.js << 'EOF'
console.log('Testing Node.js integration...');
try {
    const fs = require('fs');
    console.log('✅ Node.js is available!');
    console.log('Home:', require('os').homedir());
} catch (e) {
    console.log('❌ Node.js not available:', e.message);
}
EOF

# 测试
ELECTRON_RUN_AS_NODE=1 /Applications/Cursor.app/Contents/MacOS/Cursor /tmp/test.js
```

### 如果成功

```javascript
// 可以在 DevTools 中使用 Node.js API
const fs = require('fs');
const path = require('path');

// 读取文件
fs.readFileSync('/path/to/file', 'utf8');

// 执行系统命令
const { exec } = require('child_process');
exec('echo "Hello from Node"');

// 创建 WebSocket 服务器
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });
```

### 注入方法

```bash
# 启动时注入
ELECTRON_RUN_AS_NODE=1 \
ELECTRON_ENABLE_LOGGING=1 \
/Applications/Cursor.app/Contents/MacOS/Cursor
```

---

## 🥉 方案 3: Chrome Extension Loading

### 原理

Electron 基于 Chromium，可以加载 Chrome 扩展。

### 创建扩展

#### manifest.json
```json
{
  "name": "Cursor Ortensia Controller",
  "version": "1.0.0",
  "manifest_version": 3,
  "description": "Control Cursor for Ortensia",
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["inject.js"],
    "run_at": "document_start"
  }],
  "permissions": [
    "tabs",
    "webRequest"
  ]
}
```

#### inject.js
```javascript
console.log('🎉 Ortensia extension loaded!');

// 创建全局 API
window.ortensiaAPI = {
    sendToAI: (prompt) => {
        console.log('📤 Sending to AI:', prompt);
        
        // 查找 Cursor AI 的输入框
        const inputs = document.querySelectorAll('textarea, input[type="text"]');
        for (const input of inputs) {
            if (input.placeholder && 
                (input.placeholder.includes('AI') || 
                 input.placeholder.includes('chat'))) {
                input.value = prompt;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                
                // 模拟回车
                input.dispatchEvent(new KeyboardEvent('keydown', {
                    key: 'Enter',
                    keyCode: 13,
                    bubbles: true
                }));
                
                console.log('✅ Sent to AI input');
                break;
            }
        }
    }
};

// 监听来自外部的消息
window.addEventListener('message', (event) => {
    if (event.data.type === 'ORTENSIA_COMMAND') {
        console.log('Received command:', event.data);
        window.ortensiaAPI.sendToAI(event.data.prompt);
    }
});
```

### 加载扩展

```bash
# 启动 Cursor 并加载扩展
/Applications/Cursor.app/Contents/MacOS/Cursor \
  --load-extension=/path/to/extension
```

### 从外部控制

```javascript
// 在其他页面或脚本中
window.postMessage({
    type: 'ORTENSIA_COMMAND',
    prompt: 'Fix the error'
}, '*');
```

---

## 方案 4: userData 目录注入

### 原理

Electron 应用通常从 userData 目录加载配置。

### userData 位置

```bash
# macOS
~/Library/Application Support/Cursor

# Windows
%APPDATA%/Cursor

# Linux
~/.config/Cursor
```

### 注入方法

#### 1. 创建 preload 脚本

```bash
mkdir -p ~/Library/Application\ Support/Cursor/ortensia
cat > ~/Library/Application\ Support/Cursor/ortensia/preload.js << 'EOF'
console.log('🎉 Ortensia preload script loaded!');

window.addEventListener('DOMContentLoaded', () => {
    console.log('Injecting Ortensia API...');
    
    window.ortensiaAPI = {
        version: '1.0.0',
        sendToAI: (prompt) => {
            console.log('Sending to AI:', prompt);
        }
    };
});
EOF
```

#### 2. 修改配置

查找并修改 `settings.json` 或其他配置文件：

```json
{
    "electron.preload": "~/Library/Application Support/Cursor/ortensia/preload.js"
}
```

### 限制

- ⚠️ Cursor 可能不读取自定义 preload
- ⚠️ 需要找到正确的配置文件

---

## 方案 5: asar 包修改（不推荐）

### 原理

修改 Electron 的 asar 包，直接修改应用代码。

### 步骤

```bash
# 1. 安装 asar
npm install -g asar

# 2. 备份原始包
cp /Applications/Cursor.app/Contents/Resources/app.asar \
   /Applications/Cursor.app/Contents/Resources/app.asar.backup

# 3. 解包
asar extract /Applications/Cursor.app/Contents/Resources/app.asar \
             /tmp/cursor-extracted

# 4. 修改文件
cd /tmp/cursor-extracted
# 在 main.js 或其他文件中添加你的代码

# 5. 重新打包
asar pack /tmp/cursor-extracted \
          /Applications/Cursor.app/Contents/Resources/app.asar
```

### 注入示例

在 `main.js` 开头添加：

```javascript
// Ortensia 注入代码
const { BrowserWindow } = require('electron');

// Hook BrowserWindow creation
const originalCreateWindow = BrowserWindow.prototype.constructor;
BrowserWindow = function(...args) {
    const win = originalCreateWindow.apply(this, args);
    
    // 注入代码到所有窗口
    win.webContents.executeJavaScript(`
        console.log('Ortensia injected via asar modification');
        window.ortensiaAPI = {
            // 你的 API
        };
    `);
    
    return win;
};
```

### 劣势

- ❌ **每次更新都要重做**
- ❌ **破坏代码签名**
- ❌ **可能违反许可协议**
- ❌ **不推荐用于生产**

---

## 🧪 测试脚本

### 运行测试

```bash
cd playwright-cursor

# 1. 测试所有方法
chmod +x test-electron-injection.sh
./test-electron-injection.sh

# 2. 测试 Frida（推荐）
python frida-cursor-controller.py

# 3. 测试 Extension
/Applications/Cursor.app/Contents/MacOS/Cursor \
  --load-extension=/tmp/cursor-injector
```

---

## 📊 最佳实践建议

### 推荐路径

1. **首选**: Frida 动态注入
   - 强大、灵活、无破坏性
   - 可以实时调试和修改

2. **备选**: Chrome Extension
   - 如果 Cursor 支持扩展加载
   - 清晰的注入机制

3. **最后**: ELECTRON_RUN_AS_NODE
   - 如果其他方法都不行
   - 但可能被 Cursor 禁用

### 不推荐

- ❌ asar 修改 - 破坏性太强
- ❌ 硬编码坐标 - 不可靠

---

## 🎯 实际应用示例

### 完整工作流

```python
# 1. 使用 Frida 注入
from frida_cursor_controller import FridaCursorController

controller = FridaCursorController()
controller.attach()
controller.load_script('frida-inject-cursor.js')

# 2. 注入控制代码
controller.inject()

# 3. 集成到オルテンシア
async def on_agent_complete(result):
    # オルテンシア 分析结果
    if 'error' in result:
        # 通过 Frida 发送命令
        controller.execute_js('''
            window.ortensiaAPI.sendToAI('请修复错误');
        ''')
    
    elif 'test' not in result:
        controller.execute_js('''
            window.ortensiaAPI.sendToAI('请添加测试');
        ''')

# 4. 监听 Cursor 事件
controller.execute_js('''
    // 监听代码变化
    const editor = window.monaco.editor.getEditors()[0];
    editor.onDidChangeModelContent(() => {
        console.log('Code changed');
        // 发送到オルテンシア
    });
''')
```

---

## ⚠️ 安全性和法律考虑

### 注意事项

1. **仅用于个人使用**
   - 不要分发修改后的应用
   - 不要用于商业用途

2. **尊重许可协议**
   - 查看 Cursor 的使用条款
   - 某些注入方法可能违反协议

3. **安全风险**
   - 注入的代码可以访问所有数据
   - 不要注入不可信的代码

4. **备份**
   - 修改前备份应用
   - 保留原始文件

---

## 📚 参考资料

- [Frida 官方文档](https://frida.re/docs/)
- [Electron 文档](https://www.electronjs.org/docs)
- [Chrome Extension API](https://developer.chrome.com/docs/extensions/)
- [asar 工具](https://github.com/electron/asar)

---

## 🎉 总结

**最推荐的方案**: Frida 动态注入

理由：
- ✅ 无破坏性
- ✅ 功能强大
- ✅ 可以实时调试
- ✅ 跨平台
- ✅ 随时可以分离

**下一步**:
1. 安装 Frida: `pip install frida-tools`
2. 运行测试: `./test-electron-injection.sh`
3. 尝试注入: `python frida-cursor-controller.py`
4. 集成到オルテンシア系统

---

**状态**: 调研完成，方案可行 ✅  
**推荐方案**: Frida 动态注入 ⭐⭐⭐⭐⭐

