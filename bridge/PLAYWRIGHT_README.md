# Playwright Cursor Controller

使用 Playwright 自动化控制 Cursor 编辑器。

## 🎯 功能

### 1. DOM Inspector（DOM 检查器）

`cursor_dom_inspector.py` - 分析和导出 Cursor 的完整 DOM 结构。

**功能**：
- ✅ 启动 Cursor（无需调试模式）
- ✅ 获取完整 HTML
- ✅ 分析 DOM 结构统计
- ✅ 查找按钮、输入框、编辑器元素
- ✅ 生成 DOM 树
- ✅ 截图
- ✅ 导出 JSON 和 HTML 文件

## 📦 安装

```bash
cd bridge

# 激活虚拟环境
source venv/bin/activate

# 安装 Playwright（已完成）
pip install playwright

# 安装浏览器驱动（已完成）
playwright install
```

## 🚀 使用方法

### 运行 DOM Inspector

```bash
cd bridge
source venv/bin/activate
python cursor_dom_inspector.py
```

**输出**：
- `cursor_dom_output/cursor_full_dom_YYYYMMDD_HHMMSS.html` - 完整 HTML
- `cursor_dom_output/cursor_analysis_YYYYMMDD_HHMMSS.json` - DOM 分析结果
- `cursor_dom_output/cursor_tree_YYYYMMDD_HHMMSS.json` - DOM 树结构
- `cursor_dom_output/cursor_screenshot_YYYYMMDD_HHMMSS.png` - 截图

### 查看结果

```bash
# 查看分析结果
cat cursor_dom_output/cursor_analysis_*.json | python -m json.tool

# 在浏览器中查看 HTML
open cursor_dom_output/cursor_full_dom_*.html

# 查看截图
open cursor_dom_output/cursor_screenshot_*.png
```

## 🔍 输出示例

### DOM 分析包含：

1. **元素统计**
   - 总元素数
   - 按钮数量
   - 输入框数量
   - 等等

2. **按钮列表**
   - 按钮文本
   - aria-label
   - class 名

3. **输入框列表**
   - 类型
   - placeholder
   - name

4. **编辑器元素**
   - Monaco 编辑器相关元素

5. **AI 相关元素**
   - AI 聊天按钮
   - 聊天输入框
   - 等等

## 🛠️ 技术原理

### Playwright 如何控制 Electron

Playwright 通过 Chrome DevTools Protocol (CDP) 直接与 Electron 内部的 Chromium 通信：

```
Python 脚本
    ↓ Playwright API
Playwright
    ↓ WebSocket (CDP)
Cursor (Electron)
    ↓ Chromium Engine
    ↓ DOM 树 (HTML/CSS/JS)
```

**关键点**：
- ✅ 不需要 `--remote-debugging-port`
- ✅ Playwright 自动注入自动化能力
- ✅ 可以直接访问 DOM 树（使用选择器，不是图像识别）
- ✅ 跨平台（macOS、Windows、Linux）

### DOM 选择器示例

```python
# CSS 选择器
page.click('button.ai-chat-button')
page.click('[aria-label="Open AI Chat"]')

# 文本选择器
page.click('text=Submit')

# XPath
page.click('//button[@aria-label="Open AI Chat"]')

# 执行 JavaScript
result = page.evaluate('() => document.title')
```

## 📝 下一步计划

1. ✅ DOM Inspector - **已完成**
2. ⏳ Cursor Controller - 发送 AI 命令
3. ⏳ 与 WebSocket 集成 - 连接オルテンシア
4. ⏳ 智能决策模块 - Agent 完成后自动操作

## ⚠️ 注意事项

1. **第一次运行**可能需要较长时间启动 Cursor
2. **窗口会自动打开** - 这是正常的，Playwright 需要可见的窗口
3. **保持窗口打开** - 按 Enter 键关闭
4. **Cursor 路径** - 默认为 macOS 标准路径，其他系统需要修改

## 🐛 故障排查

### 问题：找不到 Cursor

```bash
# 检查 Cursor 是否安装
ls -la /Applications/ | grep Cursor

# 如果在其他位置，修改脚本中的路径
```

### 问题：Playwright 超时

```bash
# 增加超时时间（在脚本中修改）
page.wait_for_selector('body', timeout=60000)  # 60 秒
```

### 问题：无法访问 DOM

```bash
# 确保 Cursor 完全加载后再分析
# 等待几秒钟让编辑器初始化
```

## 📚 参考资料

- [Playwright Python 文档](https://playwright.dev/python/)
- [Playwright Electron 支持](https://playwright.dev/python/docs/api/class-electron)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)

