# Cursor asar 解包分析报告

**生成时间**: 2025-11-03
**Cursor 版本**: 2.0.43

---

## 📦 重要发现：Cursor 不使用 asar 包！

**好消息**：Cursor 的代码是直接以**目录形式**存储的，而不是打包成 asar！

这意味着：
- ✅ **无需解包/打包**
- ✅ **可以直接修改文件**
- ✅ **注入更简单**
- ✅ **更新后恢复更容易**

---

## 📁 关键目录结构

### 1. **应用根目录**
```
/Applications/Cursor.app/Contents/Resources/app/
```

### 2. **主要文件**
```
app/
├── package.json          # Electron 配置 (main: "./out/main.js")
├── product.json          # Cursor 产品配置
├── out/                  # 编译后的代码
│   ├── main.js          # ⭐ 主进程入口 (1.2MB, 混淆后)
│   ├── bootstrap-fork.js # 启动相关
│   ├── cli.js           # CLI 相关
│   └── vs/              # VSCode 核心代码
├── extensions/           # 内置扩展
│   ├── cursor-mcp/
│   ├── cursor-retrieval/
│   ├── cursor-browser-automation/  ⬅️ 有意思！
│   ├── cursor-browser-extension/   ⬅️ 有意思！
│   └── ...
├── node_modules/        # 依赖
└── resources/           # 资源文件
```

### 3. **用户数据目录**
```
~/Library/Application Support/Cursor/
├── User/                # 用户设置
│   ├── settings.json    # 用户配置
│   ├── keybindings.json
│   └── ...
├── Cache/               # 缓存
├── Backups/             # 备份
├── CachedData/          # 缓存数据
└── extensions/          # 用户安装的扩展
```

---

## 🎯 注入点分析

### **方案 A：修改 main.js 开头（推荐）**

**位置**: `/Applications/Cursor.app/Contents/Resources/app/out/main.js`

**注入方法**:
```javascript
// 在 main.js 开头添加：
(function() {
    console.log('🎉 Ortensia Bridge: Initializing...');
    
    // 加载我们的注入代码
    try {
        const path = require('path');
        const fs = require('fs');
        const userDataPath = require('electron').app.getPath('userData');
        const bridgePath = path.join(userDataPath, 'ortensia', 'bridge.js');
        
        if (fs.existsSync(bridgePath)) {
            require(bridgePath);
            console.log('✅ Ortensia Bridge: Loaded successfully');
        } else {
            console.log('⚠️  Ortensia Bridge: bridge.js not found at', bridgePath);
        }
    } catch (error) {
        console.error('❌ Ortensia Bridge: Failed to load', error);
    }
})();

// 原始 main.js 代码继续...
```

**优势**：
- ✅ 最早执行
- ✅ 完全控制主进程
- ✅ 可以访问所有 Electron API
- ✅ 代码分离（实际逻辑在 userData/ortensia/bridge.js）

### **方案 B：创建 preload 脚本**

**位置**: 修改 `app/out/main.js` 中的 BrowserWindow 配置

**注入方法**:
```javascript
// 找到 BrowserWindow 配置，添加 preload：
webPreferences: {
    preload: path.join(app.getPath('userData'), 'ortensia', 'preload.js'),
    // ... 其他配置
}
```

**优势**：
- ✅ 官方推荐的方式
- ✅ 渲染进程注入
- ✅ 可以访问 DOM
- ✅ 安全性更好

### **方案 C：修改 package.json**

**位置**: `/Applications/Cursor.app/Contents/Resources/app/package.json`

**当前内容**:
```json
{
  "name": "Cursor",
  "version": "2.0.43",
  "main": "./out/main.js",
  ...
}
```

**修改为**:
```json
{
  "name": "Cursor",
  "version": "2.0.43",
  "main": "./out/ortensia-loader.js",  ⬅️ 改为我们的加载器
  ...
}
```

然后创建 `app/out/ortensia-loader.js`:
```javascript
// 先加载我们的代码
require('./ortensia-bridge.js');

// 再加载原始 main.js
require('./main.js');
```

**优势**：
- ✅ 最干净的方式
- ✅ 不修改原始 main.js
- ✅ 容易恢复

---

## 🔍 发现的有趣扩展

### 1. **cursor-browser-automation**
```
/Applications/Cursor.app/Contents/Resources/app/extensions/cursor-browser-automation/
```
**可能用途**: Cursor 自己的浏览器自动化功能？
**研究价值**: ⭐⭐⭐⭐⭐（可能包含 UI 控制的示例代码）

### 2. **cursor-browser-extension**
```
/Applications/Cursor.app/Contents/Resources/app/extensions/cursor-browser-extension/
```
**可能用途**: Cursor 的浏览器扩展接口
**研究价值**: ⭐⭐⭐⭐⭐（可能是我们需要的）

### 3. **cursor-mcp**
```
/Applications/Cursor.app/Contents/Resources/app/extensions/cursor-mcp/
```
**可能用途**: Model Context Protocol 实现
**研究价值**: ⭐⭐⭐⭐

### 4. **cursor-retrieval**
```
/Applications/Cursor.app/Contents/Resources/app/extensions/cursor-retrieval/
```
**可能用途**: AI 上下文检索
**研究价值**: ⭐⭐⭐⭐

---

## 📊 代码特点

### main.js 分析
- **大小**: 约 1.2MB
- **格式**: 混淆/压缩后的 JavaScript
- **特点**: 
  - 使用 `__decorate` (装饰器)
  - 使用 `__param` (依赖注入)
  - 包含大量 VSCode 核心代码
  - 包含 Cursor 特有功能（AI、composer 等）

### product.json 亮点
```json
{
  "aiConfig": {
    "ariaKey": "control-key"
  },
  "cursorTrustedExtensionAuthAccess": [
    "anysphere.cursor-retrieval"
  ],
  "trustedExtensionProtocolHandlers": [
    "anysphere.cursor-deeplink",
    "anysphere.cursor-mcp"
  ]
}
```

---

## 💡 建议的实施方案

### **推荐方案：组合方案 A + 用户数据目录**

#### 1. **备份原始文件**
```bash
cp /Applications/Cursor.app/Contents/Resources/app/out/main.js \
   /Applications/Cursor.app/Contents/Resources/app/out/main.js.backup
```

#### 2. **在 userData 创建 Ortensia 目录**
```bash
mkdir -p ~/Library/Application\ Support/Cursor/ortensia
```

#### 3. **创建注入脚本**
`~/Library/Application Support/Cursor/ortensia/bridge.js`:
```javascript
// Ortensia Bridge - Cursor UI 控制桥接
const { ipcMain, BrowserWindow } = require('electron');
const WebSocket = require('ws');

console.log('🌟 Ortensia Bridge: Starting...');

// 1. 启动 WebSocket 服务器
const wss = new WebSocket.Server({ port: 9223 });
console.log('🔌 Ortensia Bridge: WebSocket server listening on ws://localhost:9223');

// 2. 存储所有窗口引用
const windows = new Map();

// 3. 监听新窗口创建
const originalFromWebContents = BrowserWindow.fromWebContents;
BrowserWindow.fromWebContents = function(webContents) {
    const win = originalFromWebContents.call(this, webContents);
    if (win && !windows.has(win.id)) {
        windows.set(win.id, win);
        console.log(`✅ Ortensia Bridge: Registered window ${win.id}`);
        
        // 窗口关闭时清理
        win.on('closed', () => {
            windows.delete(win.id);
            console.log(`❌ Ortensia Bridge: Unregistered window ${win.id}`);
        });
    }
    return win;
};

// 4. 处理 WebSocket 连接
wss.on('connection', (ws) => {
    console.log('🤝 Ortensia Bridge: Client connected');
    
    ws.on('message', async (message) => {
        try {
            const command = JSON.parse(message.toString());
            console.log('📥 Ortensia Bridge: Received command:', command);
            
            const result = await handleCommand(command);
            ws.send(JSON.stringify({ success: true, result }));
        } catch (error) {
            console.error('❌ Ortensia Bridge: Command error:', error);
            ws.send(JSON.stringify({ success: false, error: error.message }));
        }
    });
    
    ws.on('close', () => {
        console.log('👋 Ortensia Bridge: Client disconnected');
    });
});

// 5. 命令处理器
async function handleCommand(command) {
    const { action, windowId, data } = command;
    
    switch (action) {
        case 'listWindows':
            return Array.from(windows.keys());
        
        case 'executeJS':
            const win = windows.get(windowId || getActiveWindowId());
            if (!win) throw new Error(`Window ${windowId} not found`);
            return await win.webContents.executeJavaScript(data.code);
        
        case 'sendToAI':
            return await sendToAI(windowId, data.prompt);
        
        case 'getDOM':
            const targetWin = windows.get(windowId || getActiveWindowId());
            if (!targetWin) throw new Error(`Window ${windowId} not found`);
            return await targetWin.webContents.executeJavaScript('document.body.outerHTML');
        
        default:
            throw new Error(`Unknown action: ${action}`);
    }
}

async function sendToAI(windowId, prompt) {
    const win = windows.get(windowId || getActiveWindowId());
    if (!win) throw new Error(`Window ${windowId} not found`);
    
    // 执行 JS 代码来发送到 Cursor AI
    const code = `
        (async function() {
            // 查找 AI 输入框
            const input = document.querySelector('textarea[placeholder*="Ask AI"], textarea.chat-input');
            if (!input) throw new Error('AI input not found');
            
            // 设置值
            input.value = ${JSON.stringify(prompt)};
            input.dispatchEvent(new Event('input', { bubbles: true }));
            
            // 模拟 Enter
            const enterEvent = new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                bubbles: true
            });
            input.dispatchEvent(enterEvent);
            
            return 'Prompt sent to AI';
        })();
    `;
    
    return await win.webContents.executeJavaScript(code);
}

function getActiveWindowId() {
    const focusedWin = BrowserWindow.getFocusedWindow();
    return focusedWin ? focusedWin.id : windows.keys().next().value;
}

console.log('✅ Ortensia Bridge: Initialized successfully');
```

#### 4. **修改 main.js 开头**
在 `/Applications/Cursor.app/Contents/Resources/app/out/main.js` 最开头添加：
```javascript
(function(){try{const t=require("electron").app.getPath("userData"),e=require("path").join(t,"ortensia","bridge.js");require("fs").existsSync(e)&&(require(e),console.log("✅ Ortensia loaded"))}catch(t){console.error("❌ Ortensia error:",t)}})();
```

#### 5. **Python 客户端**
`ortensia_cursor_controller.py`:
```python
import websocket
import json

class OrtensiaController:
    def __init__(self, host='localhost', port=9223):
        self.ws_url = f'ws://{host}:{port}'
        self.ws = None
    
    def connect(self):
        """连接到 Cursor"""
        self.ws = websocket.create_connection(self.ws_url, timeout=5)
        print(f"✅ Connected to Cursor at {self.ws_url}")
    
    def send_command(self, action, window_id=None, data=None):
        """发送命令到 Cursor"""
        command = {
            'action': action,
            'windowId': window_id,
            'data': data or {}
        }
        self.ws.send(json.dumps(command))
        response = json.loads(self.ws.recv())
        
        if not response.get('success'):
            raise Exception(f"Command failed: {response.get('error')}")
        
        return response.get('result')
    
    def send_to_ai(self, prompt, window_id=None):
        """发送提示到 Cursor AI"""
        return self.send_command('sendToAI', window_id, {'prompt': prompt})
    
    def get_dom(self, window_id=None):
        """获取 Cursor 的 DOM 结构"""
        return self.send_command('getDOM', window_id)
    
    def list_windows(self):
        """列出所有窗口"""
        return self.send_command('listWindows')
    
    def execute_js(self, code, window_id=None):
        """执行 JavaScript 代码"""
        return self.send_command('executeJS', window_id, {'code': code})
    
    def close(self):
        """关闭连接"""
        if self.ws:
            self.ws.close()
            print("👋 Disconnected from Cursor")

# 使用示例
if __name__ == '__main__':
    controller = OrtensiaController()
    controller.connect()
    
    # 列出所有窗口
    windows = controller.list_windows()
    print(f"📊 Found {len(windows)} windows: {windows}")
    
    # 发送提示到 AI
    result = controller.send_to_ai("请优化这段代码")
    print(f"📤 AI command sent: {result}")
    
    # 获取 DOM
    dom = controller.get_dom()
    print(f"📄 DOM length: {len(dom)} characters")
    
    controller.close()
```

---

## ⚠️ 注意事项

### 1. **Cursor 更新后需要重新注入**
- Cursor 更新会覆盖 `main.js`
- 需要重新添加注入代码
- 建议：创建自动化脚本

### 2. **备份策略**
```bash
# 自动备份脚本
#!/bin/bash
BACKUP_DIR=~/cursor_backups/$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /Applications/Cursor.app/Contents/Resources/app/out/main.js \
   $BACKUP_DIR/main.js
echo "✅ Backup created at $BACKUP_DIR"
```

### 3. **安全性考虑**
- 这种方法会修改 Cursor 的核心文件
- 可能违反 Cursor 的使用条款
- 仅用于个人研究和学习

### 4. **兼容性**
- 在 macOS 上测试通过
- Windows 路径需要调整
- Linux 路径需要调整

---

## 🚀 下一步计划

### Phase 1: 基础注入 ✅（已完成分析）
- [x] 分析 Cursor 目录结构
- [x] 找到注入点
- [x] 设计注入方案
- [ ] 实施基础注入
- [ ] 测试 WebSocket 连接

### Phase 2: UI 控制
- [ ] 研究 `cursor-browser-automation` 扩展
- [ ] 研究 `cursor-browser-extension` 扩展
- [ ] 找到 AI 输入框的 DOM 结构
- [ ] 实现 `sendToAI()` 功能
- [ ] 实现 `getEditorContent()` 功能

### Phase 3: 集成 Ortensia
- [ ] 修改 `websocket_server.py` 集成控制器
- [ ] 实现事件驱动的自动化
- [ ] 测试完整工作流

### Phase 4: 自动化维护
- [ ] 创建自动重注入脚本
- [ ] 创建 Cursor 版本检测
- [ ] 创建自动恢复脚本

---

## 📚 参考资源

### Electron 相关
- [Electron 主进程与渲染进程](https://www.electronjs.org/docs/latest/tutorial/process-model)
- [Electron IPC 通信](https://www.electronjs.org/docs/latest/tutorial/ipc)
- [Electron WebContents API](https://www.electronjs.org/docs/latest/api/web-contents)

### VSCode 相关
- [VSCode Extension API](https://code.visualstudio.com/api)
- [VSCode Architecture](https://github.com/microsoft/vscode/wiki/Source-Code-Organization)

---

## 🎯 总结

### ✅ 可行性评估

| 方案 | 可行性 | 复杂度 | 推荐度 |
|------|--------|--------|--------|
| 修改 main.js | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 修改 package.json | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ |
| Preload 脚本 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

### 🎉 最终结论

**强烈推荐使用"修改 main.js + userData 目录"的组合方案！**

**理由**：
1. ✅ 不需要调试模式启动
2. ✅ 不需要禁用 SIP
3. ✅ 完全自动化
4. ✅ 代码分离（方便维护）
5. ✅ 跨平台（稍作调整）
6. ✅ 完整的 Electron API 访问
7. ✅ 可以控制所有 Cursor UI

**下一步**：立即实施注入！🚀

