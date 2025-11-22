# Agent Hooks 设计决策

## 📋 核心问题和解决方案

### 1️⃣ 多 Cursor 实例识别

**问题**：全局安装的 hooks 无法区分消息来自哪个 Cursor 实例或项目。

**解决方案**：
- 使用 `workspace_roots[0]` 作为项目标识
- 在消息 payload 中包含：
  - `workspace`: 完整路径（如 `/Users/user/project`）
  - `workspace_name`: 项目名称（如 `project`）
  - `conversation_id`: Cursor 会话 ID

**示例**：
```json
{
  "workspace": "/Users/user/Documents/ cursorgirl",
  "workspace_name": "cursorgirl",
  "conversation_id": "2d8f9386-9864-4a51-b089-a7342029bb41"
}
```

---

### 2️⃣ 短连接 vs 长连接

**问题澄清**：
- ✅ Hook 使用短连接是**正确的设计**
- Hook 是事件驱动的，不需要保持长连接
- 每次触发时：连接 → 注册 → 发送消息 → 断开

**为什么不用长连接**：
1. Hook 是被动触发的（Cursor 调用）
2. 不需要接收服务器推送的消息
3. 短连接更节省资源
4. 避免连接管理的复杂性

**优化**：
- 虽然是短连接，但使用稳定的客户端 ID
- 这样服务器可以追踪同一会话的多个操作

---

### 3️⃣ 稳定的客户端 ID

**问题**：之前每次 hook 都生成随机 ID，无法追踪同一会话。

**之前**：
```python
client_id = f"agent-hook-{uuid.uuid4().hex[:8]}"
# 每次调用: agent-hook-917f82d5, agent-hook-2fc37194, ...
```

**现在**：
```python
# 基于 workspace + conversation_id 生成稳定 ID
id_source = f"{workspace}:{conversation_id}"
id_hash = hashlib.md5(id_source.encode()).hexdigest()[:8]
client_id = f"agent-hook-{id_hash}"
# 同一会话: agent-hook-f7f2dc93, agent-hook-f7f2dc93, ...（相同）
```

**优点**：
- ✅ 同一会话的所有 hook 使用相同 ID
- ✅ 可以追踪一个 Cursor 会话的完整生命周期
- ✅ 不同 workspace 有不同 ID
- ✅ 不同会话有不同 ID

---

## 📊 客户端 ID 生成规则

```
client_id = agent-hook-{MD5(workspace:conversation_id)[:8]}
```

### 示例

| Workspace | Conversation ID | Client ID |
|-----------|----------------|-----------|
| `/tmp` | `test-123` | `agent-hook-f7f2dc93` |
| `/tmp` | `test-123` | `agent-hook-f7f2dc93` ✅ 相同 |
| `/tmp` | `test-456` | `agent-hook-xxxxxxxx` ❌ 不同 |
| `/home/project` | `test-123` | `agent-hook-yyyyyyyy` ❌ 不同 |

---

## 🔄 连接生命周期

```
┌─────────────────────────────────────────────┐
│ Cursor 触发 Hook（如 afterShellExecution）  │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│ 1. 建立 WebSocket 连接                      │
│    ws://localhost:8765                       │
│    (超时: 2 秒)                              │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│ 2. 发送 REGISTER 消息                       │
│    - client_id: agent-hook-{hash}           │
│    - client_type: agent_hook                │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│ 3. 等待 REGISTER_ACK                        │
│    (超时: 1 秒)                              │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│ 4. 发送 AITUBER_RECEIVE_TEXT 消息          │
│    - text: 事件描述                         │
│    - emotion: happy/sad/neutral             │
│    - workspace: 项目信息                    │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│ 5. 立即断开连接                             │
│    (总耗时: ~0.04 秒)                        │
└─────────────────────────────────────────────┘
```

---

## ⚡ 性能特性

- **连接时间**: ~40ms（总执行时间）
- **超时保护**: 
  - 总超时: 3 秒
  - 连接超时: 2 秒
  - 响应超时: 1 秒
- **失败处理**: 快速失败，不阻塞 Cursor

---

## 🎯 关键设计原则

1. **稳定的身份标识**：同一会话用相同 ID
2. **快速失败**：超时后立即返回，不卡住 Cursor
3. **短连接高效**：发完即断，不浪费资源
4. **信息完整**：包含 workspace、conversation 等上下文
5. **可追踪性**：日志包含所有关键信息

---

## 📝 服务器端日志示例

**之前**（无法追踪）：
```
[13:35:15] ✅ [agent-hook-917f82d5] 注册成功: agent_hook
[13:35:15] ✅ [agent-hook-2fc37194] 注册成功: agent_hook
[13:35:28] ✅ [agent-hook-a1dec476] 注册成功: agent_hook
```
❌ 无法知道这些消息是否来自同一个 Cursor

**现在**（可追踪）：
```
[13:41:41] ✅ [agent-hook-f7f2dc93] 注册成功: agent_hook (workspace: cursorgirl)
[13:41:48] ✅ [agent-hook-f7f2dc93] 注册成功: agent_hook (workspace: cursorgirl)
[13:42:00] ✅ [agent-hook-f7f2dc93] 注册成功: agent_hook (workspace: cursorgirl)
```
✅ 清楚地看到这是同一个 Cursor 会话的多次操作

---

## 🔧 未来改进建议

1. **客户端缓存**：
   - 在 hook 进程间共享连接（可选）
   - 需要进程间通信机制

2. **批量发送**：
   - 短时间内多个事件可以批量发送
   - 减少连接开销

3. **离线队列**：
   - 服务器不可用时缓存消息
   - 服务器恢复后重新发送

4. **更细粒度的标识**：
   - 添加 user 字段（区分不同用户）
   - 添加 machine 字段（区分不同机器）

---

**最后更新**: 2025-11-22
**版本**: 2.0

