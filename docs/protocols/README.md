# 📜 协议文档

> **协议是系统的核心**
> 
> 在理解或修改任何功能前，必须先阅读相关协议

---

## 核心协议

### 1. Ortensia 协议（代码即文档）

**位置**: `bridge/protocol.py`

这是系统的核心协议定义，包含：
- `MessageType` 枚举 - 所有消息类型
- `*Payload` 数据类 - 消息载荷结构
- `MessageBuilder` - 消息构建器

### 2. WebSocket 协议

**文档**: [WEBSOCKET_PROTOCOL.md](./WEBSOCKET_PROTOCOL.md)

通信规范、消息格式、生命周期

### 3. AITuber 协议

**文档**: [AITUBER_PROTOCOL.md](./AITUBER_PROTOCOL.md)

AITuber 特定的消息类型和处理逻辑

---

## 消息类型速查

```python
# 连接管理
REGISTER / REGISTER_ACK
HEARTBEAT / HEARTBEAT_ACK
DISCONNECT

# 对话发现
GET_CONVERSATION_ID / GET_CONVERSATION_ID_RESULT

# JS 执行
EXECUTE_JS / EXECUTE_JS_RESULT

# AITuber 消息
AITUBER_RECEIVE_TEXT
AITUBER_SPEAK
AITUBER_EMOTION
AITUBER_STATUS

# Cursor 操作
CURSOR_INPUT_TEXT / CURSOR_INPUT_TEXT_RESULT

# Agent 事件
AGENT_COMPLETED
AGENT_STATUS_CHANGED
AGENT_ERROR
```

---

## 协议文档列表

| 文档 | 说明 |
|-----|------|
| [WEBSOCKET_PROTOCOL.md](./WEBSOCKET_PROTOCOL.md) | WebSocket 通信协议 |
| [AITUBER_PROTOCOL.md](./AITUBER_PROTOCOL.md) | AITuber 协议 |
| [PROTOCOL_SUMMARY.md](./PROTOCOL_SUMMARY.md) | 协议摘要 |
| [PROTOCOL_USAGE_GUIDE.md](./PROTOCOL_USAGE_GUIDE.md) | 协议使用指南 |
| [WEBSOCKET_ARCHITECTURE.md](./WEBSOCKET_ARCHITECTURE.md) | WebSocket 架构 |

