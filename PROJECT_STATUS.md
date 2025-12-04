# Ortensia 项目状态

**更新时间**: 2025-11-22  
**当前版本**: v2.0 (Multi-Role Support)

---

## 🎯 项目概述

Ortensia 是一个 Cursor AI Agent 与 AITuber 的集成系统，通过中央 WebSocket 服务器连接 Cursor、Agent Hooks 和 AITuber 客户端。

---

## ✅ 已完成功能

### 1. V10 Inject-Hook 协同机制

**问题背景**：
- 多个 Cursor 实例无法区分
- Hook 不是短连接
- 同一对话的多次 Hook 使用不同 ID
- Workspace 映射不可靠

**V10 解决方案**：
- ✅ **Inject ID**: `inject-{pid}` (基于进程 ID，长连接)
- ✅ **Hook ID**: `hook-{conversation_id}` (基于对话 ID，短连接)
- ✅ **Server 映射**: `conversation_id ↔ inject_id` (首次查询，后续缓存)
- ✅ **自动发现**: Server 向 inject 查询 `conversation_id`，建立关联

**验证状态**: ✅ 完成并通过测试

**相关文件**:
- `bridge/websocket_server.py` - V10 映射机制
- `bridge/protocol.py` - 新增 `GET_CONVERSATION_ID` 消息类型
- `cursor-injector/install-v10.sh` - 支持 conversation_id 查询
- `cursor-hooks/lib/agent_hook_handler.py` - Hook ID 使用 conversation_id

### 2. Conversation ID 探索与切换

**完成内容**：
- ✅ 从 DOM 提取 `conversation_id`（`composer-bottom-add-context-{UUID}`）
- ✅ 探索聊天历史面板结构
- ✅ 实现对话切换功能（打开历史面板 → 点击对话项）
- ✅ 验证前后切换功能

**相关文件**:
- `cursor-injector/get_conversation_id_correct.py` - 正确提取 conversation_id
- `cursor-injector/final_switch_conversation.py` - 对话切换实现
- `cursor-injector/demo_switch_back_and_forth.py` - 双向切换演示
- `CONVERSATION_COMPREHENSIVE_GUIDE.md` - 完整指南

### 3. 多角色客户端支持 (v2.0)

**新功能**：
- ✅ 一个客户端可以同时拥有多个角色
- ✅ 向后兼容旧的单角色协议
- ✅ 动态添加角色（重复注册）
- ✅ 按角色查询客户端

**协议支持**：
```json
// 旧协议（单角色）
{"payload": {"client_type": "aituber_client"}}

// 新协议（多角色）
{"payload": {"client_types": ["aituber_client", "command_client"]}}
```

**测试状态**: ✅ 全部通过（`test_multirole.py`）

**相关文件**:
- `bridge/websocket_server.py` - 多角色实现
- `bridge/protocol.py` - 更新协议支持 client_types
- `bridge/test_multirole.py` - 测试脚本
- `bridge/MULTIROLE_GUIDE.md` - 使用指南

---

## 🏗️ 系统架构

```
┌─────────────────┐
│   Cursor IDE    │
│                 │
│ ┌─────────────┐ │    WebSocket (长连接)
│ │  inject.js  │ ├───────────────────────┐
│ │ inject-{pid}│ │                       │
│ └─────────────┘ │                       │
│                 │                       ▼
│ ┌─────────────┐ │    WebSocket       ┌──────────────────┐
│ │   Hook.py   │ ├──(短连接)─────────►│  Central Server  │
│ │hook-{conv_id}│ │                    │   ws://8765      │
│ └─────────────┘ │                    │                  │
└─────────────────┘                    │  ┌────────────┐  │
                                       │  │  Registry  │  │
                                       │  │  Mapping   │  │
                                       │  └────────────┘  │
                                       └──────┬───────────┘
                                              │
                                              │ WebSocket
                                              ▼
                                       ┌──────────────┐
                                       │   AITuber    │
                                       │   Client     │
                                       └──────────────┘
```

### 数据流

1. **Inject 启动**:
   - Inject 连接到 Server: `inject-{pid}`
   - 建立长连接，定期心跳

2. **Hook 触发**:
   - Hook 连接: `hook-{conversation_id}`
   - 发送事件消息给 `aituber`
   - Server 提取 `conversation_id`

3. **映射建立**:
   - Server 向所有 inject 查询: "谁有这个 conversation_id?"
   - Inject 返回结果
   - Server 缓存: `conversation_id ↔ inject_id`

4. **后续消息**:
   - Server 使用缓存映射，直接转发
   - Hook 发完立即断开（短连接）

---

## 📊 当前运行状态

### 服务器
- **状态**: 🟢 运行中
- **地址**: `ws://localhost:8765`
- **版本**: v2.0 (Multi-Role Support)
- **日志**: `/tmp/ortensia_multirole.log`

### 客户端
- **Inject**: 🟢 已连接 (`inject-32660`)
- **Hooks**: 🟢 工作正常（短连接）
- **AITuber**: 🔴 未运行（可选）

### 验证结果
```
[19:36:11] ✅ [test-single-role] 注册成功，角色: [aituber_client]
[19:36:11] ✅ [test-multi-role] 注册成功，角色: [aituber_client, command_client]
[19:36:13] ✅ [test-add-role] 动态添加角色成功
```

---

## 📁 项目结构

```
.
├── bridge/
│   ├── websocket_server.py      # 中央服务器（v2.0 多角色）
│   ├── protocol.py               # 协议定义
│   ├── test_multirole.py        # 多角色测试
│   └── MULTIROLE_GUIDE.md       # 多角色指南
│
├── cursor-injector/
│   ├── install-v10.sh           # V10 注入脚本
│   ├── get_conversation_id_correct.py
│   ├── final_switch_conversation.py
│   └── CONVERSATION_COMPREHENSIVE_GUIDE.md
│
├── cursor-hooks/
│   ├── hooks.json               # Hook 配置
│   ├── lib/
│   │   └── agent_hook_handler.py  # Hook 基类（V10）
│   └── hooks/
│       ├── afterShellExecution.py
│       ├── afterFileEdit.py
│       └── ...
│
└── PROJECT_STATUS.md  # 本文件
```

---

## 🔍 关键文件说明

### Bridge (中央服务器)

| 文件 | 说明 |
|------|------|
| `websocket_server.py` | 中央服务器主程序，支持 V10 映射和多角色 |
| `protocol.py` | 消息协议定义，包含所有消息类型和构建器 |
| `test_multirole.py` | 多角色功能测试脚本 |

### Cursor Injector

| 文件 | 说明 |
|------|------|
| `install-v10.sh` | 注入脚本，支持 conversation_id 查询 |
| `get_conversation_id_correct.py` | 从 DOM 提取 conversation_id |
| `final_switch_conversation.py` | 对话切换实现 |

### Cursor Hooks

| 文件 | 说明 |
|------|------|
| `agent_hook_handler.py` | Hook 基类，V10 版本使用 conversation_id |
| `afterShellExecution.py` | 命令执行后触发 |
| `afterFileEdit.py` | 文件编辑后触发 |

---

## 🚀 快速开始

### 1. 启动服务器

```bash
cd bridge
python3 websocket_server.py
```

### 2. 安装 Inject（如果还没有）

```bash
cd cursor-injector
./install-v10.sh
```

### 3. 重启 Cursor

```bash
killall Cursor && open -a Cursor
```

### 4. 验证

```bash
# 查看服务器日志
tail -f /tmp/ortensia_multirole.log

# 应该看到：
# ✅ [inject-xxxxx] 注册成功，角色: [cursor_inject]
# ✅ [hook-{conversation_id}] 注册成功，角色: [agent_hook]
```

---

## 📝 AITuber 消息说明

### 消息来源

Hook 在以下事件发生时会发送 `aituber_receive_text` 消息：

| Hook 事件 | 触发时机 |
|-----------|----------|
| `afterShellExecution` | 命令执行后 |
| `afterFileEdit` | 文件编辑后 |
| `afterMCPExecution` | MCP 工具执行后 |
| `afterAgentResponse` | Agent 响应后 |
| `stop` | Agent 停止时 |

### 消息格式

```json
{
  "type": "aituber_receive_text",
  "from": "hook-{conversation_id}",
  "to": "aituber",
  "payload": {
    "text": "命令完成：tail -50 /tmp/log",
    "emotion": "happy",
    "source": "hook",
    "hook_name": "afterShellExecution",
    "workspace": "/path/to/project",
    "conversation_id": "uuid"
  }
}
```

### 为什么显示"aituber 不在线"？

这是正常的。Hook 会发送消息给 `aituber` 客户端，但如果 AITuber 没有运行，服务器会记录警告。这不影响 Hook 功能，只是通知功能暂时不可用。

---

## 🐛 故障排查

### Inject 没有连接

```bash
# 1. 检查 Cursor 是否使用了修改后的 main.js
ls -la /Applications/Cursor.app/Contents/Resources/app/out/vs/code/electron-main/main.js

# 2. 重新安装 inject
cd cursor-injector
./install-v10.sh

# 3. 完全重启 Cursor
killall Cursor && sleep 2 && open -a Cursor
```

### Hook 没有触发

```bash
# 1. 检查 hooks.json 是否存在
cat ~/Library/Application\ Support/Cursor/User/globalStorage/cursor-agent/hooks.json

# 2. 检查 Hook 脚本是否可执行
ls -la ~/.cursor-agent/hooks/

# 3. 查看 Hook 日志
tail -f /tmp/ortensia_multirole.log | grep hook
```

### 服务器端口被占用

```bash
# 1. 找到占用端口的进程
lsof -i :8765

# 2. 杀掉旧进程
pkill -f websocket_server.py

# 3. 重启服务器
cd bridge && python3 websocket_server.py
```

---

## 📚 相关文档

- `bridge/MULTIROLE_GUIDE.md` - 多角色客户端使用指南
- `cursor-injector/CONVERSATION_COMPREHENSIVE_GUIDE.md` - Conversation ID 完整指南
- `V10_IMPLEMENTATION_SUMMARY.md` - V10 实现总结
- `CONVERSATION_ID_PROTOCOL.md` - Conversation ID 协议文档

---

## 🎓 下一步

### 可能的改进方向

1. **消息缓存机制**：当 inject 还没响应时，缓存 hook 消息
2. **健康检查**：定期检查映射的有效性
3. **多 Cursor 支持**：完整测试多个 Cursor 实例场景
4. **AITuber 客户端**：实现一个完整的 AITuber 客户端
5. **Web Dashboard**：可视化客户端连接和消息流

---

## 📞 技术支持

如有问题，请查看：
1. 服务器日志：`tail -f /tmp/ortensia_multirole.log`
2. Hook 日志：内联在服务器日志中
3. Cursor 控制台：Cmd+Shift+I → Console

---

**状态**: ✅ V10 + 多角色支持已完成并验证  
**最后测试**: 2025-11-22 19:36  
**测试结果**: 全部通过 ✅

