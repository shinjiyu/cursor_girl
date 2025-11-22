# Ortensia 客户端 ID 统一策略

## 🎯 设计目标

1. **区分不同组件**：Cursor Hook (inject) 和 Agent Hook 使用不同前缀
2. **支持关联**：可以通过 workspace 关联来自同一项目的消息
3. **稳定可追踪**：同一会话的操作使用稳定 ID
4. **无需共享状态**：各组件独立生成 ID，无需进程间通信

---

## 📊 ID 格式

### 1. Cursor Hook (Inject)

**格式**：`cursor-{pid}`

**生成时机**：Cursor 启动时
**生命周期**：Cursor 进程存活期间
**连接方式**：长连接

**示例**：
```
cursor-12345
cursor-67890
```

**优点**：
- ✅ 基于 PID，稳定且唯一
- ✅ 不依赖 workspace（启动时即可生成）
- ✅ 简单可靠

**代码**：
```javascript
function generateCursorId() {
    return `cursor-${process.pid}`;
}
```

---

### 2. Agent Hook

**格式**：`agent-hook-{workspace_hash}-{conversation_hash}`

**生成时机**：每次 hook 触发时
**生命周期**：单次操作（短连接）
**连接方式**：短连接（发完即断）

**示例**：
```
agent-hook-d42b-ed81    ← workspace: /tmp, conversation: test-123
agent-hook-d42b-f2c3    ← workspace: /tmp, conversation: test-456 (不同会话)
agent-hook-a7f9-ed81    ← workspace: /home/project, conversation: test-123 (不同项目)
```

**哈希规则**：
- `workspace_hash`: MD5(workspace_path)[:4]
- `conversation_hash`: MD5(conversation_id)[:4]

**优点**：
- ✅ 同一会话的所有 hook 使用相同 ID
- ✅ 包含 workspace 信息，便于关联
- ✅ ID 简短（agent-hook-xxxx-xxxx，17 字符）

**代码**：
```python
workspace_hash = hashlib.md5(workspace.encode()).hexdigest()[:4]
conversation_hash = hashlib.md5(conversation_id.encode()).hexdigest()[:4]
client_id = f"agent-hook-{workspace_hash}-{conversation_hash}"
```

---

## 🔗 组件关联

虽然 Cursor Hook 和 Agent Hook 使用不同的 ID，但可以通过 **workspace** 进行关联：

### 方案 1：通过 Workspace 关联

**Cursor Hook 注册消息**：
```json
{
  "type": "register",
  "from": "cursor-12345",
  "payload": {
    "client_type": "cursor_hook",
    "workspace": "/Users/user/project",
    "pid": 12345
  }
}
```

**Agent Hook 消息**：
```json
{
  "type": "aituber_receive_text",
  "from": "agent-hook-d42b-ed81",
  "payload": {
    "workspace": "/Users/user/project",
    "workspace_name": "project",
    "conversation_id": "test-123",
    "related_cursor_id": "cursor-d42b"
  }
}
```

**服务器端关联逻辑**：
```python
# 根据 workspace 建立映射
workspace_to_cursor = {
    "/Users/user/project": "cursor-12345"
}

# 当收到 Agent Hook 消息时
agent_workspace = message.payload["workspace"]
cursor_id = workspace_to_cursor.get(agent_workspace)

# 现在知道这条 Agent Hook 消息来自哪个 Cursor 实例
```

---

## 📋 ID 对照表

| 场景 | Cursor Hook ID | Agent Hook ID | Workspace |
|------|---------------|---------------|-----------|
| Cursor A，会话1 | `cursor-12345` | `agent-hook-a1b2-c3d4` | `/home/projectA` |
| Cursor A，会话2 | `cursor-12345` | `agent-hook-a1b2-e5f6` | `/home/projectA` |
| Cursor B，会话1 | `cursor-67890` | `agent-hook-7g8h-c3d4` | `/home/projectB` |

**分析**：
- ✅ 同一 Cursor（相同 PID）→ 相同 Cursor ID
- ✅ 同一项目不同会话 → 不同 Agent ID（conversation_hash 不同）
- ✅ 不同项目 → 完全不同的 ID
- ✅ 通过 workspace 可以关联 Cursor 和 Agent Hook

---

## 🤔 为什么不使用完全相同的 ID？

### 问题 1：Inject 启动时没有 conversation_id
- Cursor 启动时还没有任何会话
- 无法使用 conversation_id 生成 ID

### 问题 2：Agent Hook 无法获取 Cursor PID
- Agent Hook 是独立进程（由 Cursor 通过 shell 调用）
- 父进程是 shell，不是 Cursor
- 无法可靠获取 Cursor 的 PID

### 问题 3：避免共享状态
- 如果让 inject 生成 ID 并保存到文件
- Agent Hook 读取这个 ID
- 需要处理文件锁、竞态条件等问题
- 增加复杂性和故障点

### 解决方案：分层 ID + Workspace 关联
- ✅ 各组件独立生成 ID（无共享状态）
- ✅ 通过 workspace 建立关联（服务器端处理）
- ✅ 简单可靠，无竞态条件

---

## 🔄 ID 生命周期

### Cursor Hook (长连接)

```
Cursor 启动
    │
    ├─→ 生成 ID: cursor-{pid}
    │
    ├─→ 连接中央服务器
    │
    ├─→ 发送 REGISTER
    │
    ├─→ 保持连接，定期心跳
    │
    ├─→ 接收命令，执行操作
    │
    └─→ Cursor 退出时断开
```

### Agent Hook (短连接)

```
Cursor 触发 Hook
    │
    ├─→ 生成 ID: agent-hook-{workspace_hash}-{conversation_hash}
    │
    ├─→ 连接中央服务器 (2秒超时)
    │
    ├─→ 发送 REGISTER
    │
    ├─→ 等待 REGISTER_ACK (1秒超时)
    │
    ├─→ 发送消息 (AITUBER_RECEIVE_TEXT)
    │
    └─→ 立即断开 (~40ms 总耗时)
```

---

## 📊 消息示例

### Cursor Hook 注册
```json
{
  "type": "register",
  "from": "cursor-12345",
  "to": "server",
  "timestamp": 1732253400,
  "payload": {
    "client_type": "cursor_hook",
    "cursor_id": "cursor-12345",
    "workspace": "/Users/user/Documents/project",
    "platform": "darwin",
    "pid": 12345,
    "ws_port": 9876,
    "capabilities": ["composer", "editor", "terminal"]
  }
}
```

### Agent Hook 注册
```json
{
  "type": "register",
  "from": "agent-hook-d42b-ed81",
  "to": null,
  "timestamp": 1732253401000,
  "payload": {
    "client_type": "agent_hook"
  }
}
```

### Agent Hook 消息
```json
{
  "type": "aituber_receive_text",
  "from": "agent-hook-d42b-ed81",
  "to": "aituber",
  "timestamp": 1732253401001,
  "payload": {
    "text": "命令完成：git status",
    "emotion": "happy",
    "source": "agent_hook",
    "hook_name": "afterShellExecution",
    "event_type": "afterShellExecution",
    "workspace": "/Users/user/Documents/project",
    "workspace_name": "project",
    "conversation_id": "2d8f9386-9864-4a51-b089-a7342029bb41",
    "related_cursor_id": "cursor-d42b"
  }
}
```

---

## 🎯 服务器端处理建议

### 1. 维护 Workspace 映射
```python
class ClientRegistry:
    def __init__(self):
        self.clients = {}  # client_id -> ClientInfo
        self.workspace_to_cursor = {}  # workspace -> cursor_id
    
    def register_cursor_hook(self, cursor_id, workspace):
        """注册 Cursor Hook"""
        self.workspace_to_cursor[workspace] = cursor_id
    
    def get_cursor_for_agent_hook(self, agent_workspace):
        """获取 Agent Hook 对应的 Cursor ID"""
        return self.workspace_to_cursor.get(agent_workspace)
```

### 2. 关联日志
```python
def handle_agent_message(message):
    workspace = message.payload.get("workspace")
    cursor_id = registry.get_cursor_for_agent_hook(workspace)
    
    if cursor_id:
        logger.info(f"Agent Hook 来自 Cursor: {cursor_id}")
        # 可以将消息转发给特定的 Cursor Hook
    else:
        logger.warning(f"未找到对应的 Cursor Hook: {workspace}")
```

---

## ✅ 优点总结

1. **独立性**：各组件独立生成 ID，无需共享状态
2. **稳定性**：同一会话的操作使用稳定 ID
3. **可追踪**：可以追踪一个 Cursor 会话的完整操作序列
4. **可关联**：通过 workspace 关联不同组件
5. **简单性**：无需复杂的进程间通信或文件锁
6. **可扩展**：易于添加更多客户端类型

---

## 🔮 未来改进

### 如果需要更强的关联

可以让 Cursor Hook 在启动时将 ID 写入环境变量：

```javascript
// inject 启动时
process.env.ORTENSIA_CURSOR_ID = `cursor-${process.pid}`;
```

然后 Agent Hook 可以读取：

```python
cursor_pid = os.getenv('ORTENSIA_CURSOR_ID', '').split('-')[-1]
if cursor_pid:
    related_cursor_id = f"cursor-{cursor_pid}"
```

但目前的方案已经足够好，无需这个复杂性。

---

**最后更新**: 2025-11-22
**版本**: 2.0

