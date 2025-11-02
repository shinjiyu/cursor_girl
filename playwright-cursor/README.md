# Playwright Cursor DOM Inspector

使用 Playwright 的 Electron 支持来检查 Cursor 编辑器的 DOM 结构。

## ✅ 完成状态

- ✅ 创建新分支 `feature/playwright-cursor-control`
- ✅ 安装 Playwright (Node.js 版本)
- ✅ 实现 DOM Inspector 脚本
- ✅ 支持导出完整 DOM 结构

## 🎯 功能

### Cursor DOM Inspector

`cursor-dom-inspector.js` - 检查和导出 Cursor 的完整 DOM 结构

**功能**：
- ✅ 启动 Cursor（无需调试模式）
- ✅ 获取完整 HTML
- ✅ 分析 DOM 结构统计
- ✅ 查找按钮、输入框、编辑器元素、AI 元素
- ✅ 生成 DOM 树结构
- ✅ 截图
- ✅ 导出 JSON 和 HTML 文件

## 📦 环境要求

- Node.js (已安装: v22.17.1)
- Cursor 编辑器 (已安装: /Applications/Cursor.app)

## 🚀 使用方法

### 1. 运行 DOM Inspector

```bash
cd playwright-cursor
node cursor-dom-inspector.js
```

### 2. 查看输出

脚本会自动创建 `cursor_dom_output/` 目录，包含：

- `cursor_full_dom_YYYYMMDD_HHMMSS.html` - 完整 HTML
- `cursor_analysis_YYYYMMDD_HHMMSS.json` - DOM 分析结果
- `cursor_tree_YYYYMMDD_HHMMSS.json` - DOM 树结构
- `cursor_screenshot_YYYYMMDD_HHMMSS.png` - 截图

### 3. 查看结果示例

```bash
# 查看分析结果
cat cursor_dom_output/cursor_analysis_*.json | node -e "console.log(JSON.stringify(JSON.parse(require('fs').readFileSync(0, 'utf-8')), null, 2))"

# 在浏览器中查看 HTML
open cursor_dom_output/cursor_full_dom_*.html

# 查看截图
open cursor_dom_output/cursor_screenshot_*.png
```

## 🔍 输出内容

### 1. 页面信息
- 窗口标题
- URL

### 2. DOM 统计
- 总元素数量
- 按类型统计（div、button、input 等）

### 3. 元素列表
- **按钮** (前 20 个)
  - 文本内容
  - aria-label
  - class 名
  
- **输入框** (前 20 个)
  - 类型
  - placeholder
  - name
  
- **编辑器元素**
  - Monaco 编辑器相关元素
  
- **AI 相关元素**
  - AI 聊天按钮
  - 聊天输入框

### 4. DOM 树结构
- 层级结构（最大深度 4 层）
- 每个元素的标签、ID、class

### 5. 完整 HTML
- 整个页面的 HTML 源码

### 6. 截图
- 当前窗口的可视截图

## 🛠️ 技术原理

### Playwright Electron 支持

Playwright 的 Node.js 版本提供了官方的 Electron 支持：

```javascript
const { _electron: electron } = require('@playwright/test');

// 启动 Electron 应用
const app = await electron.launch({
  executablePath: '/path/to/Cursor'
});

// 获取窗口
const page = await app.firstWindow();

// 操作 DOM
const html = await page.content();
```

**关键点**：
- ✅ 不需要 `--remote-debugging-port`
- ✅ 自动注入自动化能力
- ✅ 直接访问 DOM（使用选择器）
- ✅ 跨平台支持

### 为什么用 Node.js 而不是 Python？

- ❌ **Playwright Python** 不支持 Electron
- ✅ **Playwright Node.js** 官方支持 Electron
- ✅ Electron 本身就是基于 Node.js 的

## 📊 输出示例

运行后控制台输出：

```
======================================================================
  🔍 Cursor DOM Inspector
======================================================================

📍 Cursor Path: /Applications/Cursor.app/Contents/MacOS/Cursor
🚀 Starting Cursor with Playwright...
⏳ Launching Electron app...
⏳ Waiting for main window...
⏳ Waiting for page to load...
✅ Cursor started successfully!

======================================================================
  📊 Page Information
======================================================================

🏷️  Title: Cursor
🔗 URL: file:///...

======================================================================
  🔍 DOM Structure Analysis
======================================================================

📊 Element Statistics:
   Total Elements: 1234
   Divs: 567
   Buttons: 89
   Inputs: 12
   ...

🔘 Buttons (first 20):
   1. Open AI Chat
   2. File Explorer
   3. Search
   ...

📝 Editor Elements:
   1. <div> monaco-editor
   ...

✅ Analysis saved to: cursor_dom_output/cursor_analysis_20251102_...json
```

## 🐛 故障排查

### 问题：找不到 Cursor

```bash
# 检查路径
ls -la /Applications/Cursor.app

# 如果在其他位置，修改 cursor-dom-inspector.js 中的路径
const cursorPath = '/your/custom/path/to/Cursor';
```

### 问题：超时错误

增加等待时间：

```javascript
await page.waitForLoadState('domcontentloaded', { timeout: 60000 });
```

### 问题：权限错误

确保 Cursor 可以被启动：

```bash
# 赋予执行权限
chmod +x /Applications/Cursor.app/Contents/MacOS/Cursor
```

## 📝 下一步计划

1. ✅ DOM Inspector - **已完成**
2. ⏳ Cursor Controller - 发送 AI 命令
3. ⏳ 与 Python WebSocket 集成
4. ⏳ オルテンシア智能决策模块

## 📚 参考资料

- [Playwright Electron API](https://playwright.dev/docs/api/class-electronapplication)
- [Playwright Node.js Docs](https://playwright.dev/docs/intro)
- [Electron Testing Guide](https://www.electronjs.org/docs/latest/tutorial/automated-testing)

