# 🎉 震撼发现：Cursor 内置浏览器自动化功能！

**发现时间**: 2025-11-03
**Cursor 版本**: 2.0.43

---

## 🔥 重大发现

Cursor **已经内置了完整的浏览器自动化功能**！

无需从头开发，我们可以直接利用 Cursor 的内置 API！

---

## 📦 发现的内置扩展

### 1. **cursor-browser-automation** ⭐⭐⭐⭐⭐

**位置**: `/Applications/Cursor.app/Contents/Resources/app/extensions/cursor-browser-automation/`

**功能**: 通过 MCP (Model Context Protocol) 提供完整的浏览器自动化工具

**内置工具**:
```javascript
{
  tools: [
    {
      name: "browser_navigate",
      description: "Navigate to a URL"
    },
    {
      name: "browser_snapshot",
      description: "Capture accessibility snapshot of the current page"
    },
    {
      name: "browser_click",
      description: "Perform click on a web page"
    },
    {
      name: "browser_type",
      description: "Type text into editable element"
    },
    {
      name: "browser_hover",
      description: "Hover over element on page"
    },
    {
      name: "browser_select_option",
      description: "Select an option in a dropdown"
    },
    {
      name: "browser_press_key",
      description: "Press a key on the keyboard"
    },
    {
      name: "browser_wait_for",
      description: "Wait for text to appear/disappear"
    },
    {
      name: "browser_navigate_back",
      description: "Go back to the previous page"
    },
    {
      name: "browser_resize",
      description: "Resize the browser window"
    },
    {
      name: "browser_console_messages",
      description: "Returns all console messages"
    },
    {
      name: "browser_network_requests",
      description: "Returns all network requests"
    },
    {
      name: "browser_take_screenshot",
      description: "Take a screenshot"
    }
  ]
}
```

### 2. **cursor-browser-extension**

**位置**: `/Applications/Cursor.app/Contents/Resources/app/extensions/cursor-browser-extension/`

**功能**: Playwright 集成

**描述**: "Handles Playwright integration for Cursor"

---

## 🔍 内置 API 发现

### 核心执行命令

```javascript
// 在浏览器中执行 JavaScript
await vscode.commands.executeCommand(
  'cursor.browserView.executeJavaScript',
  code
);

// 导航到 URL
await vscode.commands.executeCommand(
  'cursor.browserView.navigate',
  url
);

// 获取控制台日志
await vscode.commands.executeCommand(
  'cursor.browserView.getConsoleLogs'
);

// 获取网络请求
await vscode.commands.executeCommand(
  'cursor.browserView.getNetworkRequests'
);

// 截图
await vscode.commands.executeCommand(
  'cursor.browserView.takeScreenshot',
  options
);

// 后退
await vscode.commands.executeCommand(
  'cursor.browserView.goBack'
);

// 调整大小
await vscode.commands.executeCommand(
  'cursor.browserView.resize',
  { width, height }
);
```

---

## 💡 这意味着什么？

### ✅ 好消息

1. **Cursor 已经内置了浏览器控制功能**
   - 无需使用 Selenium/Playwright
   - 无需调试模式
   - 无需修改 asar 包

2. **完整的 DOM 访问**
   - 可以执行任意 JavaScript
   - 可以获取页面快照
   - 可以模拟用户操作

3. **官方支持的 API**
   - 稳定可靠
   - 有完整的实现
   - 不会被封禁

### ⚠️ 但是...

**关键问题**：这些 API 是用于**浏览器视图**的，不是用于 Cursor **自身 UI** 的！

- `cursor.browserView.*` = 控制 Cursor 内置的浏览器视图（用于浏览网页）
- 我们需要的 = 控制 Cursor 自身的编辑器和 AI 界面

---

## 🤔 如何利用这些发现？

### 方案 A：研究 `browserView` 的实现

如果 Cursor 能够控制浏览器视图，那么它一定有：
1. 执行 JavaScript 的机制
2. 访问 WebContents 的能力
3. IPC 通信的方式

**我们可以借鉴这些机制来控制 Cursor 自己的 UI！**

### 方案 B：找到类似的编辑器控制 API

可能存在类似的 API：
```javascript
// 猜测可能存在的 API
await vscode.commands.executeCommand('cursor.editor.executeJavaScript', code);
await vscode.commands.executeCommand('cursor.ai.sendPrompt', prompt);
```

### 方案 C：使用 Extension API + IPC

从扩展中：
1. 注册自定义命令
2. 通过 IPC 与主进程通信
3. 主进程访问 Cursor 的 WebContents
4. 执行 JavaScript 控制 UI

---

## 📊 代码分析

### 1. JavaScript 执行机制

从 `browser-automation` 的代码看，执行 JavaScript 的方式是：

```javascript
async function executeJavaScript(code) {
  try {
    return await vscode.commands.executeCommand(
      'cursor.browserView.executeJavaScript',
      code
    );
  } catch (error) {
    logger.error('Failed to execute JavaScript:', error);
    throw error;
  }
}
```

**关键发现**：
- 使用 `vscode.commands.executeCommand`
- 命令名称是 `cursor.browserView.executeJavaScript`
- 直接传递代码字符串

### 2. DOM 访问方式

扩展使用了**可访问性树**来访问 DOM：

```javascript
function buildAccessibilityTree(element, depth = 0, maxDepth = 14) {
  // ... 构建可访问性树
  const node = {
    ref: element.getAttribute('data-cursor-ref'),
    role: roleAttr || element.tagName.toLowerCase(),
    name: computeAccessibleName(element, roleAttr),
    tag: element.tagName.toLowerCase(),
    children: []
  };
  // ...
}
```

**关键发现**：
- 使用 `data-cursor-ref` 属性标记元素
- 使用可访问性信息（role, name）
- 递归构建树结构

### 3. 元素选择系统

扩展还包含了一个**视觉元素选择器**：

```javascript
function enableElementSelection() {
  // 创建覆盖层
  overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;background:rgba(58,150,221,0.3);...';
  
  // 监听鼠标事件
  document.addEventListener('mousedown', mousedownListener, true);
  document.addEventListener('click', clickListener, true);
  
  // 发送选择的元素信息
  window.cursorBrowser.send('element-selected', {
    tagName, id, className, innerText, path, ...
  });
}
```

**关键发现**：
- 使用覆盖层高亮元素
- 使用 `window.cursorBrowser.send()` 发送消息到主进程
- 支持区域截图选择

---

## 🎯 更新后的实施方案

### **新方案：利用 Cursor 内置机制**

#### 1. 研究主进程命令注册

查找 Cursor 主进程中如何注册 `cursor.browserView.executeJavaScript` 命令：

```bash
# 搜索命令注册
grep -r "browserView.executeJavaScript" /Applications/Cursor.app/Contents/Resources/app/out/
```

#### 2. 创建类似的编辑器控制扩展

模仿 `cursor-browser-automation`，创建 `ortensia-cursor-automation`：

```javascript
// ortensia-cursor-automation/src/extension.ts
import * as vscode from 'vscode';

class OrtensiaAutomationProvider {
  tools = [
    {
      name: 'editor_execute_js',
      description: 'Execute JavaScript in Cursor editor',
      parameters: { code: 'string' }
    },
    {
      name: 'ai_send_prompt',
      description: 'Send prompt to Cursor AI',
      parameters: { prompt: 'string' }
    },
    {
      name: 'editor_get_content',
      description: 'Get current editor content',
      parameters: {}
    }
  ];
  
  async callTool(name: string, args: any) {
    switch (name) {
      case 'editor_execute_js':
        return await this.executeEditorJS(args.code);
      case 'ai_send_prompt':
        return await this.sendToAI(args.prompt);
      case 'editor_get_content':
        return await this.getEditorContent();
    }
  }
  
  private async executeEditorJS(code: string) {
    // 尝试执行 JavaScript
    try {
      // 方法 1: 查找是否有类似的命令
      return await vscode.commands.executeCommand(
        'cursor.editor.executeJavaScript',
        code
      );
    } catch {
      // 方法 2: 通过 webview 执行
      // 方法 3: 通过 IPC 执行
    }
  }
  
  private async sendToAI(prompt: string) {
    // 查找 AI 相关命令
    const commands = await vscode.commands.getCommands();
    const aiCommands = commands.filter(c => c.includes('ai') || c.includes('chat'));
    
    // 尝试执行
    // ...
  }
}

export function activate(context: vscode.ExtensionContext) {
  const provider = new OrtensiaAutomationProvider();
  
  // 注册 MCP 提供者
  const registration = vscode.cursor.registerMcpProvider(provider);
  context.subscriptions.push(registration);
}
```

#### 3. 查找所有 Cursor 特有命令

```javascript
// 在扩展中列出所有命令
async function listCursorCommands() {
  const allCommands = await vscode.commands.getCommands();
  const cursorCommands = allCommands.filter(c => 
    c.startsWith('cursor.') ||
    c.includes('ai') ||
    c.includes('chat') ||
    c.includes('composer')
  );
  console.log('Cursor commands:', cursorCommands);
}
```

---

## 🔬 下一步实验

### Phase 1: 命令发现 ⬅️ **当前**
- [ ] 查找所有 `cursor.*` 命令
- [ ] 查找 AI/Chat 相关命令
- [ ] 测试命令参数和返回值
- [ ] 文档化所有可用命令

### Phase 2: 扩展开发
- [ ] 创建 Ortensia 扩展
- [ ] 注册 MCP 提供者
- [ ] 实现 JavaScript 执行
- [ ] 实现 AI 提示发送

### Phase 3: 集成测试
- [ ] 从 Python 调用扩展
- [ ] 测试完整工作流
- [ ] 优化性能
- [ ] 错误处理

---

## 💡 关键洞察

### 1. **Cursor 使用 MCP**

MCP (Model Context Protocol) 是 Cursor 与 AI 交互的标准协议。

**意义**：
- 我们可以创建自己的 MCP 服务器
- 可以通过 MCP 控制 Cursor
- 无需修改 Cursor 核心代码

### 2. **命令系统**

Cursor 的功能都是通过 `vscode.commands.executeCommand` 暴露的。

**意义**：
- 只要找到命令名称
- 就能调用任何功能
- 不需要访问内部实现

### 3. **扩展沙箱**

扩展在沙箱中运行，但可以：
- 注册命令
- 访问编辑器 API
- 通过 MCP 与外部通信

**意义**：
- 相对安全
- 官方支持
- 更新不会破坏功能

---

## 📝 总结

### ✅ 确认的事实

1. Cursor 内置了浏览器自动化功能
2. 使用 MCP 协议提供工具
3. 通过命令系统暴露功能
4. 支持执行 JavaScript
5. 有完整的 DOM 访问能力

### ❓ 待确认的问题

1. 是否有类似的编辑器控制 API？
2. 如何从扩展访问 Cursor UI 的 WebContents？
3. 是否有 AI 相关的命令？
4. MCP 服务器如何与 Cursor 通信？

### 🎯 新的实施路径

**不再需要修改 asar 包！**

改为：
1. ✅ 查找所有 Cursor 命令
2. ✅ 创建 VSCode 扩展
3. ✅ 通过命令系统控制 Cursor
4. ✅ 通过 MCP 与 Ortensia 通信

**这是一个更干净、更稳定、更官方的方案！** 🎉

---

## 🚀 立即开始

要我开始查找所有 Cursor 命令吗？

我们可以创建一个简单的扩展，列出所有可用的命令，然后测试它们！

