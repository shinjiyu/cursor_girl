# Cursor 控制系统待办事项

**状态**: 底层验证完成，准备集成  
**总体进度**: 70%

---

## 🔴 立即执行（今天）

- [ ] **更新 `composer_operations.py`**
  - 修改提交按钮选择器：`.send-with-mode`（不是 `button[type="submit"]`）
  - 添加 Cmd+I 唤出 Composer 功能
  - 添加确保在 Editor tab 的功能
  - 等待按钮出现（输入后才有）
  
- [ ] **创建完整测试 `test_complete_flow.py`**
  - 测试完整流程：输入 → 提交 → 等待完成
  - 验证所有新选择器工作正常

---

## 🟡 本周完成

### Cursor Hook 集成

- [ ] **创建 `install-v9.sh`**
  - 基于 V8，集成正确的 DOM 操作
  - 更新 `handleComposerSendPrompt` 函数
  - 更新 `handleComposerQueryStatus` 函数
  - 添加 `ensureEditorTab()` 函数
  - 添加 `invokeComposer()` 函数（Cmd+I）

- [ ] **测试 V9**
  - 本地测试（不连接中央 Server）
  - 中央 Server 模式测试
  - 验证所有功能正常

### 中央 Server 完善

- [ ] **添加语义操作消息处理**
  - `AGENT_EXECUTE_PROMPT` 处理
  - `AGENT_STOP_EXECUTION` 处理
  - 路由到正确的 Cursor 实例

### 端到端测试

- [ ] **完整流程测试**
  - 启动中央 Server
  - 启动 Cursor（V9）
  - 运行 Command Client
  - 验证提示词执行
  - 验证状态通知

- [ ] **性能测试**
  - 延迟测试
  - 并发测试
  - 稳定性测试

---

## 🟢 有空再做

### 文档更新

- [ ] 更新 `BOTTOM_UP_IMPLEMENTATION.md`（选择器）
- [ ] 更新 `END_TO_END_TESTING_GUIDE.md`（测试步骤）
- [ ] 创建 `CURSOR_SELECTORS.md`（选择器参考）
- [ ] 更新 `QUICK_START.md`（快速开始）

### 功能增强

- [ ] 实现停止执行功能
- [ ] 实现详细状态查询
- [ ] 添加多 Agent 支持
- [ ] 性能优化

---

## ✅ 已完成

- ✅ 协议设计（`protocol.py`）
- ✅ 中央 Server（`websocket_server.py`）
- ✅ DOM 监控工具（`dom_monitor.py`）
- ✅ 底层操作实现（`composer_operations.py`）- 需更新
- ✅ 实际验证所有 DOM 操作
- ✅ **发现正确的选择器**
  - 提交按钮：`.send-with-mode`
  - 状态指示器：`[class*="loading" i]`
  - 使用 Editor tab + Cmd+I

---

## 📊 关键发现

### ✅ 正确的操作方式

| 操作 | 方法 |
|------|------|
| UI 位置 | **Editor tab**（不是 Agents） |
| 唤出 Composer | **Cmd+I** |
| 提交执行 | **点击 `.send-with-mode`** |
| 判断状态 | 检查 `[class*="loading" i]` |

### ⚠️ 重要注意事项

1. **提交按钮不是 `<button>` 元素**，是 `<div class="send-with-mode">`
2. **按钮在输入后才出现**，必须在输入完成后查找
3. **永远使用 Editor tab**，不使用 Agents tab

---

*最后更新: 2025-11-03*

