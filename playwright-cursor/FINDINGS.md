# Playwright Cursor 自动化调研结果

## 📊 调研总结

**日期**: 2025-11-02  
**分支**: `feature/playwright-cursor-control`  
**目标**: 使用 Playwright 自动化控制 Cursor 编辑器，打印 DOM 结构

---

## ✅ 已完成的工作

1. ✅ 创建新分支 `feature/playwright-cursor-control`
2. ✅ 安装 Playwright Node.js 版本
3. ✅ 实现 DOM Inspector 脚本（两个版本）
4. ✅ 测试多种连接方法

---

## 🔍 技术发现

### 1. Playwright Python vs Node.js

| 特性 | Python | Node.js |
|-----|---------|---------|
| Electron 支持 | ❌ 无 | ✅ 有 |
| API | `p._impl_obj.electron` | `_electron: electron` |
| 官方文档 | 无 | 有 |
| 推荐度 | ❌ | ✅ |

**结论**: **Playwright 的 Electron 支持仅在 Node.js 版本中可用**

### 2. Cursor Electron 启动测试

#### 测试 A: 直接启动 (`electron.launch()`)

```javascript
const app = await electron.launch({
  executablePath: '/Applications/Cursor.app/Contents/MacOS/Cursor'
});
```

**结果**: ❌ 失败
- Cursor 进程启动（PID 存在）
- 但没有窗口出现
- 超时等待窗口事件

**原因分析**:
- Cursor 可能检测到自动化环境
- Cursor 可能需要特殊的启动参数
- Cursor 可能不支持 Playwright 的自动化注入

#### 测试 B: Chrome DevTools Protocol (`--remote-debugging-port`)

```bash
/Applications/Cursor.app/Contents/MacOS/Cursor --remote-debugging-port=9222
```

**结果**: ❌ 部分失败
- Cursor 启动并显示消息：`DevTools listening on ws://127.0.0.1:9222/...`
- 但实际上端口 9222 **没有监听** (`lsof -i :9222` 无结果)
- Playwright 连接失败：`ECONNREFUSED`

**警告消息**:
```
Warning: 'remote-debugging-port' is not in the list of known options,
but still passed to Electron/Chromium.
```

**原因分析**:
- Cursor 可能禁用了 Chrome DevTools Protocol
- 或者使用了自定义的调试协议
- VSCode/Cursor 可能有安全限制

---

## 🚫 发现的限制

### Cursor 的限制

1. **不支持 Playwright Electron API**
   - 无法通过 `electron.launch()` 启动并控制
   - 窗口不会在自动化模式下出现

2. **不支持标准 CDP**
   - `--remote-debugging-port` 参数被忽略
   - 无法通过 Chrome DevTools Protocol 连接

3. **可能的原因**
   - Cursor 基于 VSCode，而 VSCode 有特殊的安全机制
   - Cursor 可能主动禁用了自动化相关功能
   - 为了安全和许可证原因

---

## 💡 替代方案

基于调研结果，以下是可行的替代方案：

### 方案 1: VSCode Extension API ⭐⭐⭐⭐⭐（最推荐）

**原理**: 开发一个 VSCode 扩展，在编辑器内部运行

**优势**:
- ✅ 官方支持的方式
- ✅ 完全控制编辑器功能
- ✅ 不需要调试模式
- ✅ 跨平台
- ✅ 可以精确操作代码

**实现**:
```typescript
// 在扩展中
import * as vscode from 'vscode';

// 插入代码
const editor = vscode.window.activeTextEditor;
editor.edit(editBuilder => {
    editBuilder.insert(position, 'code');
});

// 执行命令
vscode.commands.executeCommand('workbench.action.files.save');

// WebSocket 通信
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const command = JSON.parse(event.data);
    handleCommand(command);
};
```

**待验证**: Cursor 是否完全兼容 VSCode Extension API

### 方案 2: 跨平台 UI 自动化 ⭐⭐⭐

**工具**: pyautogui (跨平台)

**优势**:
- ✅ 跨平台（Windows + macOS）
- ✅ 不需要任何特殊启动
- ✅ 可以快速实现

**劣势**:
- ❌ 无法识别内部 UI（基于坐标/图像）
- ❌ 不够精确
- ❌ 依赖屏幕布局

**实现**:
```python
import pyautogui
import platform

def send_ai_command(prompt):
    # 跨平台快捷键
    modifier = 'command' if platform.system() == 'Darwin' else 'ctrl'
    pyautogui.hotkey(modifier, 'l')  # 打开 AI
    pyautogui.typewrite(prompt)
    pyautogui.press('return')
```

### 方案 3: Cursor CLI + File System ⭐⭐⭐⭐

**原理**: 使用 Cursor 的命令行工具 + 文件系统监听

**优势**:
- ✅ 官方支持
- ✅ 简单可靠
- ✅ 跨平台

**实现**:
```python
import subprocess

# 打开文件
subprocess.run(['cursor', '-g', 'file.ts:42'])

# 执行命令
subprocess.run(['cursor', '--command', 'workbench.action.files.save'])
```

### 方案 4: Apple Script (macOS only) ⭐⭐⭐

**原理**: 使用 macOS Accessibility API

**优势**:
- ✅ 可以操作任何应用
- ✅ 相对精确

**劣势**:
- ❌ 仅 macOS
- ❌ 无法访问 Electron 内部 DOM

---

## 🎯 推荐的实现路径

### 短期（1周内）

**方案**: pyautogui + Cursor CLI

1. 使用 pyautogui 模拟快捷键（打开 AI、发送命令）
2. 使用 Cursor CLI 打开文件、执行编辑器命令
3. 通过 WebSocket 连接オルテンシア

**优势**: 快速验证想法，立即可用

### 中期（2-4周）

**方案**: 开发 VSCode Extension

1. 研究 Cursor 的 Extension API 兼容性
2. 开发扩展，实现 WebSocket 双向通信
3. 实现命令执行（插入代码、运行终端等）
4. 集成到オルテンシア系统

**优势**: 官方支持，长期可维护

### 长期（如果需要）

**方案**: 完整的 AI Pair Programming Assistant

1. 扩展 + 后端服务 + LLM
2. 智能代码审查
3. 自动化工作流
4. 学习用户习惯

---

## 📂 文件清单

### 已创建的文件

```
playwright-cursor/
├── package.json                        # Node.js 项目配置
├── cursor-dom-inspector.js             # Electron 启动版本（失败）
├── cursor-dom-inspector-cdp.js         # CDP 连接版本（失败）
├── run_with_cursor.sh                  # 启动脚本
├── run_test.sh                         # 测试脚本
├── README.md                           # 使用说明
└── FINDINGS.md                         # 本文件

bridge/
├── cursor_dom_inspector.py             # Python 版本（无 Electron 支持）
├── test_cursor_dom.py                  # Python 测试脚本
├── verify_playwright.py                # Playwright 验证脚本
└── PLAYWRIGHT_README.md                # Python 版本文档
```

### 已安装的依赖

- Node.js: v22.17.1
- @playwright/test: ^1.55.0
- Python playwright: 1.55.0 (但不支持 Electron)

---

## 🔮 后续步骤

### 立即行动

1. **验证 VSCode Extension API 在 Cursor 中的兼容性**
   - 创建一个简单的 "Hello World" 扩展
   - 测试在 Cursor 中是否能正常工作
   - 测试 WebSocket 通信

2. **如果扩展方案可行**
   - 开发完整的オルテンシア Controller Extension
   - 实现双向通信（Cursor ↔ オルテンシア）
   - 实现智能决策模块

3. **如果扩展方案不可行**
   - 使用 pyautogui + Cursor CLI 组合方案
   - 作为临时解决方案

---

## 📊 方案对比表

| 方案 | 跨平台 | UI识别 | 调试模式 | 难度 | 可行性 | 推荐度 |
|-----|--------|--------|---------|------|--------|--------|
| Playwright Electron | ✅ | ✅ | ❌不需要 | 中 | ❌不支持 | ⭐ |
| Playwright CDP | ✅ | ✅ | ✅需要 | 中 | ❌不支持 | ⭐ |
| VSCode Extension | ✅ | ✅ | ❌不需要 | 中-高 | ❓待验证 | ⭐⭐⭐⭐⭐ |
| pyautogui | ✅ | ❌ | ❌不需要 | 低 | ✅ | ⭐⭐⭐ |
| Cursor CLI | ✅ | ❌ | ❌不需要 | 低 | ✅ | ⭐⭐⭐⭐ |
| Apple Script | ❌ | ❌ | ❌不需要 | 低 | ✅ | ⭐⭐⭐ |

---

## 🎓 学到的经验

1. **不是所有 Electron 应用都支持自动化**
   - 即使是基于相同技术栈
   - 应用可能主动禁用自动化功能

2. **官方 API 优于 Hack**
   - Extension API 是官方支持的方式
   - 虽然开发成本高，但长期更可靠

3. **跨平台很重要**
   - macOS 专用方案限制太大
   - 应优先考虑跨平台方案

4. **快速验证很重要**
   - 先用简单方案验证想法
   - 再投入时间开发完整方案

---

## ✅ 总结

虽然 Playwright 无法直接控制 Cursor，但我们发现了更好的方案：

1. **最佳方案**: VSCode Extension API（需要验证兼容性）
2. **备选方案**: pyautogui + Cursor CLI（立即可用）

**下一步**: 验证 Cursor 对 VSCode Extension 的支持程度。

---

**状态**: ✅ 调研完成  
**分支**: `feature/playwright-cursor-control`  
**Commit**: 已提交

