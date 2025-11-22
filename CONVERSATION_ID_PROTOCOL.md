# Conversation ID 协议 V10

## 概述

V10 简化了 Inject 和 Hook 的关联机制，使用 `conversation_id` 作为统一的关联标识。

## 核心理念

### 之前的方案（V9）⚠️
- Inject 使用 PID: `inject-{pid}`
- Hook 使用哈希: `hook-{workspace_hash}-{conversation_hash}`
- 通过环境变量传递 inject ID（但可能失败）

### 新方案（V10）✅
- **Inject** 仍使用 PID: `inject-{pid}`
- **Hook** 使用 conversation_id: `hook-{conversation_id}`
- **服务器通过 conversation_id 关联 Inject 和 Hook**

## 协议详情

### 1. 获取 Conversation ID

#### 请求：`get_conversation_id`

从任何客户端发送到 inject，请求当前对话的 conversation_id。

**消息格式**：
```json
{
  "type": "get_conversation_id",
  "from": "client-123",
  "to": "inject-{pid}",
  "timestamp": 1700000000,
  "payload": {}
}
```

**字段说明**：
- `type`: 固定为 `"get_conversation_id"`
- `from`: 发送者 ID（任意客户端）
- `to`: 目标 inject ID
- `timestamp`: Unix 时间戳（秒）
- `payload`: 空对象

#### 响应：`get_conversation_id_result`

Inject 返回当前对话的 conversation_id。

**成功响应**：
```json
{
  "type": "get_conversation_id_result",
  "from": "inject-12345",
  "to": "client-123",
  "timestamp": 1700000001,
  "payload": {
    "success": true,
    "conversation_id": "2d8f9386-9864-4a51-b089-a7342029bb41",
    "inject_id": "inject-12345",
    "workspace": "/Users/user/project"
  }
}
```

**失败响应**：
```json
{
  "type": "get_conversation_id_result",
  "from": "inject-12345",
  "to": "client-123",
  "timestamp": 1700000001,
  "payload": {
    "success": false,
    "conversation_id": null,
    "error": "No active conversation"
  }
}
```

**字段说明**：
- `success`: 是否成功提取 conversation_id
- `conversation_id`: 当前对话的 UUID（成功时）
- `inject_id`: Inject 的 ID
- `workspace`: Cursor 的工作区路径
- `error`: 错误消息（失败时）

### 2. Hook 注册

#### Hook 客户端 ID 生成

```python
conversation_id = input_data.get('conversation_id', 'unknown')
client_id = f"hook-{conversation_id}"
```

**示例**：
- Conversation ID: `2d8f9386-9864-4a51-b089-a7342029bb41`
- Hook ID: `hook-2d8f9386-9864-4a51-b089-a7342029bb41`

#### 注册消息

```json
{
  "type": "register",
  "from": "hook-2d8f9386-9864-4a51-b089-a7342029bb41",
  "to": null,
  "timestamp": 1700000000000,
  "payload": {
    "client_type": "agent_hook"
  }
}
```

### 3. Hook 发送消息

```json
{
  "type": "aituber_receive_text",
  "from": "hook-2d8f9386-9864-4a51-b089-a7342029bb41",
  "to": "aituber",
  "timestamp": 1700000000000,
  "payload": {
    "text": "Shell 命令已执行",
    "emotion": "neutral",
    "source": "hook",
    "hook_name": "afterShellExecution",
    "event_type": "afterShellExecution",
    "workspace": "/Users/user/project",
    "workspace_name": "project",
    "conversation_id": "2d8f9386-9864-4a51-b089-a7342029bb41"
  }
}
```

**关键字段**：
- `from`: 包含 conversation_id 的 Hook ID
- `conversation_id`: 在 payload 中也携带（冗余但方便）

## 服务器端关联机制

### 方案 1：主动查询（推荐）✅

**流程**：
1. Hook 发送消息到服务器，`from` 字段为 `hook-{conversation_id}`
2. 服务器提取 `conversation_id` 从 Hook ID 中
3. 服务器向所有 inject 发送 `get_conversation_id` 请求
4. 比对返回的 `conversation_id`，找到匹配的 inject
5. 建立映射：`conversation_id → inject_id`
6. 后续消息直接使用缓存的映射

**优点**：
- 准确性最高
- 实时验证
- 支持多窗口、多对话

**代码示例**：
```python
async def find_inject_by_conversation_id(conversation_id):
    # 从 Hook ID 提取 conversation_id
    # hook-{conversation_id} → conversation_id
    
    # 查询所有 inject
    for inject_id in active_injects:
        result = await query_inject_conversation_id(inject_id)
        if result.get('conversation_id') == conversation_id:
            # 找到了！缓存映射
            conversation_to_inject[conversation_id] = inject_id
            return inject_id
    
    return None
```

### 方案 2：Inject 主动上报（备用）

Inject 定期上报当前 conversation_id：

```javascript
setInterval(async () => {
    const conversationId = await getCurrentConversationId();
    if (conversationId) {
        sendToCentral({
            type: 'conversation_update',
            from: injectId,
            payload: {
                conversation_id: conversationId,
                workspace: workspacePath
            }
        });
    }
}, 5000);  // 每 5 秒更新
```

服务器维护映射表：
```python
conversation_to_inject = {
    "2d8f9386-9864-4a51-b089-a7342029bb41": "inject-12345",
    "7ab67e25-b0c8-443a-84c4-60e9f43a2b9a": "inject-67890"
}
```

## Inject 实现要点

### 提取 Conversation ID

```javascript
async function getCurrentConversationId() {
    const electron = await import('electron');
    const windows = electron.BrowserWindow.getAllWindows();
    
    if (windows.length === 0) return null;
    
    const code = `
        (() => {
            const el = document.querySelector('[id^="composer-bottom-add-context-"]');
            if (!el) return JSON.stringify({ found: false });
            
            const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
            return JSON.stringify({
                found: true,
                conversation_id: match ? match[1] : null
            });
        })()
    `;
    
    const result = await windows[0].webContents.executeJavaScript(code);
    const data = JSON.parse(result);
    
    return data.found ? data.conversation_id : null;
}
```

### 处理查询请求

```javascript
async function handleGetConversationId(fromId, payload) {
    const conversationId = await getCurrentConversationId();
    
    const response = {
        type: 'get_conversation_id_result',
        from: injectId,
        to: fromId,
        timestamp: Math.floor(Date.now() / 1000),
        payload: {
            success: conversationId !== null,
            conversation_id: conversationId,
            inject_id: injectId,
            workspace: await getWorkspacePath()
        }
    };
    
    sendToCentral(response);
}
```

## Hook 实现要点

### 生成客户端 ID

```python
conversation_id = self.input_data.get('conversation_id', 'unknown')

if conversation_id == 'unknown' or not conversation_id:
    # 备用方案：使用 workspace hash
    workspace = self.input_data.get('workspace_roots', ['unknown'])[0]
    workspace_hash = hashlib.md5(workspace.encode()).hexdigest()[:8]
    client_id = f"hook-{workspace_hash}"
else:
    client_id = f"hook-{conversation_id}"
```

### 发送消息

```python
message_data = {
    "type": "aituber_receive_text",
    "from": client_id,  # hook-{conversation_id}
    "to": "aituber",
    "timestamp": int(time.time() * 1000),
    "payload": {
        "text": text,
        "emotion": emotion,
        "source": "hook",
        "hook_name": self.hook_name,
        "workspace": workspace,
        "conversation_id": conversation_id
    }
}
```

## 优势

### ✅ 简单直观
- Hook ID = `hook-{conversation_id}`
- 直接从 ID 提取 conversation_id
- 无需复杂的哈希计算

### ✅ 精确匹配
- conversation_id 是唯一的
- 不会出现冲突
- 支持多窗口、多对话

### ✅ 灵活扩展
- 支持对话切换
- 支持对话级别的操作
- 未来可以实现更多基于对话的功能

### ✅ 服务器主动控制
- 服务器可以主动查询
- 不依赖环境变量
- 不依赖不稳定的传递机制

## 兼容性

### 没有 conversation_id 的情况

如果 Hook 无法获取 conversation_id（极少数情况）：
- 使用 workspace hash 作为备用 ID
- 日志中会有警告信息
- 功能降级为 workspace 级别关联

## 安装和使用

### 1. 安装 V10 Inject

```bash
cd /Users/user/Documents/\ cursorgirl/cursor-injector
./install-v10.sh
```

### 2. 重启 Cursor

让 inject 生效

### 3. Hook 自动使用新机制

Hook 代码已更新，无需额外操作

### 4. 服务器端实现

服务器需要实现：
- 接收 `hook-{conversation_id}` 格式的客户端
- 提取 conversation_id
- 查询对应的 inject
- 建立关联

## 测试

### 测试 Inject

```bash
# 查看 inject 日志
tail -f /tmp/cursor_ortensia.log | grep -i conversation

# 通过本地接口测试
python3 -c "
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:9876') as ws:
        code = '''
        (async () => {
            const electron = await import(\"electron\");
            const windows = electron.BrowserWindow.getAllWindows();
            const result = await windows[0].webContents.executeJavaScript(\`
                (() => {
                    const el = document.querySelector('[id^=\"composer-bottom-add-context-\"]');
                    if (!el) return JSON.stringify({ found: false });
                    const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
                    return JSON.stringify({ found: true, conversation_id: match ? match[1] : null });
                })()
            \`);
            return result;
        })()
        '''
        await ws.send(code)
        response = await ws.recv()
        print(json.loads(response))

asyncio.run(test())
"
```

### 测试 Hook

```bash
# 查看 hook 日志
tail -f /tmp/cursor-agent-hooks.log | grep -i "Hook ID"

# 在 Cursor 中执行任意命令触发 hook
# 查看日志中的 Hook ID 格式
```

## 总结

V10 通过使用 `conversation_id` 作为统一的关联标识，大大简化了 Inject 和 Hook 的关联机制：

1. **Hook ID = `hook-{conversation_id}`** - 简单直接
2. **Inject 提供查询接口** - `get_conversation_id` 协议
3. **服务器主动关联** - 通过查询或监听建立映射
4. **精确匹配** - conversation_id 是唯一的

这个方案摒弃了之前复杂的环境变量传递和哈希计算，提供了更可靠、更灵活的关联机制。

---

**版本**: V10  
**日期**: 2025-11-22  
**状态**: ✅ 已实现

