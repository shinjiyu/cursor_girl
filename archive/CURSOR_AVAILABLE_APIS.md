# Cursor 可用 API 和控制方案

**分析时间**: 2025-11-03
**Cursor 版本**: 2.0.43

---

## 🎯 已发现的 Cursor 命令

### 1. **AI/Chat 相关命令**

```javascript
// 核心命令
"cursor.aichat"                    // AI 聊天
"cursor.composer"                  // Composer 功能
"workbench.panel.aichat.view"      // AI 聊天面板视图

// Chat UI 元素
"vscode-chat-code-block"           // 聊天代码块
"vscode-chat-code-compare-block"   // 代码对比块
"vscode-chat-editor"               // 聊天编辑器
"cursor.aichat.chatdata"           // 聊天数据

// Composer 数据
"composer.composerData"            // Composer 数据结构
```

### 2. **浏览器视图命令** ⭐⭐⭐⭐⭐

```javascript
// JavaScript 执行 (最重要!)
"cursor.browserView.executeJavaScript"   // 执行 JavaScript

// 导航控制
"cursor.browserView.navigate"            // 导航到 URL
"cursor.browserView.goBack"              // 后退

// 数据获取
"cursor.browserView.getConsoleLogs"      // 获取控制台日志
"cursor.browserView.getNetworkRequests"  // 获取网络请求

// UI 操作
"cursor.browserView.takeScreenshot"      // 截图
"cursor.browserView.resize"              // 调整大小
```

### 3. **其他重要命令**

```javascript
"cursor.aisettings"                // AI 设置
"cursor.backgroundcomposer"        // 后台 Composer
"cursor.bugbot"                    // Bug 机器人
"cursor.reviewchanges"             // 审查更改
"cursor.tinderdiffeditor"          // Diff 编辑器
"cursor.update.events"             // 更新事件
```

---

## 💡 关键发现

### **重大突破：`cursor.browserView.executeJavaScript`**

这个命令可以在 Cursor 的浏览器视图中执行 JavaScript！

虽然它是为浏览器视图设计的，但我们可以尝试：
1. 查找类似的编辑器命令
2. 研究这个命令的实现方式
3. 创建自己的命令来控制 Cursor UI

---

## 🔬 可行方案分析

### **方案 1: 直接使用 VSCode API** ⭐⭐⭐⭐⭐

#### 原理
VSCode/Cursor 提供了完整的扩展 API 来控制编辑器。

#### 可用 API
```typescript
import * as vscode from 'vscode';

// 1. 编辑器控制
vscode.window.activeTextEditor?.edit(editBuilder => {
    editBuilder.insert(position, text);
});

// 2. 命令执行
vscode.commands.executeCommand('cursor.aichat', ...args);

// 3. UI 控制
vscode.window.showInputBox({ prompt: 'Enter prompt' });
vscode.window.createWebviewPanel(...);

// 4. 文件操作
vscode.workspace.openTextDocument(uri);
vscode.window.showTextDocument(document);
```

#### 实施步骤
1. 创建 VSCode 扩展
2. 使用官方 API 控制编辑器
3. 通过 WebSocket 与 Ortensia 通信
4. 无需修改 Cursor 核心代码

#### 优势
- ✅ 官方支持
- ✅ 稳定可靠
- ✅ 文档完整
- ✅ 不会被更新破坏

---

### **方案 2: 通过 MCP 服务器** ⭐⭐⭐⭐

#### 原理
Cursor 内置了 MCP (Model Context Protocol) 支持，我们可以创建自己的 MCP 服务器。

#### MCP 服务器示例
```javascript
class OrtensiaM​CPProvider {
  id = 'ortensia-cursor-controller';
  
  tools = [
    {
      name: 'insert_code',
      description: 'Insert code at cursor position',
      parameters: {
        type: 'object',
        properties: {
          code: { type: 'string' }
        }
      }
    },
    {
      name: 'get_editor_content',
      description: 'Get current editor content',
      parameters: {}
    },
    {
      name: 'execute_command',
      description: 'Execute VSCode command',
      parameters: {
        type: 'object',
        properties: {
          command: { type: 'string' },
          args: { type: 'array' }
        }
      }
    }
  ];
  
  async callTool(name, args) {
    const vscode = require('vscode');
    
    switch (name) {
      case 'insert_code':
        const editor = vscode.window.activeTextEditor;
        if (editor) {
          await editor.edit(editBuilder => {
            editBuilder.insert(editor.selection.active, args.code);
          });
        }
        return { success: true };
        
      case 'get_editor_content':
        const doc = vscode.window.activeTextEditor?.document;
        return { content: doc?.getText() || '' };
        
      case 'execute_command':
        await vscode.commands.executeCommand(args.command, ...args.args);
        return { success: true };
    }
  }
}

// 在扩展激活时注册
vscode.cursor.registerMcpProvider(new OrtensiaM​CPProvider());
```

#### 优势
- ✅ Cursor 原生支持
- ✅ 可以调用任何 VSCode 命令
- ✅ 扩展性强

---

### **方案 3: WebSocket + VSCode 扩展** ⭐⭐⭐⭐⭐ (推荐)

#### 架构图
```
Python (Ortensia)
       ↓ WebSocket
VSCode Extension
       ↓ VSCode API
Cursor Editor & AI
```

#### 扩展实现
```typescript
// extension.ts
import * as vscode from 'vscode';
import WebSocket from 'ws';

let wss: WebSocket.Server;

export function activate(context: vscode.ExtensionContext) {
    // 1. 启动 WebSocket 服务器
    wss = new WebSocket.Server({ port: 9224 });
    
    wss.on('connection', (ws) => {
        console.log('Ortensia connected');
        
        ws.on('message', async (message) => {
            try {
                const command = JSON.parse(message.toString());
                const result = await handleCommand(command);
                ws.send(JSON.stringify({ success: true, result }));
            } catch (error) {
                ws.send(JSON.stringify({ 
                    success: false, 
                    error: error.message 
                }));
            }
        });
    });
    
    // 2. 注册命令
    context.subscriptions.push(
        vscode.commands.registerCommand('ortensia.sendToAI', async () => {
            // 打开 AI 聊天并发送提示
            await vscode.commands.executeCommand('cursor.aichat');
            // TODO: 找到发送消息的方法
        })
    );
}

async function handleCommand(command: any) {
    const { action, data } = command;
    
    switch (action) {
        case 'insertCode':
            return await insertCode(data.code);
            
        case 'getContent':
            return await getEditorContent();
            
        case 'openFile':
            return await openFile(data.path);
            
        case 'executeCommand':
            return await vscode.commands.executeCommand(
                data.command, 
                ...data.args
            );
            
        case 'sendToAI':
            return await sendToAI(data.prompt);
            
        default:
            throw new Error(`Unknown action: ${action}`);
    }
}

async function insertCode(code: string) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        throw new Error('No active editor');
    }
    
    await editor.edit(editBuilder => {
        editBuilder.insert(editor.selection.active, code);
    });
    
    return { inserted: true };
}

async function getEditorContent() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        return { content: '' };
    }
    
    return {
        content: editor.document.getText(),
        language: editor.document.languageId,
        fileName: editor.document.fileName
    };
}

async function openFile(path: string) {
    const document = await vscode.workspace.openTextDocument(path);
    await vscode.window.showTextDocument(document);
    return { opened: true };
}

async function sendToAI(prompt: string) {
    // 方法 1: 尝试直接调用 AI 命令
    try {
        await vscode.commands.executeCommand('cursor.aichat', prompt);
        return { sent: true };
    } catch (e1) {
        // 方法 2: 通过剪贴板
        try {
            await vscode.env.clipboard.writeText(prompt);
            await vscode.commands.executeCommand('cursor.aichat');
            return { 
                sent: true, 
                method: 'clipboard',
                message: 'Prompt copied to clipboard, AI chat opened'
            };
        } catch (e2) {
            throw new Error(`Failed to send to AI: ${e1}, ${e2}`);
        }
    }
}
```

#### Python 客户端
```python
# ortensia_cursor_api.py
import websocket
import json
import threading

class OrtensiaC​ursorAPI:
    def __init__(self, host='localhost', port=9224):
        self.ws_url = f'ws://{host}:{port}'
        self.ws = None
        self.connected = False
        
    def connect(self):
        """连接到 Cursor 扩展"""
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # 在后台线程运行
        thread = threading.Thread(target=self.ws.run_forever)
        thread.daemon = True
        thread.start()
        
        # 等待连接
        import time
        for _ in range(10):
            if self.connected:
                break
            time.sleep(0.1)
        
        if not self.connected:
            raise Exception('Failed to connect to Cursor')
            
    def _on_open(self, ws):
        print('✅ Connected to Cursor')
        self.connected = True
        
    def _on_message(self, ws, message):
        print(f'📥 Received: {message}')
        
    def _on_error(self, ws, error):
        print(f'❌ Error: {error}')
        
    def _on_close(self, ws, close_status_code, close_msg):
        print('👋 Disconnected from Cursor')
        self.connected = False
        
    def send_command(self, action, data=None):
        """发送命令到 Cursor"""
        if not self.connected:
            raise Exception('Not connected to Cursor')
            
        command = {
            'action': action,
            'data': data or {}
        }
        
        self.ws.send(json.dumps(command))
        
    def insert_code(self, code):
        """在光标位置插入代码"""
        self.send_command('insertCode', {'code': code})
        
    def get_content(self):
        """获取编辑器内容"""
        self.send_command('getContent')
        
    def open_file(self, path):
        """打开文件"""
        self.send_command('openFile', {'path': path})
        
    def send_to_ai(self, prompt):
        """发送提示到 Cursor AI"""
        self.send_command('sendToAI', {'prompt': prompt})
        
    def execute_command(self, command, *args):
        """执行 VSCode 命令"""
        self.send_command('executeCommand', {
            'command': command,
            'args': list(args)
        })

# 使用示例
if __name__ == '__main__':
    api = OrtensiaC​ursorAPI()
    api.connect()
    
    # 插入代码
    api.insert_code('console.log("Hello from Ortensia!");')
    
    # 发送到 AI
    api.send_to_ai('请优化这段代码')
    
    # 执行命令
    api.execute_command('editor.action.formatDocument')
```

#### 优势
- ✅ 完全控制
- ✅ 实时通信
- ✅ 易于集成到 Ortensia
- ✅ 可以调用任何 VSCode API
- ✅ 不需要修改 Cursor

---

## 🎯 推荐方案总结

### **最佳方案：VSCode 扩展 + WebSocket + MCP**

结合三种方法的优势：

```
Ortensia (Python)
      ↓ WebSocket
VSCode Extension
      ├─→ VSCode API (编辑器控制)
      ├─→ VSCode Commands (功能调用)
      └─→ MCP Tools (AI 集成)
```

#### 实施路线图

##### Phase 1: 基础扩展 (1-2 天)
- [ ] 创建 VSCode 扩展项目
- [ ] 实现 WebSocket 服务器
- [ ] 实现基础命令（插入代码、获取内容）
- [ ] Python 客户端基础版

##### Phase 2: 编辑器控制 (2-3 天)
- [ ] 实现文件操作
- [ ] 实现编辑器操作
- [ ] 实现命令执行
- [ ] 测试各种场景

##### Phase 3: AI 集成 (3-5 天)
- [ ] 研究 `cursor.aichat` 命令
- [ ] 实现发送到 AI 功能
- [ ] 实现获取 AI 响应
- [ ] 双向通信

##### Phase 4: MCP 集成 (2-3 天)
- [ ] 注册 MCP 提供者
- [ ] 实现 MCP 工具
- [ ] 与 Ortensia 集成

##### Phase 5: 完整测试 (2-3 天)
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 错误处理
- [ ] 文档编写

**总计**: 10-16 天

---

## 📊 方案对比

| 方案 | 难度 | 可行性 | 稳定性 | 功能完整度 | 推荐度 |
|------|------|--------|--------|------------|--------|
| VSCode API | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| MCP 服务器 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| WebSocket 扩展 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 组合方案 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚀 立即开始

### 快速原型 (1 小时)

创建一个最小可行版本来验证概念：

```bash
# 1. 创建扩展
mkdir ortensia-cursor-extension
cd ortensia-cursor-extension
npm init -y
npm install --save-dev @types/vscode @types/node
npm install ws

# 2. 创建 extension.ts (见上面代码)

# 3. 创建 package.json
{
  "name": "ortensia-cursor-extension",
  "version": "0.0.1",
  "engines": {
    "vscode": "^1.74.0"
  },
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "ortensia.sendToAI",
        "title": "Ortensia: Send to AI"
      }
    ]
  }
}

# 4. 编译和测试
npm install -g vsce
vsce package
# 在 Cursor 中安装 .vsix
```

---

## 📝 结论

### ✅ 可行性：**非常高**

我们找到了多条可行路径，无需修改 Cursor 核心代码。

### 🎯 推荐路径：**VSCode 扩展 + WebSocket**

1. **短期**(1-2 天)：基础扩展 + WebSocket
2. **中期**(1 周)：完整编辑器控制
3. **长期**(2 周)：AI 集成 + MCP

### 💪 优势

- ✅ 不需要修改 Cursor
- ✅ 不需要禁用 SIP
- ✅ 不需要调试模式
- ✅ 官方 API 支持
- ✅ 稳定可靠
- ✅ 易于维护
- ✅ 功能强大

### 🎉 下一步

**要我立即开始创建扩展骨架吗？**

我可以创建：
1. 完整的扩展项目结构
2. WebSocket 服务器代码
3. Python 客户端代码
4. 测试脚本
5. 部署说明

预计 1-2 小时完成基础版本！🚀

