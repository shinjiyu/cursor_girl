# 🎯 DOM 输入实验报告

**日期**: 2025-11-03  
**目标**: 分析 Cursor AI 输入框的 DOM 结构并实现自动化文字输入  
**状态**: ✅ 完全成功

---

## 📸 用户提供的截图

用户展示了 Cursor 的 AI 聊天界面，包含：
- 输入框提示文字: "Plan, @ for context, / for commands"
- Agent 选择器
- Sonnet 4.5 模型选择器

**目标**: 找到这个输入框对应的 DOM 节点，并用脚本输入测试文字

---

## 🔍 DOM 分析过程

### 步骤 1: 广泛搜索

使用 `analyze-dom.py` 进行三种搜索：

1. **搜索包含 "Plan" 关键词的元素**
   - 找到 57 个相关元素
   - 大部分是容器 div

2. **搜索所有 input 和 textarea**
   - 找到 18 个输入元素
   - 大部分是 Monaco 编辑器的 textarea
   - 没有找到 AI 聊天输入框

3. **搜索所有 contentEditable 元素** ✅
   - **找到 1 个关键元素**：
   ```
   [1] DIV
       Class: aislash-editor-input
       Role: textbox
       ContentEditable: true
   ```

**关键发现**: AI 输入框是一个 `contenteditable` 的 `div`，类名为 `aislash-editor-input`

---

### 步骤 2: 详细检查

使用 `inspect-input.py` 检查输入框详细信息：

```json
{
  "tagName": "DIV",
  "contentEditable": "true",
  "innerHTML": "<p><br></p>",
  "attributes": [
    { "name": "class", "value": "aislash-editor-input" },
    { "name": "data-lexical-editor", "value": "true" },
    { "name": "role", "value": "textbox" },
    { "name": "contenteditable", "value": "true" },
    ...
  ]
}
```

**关键发现**: 
- ✅ CSS 选择器: `.aislash-editor-input`
- ✅ 编辑器类型: **Lexical 编辑器** (Facebook/Meta 开发)
- ✅ 标识属性: `data-lexical-editor="true"`

---

## 🛠️ 输入实现

### 技术挑战

1. **Lexical 编辑器的复杂性**
   - 不能直接修改 `innerHTML` (TrustedHTML 安全策略)
   - 不能简单设置 `textContent`
   - 需要触发正确的事件让编辑器更新

2. **尝试的方法**

   **❌ 方法 1: 直接修改 textContent**
   ```javascript
   input.textContent = 'text';  // 不工作
   ```
   
   **❌ 方法 2: 直接修改 innerHTML**
   ```javascript
   input.innerHTML = '...';  // TrustedHTML 错误
   ```
   
   **✅ 方法 3: document.execCommand**
   ```javascript
   // 选中所有内容
   const sel = window.getSelection();
   const range = document.createRange();
   range.selectNodeContents(input);
   sel.removeAllRanges();
   sel.addRange(range);
   
   // 删除旧内容
   document.execCommand('delete', false, null);
   
   // 插入新文字
   document.execCommand('insertText', false, text);
   
   // 触发事件
   input.dispatchEvent(new InputEvent('input', { 
       bubbles: true,
       cancelable: true
   }));
   ```

---

## ✅ 最终实现

### 核心代码

文件: `test-input-complete.py`

```python
# 1. 连接到 Cursor
ws = await websockets.connect('ws://localhost:9876')

# 2. 在渲染进程中执行 JavaScript
code = f'''
(async () => {{
    const {{ BrowserWindow }} = await import("electron");
    const windows = BrowserWindow.getAllWindows();
    if (windows.length > 0) {{
        const code = `
            (function() {{
                const input = document.querySelector('.aislash-editor-input');
                input.focus();
                
                // 选中所有内容并删除
                const sel = window.getSelection();
                const range = document.createRange();
                range.selectNodeContents(input);
                sel.removeAllRanges();
                sel.addRange(range);
                document.execCommand('delete', false, null);
                
                // 插入新文字
                document.execCommand('insertText', false, '{text}');
                
                // 触发事件
                input.dispatchEvent(new InputEvent('input', {{ 
                    bubbles: true,
                    cancelable: true
                }}));
                
                return JSON.stringify({{ success: true }});
            }})()
        `;
        return await windows[0].webContents.executeJavaScript(code);
    }}
}})()
'''

await ws.send(code)
response = await ws.recv()
```

---

## 🧪 测试结果

### 测试用例

```bash
python3 test-input-complete.py "测试输入中文和Emoji 🎉✨"
```

### 输出

```
✅ 输入框状态:
   innerText: "测试输入中文和Emoji 🎉✨"
   textContent: "测试输入中文和Emoji 🎉✨"
   innerHTML: <p dir="ltr"><span data-lexical-text="true">测试输入中文和Emoji 🎉✨</span></p>
   
   ✅ 内容匹配！输入成功！
```

### 验证要点

- ✅ 找到输入框元素
- ✅ 成功输入文字
- ✅ 支持中文字符
- ✅ 支持 Emoji 表情
- ✅ Lexical 编辑器正确渲染
- ✅ 内容可以读取验证

---

## 📊 架构总结

```
┌─────────────────────────────────────────────────────────────┐
│ Python 脚本                                                  │
│   └─ websockets.connect('localhost:9876')                   │
└──────────────────┬──────────────────────────────────────────┘
                   │ WebSocket
                   │ 发送 JavaScript 代码
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Cursor 主进程 (Main Process)                                │
│   ├─ WebSocket Server (端口 9876)                           │
│   ├─ eval(code) 执行 JavaScript                             │
│   └─ 调用 BrowserWindow.webContents.executeJavaScript()     │
└──────────────────┬──────────────────────────────────────────┘
                   │ executeJavaScript()
                   │ 在渲染进程中执行
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Cursor 渲染进程 (Renderer Process)                          │
│   ├─ DOM: document.querySelector('.aislash-editor-input')   │
│   ├─ Lexical 编辑器处理输入                                  │
│   └─ 返回执行结果                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 实现的功能

### 1. DOM 结构分析 (`analyze-dom.py`)

```bash
python3 analyze-dom.py
```

功能：
- 搜索包含特定文字的元素
- 列出所有 input/textarea
- 查找 contentEditable 元素

### 2. 输入框详细检查 (`inspect-input.py`)

```bash
python3 inspect-input.py
```

功能：
- 显示输入框的完整 HTML 结构
- 列出所有属性
- 检查子节点

### 3. 文字输入测试 (`test-input-complete.py`)

```bash
python3 test-input-complete.py "你要输入的文字"
```

功能：
- 自动找到输入框
- 输入指定文字
- 验证输入结果
- 支持中文和 Emoji

---

## 💡 技术要点

### 1. Lexical 编辑器

Lexical 是 Facebook 开发的现代富文本编辑器框架：
- 使用 `contenteditable` DOM 节点
- 维护自己的状态树
- 不能简单地修改 DOM
- 需要触发正确的事件

### 2. document.execCommand

虽然已被标记为过时，但仍然是最可靠的方法：
- `execCommand('insertText')` 模拟用户输入
- 触发所有必要的浏览器事件
- Lexical 编辑器能正确响应

### 3. 事件触发

必须触发 `InputEvent`：
```javascript
input.dispatchEvent(new InputEvent('input', { 
    bubbles: true,
    cancelable: true
}));
```

这让 Lexical 编辑器知道内容已更改。

---

## 🚀 应用场景

现在我们可以：

### 1. 自动化 AI 对话

```python
# 发送问题到 Cursor AI
await send_to_ai_input("写一个快速排序的 Python 实现")
```

### 2. 批量测试

```python
questions = [
    "解释这段代码",
    "优化性能",
    "添加错误处理"
]

for q in questions:
    await send_to_ai_input(q)
    await asyncio.sleep(5)  # 等待回复
```

### 3. Ortensia 集成

```python
# 在 Ortensia 系统中
class OrtensiaB​ridge:
    async def send_to_cursor_ai(self, prompt):
        """发送提示到 Cursor AI"""
        await self.cursor_client.input_to_ai(prompt)
```

---

## 📝 文件清单

| 文件 | 功能 | 状态 |
|------|------|------|
| `analyze-dom.py` | DOM 结构分析 | ✅ 已提交 |
| `inspect-input.py` | 输入框详细检查 | ✅ 已提交 |
| `test-input-complete.py` | 完整输入测试 | ✅ 已提交 |
| `input-text.py` | 早期尝试 (v1) | ⚠️  未提交 |
| `input-text-v2.py` | 早期尝试 (v2) | ⚠️  未提交 |
| `input-text-lexical.py` | Lexical 专用版本 | ⚠️  未提交 |

---

## 🎉 总结

### 成就

1. ✅ 成功定位 AI 聊天输入框的 DOM 节点
2. ✅ 识别出 Lexical 编辑器
3. ✅ 找到可靠的输入方法 (`execCommand`)
4. ✅ 实现自动化文字输入
5. ✅ 支持中文和 Emoji
6. ✅ 可以验证输入结果

### 关键技术

- **DOM 选择器**: `.aislash-editor-input`
- **编辑器类型**: Lexical (data-lexical-editor="true")
- **输入方法**: `document.execCommand('insertText')`
- **事件触发**: `InputEvent` with `bubbles: true`
- **架构**: 主进程 WebSocket → executeJavaScript → 渲染进程 DOM

### 下一步

- [ ] 实现发送消息按钮点击
- [ ] 实现读取 AI 回复
- [ ] 集成到 Ortensia 系统
- [ ] 添加错误重试机制

---

**实验完成时间**: 2025-11-03 16:30 CST  
**实验人员**: AI Assistant + User  
**状态**: ✅ 完全成功，可以实际应用

