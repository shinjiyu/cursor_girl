# Ortensia WebSocket 消息协议规范

**版本**: 1.0.0  
**最后更新**: 2025-11-03

---

## 1. 概述

本文档定义了 Ortensia 系统中各组件之间通过 WebSocket 进行通信的消息协议。

### 1.1 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│              中央 Server (port 8765)                         │
│                                                              │
│  - 注册发现服务 (Registry & Discovery)                       │
│  - 消息路由 (Message Routing)                                │
│  - 事件广播 (Event Broadcasting)                             │
│  - 连接管理 (Connection Management)                          │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
       │                  │                  │
       v                  v                  v
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Cursor Hook  │   │   Command    │   │   AITuber    │
│              │   │    Client    │   │    Client    │
│ - 监听事件   │   │              │   │              │
│ - 执行命令   │   │ - 决策逻辑   │   │ - 界面展示   │
│ - 状态报告   │   │ - LLM 调用   │   │ - 语音合成   │
└──────┬───────┘   └──────────────┘   └──────────────┘
       │
       │ 执行命令
       v
┌──────────────────────────────┐
│    Cursor 注入代码            │
│                              │
│  - WS Server (localhost:9876)│ ← 本地调试模式
│  - WS Client → 中央Server    │ ← 生产模式
└──────────────────────────────┘
```

### 1.2 设计原则

1. **统一格式**: 所有消息使用 JSON 格式
2. **明确类型**: 每个消息都有明确的 `type` 字段
3. **路由清晰**: 通过 `from` 和 `to` 字段明确消息流向
4. **即时响应**: 命令执行采用立即返回策略，不等待任务完成
5. **事件驱动**: 任务状态变化通过事件主动通知
6. **向后兼容**: 预留扩展字段，支持未来功能

---

## 2. 消息基础结构

所有 WebSocket 消息均为 JSON 格式，包含以下基础字段：

```json
{
  "type": "消息类型",
  "from": "发送者ID",
  "to": "接收者ID",
  "timestamp": 1234567890,
  "payload": {}
}
```

### 2.1 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 消息类型，定义消息的用途 |
| `from` | string | 是 | 发送者的唯一标识符 |
| `to` | string | 否 | 接收者ID，空字符串或 null 表示广播 |
| `timestamp` | number | 是 | Unix 时间戳（秒） |
| `payload` | object | 是 | 消息的具体数据，根据 type 不同而变化 |

### 2.2 ID 命名规范

- **中央Server**: `"server"`
- **Cursor Hook**: `"cursor-<随机ID>"` (例如: `cursor-abc123`)
- **Command Client**: `"cc-<编号>"` (例如: `cc-001`)
- **AITuber Client**: `"aituber-<编号>"` (例如: `aituber-001`)

---

## 3. 消息类型定义

### 3.1 连接和注册

#### 3.1.1 REGISTER

**方向**: Client → Server  
**用途**: 客户端注册到中央Server

```json
{
  "type": "register",
  "from": "cursor-abc123",
  "to": "server",
  "timestamp": 1730678400,
  "payload": {
    "client_type": "cursor_hook",
    "cursor_id": "cursor-abc123",
    "workspace": "/Users/user/projects/myapp",
    "platform": "darwin",
    "pid": 12345,
    "ws_port": 9876,
    "capabilities": ["composer", "editor", "terminal"]
  }
}
```

**Payload 字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `client_type` | string | 客户端类型: `cursor_hook`, `command_client`, `aituber_client` |
| `cursor_id` | string | Cursor 实例的唯一ID（仅 cursor_hook） |
| `workspace` | string | 工作区路径（仅 cursor_hook） |
| `platform` | string | 操作系统: `darwin`, `win32`, `linux` |
| `pid` | number | 进程ID |
| `ws_port` | number | 本地 WebSocket Server 端口（仅 cursor_hook） |
| `capabilities` | array | 支持的功能列表 |

**Capabilities 可选值**:
- `composer`: 支持 Composer AI 操作
- `editor`: 支持编辑器操作
- `terminal`: 支持终端操作
- `git`: 支持 Git 操作

#### 3.1.2 REGISTER_ACK

**方向**: Server → Client  
**用途**: 确认注册成功

```json
{
  "type": "register_ack",
  "from": "server",
  "to": "cursor-abc123",
  "timestamp": 1730678401,
  "payload": {
    "success": true,
    "assigned_id": "cursor-abc123",
    "server_info": {
      "version": "1.0.0",
      "supported_protocols": ["composer_v1", "editor_v1"]
    }
  }
}
```

失败响应:

```json
{
  "type": "register_ack",
  "from": "server",
  "to": "cursor-abc123",
  "timestamp": 1730678401,
  "payload": {
    "success": false,
    "error": "ID already registered",
    "assigned_id": null,
    "server_info": null
  }
}
```

---

### 3.2 Composer 操作

#### 3.2.1 COMPOSER_SEND_PROMPT

**方向**: Command Client → Server → Cursor Hook  
**用途**: 发送提示词到 Cursor Composer

```json
{
  "type": "composer_send_prompt",
  "from": "cc-001",
  "to": "cursor-abc123",
  "timestamp": 1730678410,
  "payload": {
    "agent_id": "default",
    "prompt": "写一个快速排序的 Python 实现",
    "wait_for_start": false
  }
}
```

**Payload 字段**:

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `agent_id` | string | 是 | - | Agent ID，当前使用 `"default"` |
| `prompt` | string | 是 | - | 要发送的提示词内容 |
| `wait_for_start` | boolean | 否 | false | 是否等待 AI 开始处理（预留，当前版本总是 false） |

#### 3.2.2 COMPOSER_SEND_PROMPT_RESULT

**方向**: Cursor Hook → Server → Command Client  
**用途**: 返回提示词发送结果（立即返回）

成功响应:

```json
{
  "type": "composer_send_prompt_result",
  "from": "cursor-abc123",
  "to": "cc-001",
  "timestamp": 1730678411,
  "payload": {
    "success": true,
    "agent_id": "default",
    "message": "提示词已输入",
    "error": null
  }
}
```

失败响应:

```json
{
  "type": "composer_send_prompt_result",
  "from": "cursor-abc123",
  "to": "cc-001",
  "timestamp": 1730678411,
  "payload": {
    "success": false,
    "agent_id": "default",
    "message": null,
    "error": "输入框未找到"
  }
}
```

**错误类型**:
- `"输入框未找到"`: Composer 输入框 DOM 元素不存在
- `"输入失败"`: JavaScript 执行失败
- `"Cursor 未响应"`: WebSocket 连接超时
- `"未知错误"`: 其他错误

#### 3.2.3 COMPOSER_QUERY_STATUS

**方向**: Command Client → Server → Cursor Hook  
**用途**: 查询 Agent 当前状态

```json
{
  "type": "composer_query_status",
  "from": "cc-001",
  "to": "cursor-abc123",
  "timestamp": 1730678420,
  "payload": {
    "agent_id": "default"
  }
}
```

#### 3.2.4 COMPOSER_STATUS_RESULT

**方向**: Cursor Hook → Server → Command Client  
**用途**: 返回 Agent 状态查询结果

```json
{
  "type": "composer_status_result",
  "from": "cursor-abc123",
  "to": "cc-001",
  "timestamp": 1730678421,
  "payload": {
    "success": true,
    "agent_id": "default",
    "status": "working",
    "error": null
  }
}
```

**状态值定义**:

| 状态 | 说明 |
|------|------|
| `idle` | 空闲，等待新任务 |
| `thinking` | AI 正在思考和规划 |
| `working` | 正在执行任务（生成代码、修改文件等） |
| `completed` | 任务已完成 |

---

### 3.3 事件通知

事件通知由 Cursor Hook 主动发送，Server 负责广播给所有订阅的客户端。

#### 3.3.1 AGENT_STATUS_CHANGED

**方向**: Cursor Hook → Server → 广播  
**用途**: Agent 状态发生变化时主动通知

```json
{
  "type": "agent_status_changed",
  "from": "cursor-abc123",
  "to": "",
  "timestamp": 1730678430,
  "payload": {
    "agent_id": "default",
    "old_status": "thinking",
    "new_status": "working",
    "task_description": "生成快速排序代码中..."
  }
}
```

**Payload 字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `agent_id` | string | Agent ID |
| `old_status` | string | 之前的状态 |
| `new_status` | string | 当前的状态 |
| `task_description` | string | 任务描述（可选） |

#### 3.3.2 AGENT_COMPLETED

**方向**: Cursor Hook → Server → 广播  
**用途**: Agent 完成任务时通知

```json
{
  "type": "agent_completed",
  "from": "cursor-abc123",
  "to": "",
  "timestamp": 1730678450,
  "payload": {
    "agent_id": "default",
    "result": "success",
    "files_modified": ["main.py", "test_main.py"],
    "summary": "已生成快速排序实现及单元测试"
  }
}
```

**Payload 字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `agent_id` | string | Agent ID |
| `result` | string | 执行结果: `success`, `partial`, `failed` |
| `files_modified` | array | 修改的文件列表 |
| `summary` | string | 任务完成总结 |

**Result 值定义**:
- `success`: 任务完全成功
- `partial`: 部分完成，有错误或警告
- `failed`: 任务失败

#### 3.3.3 AGENT_ERROR

**方向**: Cursor Hook → Server → 广播  
**用途**: Agent 执行过程中发生错误

```json
{
  "type": "agent_error",
  "from": "cursor-abc123",
  "to": "",
  "timestamp": 1730678460,
  "payload": {
    "agent_id": "default",
    "error_type": "execution_error",
    "error_message": "Python syntax error in generated code",
    "can_retry": true
  }
}
```

---

### 3.4 连接管理

#### 3.4.1 HEARTBEAT

**方向**: Client → Server  
**用途**: 心跳包，保持连接活跃

```json
{
  "type": "heartbeat",
  "from": "cursor-abc123",
  "timestamp": 1730678500,
  "to": "server",
  "payload": {}
}
```

**频率**: 建议每 30 秒发送一次

#### 3.4.2 HEARTBEAT_ACK

**方向**: Server → Client  
**用途**: 心跳响应

```json
{
  "type": "heartbeat_ack",
  "from": "server",
  "to": "cursor-abc123",
  "timestamp": 1730678500,
  "payload": {
    "server_time": 1730678500
  }
}
```

#### 3.4.3 DISCONNECT

**方向**: Client → Server  
**用途**: 客户端主动断开连接前的通知

```json
{
  "type": "disconnect",
  "from": "cursor-abc123",
  "to": "server",
  "timestamp": 1730678600,
  "payload": {
    "reason": "user_quit"
  }
}
```

**Reason 值**:
- `user_quit`: 用户关闭应用
- `restart`: 重启中
- `error`: 发生错误

---

## 4. 消息流示例

### 4.1 完整的任务执行流程

```
1. Cursor 启动并注册
Cursor Hook → Server: REGISTER
Server → Cursor Hook: REGISTER_ACK

2. Command Client 连接
CC → Server: REGISTER
Server → CC: REGISTER_ACK

3. CC 发送提示词
CC → Server → Cursor Hook: COMPOSER_SEND_PROMPT
Cursor Hook → Server → CC: COMPOSER_SEND_PROMPT_RESULT (立即返回)

4. Agent 开始工作（状态变化）
Cursor Hook → Server → 广播: AGENT_STATUS_CHANGED (idle → thinking)
Cursor Hook → Server → 广播: AGENT_STATUS_CHANGED (thinking → working)

5. CC 查询状态
CC → Server → Cursor Hook: COMPOSER_QUERY_STATUS
Cursor Hook → Server → CC: COMPOSER_STATUS_RESULT (status: working)

6. Agent 完成任务
Cursor Hook → Server → 广播: AGENT_STATUS_CHANGED (working → completed)
Cursor Hook → Server → 广播: AGENT_COMPLETED

7. 心跳维持连接
Cursor Hook → Server: HEARTBEAT
Server → Cursor Hook: HEARTBEAT_ACK
```

### 4.2 错误处理流程

```
1. 发送提示词失败
CC → Server → Cursor Hook: COMPOSER_SEND_PROMPT
Cursor Hook → Server → CC: COMPOSER_SEND_PROMPT_RESULT (success: false)

2. Agent 执行出错
Cursor Hook → Server → 广播: AGENT_ERROR
CC 收到错误通知，决定是否重试
```

---

## 5. 实现指南

### 5.1 服务端实现要点

1. **注册管理**
   - 维护客户端注册表 (client_id → connection)
   - 处理重复注册（同一 ID 多次连接）
   - 客户端断开时清理注册信息

2. **消息路由**
   - 检查 `to` 字段决定路由方式
   - `to` 为空或 null：广播给所有客户端
   - `to` 为特定 ID：只发送给该客户端
   - 未注册的 `to` ID：返回错误

3. **心跳检测**
   - 超过 60 秒未收到心跳：标记为离线
   - 超过 120 秒：主动断开连接

### 5.2 客户端实现要点

1. **Cursor Hook**
   - 启动时自动连接并注册
   - 监听 DOM 事件检测 Agent 状态变化
   - 实现命令处理器（接收并执行命令）
   - 定时发送心跳

2. **Command Client**
   - 连接并注册为 `command_client` 类型
   - 订阅所有事件通知
   - 实现状态机跟踪 Agent 状态
   - 根据事件触发新命令

3. **错误处理**
   - 网络断开：自动重连（指数退避）
   - 命令超时：设置 5 秒超时
   - 无效消息：记录日志并忽略

### 5.3 安全考虑

1. **认证**（预留）
   - 当前版本：仅 localhost 连接，无需认证
   - 未来版本：添加 token 或证书认证

2. **授权**（预留）
   - 限制客户端只能向特定目标发送消息
   - 敏感操作需要额外确认

3. **输入验证**
   - 验证所有字段类型和格式
   - 限制字符串长度（防止 DoS）
   - 过滤特殊字符

---

## 6. 扩展性

### 6.1 新增消息类型

添加新消息类型时，遵循以下规范：

1. 类型名使用大写+下划线: `EDITOR_OPEN_FILE`
2. 添加到本文档
3. 更新 `bridge/protocol.py` 中的类型定义
4. 保持向后兼容（可选字段）

### 6.2 多 Agent 支持

当前协议已预留 `agent_id` 字段：

```json
{
  "agent_id": "default"
}
```

未来可支持多个 Agent 实例：

```json
{
  "agent_id": "agent-001",
  "agent_name": "Code Generator",
  "agent_role": "code_writer"
}
```

### 6.3 其他功能扩展

协议设计支持以下扩展（未来版本）：

- **编辑器操作**: `EDITOR_OPEN_FILE`, `EDITOR_INSERT_CODE`
- **终端操作**: `TERMINAL_EXECUTE_COMMAND`
- **Git 操作**: `GIT_COMMIT`, `GIT_PUSH`
- **文件系统**: `FILE_READ`, `FILE_WRITE`

---

## 7. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0.0 | 2025-11-03 | 初始版本，定义基础协议 |

---

## 附录 A: 完整消息类型列表

### 连接管理
- `REGISTER` - 注册
- `REGISTER_ACK` - 注册确认
- `HEARTBEAT` - 心跳
- `HEARTBEAT_ACK` - 心跳响应
- `DISCONNECT` - 断开连接

### Composer 操作
- `COMPOSER_SEND_PROMPT` - 发送提示词
- `COMPOSER_SEND_PROMPT_RESULT` - 提示词发送结果
- `COMPOSER_QUERY_STATUS` - 查询状态
- `COMPOSER_STATUS_RESULT` - 状态查询结果

### 事件通知
- `AGENT_STATUS_CHANGED` - Agent 状态变化
- `AGENT_COMPLETED` - Agent 任务完成
- `AGENT_ERROR` - Agent 错误

---

## 附录 B: 常见问题

**Q: 为什么 COMPOSER_SEND_PROMPT_RESULT 立即返回？**  
A: 为了支持状态机设计。Server 和 Client 都需要维护状态机，立即返回可以确认命令已接收，实际任务进度通过事件通知。

**Q: 如何处理消息丢失？**  
A: 关键命令应该有超时重试机制。事件通知是"尽力而为"，丢失不重发。

**Q: 支持多个 Cursor 实例吗？**  
A: 支持。每个 Cursor 实例注册时获得唯一 ID，Command Client 可以指定目标 Cursor。

**Q: 消息顺序能保证吗？**  
A: WebSocket 保证单个连接内的消息顺序。但广播消息到达不同客户端的顺序无法保证。

---

*本文档由 Ortensia 团队维护*

