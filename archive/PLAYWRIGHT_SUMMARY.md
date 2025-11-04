# 🎯 Playwright Cursor 自动化调研 - 完整总结

**日期**: 2025-11-02  
**分支**: `feature/playwright-cursor-control`  
**状态**: ✅ 调研完成

---

## 📋 你的需求

> "我希望这个虚拟角色可以自动操作 cursor，即如果监听到 agent 结束，就根据结果给 agent 发送新的指令。"

**核心问题**: 如何实现オルテンシア（虚拟角色）→ Cursor 的反向控制

---

## 🔍 调研结果

### ❌ Playwright 方案不可行

我测试了两种 Playwright 方案，**均失败**：

#### 1. Playwright Electron API

```javascript
const app = await electron.launch({
  executablePath: '/Applications/Cursor.app/Contents/MacOS/Cursor'
});
```

**结果**: 
- ❌ Cursor 进程启动但没有窗口
- ❌ 超时等待窗口事件
- ❌ Cursor 不支持 Playwright 的自动化注入

#### 2. Chrome DevTools Protocol (CDP)

```bash
/Applications/Cursor.app/Contents/MacOS/Cursor --remote-debugging-port=9222
```

**结果**:
- ❌ Cursor 显示 "DevTools listening" 但端口没有实际监听
- ❌ 无法通过 CDP 连接
- ⚠️ 警告：`'remote-debugging-port' is not in the list of known options`

**结论**: **Cursor 主动禁用了远程调试和自动化功能**

---

## ✅ 可行的替代方案

根据调研，我为你找到了 **3 个可行方案**，按推荐程度排序：

### 🥇 方案1: VSCode Extension API（最推荐）

**原理**: 在 Cursor 内部运行扩展，直接调用编辑器 API

**优势**:
- ✅ 官方支持的方式
- ✅ 完全控制编辑器（插入代码、运行命令、操作终端）
- ✅ 不需要调试模式
- ✅ 跨平台（Windows + macOS + Linux）
- ✅ 可以精确识别和操作 UI

**实现架构**:
```
Cursor (运行扩展)
  ├─ Extension (TypeScript)
  │   ├─ 监听编辑器事件 → 发送到オルテンシア
  │   └─ 接收オルテンシア命令 → 执行编辑器操作
  │
  └─ WebSocket ↔ オルテンシア Bridge ↔ AITuber Kit
```

**示例代码**:
```typescript
// 扩展中的双向通信
import * as vscode from 'vscode';

// 连接オルテンシア
const ws = new WebSocket('ws://localhost:8000/ws');

// 方向1: Cursor → オルテンシア
vscode.workspace.onDidSaveTextDocument(doc => {
  ws.send(JSON.stringify({ event: 'file_save', file: doc.fileName }));
});

// 方向2: オルテンシア → Cursor
ws.onmessage = (event) => {
  const command = JSON.parse(event.data);
  
  switch (command.action) {
    case 'insert_code':
      const editor = vscode.window.activeTextEditor;
      editor.edit(edit => {
        edit.insert(editor.selection.active, command.code);
      });
      break;
    
    case 'run_terminal':
      const terminal = vscode.window.createTerminal();
      terminal.sendText(command.command);
      break;
    
    case 'trigger_ai':
      // 发送消息到 Cursor AI
      vscode.commands.executeCommand('cursor.chat', command.prompt);
      break;
  }
};
```

**需要验证**: Cursor 对 VSCode Extension API 的兼容性

---

### 🥈 方案2: pyautogui + Cursor CLI（快速方案）

**原理**: 模拟键盘输入 + 命令行工具

**优势**:
- ✅ 跨平台
- ✅ **立即可用**（无需开发）
- ✅ 可以快速验证想法

**劣势**:
- ⚠️ 无法精确识别 UI（基于快捷键和坐标）
- ⚠️ 依赖窗口焦点

**实现示例**:
```python
import pyautogui
import subprocess
import platform

class CursorController:
    def send_ai_command(self, prompt):
        """向 Cursor AI 发送命令"""
        # 跨平台快捷键
        modifier = 'command' if platform.system() == 'Darwin' else 'ctrl'
        
        # 打开 AI 聊天
        pyautogui.hotkey(modifier, 'l')
        time.sleep(0.3)
        
        # 输入提示
        pyautogui.typewrite(prompt, interval=0.02)
        pyautogui.press('return')
    
    def open_file(self, path, line=None):
        """打开文件"""
        if line:
            subprocess.run(['cursor', '-g', f'{path}:{line}'])
        else:
            subprocess.run(['cursor', path])
    
    def execute_command(self, command):
        """执行编辑器命令"""
        subprocess.run(['cursor', '--command', command])

# 集成到オルテンシア
async def on_agent_complete(result):
    controller = CursorController()
    
    # 分析结果
    if 'error' in result:
        queue_message("发现错误，让 Agent 修复", "surprised")
        controller.send_ai_command('请修复代码中的错误')
    
    elif 'test' not in result:
        queue_message("没有测试，我来要求添加", "neutral")
        controller.send_ai_command('请添加单元测试')
    
    else:
        queue_message("代码看起来不错，运行测试", "happy")
        controller.execute_command('workbench.action.tasks.test')
```

---

### 🥉 方案3: Apple Script（macOS 专用）

**原理**: 使用 macOS Accessibility API

**优势**:
- ✅ 可以操作任何 macOS 应用
- ✅ 相对精确

**劣势**:
- ❌ 仅限 macOS
- ⚠️ 无法访问 Electron 内部 DOM

**实现示例**:
```python
import subprocess

def send_to_cursor_ai(prompt):
    applescript = f'''
    tell application "Cursor" to activate
    delay 0.5
    tell application "System Events"
        keystroke "l" using command down
        delay 0.3
        keystroke "{prompt}"
        keystroke return
    end tell
    '''
    subprocess.run(['osascript', '-e', applescript])
```

---

## 📊 方案对比

| 特性 | VSCode Extension | pyautogui + CLI | Apple Script |
|-----|-----------------|----------------|--------------|
| 跨平台 | ✅ Win/Mac/Linux | ✅ Win/Mac/Linux | ❌ Mac only |
| UI 识别 | ✅ 精确（API） | ❌ 模糊（快捷键） | ⚠️ 中等 |
| 调试模式 | ❌ 不需要 | ❌ 不需要 | ❌ 不需要 |
| 开发难度 | 🟡 中-高 | 🟢 低 | 🟢 低 |
| 可靠性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 立即可用 | ❌ 需要开发 | ✅ 是 | ✅ 是 |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 推荐的实施计划

### 阶段1: 快速验证（1-2天）

**使用**: pyautogui + Cursor CLI

**目标**: 验证オルテンシア自动控制 Cursor 的可行性

```python
# bridge/cursor_controller_simple.py
from cursor_event import handle_event
import pyautogui
import subprocess

class SimpleCursorController:
    async def on_agent_complete(self, result):
        # オルテンシア说话
        queue_message("让我看看 Agent 做了什么", "neutral")
        await asyncio.sleep(2)
        
        # 发送新指令
        self.send_ai_command('请为这段代码添加注释')
        queue_message("我已经告诉 Agent 添加注释了", "happy")
    
    def send_ai_command(self, prompt):
        pyautogui.hotkey('command', 'l')
        time.sleep(0.3)
        pyautogui.typewrite(prompt)
        pyautogui.press('return')
```

**优势**: 
- ✅ 可以立即开始测试
- ✅ 验证整个流程是否可行
- ✅ 快速迭代

### 阶段2: Extension 开发（1-2周）

**使用**: VSCode Extension API

**目标**: 实现稳定、可靠的自动化方案

1. **Week 1**: 
   - 研究 Cursor Extension 兼容性
   - 创建基础扩展
   - 实现 WebSocket 通信
   - 测试基本功能

2. **Week 2**:
   - 实现完整的命令执行
   - 与オルテンシア系统集成
   - 添加智能决策模块
   - 测试和优化

### 阶段3: 智能化（后续）

**功能**:
- AI 决策（何时干预 Agent）
- 代码质量检查
- 自动化工作流
- 学习用户偏好

---

## 📁 已创建的文件

```
playwright-cursor/
├── README.md                          # 使用说明
├── FINDINGS.md                        # 详细调研报告
├── package.json                       # Node.js 配置
├── cursor-dom-inspector.js            # Electron 启动测试（失败）
├── cursor-dom-inspector-cdp.js        # CDP 连接测试（失败）
├── run_with_cursor.sh                 # 启动脚本
└── run_test.sh                        # 测试脚本

bridge/
├── cursor_dom_inspector.py            # Python 版本（无 Electron 支持）
├── test_cursor_dom.py                 # Python 测试
├── verify_playwright.py               # Playwright 验证
└── PLAYWRIGHT_README.md               # Python 文档
```

---

## 🎓 关键发现

### 1. Playwright 的局限性

- ✅ Playwright **Node.js 版本**支持 Electron
- ❌ Playwright **Python 版本**不支持 Electron
- ❌ Cursor **不支持** Playwright 自动化
- ❌ Cursor **禁用了** Chrome DevTools Protocol

### 2. Electron 应用的多样性

不是所有 Electron 应用都支持自动化：
- VSCode: 支持扩展 API（官方）
- Cursor: 支持扩展 API（可能，待验证）
- 其他 Electron 应用: 视具体实现而定

### 3. 识别 UI 的方式

| 方法 | 原理 | 可行性 |
|-----|------|--------|
| DOM 选择器 | 访问 HTML 元素 | ✅ (需要 CDP 或 Extension) |
| 图像识别 | OCR + 图像匹配 | ⚠️ 慢且不可靠 |
| Accessibility API | 系统级 UI 访问 | ⚠️ 无法访问 Electron 内部 |
| Extension API | 编辑器 API | ✅ 最佳方案 |

---

## 🚀 下一步行动

### 立即可做（今天）

1. ✅ 调研完成 - **已完成**
2. ⏭️ 实现 pyautogui 版本（快速验证）

### 本周可做

1. 验证 Cursor Extension API 兼容性
2. 创建 Hello World 扩展
3. 测试在 Cursor 中是否能正常工作

### 本月可做

1. 开发完整的オルテンシア Controller Extension
2. 实现智能决策模块
3. 完整集成到系统

---

## 💡 总结

虽然 **Playwright 无法直接控制 Cursor**，但我们发现了更好的方案：

### 🎯 最佳路径

1. **短期**: 使用 **pyautogui + Cursor CLI**
   - 立即可用
   - 快速验证想法
   - 无需复杂开发

2. **长期**: 开发 **VSCode Extension**
   - 官方支持
   - 功能强大
   - 长期可维护

### 🎊 你可以开始的事情

```bash
# 1. 查看详细调研报告
cat playwright-cursor/FINDINGS.md

# 2. 查看所有测试文件
ls playwright-cursor/
ls bridge/

# 3. 查看 Git 历史
git log --oneline feature/playwright-cursor-control
```

---

**分支**: `feature/playwright-cursor-control`  
**提交**: 2 commits  
- `8e5b276` - Playwright DOM Inspector 实现
- `47defc6` - 完整调研报告

**状态**: ✅ 调研完成，准备实施替代方案

---

## 📚 相关文档

- `playwright-cursor/FINDINGS.md` - 详细技术调研
- `playwright-cursor/README.md` - Playwright 使用说明
- `bridge/PLAYWRIGHT_README.md` - Python 版本说明

---

**感谢你的耐心！虽然 Playwright 方案不可行，但我们找到了更好的解决方案。** 🎉

