# 🤖 AI 协作索引

> **处理任何任务前，请先阅读本文档**
> 
> 目的：快速定位代码、理解协议、避免踩坑

---

## 📜 协议优先

> **协议是系统的核心**。在理解或修改任何功能前，必须先阅读相关协议。

### 核心协议

| 协议 | 位置 | 说明 |
|-----|------|------|
| **Ortensia 协议** | [`bridge/protocol.py`](../bridge/protocol.py) | 消息类型、Payload、MessageBuilder |
| **协议文档目录** | [`protocols/`](./protocols/) | 所有协议文档 |

### 消息类型速查

```python
# bridge/protocol.py - MessageType
REGISTER / REGISTER_ACK          # 客户端注册
HEARTBEAT / HEARTBEAT_ACK        # 心跳保活
GET_CONVERSATION_ID / _RESULT    # 对话发现
EXECUTE_JS / _RESULT             # JS 执行（Inject 唯一处理的消息）
AITUBER_RECEIVE_TEXT             # AITuber 接收文本
CURSOR_INPUT_TEXT / _RESULT      # Cursor 输入
AGENT_COMPLETED                  # Agent 完成
```

---

## 🗺️ 代码地图

### 前端 (aituber-kit/src)

| 职责 | 文件 | 关键代码 |
|-----|------|---------|
| WebSocket 客户端 | `utils/OrtensiaClient.ts` | `connect()`, `send()`, `subscribe()` |
| 消息管理（单例） | `utils/OrtensiaManager.ts` | `on()`, `dispatchMessage()` |
| 消息处理入口 | `pages/assistant.tsx:270` | `useEffect` 注册处理器 |
| 对话状态 | `features/stores/conversationStore.ts` | `getOrCreateConversation()` |

### 后端 (bridge)

| 职责 | 文件 | 关键代码 |
|-----|------|---------|
| WebSocket 服务器 | `websocket_server.py` | `handle_client()` |
| 消息分发 | `websocket_server.py:240` | `handle_new_protocol_message()` |
| 对话发现 | `websocket_server.py:560` | `handle_get_conversation_id()` |
| 消息路由 | `websocket_server.py:850` | `route_message()` |
| 协议定义 | `protocol.py` | `Message`, `MessageBuilder` |
| TTS 生成 | `tts_manager.py` | `TTSManager` |

### Cursor 注入

| 职责 | 文件 |
|-----|------|
| 安装脚本 | `cursor-injector/install-v10.sh` |
| Agent Hooks | `cursor-hooks/` |

---

## 🔑 核心设计原则

### 1. Inject 只执行 JS

```
❌ 发送 GET_CONVERSATION_ID 给 Inject
✅ 服务器生成 JS 代码，通过 EXECUTE_JS 发给 Inject
```

### 2. 服务器是消息中枢

```
AITuber ←→ 中央服务器 ←→ Inject
              ↑
            Hook
```

### 3. 单例防重复

使用 `OrtensiaManager` 单例 + `isSubscribed` 标记防止 React Strict Mode 重复订阅

---

## ⚠️ 已知陷阱

| 陷阱 | 表现 | 解决方案 | 位置 |
|-----|------|---------|-----|
| logging 配置顺序 | DEBUG 不显示 | `basicConfig()` 在任何 `logging.xxx()` 之前 | `websocket_server.py:20` |
| 消息类型未处理 | `未知消息类型: xxx` | 在 `handle_new_protocol_message()` 添加处理 | `websocket_server.py:240` |
| React 双重执行 | 日志出现两次 | 单例 + 幂等设计 | `OrtensiaManager.ts` |
| ID 不匹配 | 自动检查不触发 | 使用短 ID（前8字符）匹配 | `assistant.tsx:200` |
| Inject 不响应 | 消息发出无反应 | Inject 只处理 EXECUTE_JS | - |

---

## 📂 功能实现索引

| 功能 | 文档 | 核心代码 |
|-----|------|---------|
| 对话发现 | [`_FEATURES/conversation_discovery.md`](./_FEATURES/conversation_discovery.md) | `handle_get_conversation_id()` |
| 消息管理 | [`_DECISIONS/ADR-001`](./_DECISIONS/ADR-001-message-handling-architecture.md) | `OrtensiaManager` |
| 架构指南 | [`guides/AITUBER_ARCHITECTURE_GUIDE.md`](./guides/AITUBER_ARCHITECTURE_GUIDE.md) | - |
| 故障排查 | [`guides/TROUBLESHOOTING_INDEX.md`](./guides/TROUBLESHOOTING_INDEX.md) | - |

---

## 🔍 快速定位

### 按问题找代码

| 问题 | 代码位置 |
|-----|---------|
| WebSocket 连接失败 | `OrtensiaClient.ts:connect()` |
| 消息未收到 | `websocket_server.py:route_message()` |
| 消息处理多次 | `OrtensiaManager.ts:isSubscribed` |
| 对话发现失败 | `websocket_server.py:handle_get_conversation_id()` |
| 自动检查不触发 | `assistant.tsx:handleAgentCompleted()` |
| TTS 无声音 | `bridge/tts_manager.py` |

### 按消息类型找代码

| 消息类型 | 服务器处理 | 前端处理 |
|---------|-----------|---------|
| `register` | `handle_register()` | - |
| `get_conversation_id` | `handle_get_conversation_id()` | `discoverExistingConversations()` |
| `execute_js_result` | `handle_execute_js_result_for_discovery()` | - |
| `aituber_receive_text` | `handle_aituber_receive_text()` | `handleAituberReceiveText()` |
| `agent_completed` | `broadcast_event()` | `handleAgentCompleted()` |
| `cursor_input_text` | `handle_cursor_input_text()` | `sendCursorInputText()` |

---

## 📝 维护指南

### 添加新消息类型

1. `bridge/protocol.py` - 添加 `MessageType` 枚举
2. `bridge/protocol.py` - 创建 `Payload` dataclass
3. `bridge/protocol.py` - `MessageBuilder` 添加方法
4. `bridge/websocket_server.py` - `handle_new_protocol_message()` 添加处理
5. **更新本文档的消息类型速查表**

### 添加新功能

1. 创建 `_FEATURES/功能名.md`（使用模板）
2. 更新本文档的"功能实现索引"

---

## 📂 目录结构

```
docs/
├── AI_INDEX.md          # 本文件
├── protocols/           # 📜 协议文档
├── _FEATURES/           # 📦 功能实现
├── _DECISIONS/          # 🎯 架构决策
├── guides/              # 📖 使用指南
└── archive/             # 📁 归档文档
```

---

**最后更新**: 2025-12-21
