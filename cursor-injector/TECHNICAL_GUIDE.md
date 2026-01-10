# Cursor Injector 技术深度指南

> 版本: V11.2 | 最后更新: 2026-01-06

## 目录

1. [架构概述](#1-架构概述)
2. [注入机制原理](#2-注入机制原理)
3. [DOM 元素识别与自动化分析](#3-dom-元素识别与自动化分析)
4. [WebSocket 通信协议](#4-websocket-通信协议)
5. [窗口定位模式](#5-窗口定位模式)
6. [使用示例](#6-使用示例)
7. [故障排除](#7-故障排除)

---

## 1. 架构概述

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Ortensia 系统架构                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │   AITuber Kit    │         │   Agent Hooks    │                      │
│  │   (Next.js)      │         │   (Python)       │                      │
│  └────────┬─────────┘         └────────┬─────────┘                      │
│           │                            │                                │
│           │         WebSocket          │                                │
│           └──────────┬─────────────────┘                                │
│                      ▼                                                  │
│           ┌──────────────────┐                                          │
│           │   中央 Server    │ ◀─── bridge/websocket_server.py          │
│           │   (Python)       │                                          │
│           │   端口: 8765     │                                          │
│           └────────┬─────────┘                                          │
│                    │                                                    │
│                    │ WebSocket                                          │
│                    ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Cursor Injector                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐ │   │
│  │  │                  注入到 Cursor main.js                       │ │   │
│  │  │                                                             │ │   │
│  │  │   • 本地 WebSocket Server (端口 9876) ─ 调试用              │ │   │
│  │  │   • WebSocket Client → 连接中央 Server (8765)               │ │   │
│  │  │   • Electron BrowserWindow API 访问                         │ │   │
│  │  │   • webContents.executeJavaScript() 执行 DOM 操作           │ │   │
│  │  └─────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                    │                                                    │
│                    ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              Cursor 渲染进程 (BrowserWindow)                      │   │
│  │                                                                   │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │   │  窗口 0     │  │  窗口 1     │  │  窗口 N     │              │   │
│  │   │  conv: xxx  │  │  conv: yyy  │  │  conv: zzz  │              │   │
│  │   └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │                          ↑                                        │   │
│  │           executeJavaScript() 直接操作 DOM                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件

| 组件 | 位置 | 职责 |
|-----|------|------|
| **install-v10.sh** | 安装脚本 | 注入代码到 Cursor main.js |
| **中央 Server** | bridge/websocket_server.py | 消息路由、会话仲裁（多端输入队列）、事件广播 |
| **协议定义** | bridge/protocol.py | 消息类型和格式 |
| **Inject 代码** | 嵌入 main.js | WebSocket 通信 + JS 执行 |

---

## 2. 注入机制原理

### 2.1 注入流程

```bash
./install-v10.sh
```

执行流程：

1. **备份原始文件**
   ```bash
   cp "/Applications/Cursor.app/Contents/Resources/app/out/main.js" \
      "/Applications/Cursor.app/Contents/Resources/app/out/main.js.ortensia.backup"
   ```

2. **创建新 main.js**
   - 在文件开头插入 Ortensia 注入代码
   - 追加原始 main.js 内容

3. **重签名**（可选）
   ```bash
   codesign --force --deep --sign - "/Applications/Cursor.app"
   ```

### 2.2 注入代码结构

```javascript
// ============================================================================
// ORTENSIA V11.2: 注入代码架构
// ============================================================================

(async function() {
    // 1. 日志系统
    const LOG = '/tmp/cursor_ortensia.log';
    function log(msg) { ... }
    
    // 2. 等待 Electron 初始化
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 3. 加载 WebSocket 模块
    const ws_module = await import('ws');
    const WebSocketServer = ws_module.WebSocketServer;
    const WebSocketClient = ws_module.WebSocket;
    
    // 4. 启动本地 Server (端口 9876) - 调试用
    const localServer = new WebSocketServer({ port: 9876 });
    
    // 5. 连接中央 Server (端口 8765) - 生产用
    const centralWs = new WebSocketClient('ws://localhost:8765');
    
    // 6. 注册到中央 Server
    register();
    
    // 7. 处理命令
    handleCommand(message);
})();

// 原始 Cursor main.js 内容...
```

### 2.3 关键技术点

#### Electron API 访问

```javascript
// 在 main.js（主进程）中可以直接访问 Electron API
const electron = await import('electron');
const windows = electron.BrowserWindow.getAllWindows();
```

#### 渲染进程代码执行

```javascript
// 在渲染进程（DOM 环境）执行 JavaScript
const result = await windows[0].webContents.executeJavaScript(`
    document.querySelector('.some-element').textContent
`);
```

---

## 3. DOM 元素识别与自动化分析

### 3.1 核心识别方法

Cursor 使用 React 构建 UI，DOM 元素具有可预测的特征。以下是关键的 DOM 识别技术：

#### 3.1.1 Conversation ID 提取

Cursor 的对话 ID 被编码在特定 DOM 元素的 `id` 属性中：

```javascript
// 查找包含 conversation_id 的元素
const convElement = document.querySelector('[id^="composer-bottom-add-context-"]');

// 提取 conversation_id (UUID 格式)
const match = convElement.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
const conversationId = match ? match[1] : null;

// 示例结果: "abc12345-6789-def0-1234-567890abcdef"
```

#### 3.1.2 完整的 Conversation 发现代码

```javascript
(() => {
    // 1. 查找 conversation_id 元素
    const el = document.querySelector('[id^="composer-bottom-add-context-"]');
    if (!el) {
        return JSON.stringify({ 
            found: false, 
            conversationId: null,
            title: null
        });
    }
    
    // 2. 提取 conversation_id
    const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
    const conversationId = match ? match[1] : null;
    
    // 3. 获取窗口标题
    let title = document.querySelector('.window-title')?.textContent?.trim();
    if (!title) {
        title = document.querySelector('.titlebar-center')?.textContent?.trim();
    }
    // 清理标题
    if (title) {
        title = title.replace(/^AgentsEditor\s*/, '').trim();
    }
    if (!title) {
        title = 'Untitled Conversation';
    }
    
    return JSON.stringify({ 
        found: true, 
        conversationId: conversationId,
        title: title,
        elementId: el.id
    });
})()
```

### 3.2 Composer 输入框定位

Cursor 的 Composer（AI 对话输入框）使用 Lexical 富文本编辑器：

```javascript
// Composer 输入框选择器（按优先级）
const inputSelectors = [
    'div[contenteditable="true"][role="textbox"]',
    'div[contenteditable="true"][aria-label*="composer"]',
    'textarea[placeholder*="Ask"]'
];

// 查找输入框
const inputSelector = inputSelectors.join(',');
const inputElement = document.querySelector(inputSelector);
```

### 3.3 文本输入模拟

由于 Lexical 编辑器不响应普通的 `value` 赋值，需要使用 `execCommand`：

```javascript
async function inputText(text) {
    const inputElement = document.querySelector('div[contenteditable="true"][role="textbox"]');
    if (!inputElement) return { success: false, error: '找不到输入框' };
    
    // 1. 聚焦
    inputElement.focus();
    
    // 2. 清空现有内容
    const range = document.createRange();
    range.selectNodeContents(inputElement);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    document.execCommand('delete', false);
    
    // 3. 插入文本（对 Lexical 有效）
    document.execCommand('insertText', false, text);
    
    return { 
        success: true, 
        inputLength: text.length,
        preview: inputElement.textContent.substring(0, 50)
    };
}
```

### 3.4 命令执行（按 Enter 键）

```javascript
async function executeCommand() {
    const inputElement = document.querySelector('div[contenteditable="true"][role="textbox"]');
    
    // 模拟 Enter 键
    const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        bubbles: true,
        cancelable: true
    });
    inputElement.dispatchEvent(enterEvent);
    
    // 备用：尝试点击发送按钮
    const sendButton = document.querySelector('button[aria-label*="Send"]') ||
                       document.querySelector('button[title*="Send"]') ||
                       document.querySelector('button[type="submit"]');
    if (sendButton) {
        sendButton.click();
    }
}
```

### 3.5 DOM 分析技巧

#### 使用 DevTools 分析 Cursor UI

1. **打开 DevTools**
   - macOS: `Cmd + Option + I`
   - 或通过菜单: View → Toggle Developer Tools

2. **元素检查技巧**
   ```javascript
   // 在 Console 中运行，列出所有带 id 的元素
   document.querySelectorAll('[id]').forEach(el => {
       console.log(el.id, el.tagName, el.className.substring(0, 50));
   });
   ```

3. **查找 React 组件名**
   ```javascript
   // 查找 React Fiber 节点
   function getReactFiber(element) {
       const key = Object.keys(element).find(k => k.startsWith('__reactFiber'));
       return element[key];
   }
   
   const fiber = getReactFiber(document.querySelector('.some-element'));
   console.log(fiber?.type?.name); // React 组件名
   ```

4. **监听 DOM 变化**
   ```javascript
   const observer = new MutationObserver((mutations) => {
       mutations.forEach(m => {
           console.log('DOM 变化:', m.type, m.target);
       });
   });
   
   observer.observe(document.body, {
       childList: true,
       subtree: true,
       attributes: true
   });
   ```

### 3.6 常用 DOM 选择器参考

| 元素 | 选择器 | 说明 |
|-----|--------|------|
| Conversation ID | `[id^="composer-bottom-add-context-"]` | UUID 在元素 ID 中 |
| Composer 输入框 | `div[contenteditable="true"][role="textbox"]` | Lexical 编辑器 |
| 发送按钮 | `button[aria-label*="Send"]` | AI 请求发送 |
| 窗口标题 | `.window-title`, `.titlebar-center` | 当前文件/对话名 |
| Agent 状态 | `[data-state]` | 任务执行状态 |
| 编辑器区域 | `.monaco-editor` | Monaco Editor |
| 侧边栏 | `.sidebar` | 文件树等 |

---

## 4. WebSocket 通信协议

### 4.1 消息格式

所有消息使用 JSON 格式，基础结构：

```json
{
    "type": "消息类型",
    "from": "发送者ID",
    "to": "接收者ID (空字符串表示广播)",
    "timestamp": 1704518400,
    "payload": { ... }
}
```

### 4.2 核心消息类型

| 消息类型 | 方向 | 说明 |
|---------|------|------|
| `register` | Client → Server | 客户端注册 |
| `register_ack` | Server → Client | 注册确认 |
| `heartbeat` | Client → Server | 心跳 |
| `execute_js` | Server → Inject | 执行 JavaScript |
| `execute_js_result` | Inject → Server | 执行结果 |
| `cursor_input_text` | AITuber → Server | 输入文本请求 |
| `get_conversation_id` | Any → Server | 查询对话 ID |

### 4.3 execute_js 详解

这是最重要的消息类型，用于在 Cursor 渲染进程执行任意 JavaScript：

```json
{
    "type": "execute_js",
    "from": "server",
    "to": "inject-12345",
    "timestamp": 1704518400,
    "payload": {
        "code": "(async function() { return document.title; })()",
        "request_id": "req-001",
        "window_index": null,
        "conversation_id": null
    }
}
```

返回结果：

```json
{
    "type": "execute_js_result",
    "from": "inject-12345",
    "to": "server",
    "timestamp": 1704518401,
    "payload": {
        "success": true,
        "result": "main.py — cursorgirl",
        "request_id": "req-001"
    }
}
```

---

## 5. 窗口定位模式

Cursor 可以同时打开多个窗口，每个窗口有独立的 conversation_id。V11.2 支持三种窗口定位模式：

### 5.1 广播模式 + JS 内检查 ⭐ 推荐

**当前默认使用的模式**

```python
# 服务器端生成包含 conversation_id 检查的 JS 代码
js_code = f"""
(async function() {{
    // 检查 conversation_id
    const targetConvId = {json.dumps(conversation_id)};
    
    if (targetConvId) {{
        const convEl = document.querySelector('[id^="composer-bottom-add-context-"]');
        const match = convEl?.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
        const currentConvId = match ? match[1] : null;
        
        if (currentConvId !== targetConvId) {{
            return JSON.stringify({{ skipped: true, reason: 'conversation_id 不匹配' }});
        }}
    }}
    
    // 匹配的窗口继续执行...
    return JSON.stringify({{ success: true }});
}})()
"""

# 发送时不指定 window_index 或 conversation_id，广播到所有窗口
execute_msg = MessageBuilder.execute_js(
    from_id="server",
    to_id="inject-12345",
    code=js_code
)
```

**优点**：
- ✅ Inject 代码保持简单
- ✅ 逻辑在服务器端，易于维护
- ✅ 可靠性高

### 5.2 单播模式 - window_index

直接指定窗口索引：

```python
execute_msg = MessageBuilder.execute_js(
    from_id="server",
    to_id="inject-12345",
    code="console.log('Hello')",
    window_index=0  # 第一个窗口
)
```

**优点**：最快
**缺点**：窗口索引可能变化

### 5.3 单播模式 - conversation_id

Inject 自动查找匹配的窗口：

```python
execute_msg = MessageBuilder.execute_js(
    from_id="server",
    to_id="inject-12345",
    code="console.log('Hello')",
    conversation_id="abc123-..."  # Inject 自动查找
)
```

**优点**：可靠
**缺点**：需要遍历窗口，稍慢

---

## 6. 使用示例

### 6.1 Python 连接示例

```python
import asyncio
import websockets
import json

async def main():
    uri = "ws://localhost:9876"  # 直连 Inject（调试用）
    # uri = "ws://localhost:8765"  # 通过中央 Server（生产用）
    
    async with websockets.connect(uri) as ws:
        # 执行 JavaScript 获取页面标题
        code = """
        (async () => {
            const { BrowserWindow } = await import('electron');
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                return await windows[0].webContents.executeJavaScript('document.title');
            }
            return null;
        })()
        """
        
        await ws.send(code)
        response = await ws.recv()
        result = json.loads(response)
        
        print(f"页面标题: {result['result']}")

asyncio.run(main())
```

### 6.2 获取所有窗口的 Conversation ID

```python
async def get_all_conversations():
    code = """
    (async () => {
        const { BrowserWindow } = await import('electron');
        const windows = BrowserWindow.getAllWindows();
        const results = [];
        
        for (let i = 0; i < windows.length; i++) {
            try {
                const convCode = `
                    (() => {
                        const el = document.querySelector('[id^="composer-bottom-add-context-"]');
                        if (!el) return JSON.stringify({ found: false });
                        const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
                        return JSON.stringify({
                            found: true,
                            conversation_id: match ? match[1] : null
                        });
                    })()
                `;
                const result = await windows[i].webContents.executeJavaScript(convCode);
                const data = JSON.parse(result);
                results.push({
                    window_index: i,
                    ...data
                });
            } catch (e) {
                results.push({ window_index: i, error: e.message });
            }
        }
        
        return JSON.stringify(results);
    })()
    """
    
    # ... 发送并接收结果
```

### 6.3 向指定对话发送命令

```python
from bridge.protocol import MessageBuilder

async def send_to_conversation(conversation_id: str, text: str):
    """向指定 conversation 发送文本并执行"""
    
    msg = MessageBuilder.cursor_input_text(
        from_id="my-client",
        to_id="server",
        text=text,
        conversation_id=conversation_id,
        execute=True  # 按 Enter 键执行
    )
    
    # 发送到中央 Server
    await websocket.send(msg.to_json())
```

---

## 7. 故障排除

### 7.1 查看日志

```bash
# 实时查看 Inject 日志
tail -f /tmp/cursor_ortensia.log

# 查看中央 Server 日志
# (输出到终端)
```

### 7.2 常见问题

| 问题 | 可能原因 | 解决方案 |
|-----|---------|---------|
| 无法连接 Inject | Cursor 未重启 | 重启 Cursor |
| 端口 9876 被占用 | 多个 Cursor 实例 | 关闭其他实例 |
| executeJavaScript 失败 | 窗口未完全加载 | 增加等待时间 |
| conversation_id 为空 | 未打开对话 | 确保有活跃对话 |
| 命令发送到所有窗口 | JS 代码缺少检查 | 使用广播模式 + JS 内检查 |

### 7.3 调试技巧

1. **在 Inject 日志中查看消息流**
   ```bash
   grep "📨\|📤\|📥" /tmp/cursor_ortensia.log
   ```

2. **测试 DOM 选择器**
   在 Cursor DevTools Console 中：
   ```javascript
   document.querySelector('[id^="composer-bottom-add-context-"]')
   ```

3. **验证 Inject 连接**
   ```bash
   # 检查端口是否监听
   lsof -i :9876
   lsof -i :8765
   ```

---

## 附录 A: 文件结构

```
cursor-injector/
├── install-v10.sh          # 安装脚本（注入代码）
├── uninstall.sh            # 卸载脚本
├── README.md               # 快速入门
├── TECHNICAL_GUIDE.md      # 本文档
├── WINDOW_MODES.md         # 窗口模式说明
├── CONFIG.md               # 配置指南
└── QUICK_START.md          # 快速开始
```

## 附录 B: 环境变量

| 变量 | 默认值 | 说明 |
|-----|--------|------|
| `ORTENSIA_SERVER` | `ws://localhost:8765` | 中央 Server 地址 |

设置方法：
```bash
export ORTENSIA_SERVER=ws://192.168.1.100:8765
```

---

## 更新历史

| 版本 | 日期 | 变更 |
|-----|------|------|
| V11.2 | 2026-01-06 | 广播模式 + JS 内检查 |
| V11.0 | 2025-12 | 多窗口支持 |
| V10.0 | 2025-12 | conversation_id 支持 |
| V9.0 | 2025-11 | 中央 Server 架构 |

