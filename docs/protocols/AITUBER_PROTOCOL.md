# 中央服务器 ↔ AITuber 协议文档

**版本**: 1.0.0  
**最后更新**: 2024-12-04

---

## 📋 目录

1. [概述](#概述)
2. [系统架构](#系统架构)
3. [协议总览](#协议总览)
4. [详细协议定义](#详细协议定义)
5. [消息流示例](#消息流示例)
6. [实现状态](#实现状态)
7. [扩展性](#扩展性)

---

## 概述

本文档定义中央服务器（Central Server）与 AITuber 客户端之间的 WebSocket 通信协议。

### 关键特性

- ✅ **多角色注册**: AITuber 可同时注册为 `aituber_client` 和 `command_client`
- ✅ **会话事件流**: 中央服务器负责输入仲裁与事件广播（多端一致性）
- ✅ **事件驱动**: Cursor Hook 事件自动转发给 AITuber
- ✅ **命令控制**: AITuber 可向 Cursor 发送命令（输入文本、执行等）

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                  中央服务器 (ws://localhost:8765)                 │
│                                                                   │
│  - 消息路由 (Message Routing)                                    │
│  - 会话仲裁与顺序一致性 (Session Ordering)                        │
│  - 事件广播 (Event Broadcasting)                                 │
│  - JavaScript 动态执行 (Dynamic JS Execution)                    │
└────┬──────────────────┬──────────────────┬────────────────────┘
     │                  │                  │
     │                  │                  │
     v                  v                  v
┌────────────┐    ┌────────────┐    ┌─────────────────────┐
│ AITuber    │    │   Cursor   │    │   Cursor Hook       │
│  Client    │    │   Inject   │    │   (Python)          │
│            │    │            │    │                     │
│ 角色:      │    │ 角色:      │    │ 角色:               │
│ - aituber  │    │ - inject   │    │ - hook-{conv_id}    │
│ - command  │    │            │    │                     │
└────────────┘    └────────────┘    └─────────────────────┘
```

**通信流程**:
1. Cursor Hook (Python) 监听 Cursor 事件 → 发送到中央服务器
2. 中央服务器转发为会话事件 → 广播给 AITuber
3. AITuber 显示消息（渲染由终端决定）
4. AITuber 发送命令 → 中央服务器 → Cursor Inject → 执行

---

## 协议总览

### 3.1 连接与注册

| 消息类型 | 方向 | 说明 |
|---------|------|------|
| `REGISTER` | AITuber → Server | AITuber 注册（多角色） |
| `REGISTER_ACK` | Server → AITuber | 注册确认 |
| `HEARTBEAT` | AITuber ↔ Server | 心跳保持连接 |
| `HEARTBEAT_ACK` | Server → AITuber | 心跳响应 |
| `DISCONNECT` | AITuber → Server | 断开连接通知 |

### 3.2 AITuber 专用消息

| 消息类型 | 方向 | 说明 | 实现状态 |
|---------|------|------|----------|
| `AITUBER_RECEIVE_TEXT` | Hook → Server → AITuber | Cursor 事件文本（不含 TTS） | ✅ 已实现 |
| `AITUBER_SPEAK` | AITuber → Server | AITuber 说话（预留） | ⚠️ 定义但未使用 |
| `AITUBER_EMOTION` | AITuber → Server | 情绪变化（预留） | ⚠️ 定义但未使用 |
| `AITUBER_STATUS` | AITuber → Server | 状态更新（预留） | ⚠️ 定义但未使用 |

### 3.3 命令控制消息（Command Client 角色）

| 消息类型 | 方向 | 说明 | 实现状态 |
|---------|------|------|----------|
| `CURSOR_INPUT_TEXT` | AITuber → Server → Inject | 向 Cursor 输入文本 | ✅ 已实现 |
| `CURSOR_INPUT_TEXT_RESULT` | Inject → Server → AITuber | 输入结果 | ✅ 已实现 |
| `EXECUTE_JS` | Server → Inject | 执行 JavaScript | ✅ 已实现 (内部) |
| `EXECUTE_JS_RESULT` | Inject → Server | 执行结果 | ✅ 已实现 |

### 3.4 Cursor 事件通知（接收）

| 消息类型 | 方向 | 说明 |
|---------|------|------|
| `AGENT_STATUS_CHANGED` | Hook → Server → **广播** | Cursor Agent 状态变化 |
| `AGENT_COMPLETED` | Hook → Server → **广播** | Agent 任务完成 |
| `AGENT_ERROR` | Hook → Server → **广播** | Agent 错误 |

---

## 详细协议定义

### 4.1 注册协议

#### 4.1.1 REGISTER (AITuber → Server)

**新协议：多角色注册**

```json
{
  "type": "register",
  "from": "aituber-12345",
  "to": "server",
  "timestamp": 1733320800,
  "payload": {
    "client_types": ["aituber_client", "command_client"],
    "platform": "darwin",
    "pid": 20073,
    "version": "1.0.0",
    "metadata": {
      "user_agent": "Mozilla/5.0...",
      "screen_resolution": "1920x1080"
    }
  }
}
```

**Payload 字段**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `client_types` | array | 是 | 角色列表: `["aituber_client", "command_client"]` |
| `platform` | string | 是 | 操作系统: `darwin`, `win32`, `linux` |
| `pid` | number | 是 | 进程 ID |
| `version` | string | 否 | 客户端版本 |
| `metadata` | object | 否 | 额外元数据 |

#### 4.1.2 REGISTER_ACK (Server → AITuber)

```json
{
  "type": "register_ack",
  "from": "server",
  "to": "aituber-12345",
  "timestamp": 1733320801,
  "payload": {
    "success": true,
    "assigned_id": "aituber-12345",
    "server_info": {
      "version": "1.0.0",
      "tts_enabled": true
    }
  }
}
```

---

### 4.2 核心消息：AITUBER_RECEIVE_TEXT

#### 4.2.1 消息流程

```
1. Cursor Hook 检测到事件 (例如: 命令执行完成)
   ↓
2. Hook 发送 aituber_receive_text → 中央服务器
   ↓
3. 中央服务器添加 conversation_id 等上下文
   ↓
4. 转发给所有 aituber_client
```

#### 4.2.2 AITUBER_RECEIVE_TEXT (Hook → Server → AITuber)

**从 Hook 接收**:

```json
{
  "type": "aituber_receive_text",
  "from": "hook-conv_abc123",
  "to": "aituber",
  "timestamp": 1733320900,
  "payload": {
    "text": "命令执行完成，文件已保存。",
    "emotion": "happy",
    "context": {
      "event_type": "shell_execution",
      "exit_code": 0
    }
  }
}
```

**转发给 AITuber（纯文本事件，不再添加 audio_file）**:

```json
{
  "type": "aituber_receive_text",
  "from": "hook-conv_abc123",
  "to": "aituber",
  "timestamp": 1733320900,
  "payload": {
    "text": "命令执行完成，文件已保存。",
    "emotion": "happy",
    "context": {
      "event_type": "shell_execution",
      "exit_code": 0
    }
  }
}
```

**Payload 字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | string | 要显示和朗读的文本 |
| `emotion` | string | 情绪: `happy`, `sad`, `neutral`, `excited`, `worried` |
| `context` | object | 事件上下文信息（可选） |
| `audio_file` | string | （已废弃）旧版 TTS 音频文件路径 |

**AITuber 客户端处理**:

```typescript
case MessageType.AITUBER_RECEIVE_TEXT:
  const { text, emotion, audio_file } = payload
  
  // 1. 添加到聊天记录
  homeStore.getState().upsertMessage({
    role: 'assistant',
    content: text,
  })
  
  // 2. 渲染由终端决定（可选：端侧 TTS/动作渲染器）
  break
```

---

### 4.3 命令控制：CURSOR_INPUT_TEXT

#### 4.3.1 CURSOR_INPUT_TEXT (AITuber → Server → Inject)

**用途**: 在 AITuber 聊天窗口输入文本，发送到 Cursor

```json
{
  "type": "cursor_input_text",
  "from": "aituber-12345",
  "to": "cursor_inject",
  "timestamp": 1733321000,
  "payload": {
    "text": "列出当前目录下的所有文件",
    "conversation_id": null,
    "execute": true
  }
}
```

**Payload 字段**:

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | string | 是 | - | 要输入的文本 |
| `conversation_id` | string | 否 | null | 目标对话 ID（可选） |
| `execute` | boolean | 否 | false | 是否立即执行（按 Enter） |

**中央服务器处理逻辑**:

```python
async def handle_cursor_input_text(client_info: ClientInfo, message: Message):
    text = message.payload.get('text', '')
    execute = message.payload.get('execute', False)
    
    # 生成 JavaScript 代码
    js_code = f"""
    (async function() {{
        const inputElement = document.querySelector('div[contenteditable="true"]');
        if (!inputElement) {{ return JSON.stringify({{ success: false }}); }}
        
        inputElement.focus();
        document.execCommand('insertText', false, {json.dumps(text)});
        
        if ({json.dumps(execute)}) {{
            const submitButton = document.querySelector('button[aria-label*="Submit"]');
            if (submitButton) {{ submitButton.click(); }}
        }}
        
        return JSON.stringify({{ success: true }});
    }})()
    """
    
    # 发送 EXECUTE_JS 到 Inject
    execute_msg = MessageBuilder.execute_js(
        from_id="server",
        to_id=target_inject.client_id,
        code=js_code,
        request_id=f"input_text_{from_id}_{int(time.time())}"
    )
    await target_inject.websocket.send(execute_msg.to_json())
```

#### 4.3.2 CURSOR_INPUT_TEXT_RESULT (Inject → Server → AITuber)

```json
{
  "type": "cursor_input_text_result",
  "from": "server",
  "to": "aituber-12345",
  "timestamp": 1733321001,
  "payload": {
    "success": true,
    "message": "文本已输入到 Cursor 并点击了执行按钮",
    "error": null
  }
}
```

---

### 4.4 事件通知（广播）

AITuber 会接收所有 Cursor Hook 发送的事件广播。

#### 4.4.1 AGENT_STATUS_CHANGED

```json
{
  "type": "agent_status_changed",
  "from": "hook-conv_abc123",
  "to": "",
  "timestamp": 1733321100,
  "payload": {
    "agent_id": "default",
    "old_status": "thinking",
    "new_status": "working",
    "task_description": "正在生成代码..."
  }
}
```

#### 4.4.2 AGENT_COMPLETED

```json
{
  "type": "agent_completed",
  "from": "hook-conv_abc123",
  "to": "",
  "timestamp": 1733321200,
  "payload": {
    "agent_id": "default",
    "result": "success",
    "files_modified": ["main.py", "test_main.py"],
    "summary": "已生成快速排序实现及单元测试"
  }
}
```

---

## 消息流示例

### 5.1 完整交互流程

```
步骤 1: AITuber 启动并注册
────────────────────────────────────────────────────
AITuber → Server: REGISTER
  payload: { client_types: ["aituber_client", "command_client"], ... }
  
Server → AITuber: REGISTER_ACK
  payload: { success: true, assigned_id: "aituber-12345" }


步骤 2: Cursor Hook 发送事件
────────────────────────────────────────────────────
Hook → Server: AITUBER_RECEIVE_TEXT
  payload: { text: "命令执行完成", emotion: "happy" }

Server 处理:
  1. 检测到 aituber_receive_text 消息
  2. 添加 conversation_id 等上下文

Server → AITuber: AITUBER_RECEIVE_TEXT
  payload: { 
    text: "命令执行完成", 
    emotion: "happy"
  }

AITuber 处理:
  1. 显示消息到聊天窗口
  2. （可选）端侧渲染器处理（例如 TTS/动作）


步骤 3: AITuber 发送命令到 Cursor
────────────────────────────────────────────────────
AITuber → Server: CURSOR_INPUT_TEXT
  payload: { 
    text: "列出当前目录下的所有文件", 
    execute: true 
  }

Server 处理:
  1. 生成 JavaScript 代码
  2. 查找 cursor_inject 客户端
  3. 发送 EXECUTE_JS 消息

Server → Inject: EXECUTE_JS
  payload: { code: "(async function() { ... })()", request_id: "..." }

Inject 执行:
  1. 查找 Cursor 输入框
  2. 使用 document.execCommand('insertText') 输入文本
  3. 模拟点击提交按钮

Inject → Server: EXECUTE_JS_RESULT
  payload: { success: true, result: { success: true, message: "..." } }

Server → AITuber: CURSOR_INPUT_TEXT_RESULT
  payload: { success: true, message: "文本已输入并执行" }


步骤 4: 心跳维持
────────────────────────────────────────────────────
每 30 秒:
AITuber → Server: HEARTBEAT
Server → AITuber: HEARTBEAT_ACK
```

---

## 实现状态

### 6.1 已实现的协议

| 协议 | 文件位置 | 实现状态 |
|------|---------|----------|
| **注册协议** | `bridge/protocol.py` | ✅ 完整实现 |
| **多角色注册** | `aituber-kit/src/utils/OrtensiaClient.ts` | ✅ 完整实现 |
| **AITUBER_RECEIVE_TEXT** | `bridge/websocket_server.py` | ✅ 完整实现（不含 TTS） |
| **CURSOR_INPUT_TEXT** | `bridge/websocket_server.py:553` | ✅ 完整实现 |
| **EXECUTE_JS (动态)** | `cursor-injector/install-v10.sh` | ✅ 完整实现 |
| **心跳机制** | `OrtensiaClient.ts` + `websocket_server.py` | ✅ 完整实现 |

### 6.2 定义但未使用的协议

| 协议 | 定义位置 | 说明 |
|------|---------|------|
| `AITUBER_SPEAK` | `bridge/protocol.py:91` | 预留用于 AITuber 主动说话 |
| `AITUBER_EMOTION` | `bridge/protocol.py:93` | 预留用于情绪变化通知 |
| `AITUBER_STATUS` | `bridge/protocol.py:94` | 预留用于状态更新 |

**建议**: 这些消息类型可以在未来版本中实现，用于更丰富的 AITuber 交互。

### 6.3 核心文件清单

```
项目结构
├── bridge/
│   ├── protocol.py              ✅ 协议定义（Python）
│   ├── websocket_server.py      ✅ 中央服务器实现
│   ├── tts_manager.py          ⚠️ 已暂时移除中央依赖（端侧渲染器可选）
│   └── tts_output/             ⚠️ 旧版遗留目录（可清理）
├── aituber-kit/
│   ├── src/
│   │   ├── utils/
│   │   │   └── OrtensiaClient.ts  ✅ WebSocket 客户端
│   │   ├── pages/
│   │   │   └── assistant.tsx      ✅ 聊天 UI + 消息处理
│   │   └── api/                 ⚠️ 端侧渲染器相关（可选）
├── cursor-injector/
│   └── install-v10.sh           ✅ Inject 代码（含 EXECUTE_JS）
└── cursor-hooks/
    └── lib/
        └── agent_hook_handler.py  ✅ Hook 事件监听
```

---

## 扩展性

### 7.1 未来可扩展的功能

#### 7.1.1 AITuber 主动说话

```json
{
  "type": "aituber_speak",
  "from": "aituber-12345",
  "to": "",
  "timestamp": 1733321300,
  "payload": {
    "text": "你好，我是 AI 助手，需要帮助吗？",
    "emotion": "happy",
    "trigger": "manual"
  }
}
```

**用途**: AITuber 主动发起对话，而不是被动响应。

#### 7.1.2 情绪变化通知

```json
{
  "type": "aituber_emotion",
  "from": "aituber-12345",
  "to": "server",
  "timestamp": 1733321400,
  "payload": {
    "emotion": "thinking",
    "reason": "processing_command"
  }
}
```

**用途**: 通知其他组件 AITuber 当前情绪状态。

#### 7.1.3 （可选）端侧 TTS 支持

在 `aituber_receive_text` 中添加语言字段：

```json
{
  "payload": {
    "text": "Hello, world!",
    "language": "en-US",
    "emotion": "neutral"
  }
}
```

### 7.2 性能优化建议

1. **事件流去重**: 基于 `client_event_id` 做幂等，避免重连重发导致重复
2. **队列串行化**: 对会影响下游（inject）的指令按 session 串行执行，避免交错
3. **消息压缩**: 对大型 payload 使用压缩
4. **连接池**: 复用 WebSocket 连接

---

## 相关文档

- **完整协议规范**: `docs/WEBSOCKET_PROTOCOL.md`
- **协议使用指南**: `docs/PROTOCOL_USAGE_GUIDE.md`
- **Python 协议实现**: `bridge/protocol.py`
- **多角色注册指南**: `bridge/MULTIROLE_GUIDE.md`

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0.0 | 2024-12-04 | 初始版本，记录现有协议实现 |

---

*本文档由 Ortensia 项目维护*



