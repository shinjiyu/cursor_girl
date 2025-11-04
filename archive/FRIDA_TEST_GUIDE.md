# 🔥 Frida 动态注入测试指南

## ✅ 已完成

1. **Frida 安装成功** ✅
   - 版本: 17.4.4
   - 位置: `bridge/venv`

2. **测试脚本已就绪** ✅
   - Shell 测试: `playwright-cursor/test-frida-dynamic.sh`
   - Python 基础测试: `playwright-cursor/test-frida-python.py`
   - **完整测试（推荐）**: `playwright-cursor/frida-find-renderer.py`

3. **技术文档已完成** ✅
   - 注入原理: `FRIDA_INJECTION_MECHANISM.md`
   - DOM 访问能力: `FRIDA_DOM_ACCESS_EXPLAINED.md`

---

## 🚀 测试步骤

### 步骤 1: 启动 Cursor

```bash
open -a Cursor

# 建议: 打开一个代码文件，确保编辑器已加载
```

### 步骤 2: 运行测试（3 选 1）

#### 方法 A: 完整自动测试（推荐）⭐⭐⭐⭐⭐

```bash
cd "/Users/user/Documents/ cursorgirl/bridge"
source venv/bin/activate
cd ..
python playwright-cursor/frida-find-renderer.py
```

**这个脚本会**：
- ✅ 自动查找所有 Cursor 进程
- ✅ 自动识别渲染进程（有 DOM 的那个）
- ✅ 动态注入控制代码
- ✅ 测试 DOM 访问
- ✅ 测试 Monaco Editor 访问
- ✅ 测试查找 AI 输入框
- ✅ 测试获取编辑器代码
- ✅ （可选）测试发送 AI 命令

#### 方法 B: 基础 Python 测试

```bash
cd "/Users/user/Documents/ cursorgirl/bridge"
source venv/bin/activate
cd ..
python playwright-cursor/test-frida-python.py
```

**这个脚本会**：
- 附加到 Cursor
- 检测是主进程还是渲染进程
- 给出下一步建议

#### 方法 C: Shell 快速测试

```bash
cd "/Users/user/Documents/ cursorgirl"
./playwright-cursor/test-frida-dynamic.sh
```

**这个脚本会**：
- 检查 Frida 安装
- 检查 Cursor 是否运行
- 尝试快速注入

---

## 🎯 预期结果

### 成功的标志

如果测试成功，你会看到：

```
✅ 成功附加到 Cursor
✅ 找到渲染进程
✅ 可以访问 DOM
✅ 可以访问 Monaco Editor
✅ 找到 AI 输入框
✅ 可以获取编辑器代码

🎉 Frida 动态注入测试通过！
```

### 可能的问题

#### 问题 1: 附加到了主进程

```
⚠️ 不在渲染进程中（这是主进程）
```

**解决方法**: 使用 `frida-find-renderer.py`，它会自动找到渲染进程。

#### 问题 2: 权限问题

```
❌ Failed to attach: unable to access process
```

**解决方法**: 
1. 关闭 Cursor 的 SIP 保护（不推荐）
2. 或者以 root 运行（不推荐）
3. 或者检查是否有安全软件阻止

#### 问题 3: Cursor 未运行

```
❌ Cursor 未运行
```

**解决方法**: 先启动 Cursor

---

## 📊 测试能力

### Frida 可以做什么

| 能力 | 说明 | 示例 |
|-----|------|------|
| ✅ **访问 DOM** | 像浏览器 DevTools 一样 | `document.querySelector()` |
| ✅ **查找元素** | 找到 AI 输入框、按钮等 | `textarea[placeholder*="Ask"]` |
| ✅ **读取编辑器** | 获取当前代码 | `monaco.editor.getEditors()[0].getValue()` |
| ✅ **修改编辑器** | 插入代码 | `editor.setValue('new code')` |
| ✅ **模拟输入** | 自动填写 AI 命令 | `input.value = 'prompt'` |
| ✅ **监听变化** | 监听 AI 响应 | `MutationObserver` |
| ✅ **RPC 调用** | Python 控制 Cursor | `script.exports.sendToAI()` |

---

## 🎮 实际使用示例

### 在测试中你可以尝试

1. **查找 AI 输入框**
   ```python
   # 脚本会自动查找并显示
   ai_input = script.exports.find_ai_input()
   ```

2. **获取当前代码**
   ```python
   code_info = script.exports.get_editor_code()
   print(code_info['code'])
   ```

3. **发送 AI 命令**
   ```python
   # 测试时会询问是否尝试
   result = script.exports.send_to_ai("请解释这段代码")
   ```

---

## 🚀 测试成功后

### 下一步计划

如果 Frida 测试成功，我们可以：

1. ✅ **集成到 Ortensia**
   - 创建 `ortensia_frida_bridge.py`
   - 从 WebSocket 服务器接收事件
   - 动态注入 Frida 控制 Cursor
   - 发送 AI 命令
   - 监听 AI 响应

2. ✅ **实现自动化工作流**
   ```
   用户提交代码 
   → Cursor hooks 触发
   → Ortensia 收到事件
   → Ortensia 决策（需要发送什么命令）
   → 动态注入 Frida 到 Cursor
   → 发送 AI 命令
   → 监听 AI 完成
   → 分离 Frida
   → Ortensia 继续监听
   ```

3. ✅ **优化用户体验**
   - 无缝集成
   - 用户无感知
   - 不干扰正常使用

---

## 📝 注意事项

1. **Electron 多进程**
   - Cursor 有多个进程
   - 主进程：管理窗口（Node.js）
   - 渲染进程：UI 界面（浏览器）
   - 我们需要附加到**渲染进程**

2. **动态注入特点**
   - ✅ 无需重启 Cursor
   - ✅ 无需修改 Cursor 文件
   - ✅ 随时可以附加/分离
   - ✅ 不影响正常使用

3. **安全考虑**
   - Frida 需要进程调试权限
   - macOS 可能会弹出权限确认
   - 这是正常的系统安全机制

---

## 🆘 遇到问题？

### 日志位置

测试脚本会输出详细日志，如果遇到问题：

1. 复制完整的错误信息
2. 检查 Cursor 是否完全启动
3. 确认打开了一个代码文件
4. 尝试重启 Cursor 后再测试

### 常见错误

| 错误 | 原因 | 解决 |
|-----|------|------|
| `ProcessNotFoundError` | Cursor 未运行 | 启动 Cursor |
| `Unable to access` | 权限问题 | 允许系统权限请求 |
| `window is undefined` | 附加到主进程 | 使用 `frida-find-renderer.py` |

---

## ✅ 测试清单

- [ ] Cursor 已启动
- [ ] 打开了一个代码文件
- [ ] 运行 `frida-find-renderer.py`
- [ ] 看到 "✅ 这是渲染进程！"
- [ ] 看到 DOM 信息输出
- [ ] 看到 Monaco Editor 信息
- [ ] （可选）测试发送 AI 命令

---

## 🎉 成功标准

当你看到这些输出时，说明 Frida 完全可用：

```
✅ 找到 N 个 Cursor 进程
✅ 这是渲染进程！
✅ 成功附加到渲染进程
📄 DOM 信息:
   document.title: Cursor - filename.js
   body children: 123
📝 Monaco Editor:
   编辑器数量: 1
   当前行数: 45
🔍 查找 Cursor UI 元素:
   textarea 数量: 2
🎮 创建 Ortensia 控制 API...
✅ ortensiaAPI 已创建

🎉 测试完成！
✅ Frida 可以:
   • 动态附加到 Cursor 渲染进程
   • 完整访问 DOM 和 window 对象
   • 查找和控制 UI 元素
   • 访问 Monaco Editor
   • 发送 AI 命令
```

**如果看到以上输出 → Frida 方案 100% 可行！** 🚀

---

**准备好了吗？启动 Cursor，然后运行测试！** 🔥

