# Ortensia WebSocket 协议使用指南

本文档介绍如何使用 Ortensia WebSocket 消息协议在各组件之间进行通信。

---

## 📚 相关文档

- **协议规范**: `WEBSOCKET_PROTOCOL.md` - 完整的消息格式定义
- **Python 实现**: `../bridge/protocol.py` - Python 数据类和消息构建器
- **示例代码**: `../examples/command_client_example.py` - Command Client 示例

---

## 🏗️ 系统组件

### 1. 中央 Server (待实现)
- **位置**: `bridge/websocket_server.py`
- **职责**: 消息路由、注册管理、事件广播
- **端口**: 8765 (默认)

### 2. Cursor Hook
- **位置**: `cursor-injector/install-v8.sh`
- **职责**: 
  - 本地 WebSocket Server (端口 9876) - 开发调试
  - 作为 Client 连接到中央Server - 生产环境
  - 执行 Composer 命令
  - 监听并发送事件

### 3. Command Client
- **示例**: `examples/command_client_example.py`
- **职责**:
  - 接收事件通知
  - 决策逻辑
  - 发送命令

### 4. AITuber Client (现有)
- **位置**: `aituber/`
- **职责**: 界面展示、语音合成

---

## 🚀 快速开始

### 步骤 1: 安装 Cursor Hook (V8版本)

```bash
cd cursor-injector
./install-v8.sh
```

**V8 新功能**:
- ✅ 保留本地 WebSocket Server (端口 9876)
- ✅ 支持连接到中央Server (通过环境变量配置)
- ✅ 实现 Composer 操作命令
- ✅ 自动注册和心跳机制
- ✅ 自动重连（指数退避）

### 步骤 2: 配置环境

**开发模式**（仅本地）:
```bash
# 无需设置环境变量
# Cursor 启动后只会启动本地 WebSocket Server
```

**生产模式**（连接中央Server）:
```bash
export ORTENSIA_SERVER=ws://localhost:8765
# 或者远程Server
export ORTENSIA_SERVER=ws://192.168.1.100:8765
```

### 步骤 3: 重启 Cursor

```bash
# 完全退出 Cursor (Cmd+Q)
# 然后重新启动

# 等待 10 秒，查看日志
cat /tmp/cursor_ortensia.log
```

**预期日志输出**:

```
[2025-11-03T16:00:00.000Z] [PID:12345] 🎉 Ortensia V8 启动中...
[2025-11-03T16:00:03.000Z] [PID:12345] ✅ WebSocket 模块加载成功
[2025-11-03T16:00:03.100Z] [PID:12345] ══════════════════════════════
[2025-11-03T16:00:03.100Z] [PID:12345]   ✅ 本地 WebSocket Server 启动成功！
[2025-11-03T16:00:03.100Z] [PID:12345]   📍 端口: 9876
[2025-11-03T16:00:03.100Z] [PID:12345] ══════════════════════════════
[2025-11-03T16:00:03.200Z] [PID:12345] 🔗 [中央] 尝试连接到 ws://localhost:8765...
[2025-11-03T16:00:03.300Z] [PID:12345] ✅ 已连接到中央Server！
[2025-11-03T16:00:03.300Z] [PID:12345]   🔑 Cursor ID: cursor-abc123
```

### 步骤 4: (待实现) 启动中央 Server

```bash
# TODO: 实现中央Server
cd bridge
python3 websocket_server.py
```

### 步骤 5: 运行示例 Command Client

```bash
cd examples
python3 command_client_example.py
```

---

## 💻 开发指南

### 使用 Python 协议库

```python
from bridge.protocol import (
    MessageBuilder,
    MessageType,
    AgentStatus,
    ClientType,
    Platform
)

# 创建注册消息
msg = MessageBuilder.register(
    from_id="cursor-abc123",
    client_type=ClientType.CURSOR_HOOK,
    platform=Platform.DARWIN,
    pid=12345,
    workspace="/path/to/project",
    ws_port=9876,
    capabilities=["composer", "editor"]
)

# 发送消息
await websocket.send(msg.to_json())

# 接收并解析消息
message_str = await websocket.recv()
message = Message.from_json(message_str)
```

### 实现自定义 Command Client

参考 `examples/command_client_example.py`，实现以下方法：

1. **connect()** - 连接到中央Server
2. **register()** - 注册为 Command Client
3. **listen()** - 监听消息
4. **handle_message()** - 处理不同类型的消息
5. **send_prompt()** - 发送提示词到 Cursor
6. **query_status()** - 查询 Agent 状态

---

## 📨 常用消息示例

### 1. 发送提示词

```python
msg = MessageBuilder.composer_send_prompt(
    from_id="cc-001",
    to_id="cursor-abc123",
    agent_id="default",
    prompt="写一个快速排序的 Python 实现"
)

await ws.send(msg.to_json())
```

### 2. 查询 Agent 状态

```python
msg = MessageBuilder.composer_query_status(
    from_id="cc-001",
    to_id="cursor-abc123",
    agent_id="default"
)

await ws.send(msg.to_json())
```

### 3. 监听 Agent 完成事件

```python
async for message_str in ws:
    message = Message.from_json(message_str)
    
    if message.type == MessageType.AGENT_COMPLETED:
        payload = message.payload
        print(f"任务完成: {payload['result']}")
        print(f"修改的文件: {payload['files_modified']}")
```

---

## 🧪 测试

### 测试 1: 本地模式（不连接中央Server）

```bash
# 1. 安装 V8
cd cursor-injector
./install-v8.sh

# 2. 不设置 ORTENSIA_SERVER，重启 Cursor

# 3. 测试本地连接
python3 test-input-complete.py "测试文字"
```

**预期结果**: ✅ 输入框成功显示文字

### 测试 2: 生产模式（连接中央Server）

```bash
# 1. 设置环境变量
export ORTENSIA_SERVER=ws://localhost:8765

# 2. 启动中央Server (待实现)
# python3 bridge/websocket_server.py

# 3. 重启 Cursor

# 4. 查看日志
cat /tmp/cursor_ortensia.log
```

**预期日志**: 看到 "✅ 已连接到中央Server" 和注册成功

### 测试 3: 完整流程

```bash
# 1. 启动中央Server
# python3 bridge/websocket_server.py

# 2. 启动 Cursor (已设置 ORTENSIA_SERVER)

# 3. 运行 Command Client 示例
python3 examples/command_client_example.py
```

**预期行为**:
1. Command Client 连接并注册
2. 检测到 Cursor 实例
3. 自动发送测试提示词
4. 接收并显示事件通知

---

## 🔧 故障排除

### 问题 1: Cursor Hook 无法连接到中央Server

**检查项**:
1. 环境变量是否设置: `echo $ORTENSIA_SERVER`
2. 中央Server 是否运行: `lsof -i :8765`
3. 网络是否可达: `ping server-ip`
4. 查看日志: `cat /tmp/cursor_ortensia.log`

**常见错误**:
- `Connection refused` - Server 未启动
- `Connection timeout` - 网络不通或防火墙阻止
- `401 Unauthorized` - 认证失败（未来版本）

### 问题 2: 消息发送失败

**检查项**:
1. WebSocket 连接状态
2. 目标 Client 是否已注册
3. 消息格式是否正确

**调试方法**:
```python
# 打印消息 JSON
print(msg.to_json())

# 检查 payload
print(msg.payload)
```

### 问题 3: Cursor 未执行命令

**可能原因**:
1. 输入框 DOM 结构变化（Cursor 版本更新）
2. JavaScript 执行失败
3. 权限不足

**调试步骤**:
1. 查看 Cursor DevTools Console 错误
2. 手动测试: `python3 test-input-complete.py "test"`
3. 检查日志中的错误信息

---

## 📊 性能考虑

### 消息频率

- **心跳**: 每 30 秒
- **状态查询**: 按需，不超过每秒 1 次
- **事件通知**: 实时发送

### 连接管理

- **心跳超时**: 60 秒标记离线，120 秒断开
- **重连策略**: 指数退避，最大延迟 60 秒
- **消息队列**: 建议在 Client 端实现队列机制

### 资源占用

- **内存**: Cursor Hook ~10MB 额外内存
- **CPU**: 空闲时 ~0%，执行命令时短暂峰值
- **网络**: 心跳 ~100 bytes/30s，消息 ~1KB/条

---

## 🔐 安全建议

### 当前版本 (V1.0)

- ✅ 仅支持 localhost 连接
- ⚠️ 无认证机制
- ⚠️ 无加密传输

### 未来版本

计划添加:
1. **认证**: Token 或证书
2. **加密**: WSS (WebSocket Secure)
3. **授权**: 基于角色的权限控制
4. **审计**: 记录所有命令执行

### 生产环境建议

1. 使用 VPN 或内网
2. 配置防火墙规则
3. 定期更新依赖
4. 监控异常连接

---

## 📈 扩展开发

### 添加新的消息类型

1. 在 `docs/WEBSOCKET_PROTOCOL.md` 中定义消息格式
2. 在 `bridge/protocol.py` 中添加枚举和 Payload 类
3. 在 `MessageBuilder` 中添加构建方法
4. 在各 Client 中实现处理逻辑

### 添加新的 Cursor 操作

1. 在 Cursor Hook 的 `handleCommand()` 中添加新的 case
2. 实现具体的操作逻辑（DOM 操作、API 调用等）
3. 返回结果消息
4. 更新协议文档

### 实现多 Agent 支持

当前 `agent_id` 字段已预留：

```python
payload = {
    "agent_id": "agent-001",  # 不再只是 "default"
    "agent_name": "Code Generator",
    "agent_role": "code_writer"
}
```

---

## 📞 支持

- **协议问题**: 查看 `docs/WEBSOCKET_PROTOCOL.md`
- **代码问题**: 查看 `bridge/protocol.py` 和示例
- **Bug 报告**: 创建 Issue

---

*最后更新: 2025-11-03*

