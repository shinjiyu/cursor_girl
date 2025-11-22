# Workspace 映射：Agent Hook → Cursor Hook 关联

## 🎯 核心问题

**场景**：收到 Agent Hook 的 "complete" 事件，想给对应的 Cursor 发送新任务。

**问题**：如何找到对应的 Cursor Hook？

---

## ❌ 为什么不能直接匹配 ID？

### Agent Hook 消息
```json
{
  "from": "agent-hook-d42b-ed81",
  "payload": {
    "related_cursor_id": "cursor-d42b"  // ← 这只是推测的哈希
  }
}
```

### Cursor Hook (Inject)
```
client_id: "cursor-12345"  // ← 基于 PID，无法匹配
```

**问题**：
- Agent Hook 的 `cursor-d42b` 是基于 workspace 哈希推测的
- Cursor Hook 的 `cursor-12345` 是基于真实 PID
- **两者无法直接匹配！**

---

## ✅ 解决方案：Workspace 映射

### 核心思路

通过 **workspace** 字段在服务器端建立关联：

```
Cursor Hook 注册时:
  cursor-12345 → workspace: /Users/user/project

Agent Hook 发送消息时:
  agent-hook-xxx → workspace: /Users/user/project

服务器查询映射:
  /Users/user/project → cursor-12345

找到对应的 Cursor！✅
```

---

## 📊 完整流程

### 步骤 1：Cursor Hook 注册

```javascript
// Cursor 启动时 (inject)
{
  "type": "register",
  "from": "cursor-12345",
  "payload": {
    "client_type": "cursor_hook",
    "workspace": "/Users/user/Documents/project",
    "pid": 12345
  }
}
```

**服务器处理**：
```python
# 在 handle_register 中
if client_type == 'cursor_hook':
    workspace = payload.get('workspace')
    registry.register_cursor_workspace("cursor-12345", workspace)
    # 维护映射: {"/Users/user/Documents/project": "cursor-12345"}
```

---

### 步骤 2：Agent Hook 发送消息

```json
{
  "type": "aituber_receive_text",
  "from": "agent-hook-d42b-ed81",
  "payload": {
    "text": "命令完成：git status",
    "workspace": "/Users/user/Documents/project"
  }
}
```

---

### 步骤 3：服务器查找并发送命令

```python
# 提取 workspace
workspace = message.payload.get('workspace')
# → "/Users/user/Documents/project"

# 查找对应的 Cursor ID
cursor_id = registry.get_cursor_by_workspace(workspace)
# → "cursor-12345"

# 获取 Cursor 客户端
cursor_client = registry.get_by_id(cursor_id)

# 发送新任务
command = MessageBuilder.agent_execute_prompt(
    from_id="server",
    to_id=cursor_id,  # ← 发送给找到的 Cursor
    agent_id="default",
    prompt="请分析当前项目"
)

await cursor_client.websocket.send(command.to_json())
# ✅ 任务已发送！
```

---

## 🔧 服务器端实现

### ClientRegistry 增强

```python
class ClientRegistry:
    def __init__(self):
        self.clients = {}
        self.ws_to_id = {}
        self.workspace_to_cursor = {}  # ← 新增映射
    
    def register_cursor_workspace(self, cursor_id: str, workspace: str):
        """注册 Cursor 的 workspace 映射"""
        if workspace:
            self.workspace_to_cursor[workspace] = cursor_id
            logger.info(f"🗺️  注册 workspace 映射: {workspace} → {cursor_id}")
    
    def get_cursor_by_workspace(self, workspace: str) -> Optional[str]:
        """根据 workspace 获取对应的 Cursor ID"""
        cursor_id = self.workspace_to_cursor.get(workspace)
        if cursor_id and cursor_id in self.clients:
            return cursor_id
        return None
```

### 自动清理

```python
def unregister(self, websocket):
    """注销客户端"""
    # ...
    # 如果是 cursor_hook，清理 workspace 映射
    if client_type == 'cursor_hook':
        workspace = client_info.metadata.get('workspace')
        if workspace and self.workspace_to_cursor.get(workspace) == client_id:
            del self.workspace_to_cursor[workspace]
            logger.info(f"🗑️  清理 workspace 映射: {workspace}")
```

---

## 📝 使用示例

### 场景：收到 complete 事件后发送新任务

```python
async def handle_agent_complete(message: Message):
    """处理 Agent Hook 的 complete 事件"""
    
    # 1. 提取 workspace
    workspace = message.payload.get('workspace')
    
    # 2. 查找对应的 Cursor
    cursor_id = registry.get_cursor_by_workspace(workspace)
    
    if not cursor_id:
        logger.warning(f"未找到对应的 Cursor: {workspace}")
        return
    
    cursor_client = registry.get_by_id(cursor_id)
    
    if not cursor_client:
        logger.warning(f"Cursor 已断开: {cursor_id}")
        return
    
    # 3. 发送新任务
    command = MessageBuilder.agent_execute_prompt(
        from_id="server",
        to_id=cursor_id,
        agent_id="default",
        prompt="下一个任务"
    )
    
    await cursor_client.websocket.send(command.to_json())
    logger.info(f"✅ 任务已发送到 {cursor_id}")
```

---

## 🚨 边界情况处理

### 1. 同一 Workspace 多个 Cursor

**当前策略**：最后注册的 Cursor 覆盖之前的映射

```python
# Cursor A 注册
workspace_to_cursor["/Users/user/project"] = "cursor-12345"

# Cursor B 注册（相同 workspace）
workspace_to_cursor["/Users/user/project"] = "cursor-67890"  # 覆盖
```

**改进建议**：
- 可以改为 `workspace → List[cursor_id]`
- 或者使用最近活跃的 Cursor
- 或者让用户选择目标 Cursor

### 2. Cursor 关闭但映射未清理

**已处理**：在 `unregister()` 中自动清理映射

```python
if client_type == 'cursor_hook':
    workspace = client_info.metadata.get('workspace')
    if self.workspace_to_cursor.get(workspace) == client_id:
        del self.workspace_to_cursor[workspace]
```

### 3. Agent Hook 消息缺少 workspace

```python
workspace = message.payload.get('workspace')
if not workspace:
    logger.warning("Agent Hook 消息缺少 workspace 字段")
    return None
```

---

## 📊 对比表

| 方案 | ID 匹配 | Workspace 映射 |
|------|---------|---------------|
| **可行性** | ❌ 无法匹配 | ✅ 可以工作 |
| **实现复杂度** | 简单（但不可行） | 中等 |
| **准确性** | 0% | 100%（单 Cursor）|
| **维护成本** | 低 | 需要清理映射 |
| **边界情况** | 无法处理 | 需要处理多 Cursor |

---

## ✅ 优点

1. **准确**：通过 workspace 精确匹配
2. **可靠**：不依赖 ID 格式
3. **灵活**：可以扩展支持多 Cursor
4. **自动清理**：Cursor 断开时自动清理映射

---

## 🔮 未来改进

### 支持多 Cursor

```python
class ClientRegistry:
    def __init__(self):
        self.workspace_to_cursors = {}  # workspace → List[cursor_id]
    
    def register_cursor_workspace(self, cursor_id, workspace):
        if workspace not in self.workspace_to_cursors:
            self.workspace_to_cursors[workspace] = []
        self.workspace_to_cursors[workspace].append(cursor_id)
    
    def get_cursors_by_workspace(self, workspace):
        """返回所有相关的 Cursor"""
        return self.workspace_to_cursors.get(workspace, [])
    
    def get_active_cursor(self, workspace):
        """返回最近活跃的 Cursor"""
        cursors = self.get_cursors_by_workspace(workspace)
        for cursor_id in reversed(cursors):  # 最后注册的优先
            if cursor_id in self.clients:
                return cursor_id
        return None
```

---

## 📚 相关文档

- `ID_STRATEGY.md` - ID 格式和生成规则
- `DESIGN_DECISIONS.md` - 架构决策
- `example_find_cursor.py` - 完整代码示例

---

**最后更新**: 2025-11-22
**版本**: 2.0

