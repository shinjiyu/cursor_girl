# DOM 操作重构方案

**目标**: 将嵌入在 `install-v8.sh` 中的 DOM 操作代码提取为独立模块

---

## 🎯 重构目标

### 当前问题

1. **代码耦合** - DOM 操作代码嵌入在 464 行的 shell 脚本中
2. **难以维护** - Cursor UI 更新时需要在 shell 脚本中查找修改
3. **难以测试** - 无法独立测试 DOM 操作
4. **难以扩展** - 添加新功能需要修改大型脚本

### 重构后优势

1. **清晰的分层** - DOM 操作、协议处理、网络通信分离
2. **易于维护** - Cursor UI 变化只需修改 `cursor_dom_operations.js`
3. **便于测试** - 可以独立测试每个操作
4. **便于扩展** - 添加新功能只需在操作类中添加方法

---

## 📁 新的文件结构

```
cursor-injector/
├── cursor_dom_operations.js      ✅ DOM 操作封装（新）
├── test_dom_operations.py        ✅ 测试脚本（新）
├── install-v9.sh                 🔄 使用封装的新版本（待创建）
├── install-v8.sh                 📦 当前版本（保留）
└── test-input-complete.py        📦 现有测试（保持兼容）
```

---

## 🏗️ 封装架构

### 1. CursorDOMManager（管理器）

```javascript
const cursorDOM = new CursorDOMManager();

// 访问各个操作类
cursorDOM.composer.*    // Composer 操作
cursorDOM.editor.*      // Editor 操作（预留）
cursorDOM.terminal.*    // Terminal 操作（预留）
```

### 2. ComposerOperations（Composer 操作）

**已实现的方法**:

```javascript
// 查找输入框
composer.findInputElement()
// => { success: true, data: <Element> }

// 输入文本
composer.inputText("Hello World")
// => { success: true, message: "成功输入 11 个字符", data: {...} }

// 追加文本
composer.appendText(" - 追加内容")
// => { success: true, ... }

// 清空输入
composer.clearInput()
// => { success: true, message: "输入框已清空" }

// 获取内容
composer.getInputContent()
// => { success: true, data: { innerText: "...", length: 11, ... } }

// 检测状态
composer.detectStatus()
// => { success: true, data: { status: "idle", ... } }

// 点击提交
composer.clickSubmit()
// => { success: true, message: "提交按钮已点击" }

// 等待输入框可用
await composer.waitForInput(5000)
// => { success: true, data: <Element> }
```

### 3. 统一的返回格式

所有操作返回统一的 `OperationResult`:

```typescript
interface OperationResult {
    success: boolean;      // 操作是否成功
    data?: any;            // 成功时的数据
    error?: string;        // 失败时的错误信息
    message?: string;      // 附加信息
}
```

---

## 🔄 集成方案

### 方案 A: 在渲染进程加载模块（推荐）

**优势**: 
- DOM 操作在渲染进程执行，性能更好
- 可以使用浏览器 API
- 符合 Electron 架构

**实现**:

```javascript
// 在 install-v9.sh 中（主进程）
async function handleComposerSendPrompt(fromId, payload) {
    const { agent_id, prompt } = payload;
    
    try {
        const electron = await import("electron");
        const windows = electron.BrowserWindow.getAllWindows();
        
        if (windows.length === 0) {
            throw new Error('没有打开的窗口');
        }
        
        // 读取 DOM 操作模块（运行时加载）
        const fs = await import('fs');
        const domOpsCode = fs.readFileSync('./cursor_dom_operations.js', 'utf8');
        
        // 在渲染进程执行
        const code = `
            ${domOpsCode}
            
            // 使用封装的操作
            const result = window.CursorDOM.composer.inputText(${JSON.stringify(prompt)});
            JSON.stringify(result);
        `;
        
        const resultStr = await windows[0].webContents.executeJavaScript(code);
        const result = JSON.parse(resultStr);
        
        // 发送结果
        const resultMessage = {
            type: 'composer_send_prompt_result',
            from: cursorId,
            to: fromId,
            timestamp: Math.floor(Date.now() / 1000),
            payload: {
                success: result.success,
                agent_id: agent_id,
                message: result.message || (result.success ? '提示词已输入' : null),
                error: result.error || null
            }
        };
        
        sendToCentral(resultMessage);
        
    } catch (error) {
        // 错误处理...
    }
}
```

### 方案 B: 预加载到渲染进程（更优雅）

**优势**:
- 只加载一次，性能更好
- 代码更简洁

**实现**:

```javascript
// 在 Cursor 启动时预加载
async function preloadDOMOperations() {
    const electron = await import("electron");
    const windows = electron.BrowserWindow.getAllWindows();
    
    if (windows.length > 0) {
        const fs = await import('fs');
        const domOpsCode = fs.readFileSync('./cursor_dom_operations.js', 'utf8');
        
        await windows[0].webContents.executeJavaScript(domOpsCode);
        log('✅ DOM 操作模块已预加载');
    }
}

// 在启动时调用
setTimeout(() => {
    preloadDOMOperations();
}, 3000);

// 使用时直接调用
async function handleComposerSendPrompt(fromId, payload) {
    const { prompt } = payload;
    
    const code = `
        JSON.stringify(window.CursorDOM.composer.inputText(${JSON.stringify(prompt)}));
    `;
    
    const resultStr = await windows[0].webContents.executeJavaScript(code);
    const result = JSON.parse(resultStr);
    
    // 处理结果...
}
```

---

## 🧪 测试流程

### 1. 独立测试 DOM 操作

```bash
cd cursor-injector
chmod +x test_dom_operations.py
python3 test_dom_operations.py
```

**测试内容**:
- ✅ 加载模块
- ✅ 测试选择器
- ✅ 查找输入框
- ✅ 输入文字
- ✅ 获取内容
- ✅ 清空输入框

### 2. 测试集成（使用新的 install-v9.sh）

```bash
# 安装 V9
./install-v9.sh

# 重启 Cursor

# 测试完整流程
python3 test-input-complete.py "测试新封装"
```

---

## 📝 迁移计划

### 阶段 1: 创建封装（✅ 已完成）

- ✅ `cursor_dom_operations.js` - DOM 操作封装
- ✅ `test_dom_operations.py` - 测试脚本
- ✅ 本文档

### 阶段 2: 创建 V9 版本

- [ ] 创建 `install-v9.sh`
- [ ] 集成 DOM 操作模块
- [ ] 使用方案 B（预加载）
- [ ] 保持协议兼容

### 阶段 3: 测试验证

- [ ] 本地模式测试
- [ ] 完整系统测试
- [ ] 性能对比

### 阶段 4: 扩展功能

- [ ] 实现 Editor 操作
- [ ] 实现 Terminal 操作
- [ ] 添加更多 Composer 功能

---

## 🎯 V9 vs V8 对比

| 特性 | V8 | V9 |
|------|----|----|
| DOM 操作 | 嵌入在 shell 脚本 | 独立 JS 模块 |
| 可维护性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 可测试性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 可扩展性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 协议兼容 | ✅ | ✅ |
| 向后兼容 | N/A | ✅ |

---

## 💡 扩展示例

### 添加新的 Composer 操作

```javascript
// 在 ComposerOperations 类中添加
class ComposerOperations {
    // ... 现有方法 ...
    
    /**
     * 获取建议列表
     * @returns {OperationResult}
     */
    getSuggestions() {
        try {
            const suggestions = document.querySelectorAll('.suggestion-item');
            
            const list = Array.from(suggestions).map(item => ({
                text: item.textContent,
                type: item.dataset.type
            }));
            
            return {
                success: true,
                data: {
                    count: list.length,
                    suggestions: list
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}
```

### 实现 Editor 操作

```javascript
class EditorOperations {
    /**
     * 获取当前文件内容（使用 VSCode API）
     * @returns {OperationResult}
     */
    async getCurrentFileContent() {
        try {
            // 假设可以访问 vscode 对象
            if (typeof vscode === 'undefined') {
                return {
                    success: false,
                    error: 'VSCode API 不可用'
                };
            }
            
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                return {
                    success: false,
                    error: '没有活动编辑器'
                };
            }
            
            const content = editor.document.getText();
            
            return {
                success: true,
                data: {
                    content: content,
                    language: editor.document.languageId,
                    fileName: editor.document.fileName
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}
```

---

## 🔧 选择器更新策略

当 Cursor 更新导致 UI 变化时：

### 1. 使用 DevTools 分析新的 DOM 结构

```javascript
// 在 Cursor DevTools Console 中
document.querySelector('.aislash-editor-input')  // 旧选择器
document.querySelector('.new-input-class')       // 新选择器
```

### 2. 更新 cursor_dom_operations.js

```javascript
class ComposerOperations {
    constructor() {
        this.selectors = {
            // 更新这里的选择器
            input: '.new-input-class',  // 从 '.aislash-editor-input' 改为新的
            // ...
        };
    }
}
```

### 3. 运行测试验证

```bash
python3 test_dom_operations.py
```

### 4. 无需修改其他代码

因为所有操作都通过统一的接口调用，只要选择器正确，其他代码无需改动。

---

## 📊 性能考虑

### 加载开销

- **方案 A（每次加载）**: ~5-10ms
- **方案 B（预加载）**: ~5ms（启动时），后续 0ms

**推荐**: 使用方案 B，预加载到渲染进程

### 执行性能

DOM 操作本身的性能与 V8 相同，因为底层使用相同的 API。

---

## 🎉 总结

通过这次重构：

1. ✅ **代码更清晰** - 职责分离，易读易懂
2. ✅ **维护更简单** - UI 变化只改一个文件
3. ✅ **测试更容易** - 可以独立测试每个操作
4. ✅ **扩展更方便** - 添加新功能只需加方法
5. ✅ **向后兼容** - V8 功能完全保留

**下一步**: 创建 `install-v9.sh` 并集成这个封装。

---

*最后更新: 2025-11-03*

