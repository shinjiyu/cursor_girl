# VSCode Extension 可以做什么？

**关键问题**: 我们写的 VSCode 扩展，能调用 Cursor 的内部代码吗？

---

## ✅ 可以调用的

### 1. **标准 VSCode API** ✅✅✅

这些是**完全可以用的**，因为 Cursor 基于 VSCode：

```typescript
import * as vscode from 'vscode';

// ✅ 编辑器操作
const editor = vscode.window.activeTextEditor;
await editor.edit(builder => {
    builder.insert(position, 'code');
});

// ✅ 文件操作
const doc = await vscode.workspace.openTextDocument(path);
await vscode.window.showTextDocument(doc);

// ✅ 命令注册
vscode.commands.registerCommand('myExtension.doSomething', () => {});

// ✅ WebView 创建
const panel = vscode.window.createWebviewPanel(...);

// ✅ 状态栏、通知等
vscode.window.showInformationMessage('Hello!');
```

### 2. **执行 Cursor 注册的命令** ✅✅

通过 `executeCommand` 可以调用 Cursor 注册的命令：

```typescript
// ✅ 调用 Cursor 的命令（如果它们是公开注册的）
await vscode.commands.executeCommand('cursor.aichat');
await vscode.commands.executeCommand('cursor.composer');

// ✅ 但问题是：我们不知道这些命令的参数！
// 可能需要：
await vscode.commands.executeCommand('cursor.aichat', {
    prompt: 'Hello',  // 猜测的参数
    // ... 其他参数？
});
```

**关键问题**：
- ❓ 这些命令是否公开注册？
- ❓ 它们接受什么参数？
- ❓ 它们返回什么？

---

## ❌ **不能**调用的

### 1. **Cursor 内部 API** ❌

我之前提到的 `vscode.cursor.*` API **可能不存在**：

```typescript
// ❌ 这个可能不行（我猜测的 API）
vscode.cursor.registerMcpProvider(...)

// ❌ Cursor 内部的私有 API
// 这些只在 Cursor 内部使用，不对外暴露
```

### 2. **直接访问 Cursor 的内部状态** ❌

```typescript
// ❌ 无法直接访问
cursor.internal.aiState
cursor.internal.chatHistory
cursor.internal.composerContext
```

---

## 🔍 需要验证的方案

### **方法 1: 尝试调用 Cursor 命令**

```typescript
// 我们需要测试这些命令是否真的存在

// 获取所有注册的命令
const allCommands = await vscode.commands.getCommands();
const cursorCommands = allCommands.filter(cmd => 
    cmd.startsWith('cursor.')
);

console.log('Cursor 命令:', cursorCommands);

// 尝试调用
try {
    await vscode.commands.executeCommand('cursor.aichat');
    // 如果成功，说明这个命令是公开的
} catch (error) {
    // 如果失败，说明不可用或需要参数
    console.error(error);
}
```

### **方法 2: 监听 Cursor 的命令执行**

```typescript
// VSCode API 允许拦截命令执行
// 但只能在执行前/后，不能修改

// 这个可能不行，需要测试
```

### **方法 3: 通过 UI 自动化（退而求其次）**

如果命令不可用，我们可以：

```typescript
// 1. 通过剪贴板传递数据
await vscode.env.clipboard.writeText('prompt for AI');

// 2. 打开 AI 聊天
await vscode.commands.executeCommand('workbench.panel.aichat.view');

// 3. 模拟快捷键（通过 executeCommand）
await vscode.commands.executeCommand('type', { text: prompt });
await vscode.commands.executeCommand('editor.action.submitComment');
```

---

## 🎯 **实际可行的方案**

### **方案 A: 基础扩展（100% 可行）** ⭐⭐⭐⭐⭐

**只使用标准 VSCode API**：

```typescript
class OrtensiaExtension {
    // ✅ 编辑器控制
    async insertCode(code: string) {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;
        
        await editor.edit(builder => {
            builder.insert(editor.selection.active, code);
        });
    }
    
    // ✅ 获取内容
    async getContent() {
        const editor = vscode.window.activeTextEditor;
        return editor?.document.getText() || '';
    }
    
    // ✅ 打开文件
    async openFile(path: string) {
        const doc = await vscode.workspace.openTextDocument(path);
        await vscode.window.showTextDocument(doc);
    }
    
    // ✅ 执行格式化等命令
    async formatDocument() {
        await vscode.commands.executeCommand(
            'editor.action.formatDocument'
        );
    }
    
    // ✅ WebSocket 服务器（与 Ortensia 通信）
    startWebSocketServer() {
        // 完全可行
    }
}
```

**优势**：
- ✅ 100% 可行
- ✅ 稳定可靠
- ✅ 不依赖 Cursor 特定功能

**限制**：
- ❌ 无法直接发送消息到 Cursor AI
- ❌ 无法获取 AI 响应

---

### **方案 B: 扩展 + 剪贴板（90% 可行）** ⭐⭐⭐⭐

**通过剪贴板间接与 AI 交互**：

```typescript
class OrtensiaAIBridge {
    async sendToAI(prompt: string) {
        // 1. 复制提示到剪贴板
        await vscode.env.clipboard.writeText(prompt);
        
        // 2. 尝试打开 AI 聊天
        try {
            // 尝试不同的命令
            await vscode.commands.executeCommand('cursor.aichat');
        } catch {
            try {
                await vscode.commands.executeCommand('workbench.panel.aichat.view');
            } catch {
                // 如果都失败，显示提示
                vscode.window.showInformationMessage(
                    'Please open AI chat and paste (Cmd+V)'
                );
            }
        }
        
        // 3. 提示用户粘贴
        // 或者尝试模拟粘贴（可能不行）
        return { 
            method: 'clipboard',
            message: 'Prompt copied, please paste in AI chat'
        };
    }
}
```

**优势**：
- ✅ 基本可行
- ✅ 不依赖私有 API

**限制**：
- ⚠️ 需要用户手动粘贴
- ⚠️ 无法自动化

---

### **方案 C: 测试然后决定（推荐）** ⭐⭐⭐⭐⭐

**先创建扩展，测试哪些 Cursor 命令可用**：

```typescript
// Step 1: 列出所有命令
export async function activate(context: vscode.ExtensionContext) {
    // 获取所有命令
    const commands = await vscode.commands.getCommands(true);
    const cursorCommands = commands.filter(c => 
        c.includes('cursor') || 
        c.includes('ai') || 
        c.includes('chat')
    );
    
    console.log('='.repeat(80));
    console.log('Available Cursor Commands:');
    console.log('='.repeat(80));
    cursorCommands.forEach(cmd => console.log(`  - ${cmd}`));
    console.log('='.repeat(80));
    
    // Step 2: 测试每个命令
    for (const cmd of cursorCommands) {
        try {
            const result = await vscode.commands.executeCommand(cmd);
            console.log(`✅ ${cmd} -> ${JSON.stringify(result)}`);
        } catch (error) {
            console.log(`❌ ${cmd} -> ${error.message}`);
        }
    }
}
```

**然后根据测试结果决定**：
1. 如果 `cursor.aichat` 等命令可用 → 直接调用
2. 如果不可用 → 使用剪贴板方案
3. 如果都不行 → 纯编辑器控制

---

## 🔬 实验方案

### **立即测试 Cursor 命令可用性**

我们可以创建一个**最小测试扩展**：

```typescript
// test-cursor-commands/extension.ts
import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {
    console.log('🔍 Testing Cursor Commands...');
    
    // 1. 列出所有命令
    const allCommands = await vscode.commands.getCommands(true);
    
    // 2. 过滤 Cursor 相关命令
    const cursorCommands = allCommands.filter(cmd => 
        cmd.startsWith('cursor.') ||
        cmd.includes('aichat') ||
        cmd.includes('composer')
    );
    
    console.log('\n📋 Found Cursor Commands:');
    cursorCommands.forEach(cmd => console.log(`  - ${cmd}`));
    
    // 3. 注册测试命令
    context.subscriptions.push(
        vscode.commands.registerCommand('test.cursorCommands', async () => {
            const results = [];
            
            for (const cmd of cursorCommands) {
                try {
                    // 尝试不带参数执行
                    const result = await vscode.commands.executeCommand(cmd);
                    results.push({
                        command: cmd,
                        success: true,
                        result: result
                    });
                } catch (error) {
                    results.push({
                        command: cmd,
                        success: false,
                        error: error.message
                    });
                }
            }
            
            // 显示结果
            const panel = vscode.window.createWebviewPanel(
                'cursorCommandsTest',
                'Cursor Commands Test Results',
                vscode.ViewColumn.One,
                {}
            );
            
            panel.webview.html = generateResultsHTML(results);
        })
    );
    
    console.log('✅ Test extension activated');
    console.log('💡 Run command: "Test Cursor Commands" to see results');
}

function generateResultsHTML(results: any[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: monospace; padding: 20px; }
                .success { color: green; }
                .error { color: red; }
                .command { font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Cursor Commands Test Results</h1>
            ${results.map(r => `
                <div class="${r.success ? 'success' : 'error'}">
                    <span class="command">${r.command}</span>:
                    ${r.success ? 
                        `✅ Success (${JSON.stringify(r.result)})` :
                        `❌ Error (${r.error})`
                    }
                </div>
            `).join('')}
        </body>
        </html>
    `;
}
```

---

## 💡 结论

### **我们能做什么？**

#### 100% 确定可以：
1. ✅ 编辑器操作（插入、删除、选择、格式化）
2. ✅ 文件操作（打开、保存、关闭）
3. ✅ WebSocket 服务器（与 Ortensia 通信）
4. ✅ UI 控制（通知、输入框、WebView）
5. ✅ 执行标准 VSCode 命令

#### 需要测试才知道：
1. ❓ 调用 `cursor.aichat` 等命令
2. ❓ 获取 AI 响应
3. ❓ 控制 Composer

#### 确定不能：
1. ❌ 直接访问 Cursor 内部 API
2. ❌ 修改 Cursor 核心行为
3. ❌ Hook Cursor 内部事件

---

## 🎯 推荐策略

### **分阶段实施**

#### Phase 1: 基础版（立即开始）
**只用标准 VSCode API**：
- ✅ WebSocket 服务器
- ✅ 编辑器控制
- ✅ 文件操作
- ✅ 与 Ortensia 通信

**这个阶段 100% 可行！**

#### Phase 2: 测试版（第 2-3 天）
**创建测试扩展**：
- 列出所有 Cursor 命令
- 测试哪些可以调用
- 测试参数和返回值
- 根据结果调整方案

#### Phase 3: 增强版（根据测试结果）
**如果 Cursor 命令可用**：
- ✅ 直接调用 AI
- ✅ 控制 Composer

**如果不可用**：
- ✅ 使用剪贴板方案
- ✅ 或者纯编辑器控制

---

## 📝 修正后的方案

### **实际可行的架构**

```
Ortensia (Python)
       ↓
WebSocket (9224)
       ↓
VSCode Extension
       ├─→ ✅ 标准 VSCode API (100% 可用)
       │   ├─ 编辑器操作
       │   ├─ 文件操作
       │   └─ UI 控制
       │
       └─→ ❓ Cursor 命令 (需要测试)
           ├─ cursor.aichat
           ├─ cursor.composer
           └─ workbench.panel.aichat.view
```

### **最坏情况下的功能**

即使 Cursor 命令都不可用，我们仍然可以：

1. **完全控制编辑器**
   - 插入/删除代码
   - 移动光标
   - 选择文本
   - 格式化

2. **文件系统集成**
   - 打开/保存文件
   - 创建/删除文件
   - 文件监听

3. **与 Ortensia 通信**
   - 接收事件
   - 发送响应
   - 实时同步

4. **用户交互**
   - 显示通知
   - 输入框
   - WebView 界面

**这已经很强大了！** 只是无法直接控制 AI，但可以控制编辑器本身。

---

## 🚀 下一步

### **建议**：

1. **先创建基础扩展**（100% 可行的部分）
2. **然后创建测试扩展**（测试 Cursor 命令）
3. **根据测试结果**决定是否需要调整方案

**要我开始吗？**

我会创建：
1. ✅ 基础扩展（只用标准 API）
2. ✅ 测试扩展（测试 Cursor 命令）
3. ✅ Python 客户端
4. ✅ 完整测试脚本

这样我们就能**实际验证**哪些功能可用！

