# 📝 获取 Cursor DOM 结构 - 手动方法

## ⚠️ 为什么需要手动方法？

macOS 的安全机制阻止了 Frida 附加到 Cursor 进程（需要特殊权限）。  
但是我们可以直接在 Cursor 的 DevTools 中运行 JavaScript 来获取 DOM 结构！

---

## 🚀 使用步骤（非常简单）

### Step 1: 打开 Cursor DevTools

在 Cursor 中按：
- **macOS**: `Cmd + Shift + I`
- **Windows/Linux**: `Ctrl + Shift + I`

或者通过菜单：
- `Help` → `Toggle Developer Tools`

### Step 2: 切换到 Console 标签

在 DevTools 窗口中，点击顶部的 `Console` 标签。

### Step 3: 运行脚本

#### 方法 A: 复制整个脚本（推荐）

1. 打开文件:
   ```bash
   code "playwright-cursor/get-dom-devtools.js"
   ```

2. 复制整个文件内容（Cmd+A, Cmd+C）

3. 在 Cursor DevTools Console 中粘贴（Cmd+V）

4. 按 `Enter` 运行

#### 方法 B: 直接在终端查看脚本

```bash
cat "/Users/user/Documents/ cursorgirl/playwright-cursor/get-dom-devtools.js"
```

然后复制输出的内容到 DevTools Console。

### Step 4: 查看结果

脚本运行后，你会看到：

```
🔍 开始获取 Cursor DOM 结构...

📝 查找 textareas...
   找到 2 个 textareas

📝 查找 inputs...
   找到 15 个 inputs

📝 查找 buttons...
   找到 87 个 buttons

... (更多输出)

✅ 分析完成！

📝 结果已保存到变量 cursorDomData
```

### Step 5: 导出数据

在 Console 中运行以下任一命令：

#### 选项 1: 复制到剪贴板（推荐）

```javascript
copy(cursorDomData)
```

然后粘贴到文本编辑器并保存为 `cursor_dom_data.json`。

#### 选项 2: 查看 JSON 格式

```javascript
JSON.stringify(cursorDomData, null, 2)
```

右键点击输出 → `Copy string contents`

#### 选项 3: 直接查看对象

```javascript
cursorDomData
```

在 Console 中展开查看各个部分。

---

## 📊 数据结构说明

获取的数据包含以下信息：

```javascript
{
  timestamp: "2024-11-03T...",
  
  pageInfo: {
    title: "Cursor - filename.js",
    url: "file://...",
    userAgent: "..."
  },
  
  summary: {
    totalElements: 12345,    // 总元素数
    divs: 5678,
    textareas: 2,            // textarea 数量
    inputs: 15,
    buttons: 87
  },
  
  keyElements: {
    textareas: [              // 所有 textarea 详情
      {
        index: 0,
        placeholder: "Ask AI...",
        visible: true,
        focused: false,
        classes: "...",
        position: { top: 100, left: 200, ... }
      }
    ],
    
    buttons: [                // 按钮列表（前30个）
      {
        text: "Send",
        ariaLabel: "Send message",
        visible: true,
        classes: [...]
      }
    ],
    
    aiRelated: [              // AI 相关元素
      {
        tag: "div",
        classes: ["ai-chat", ...],
        text: "...",
        visible: true
      }
    ],
    
    editorElements: [         // 编辑器相关元素
      { selector: ".monaco-editor", ... }
    ]
  },
  
  monacoEditor: {
    count: 1,
    currentEditor: {
      language: "javascript",
      lineCount: 45,
      valueLength: 1234,
      firstLine: "import ...",
      uri: "file://..."
    }
  },
  
  bodyStructure: {            // body 的 DOM 树结构（深度3）
    tag: "body",
    classes: [...],
    children: [...]
  }
}
```

---

## 🔍 关键信息位置

### 查找 AI 输入框

```javascript
// 所有 textareas
cursorDomData.keyElements.textareas

// 第一个 textarea 的 placeholder
cursorDomData.keyElements.textareas[0].placeholder

// 可见的 textareas
cursorDomData.keyElements.textareas.filter(ta => ta.visible)
```

### 查找按钮

```javascript
// 所有按钮
cursorDomData.keyElements.buttons

// 包含 "Send" 的按钮
cursorDomData.keyElements.buttons.filter(btn => 
  btn.text.includes('Send') || btn.ariaLabel?.includes('Send')
)
```

### 查找 AI 相关元素

```javascript
// 所有 AI 相关元素
cursorDomData.keyElements.aiRelated

// 可见的 AI 元素
cursorDomData.keyElements.aiRelated.filter(elem => elem.visible)
```

### Monaco Editor 信息

```javascript
// 编辑器信息
cursorDomData.monacoEditor

// 当前语言
cursorDomData.monacoEditor.currentEditor.language

// 当前行数
cursorDomData.monacoEditor.currentEditor.lineCount
```

---

## 🎯 实时查询

脚本运行后，你还可以在 Console 中实时查询：

### 查找特定元素

```javascript
// 查找所有 textareas
document.querySelectorAll('textarea')

// 查找AI相关
document.querySelectorAll('[class*="ai"]')

// 查找可见的 textarea
Array.from(document.querySelectorAll('textarea')).filter(ta => 
  ta.offsetParent !== null
)
```

### 测试选择器

```javascript
// 测试某个选择器
const elem = document.querySelector('textarea[placeholder*="Ask"]');
if (elem) {
    console.log('找到了！', elem);
    console.log('placeholder:', elem.placeholder);
    console.log('classes:', elem.className);
}
```

### 监听变化

```javascript
// 监听 DOM 变化
const observer = new MutationObserver((mutations) => {
    console.log('DOM changed:', mutations.length, 'mutations');
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// 停止监听
// observer.disconnect();
```

---

## 💾 保存结果

### 保存到文件（在终端中）

如果你已经用 `copy(cursorDomData)` 复制了数据：

```bash
# 粘贴到文件
pbpaste > /Users/user/Documents/\ cursorgirl/playwright-cursor/output/cursor_dom_manual.json

# 或者用编辑器
pbpaste | code -
```

### 在 Cursor 中直接保存

1. 在 Console 中运行 `copy(cursorDomData)`
2. 在 Cursor 中新建文件
3. 粘贴内容
4. 保存为 `cursor_dom_data.json`

---

## 🚀 下一步

获取 DOM 数据后，我们可以：

1. ✅ 分析 Cursor UI 结构
2. ✅ 找到 AI 输入框的准确选择器
3. ✅ 找到发送按钮
4. ✅ 了解 Monaco Editor API
5. ✅ 开发自动化控制脚本

---

## ❓ 常见问题

### Q: 脚本运行后没有输出？

A: 确保在 Console 标签，不是 Sources 或其他标签。

### Q: 提示语法错误？

A: 确保复制了完整的脚本，包括开头和结尾。

### Q: 找不到 window.monaco？

A: 确保至少打开了一个代码文件，让编辑器加载。

### Q: copy() 命令不可用？

A: 有些浏览器/环境不支持 copy()，可以手动右键复制结果。

---

## 📝 快速参考

```bash
# 1. 打开 DevTools
Cmd+Shift+I (macOS) 或 Ctrl+Shift+I (Windows)

# 2. 运行脚本
粘贴 get-dom-devtools.js 的内容

# 3. 复制结果
copy(cursorDomData)

# 4. 保存
粘贴到文件并保存为 JSON
```

---

**准备好了吗？打开 Cursor DevTools，运行脚本！** 🚀

