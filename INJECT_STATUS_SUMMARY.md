# Inject 和 Hook 的 ID 策略现状

## 📋 总结

### ✅ **Inject 已经使用 PID 作为 ID - 不需要重新安装！**

## 当前实现状态

### 1. Inject（`install-v9.sh`）✅ 已完成

**ID 生成方式**：
```javascript
const injectId = `inject-${process.pid}`;
process.env.ORTENSIA_INJECT_ID = injectId;
```

**注册消息**：
```javascript
{
    type: 'register',
    from: injectId,  // ✅ inject-{pid}
    payload: {
        cursor_id: injectId,
        pid: process.pid,
        workspace: workspace,
        ws_port: 9876,
        // ...
    }
}
```

**优点**：
- ✅ 使用 PID，稳定且唯一
- ✅ 同一个 Cursor 进程总是使用相同的 ID
- ✅ 重启后会生成新的 ID（符合预期）

### 2. Hook（`agent_hook_handler.py`）⚠️ 部分完成

**自身 ID 生成**：
```python
# Hook 自己的客户端 ID（用于注册到中央服务器）
workspace_hash = hashlib.md5(workspace.encode()).hexdigest()[:4]
conversation_hash = hashlib.md5(conversation_id.encode()).hexdigest()[:4]
client_id = f"hook-{workspace_hash}-{conversation_hash}"
```

**读取 Inject ID**：
```python
# 尝试从环境变量获取对应的 inject ID
inject_id = os.getenv('ORTENSIA_INJECT_ID', '')

# 在消息中携带 inject ID
"inject_id": inject_id if inject_id else None
```

**问题**：
- ⚠️ **环境变量可能无法传递**
  - Inject 在 Electron 主进程中设置环境变量
  - Hook 是 Cursor 启动的子进程（通过 shell script）
  - Cursor 可能不会传递 Electron 的环境变量给子进程

## 🔍 需要验证

### 测试环境变量传递

创建了测试脚本 `test_env_var.py`，可以添加到 `hooks.json` 中测试：

```json
{
  "beforeShellExecution": [{
    "command": "$HOME/.cursor-agent/run_hook.sh /path/to/test_env_var.py"
  }]
}
```

**测试步骤**：
1. 确保 inject 已安装并运行
2. 添加测试 hook
3. 在 Cursor 中执行任意 shell 命令
4. 查看 `/tmp/cursor-agent-hooks.log` 日志

**预期结果**：
- ✅ 如果能看到 `ORTENSIA_INJECT_ID = inject-{pid}`：环境变量成功传递
- ❌ 如果看到 `ORTENSIA_INJECT_ID = ''`：环境变量未传递，需要备用方案

## 🔧 备用方案（如果环境变量无法传递）

### 方案 A：通过中央服务器映射（推荐）✅

**流程**：
1. Inject 注册时发送：`cursor_id: inject-{pid}` + `workspace: /path/to/workspace`
2. 中央服务器维护映射：`workspace → inject-{pid}`
3. Hook 发送消息时包含：`workspace: /path/to/workspace`
4. 中央服务器查找：根据 workspace 找到对应的 inject ID
5. 转发消息时携带正确的 inject ID

**优点**：
- 不依赖环境变量
- 中央服务器统一管理
- 支持 workspace 切换

**缺点**：
- 一个 workspace 可能被多个 Cursor 打开（需要处理）

### 方案 B：通过 conversation_id 关联

**发现**：今天的工作中我们发现了如何提取 `conversation_id`！

**可行性**：
1. Inject 定期提取当前的 `conversation_id`：
   ```javascript
   const el = document.querySelector('[id^="composer-bottom-add-context-"]');
   const conversation_id = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/)[1];
   ```

2. Inject 上报给中央服务器：`inject-{pid} ↔ conversation_id`

3. Hook 从 Cursor 输入中获取 `conversation_id`

4. 中央服务器根据 `conversation_id` 找到对应的 inject

**优点**：
- ✅ **最精确的匹配**：conversation_id 是唯一的
- ✅ 支持多 workspace、多对话
- ✅ 可以实现对话级别的操作（如切换对话）

**缺点**：
- 需要 inject 定期更新 conversation_id
- Hook 执行时对话可能已经切换

## 📝 建议行动

### 立即执行

1. **✅ 不需要重新安装 inject** - 已经使用 PID
2. **测试环境变量传递** - 运行 `test_env_var.py`

### 根据测试结果

#### 如果环境变量可以传递 ✅
- 无需额外工作
- 当前实现已满足需求

#### 如果环境变量无法传递 ❌
实现**方案 A + 方案 B 组合**：

1. **Inject 增强**（添加到 `install-v9.sh`）：
   ```javascript
   // 定期提取并上报 conversation_id
   setInterval(async () => {
       const conversationId = await getCurrentConversationId();
       sendToCentral({
           type: 'conversation_update',
           inject_id: injectId,
           conversation_id: conversationId,
           workspace: workspacePath
       });
   }, 5000);  // 每 5 秒更新一次
   ```

2. **中央服务器增强**：
   - 维护 `conversation_id → inject_id` 映射
   - 维护 `workspace → inject_id` 映射（备用）
   - Hook 消息到达时自动关联 inject

3. **Hook 保持不变**：
   - 继续发送 workspace 和 conversation_id
   - 由服务器负责查找对应的 inject

## 🎯 下一步

**立即测试**：
```bash
# 1. 重启 Cursor（确保 inject 运行）
# 2. 运行测试脚本
python3 /Users/user/Documents/\ cursorgirl/cursor-hooks/test_env_var.py

# 3. 或者在 Cursor 中触发 hook 查看日志
tail -f /tmp/cursor-agent-hooks.log | grep ORTENSIA_INJECT_ID
```

**结论**：
- **Inject 不需要重新安装**，已经使用 PID ✅
- 需要验证环境变量传递
- 如果需要，实现 conversation_id 映射方案

---

**日期**: 2025-11-22  
**状态**: 分析完成，等待测试验证

