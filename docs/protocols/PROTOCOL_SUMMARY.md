# Ortensia 协议总览

**版本**: 1.0.0  
**最后更新**: 2024-12-04

---

## 📋 所有协议类型汇总

本文档提供 Ortensia 系统中所有 WebSocket 消息协议的快速索引。

---

## 1. 连接管理协议（5个）

| 消息类型 | 方向 | 说明 | 文档 |
|---------|------|------|------|
| `REGISTER` | Client → Server | 客户端注册 | [WEBSOCKET_PROTOCOL.md](./WEBSOCKET_PROTOCOL.md#311-register) |
| `REGISTER_ACK` | Server → Client | 注册确认 | [WEBSOCKET_PROTOCOL.md](./WEBSOCKET_PROTOCOL.md#312-register_ack) |
| `HEARTBEAT` | Client → Server | 心跳包 | [WEBSOCKET_PROTOCOL.md](./WEBSOCKET_PROTOCOL.md#341-heartbeat) |
| `HEARTBEAT_ACK` | Server → Client | 心跳响应 | [WEBSOCKET_PROTOCOL.md](./WEBSOCKET_PROTOCOL.md#342-heartbeat_ack) |
| `DISCONNECT` | Client → Server | 断开连接通知 | [WEBSOCKET_PROTOCOL.md](./WEBSOCKET_PROTOCOL.md#343-disconnect) |

---

## 2. Composer 操作协议（4个）

底层 Composer 操作，直接控制 Cursor 输入框。

| 消息类型 | 方向 | 说明 | 实现状态 |
|---------|------|------|----------|
| `COMPOSER_SEND_PROMPT` | CC → Server → Hook | 发送提示词 | ⚠️ 部分实现 |
| `COMPOSER_SEND_PROMPT_RESULT` | Hook → Server → CC | 提示词发送结果 | ⚠️ 部分实现 |
| `COMPOSER_QUERY_STATUS` | CC → Server → Hook | 查询 Agent 状态 | ⚠️ 部分实现 |
| `COMPOSER_STATUS_RESULT` | Hook → Server → CC | Agent 状态查询结果 | ⚠️ 部分实现 |

**说明**: 这些协议定义完整，但 Hook 端实现不完整（需要监听 Cursor DOM 事件）。

---

## 3. Agent 语义操作协议（4个）

高层次语义操作，包含完整的执行流程。

| 消息类型 | 方向 | 说明 | 实现状态 |
|---------|------|------|----------|
| `AGENT_EXECUTE_PROMPT` | CC → Server → Hook | 执行提示词（高层次） | ⚠️ 定义但未实现 |
| `AGENT_EXECUTE_PROMPT_RESULT` | Hook → Server → CC | 执行提示词结果 | ⚠️ 定义但未实现 |
| `AGENT_STOP_EXECUTION` | CC → Server → Hook | 停止 Agent 执行 | ⚠️ 定义但未实现 |
| `AGENT_STOP_EXECUTION_RESULT` | Hook → Server → CC | 停止执行结果 | ⚠️ 定义但未实现 |

**说明**: 协议已在 `protocol.py` 中定义，但尚未在 Server 和 Hook 中实现完整逻辑。

---

## 4. 事件通知协议（3个）

Cursor Hook 主动发送的事件广播。

| 消息类型 | 方向 | 说明 | 实现状态 |
|---------|------|------|----------|
| `AGENT_STATUS_CHANGED` | Hook → Server → 广播 | Agent 状态变化 | ⚠️ 定义但未触发 |
| `AGENT_COMPLETED` | Hook → Server → 广播 | Agent 任务完成 | ⚠️ 定义但未触发 |
| `AGENT_ERROR` | Hook → Server → 广播 | Agent 错误 | ⚠️ 定义但未触发 |

**说明**: 协议已定义，Server 支持广播，但 Hook 端未监听 Cursor 事件来触发这些消息。

---

## 5. AITuber 协议（4个）

AITuber 客户端专用消息。

| 消息类型 | 方向 | 说明 | 实现状态 |
|---------|------|------|----------|
| `AITUBER_RECEIVE_TEXT` | Hook → Server → AITuber | 发送文本给 AITuber + TTS | ✅ **完整实现** |
| `AITUBER_SPEAK` | AITuber → Server | AITuber 主动说话 | ⚠️ 定义但未使用 |
| `AITUBER_EMOTION` | AITuber → Server | 情绪变化通知 | ⚠️ 定义但未使用 |
| `AITUBER_STATUS` | AITuber → Server | 状态更新 | ⚠️ 定义但未使用 |

**详细文档**: [AITUBER_PROTOCOL.md](./AITUBER_PROTOCOL.md)

---

## 6. Cursor 控制协议（2个）

AITuber 控制 Cursor 的命令。

| 消息类型 | 方向 | 说明 | 实现状态 |
|---------|------|------|----------|
| `CURSOR_INPUT_TEXT` | AITuber → Server → Inject | 向 Cursor 输入文本 | ✅ **完整实现** |
| `CURSOR_INPUT_TEXT_RESULT` | Inject → Server → AITuber | 输入文本结果 | ✅ **完整实现** |

**特性**: 
- ✅ 支持输入文本到 Cursor composer
- ✅ 支持立即执行（`execute: true`）
- ✅ 兼容 Lexical 编辑器

---

## 7. JavaScript 执行协议（2个）

通用 JavaScript 动态执行机制。

| 消息类型 | 方向 | 说明 | 实现状态 |
|---------|------|------|----------|
| `EXECUTE_JS` | Server → Inject | 执行 JavaScript 代码 | ✅ **完整实现** |
| `EXECUTE_JS_RESULT` | Inject → Server | JavaScript 执行结果 | ✅ **完整实现** |

**说明**: 这是核心机制，`CURSOR_INPUT_TEXT` 底层通过此协议实现。

---

## 8. Conversation ID 协议（2个）

V10 新增，用于关联 Inject 和 Hook。

| 消息类型 | 方向 | 说明 | 实现状态 |
|---------|------|------|----------|
| `GET_CONVERSATION_ID` | Server → Inject | 查询 conversation_id | ✅ 完整实现 |
| `GET_CONVERSATION_ID_RESULT` | Inject → Server | conversation_id 查询结果 | ✅ 完整实现 |

---

## 📊 实现状态统计

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ **完整实现** | 11 | 42% |
| ⚠️ **部分实现/定义但未使用** | 15 | 58% |
| **总计** | 26 | 100% |

---

## 🎯 按组件分类

### 中央服务器与 AITuber

**核心工作协议**（已完整实现）:
1. ✅ `REGISTER` / `REGISTER_ACK` - 多角色注册
2. ✅ `AITUBER_RECEIVE_TEXT` - Cursor 事件 → AITuber + TTS
3. ✅ `CURSOR_INPUT_TEXT` / `CURSOR_INPUT_TEXT_RESULT` - AITuber 控制 Cursor
4. ✅ `HEARTBEAT` / `HEARTBEAT_ACK` - 连接保持

**详细文档**: [AITUBER_PROTOCOL.md](./AITUBER_PROTOCOL.md)

---

### 中央服务器与 Cursor Hook

**已实现**:
1. ✅ `REGISTER` / `REGISTER_ACK`
2. ✅ `AITUBER_RECEIVE_TEXT` - Hook 发送事件给 AITuber
3. ✅ 心跳机制

**未完全实现**（需要 Hook 端监听 Cursor DOM 事件）:
- ⚠️ `AGENT_STATUS_CHANGED` - 状态变化监听
- ⚠️ `AGENT_COMPLETED` - 任务完成监听
- ⚠️ `COMPOSER_QUERY_STATUS` - 状态查询

---

### 中央服务器与 Cursor Inject

**已实现**:
1. ✅ `REGISTER` / `REGISTER_ACK`
2. ✅ `EXECUTE_JS` / `EXECUTE_JS_RESULT` - 动态 JavaScript 执行
3. ✅ `GET_CONVERSATION_ID` / `GET_CONVERSATION_ID_RESULT`
4. ✅ `CURSOR_INPUT_TEXT` (通过 `EXECUTE_JS` 实现)

---

## 📚 相关文档

### 核心协议文档
- **完整协议规范**: [WEBSOCKET_PROTOCOL.md](./WEBSOCKET_PROTOCOL.md)
- **AITuber 专用协议**: [AITUBER_PROTOCOL.md](./AITUBER_PROTOCOL.md)
- **协议使用指南**: [PROTOCOL_USAGE_GUIDE.md](./PROTOCOL_USAGE_GUIDE.md)
- **多角色注册**: [../bridge/MULTIROLE_GUIDE.md](../bridge/MULTIROLE_GUIDE.md)

### 实现代码
- **Python 协议定义**: `bridge/protocol.py`
- **中央服务器**: `bridge/websocket_server.py`
- **AITuber 客户端**: `aituber-kit/src/utils/OrtensiaClient.ts`
- **Cursor Inject**: `cursor-injector/install-v10.sh`
- **Cursor Hook**: `cursor-hooks/lib/agent_hook_handler.py`

---

## 🚀 快速查找

### 我想实现...

**AITuber 接收 Cursor 事件**:
→ [AITUBER_PROTOCOL.md § 4.2 AITUBER_RECEIVE_TEXT](./AITUBER_PROTOCOL.md#42-核心消息aituber_receive_text)

**AITuber 控制 Cursor 输入命令**:
→ [AITUBER_PROTOCOL.md § 4.3 CURSOR_INPUT_TEXT](./AITUBER_PROTOCOL.md#43-命令控制cursor_input_text)

**注册新的客户端**:
→ [WEBSOCKET_PROTOCOL.md § 3.1 注册协议](./WEBSOCKET_PROTOCOL.md#31-连接和注册)

**多角色注册（一个客户端多个角色）**:
→ [MULTIROLE_GUIDE.md](../bridge/MULTIROLE_GUIDE.md)

**监听 Cursor Agent 状态变化**:
→ [WEBSOCKET_PROTOCOL.md § 3.3 事件通知](./WEBSOCKET_PROTOCOL.md#33-事件通知) (⚠️ 需要实现 Hook 监听)

**添加 TTS 语音**:
→ `bridge/tts_manager.py` + `handle_aituber_receive_text()`

---

## 🔧 开发建议

### 优先实现的功能

1. **Hook 端事件监听** (高优先级)
   - 监听 Cursor DOM 变化，检测 Agent 状态
   - 触发 `AGENT_STATUS_CHANGED`, `AGENT_COMPLETED` 事件

2. **AITuber 主动对话** (中优先级)
   - 实现 `AITUBER_SPEAK`
   - 允许 AITuber 主动发起对话

3. **完整的 Agent 操作** (低优先级)
   - 实现 `AGENT_EXECUTE_PROMPT` 等高层次语义操作
   - 提供更友好的 API

---

## 📞 问题反馈

- **协议设计问题**: 查看 `docs/WEBSOCKET_PROTOCOL.md`
- **AITuber 集成问题**: 查看 `docs/AITUBER_PROTOCOL.md`
- **代码实现问题**: 查看 `bridge/protocol.py` 和示例代码

---

*本文档由 Ortensia 项目维护*



