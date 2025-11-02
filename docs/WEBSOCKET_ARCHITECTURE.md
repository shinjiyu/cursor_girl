# WebSocket 架构说明

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  ┌───────────────┐              ┌─────────────────┐             │
│  │  测试脚本      │              │  WebSocket      │             │
│  │test_emotions.py│◄────────────►│  Server         │             │
│  │               │  WebSocket   │  (Port 8000)    │             │
│  │ (客户端 A)     │  Client      │                 │             │
│  └───────────────┘              └────────┬────────┘             │
│                                           │                       │
│                                           │ 广播                  │
│                                           │                       │
│  ┌───────────────┐                       │                       │
│  │  Electron     │◄──────────────────────┘                       │
│  │  オルテンシア │  WebSocket                                    │
│  │  assistant.tsx│  (useExternalLinkage)                        │
│  │               │                                                │
│  │ (客户端 B)     │                                                │
│  └───────────────┘                                                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 消息流程

### 1️⃣ 启动阶段

```bash
# Terminal 1: 启动 WebSocket Server
cd bridge
python websocket_server.py

# Terminal 2: 启动 Electron (包含 Next.js dev server)
cd aituber-kit
npm run assistant:dev
```

**结果**：
- ✅ WebSocket Server 监听 `ws://localhost:8000/ws`
- ✅ Electron 自动连接到 Server（因为 `externalLinkageMode: true`）
- ✅ Server 日志显示：`✅ Client connected ... 👥 Total connected clients: 1`

### 2️⃣ 测试阶段

```bash
# Terminal 3: 运行测试脚本
cd bridge
source venv/bin/activate
python test_emotions.py
# 或
python cursor_event.py celebration
```

**消息流向**：

```
测试脚本
  ↓ 调用
cursor_event.handle_event('celebration')
  ↓ 创建
WebSocketClient (新连接到 Server)
  ↓ 发送 JSON
{"text": "太棒了！", "emotion": "happy", "type": "celebration"}
  ↓ 到达
WebSocket Server (8000)
  ↓ 接收消息
handle_client() 函数
  ↓ 调用
broadcast_to_aituber(message, exclude=发送者)
  ↓ 广播给
Electron (客户端 B)
  ↓ 接收
useExternalLinkage → handleReceiveTextFromWs
  ↓ 显示
オルテンシア表情变化 + 语音 + 文字 ✨
```

### 3️⃣ Server 日志示例

```
[21:19:20] INFO: ✅ Client connected from ('::1', 55664, 0, 0), path: /ws
[21:19:20] INFO: 👥 Total connected clients: 1                    ← Electron 连接

[21:19:53] INFO: ✅ Client connected from ('::1', 55682, 0, 0), path: /ws
[21:19:53] INFO: 👥 Total connected clients: 2                    ← 测试脚本连接

[21:19:53] INFO: 📨 Received message: {'text': '保存成功~', ...}  ← Server 收到
[21:19:53] INFO: 📤 Broadcast to 1/1 clients                      ← 广播给 Electron

[21:19:53] INFO: 👋 Client disconnected, remaining: 1             ← 测试脚本断开
```

## 🎯 关键点

### ✅ 正确的理解

1. **WebSocket Server** 可以同时接受**多个客户端连接**
2. **测试脚本**每次运行时：
   - 连接到 Server（成为客户端 2）
   - 发送消息
   - 断开连接
3. **Electron** 持续连接（客户端 1），接收广播的消息
4. **Server** 收到消息后，会广播给**除了发送者之外**的所有客户端

### ⚙️ 必需的配置

1. **Electron 端** (`assistant.tsx`)：
   ```typescript
   settingsStore.setState({ externalLinkageMode: true })
   ```
   ✅ 已自动配置

2. **WebSocket 地址** (`useExternalLinkage.tsx:81`)：
   ```typescript
   return new WebSocket('ws://localhost:8000/ws')
   ```
   ✅ 与 Server 地址一致

3. **测试脚本** (`websocket_client.py:25`)：
   ```python
   def __init__(self, uri: str = 'ws://localhost:8000/ws'):
   ```
   ✅ 与 Server 地址一致

## 🧪 测试方法

### 快速测试单个事件

```bash
cd bridge
source venv/bin/activate
python cursor_event.py celebration
python cursor_event.py git_commit --files=5
python cursor_event.py syntax_error --error="undefined variable"
```

### 运行完整测试套件

```bash
cd bridge
./run_tests.sh
# 或
python test_emotions.py
```

### 交互式测试

```bash
cd bridge
python test_single_events.py
```

## 📝 可用的事件类型

查看 `bridge/config/emotion_rules.yaml`，包含 36 种事件：

- **文件操作**: `file_save`, `file_create`, `file_delete`
- **Git 操作**: `git_commit`, `git_push`, `git_merge`
- **AI 工作**: `ai_start`, `ai_complete`, `ai_thinking`
- **错误**: `syntax_error`, `build_error`, `critical_error`
- **测试**: `test_pass`, `test_fail`, `test_start`
- **调试**: `debug_start`, `bug_found`, `bug_fixed`
- **性能**: `performance_slow`, `performance_improved`
- **特殊**: `celebration`, `work_start`, `work_end`

## 🔧 故障排查

### 问题 1: Electron 没有连接

**症状**: Server 日志只显示 0 或 1 个客户端

**解决**:
1. 确认 Electron 窗口已打开
2. 检查浏览器控制台（DevTools）
3. 确认 `externalLinkageMode` 已开启

### 问题 2: 消息没有广播

**症状**: Server 收到消息，但显示 "No AITuber clients to broadcast to"

**原因**: 只有测试脚本连接，没有 Electron 连接

**解决**: 见问题 1

### 问题 3: Server 连接失败

**症状**: `Connection refused`

**解决**:
```bash
# 检查 Server 是否运行
lsof -i :8000

# 重启 Server
pkill -f websocket_server.py
cd bridge
python websocket_server.py > /tmp/ortensia-websocket.log 2>&1 &
```

## 🚀 一键启动

```bash
# 使用启动脚本
./START_ALL.sh

# 或手动启动
cd bridge && python websocket_server.py &
cd aituber-kit && npm run assistant:dev
```

## 📊 系统状态检查

```bash
# 检查端口
lsof -i :3000  # Next.js
lsof -i :8000  # WebSocket Server

# 检查进程
ps aux | grep electron
ps aux | grep "python.*websocket_server"

# 查看日志
tail -f /tmp/ortensia-websocket.log
```

---

## 💡 总结

这个架构的核心是：

1. **WebSocket Server** 作为**中心枢纽**
2. **Electron** 作为**长连接客户端**，持续监听
3. **测试脚本**作为**临时客户端**，发送事件后断开
4. Server 收到消息后，**广播给所有其他客户端**（排除发送者）

这样的设计使得：
- ✅ 测试脚本与 Electron 解耦
- ✅ 可以有多个消息源（未来可以添加真正的 Cursor Hooks）
- ✅ Server 可以记录、过滤、转发消息
- ✅ 易于扩展（添加更多客户端）

