# Ortensia WebSocket 协议 - 快速开始

**版本**: 1.0  
**最后更新**: 2025-11-03

---

## 🚀 3 分钟快速开始

### 方式 1: 本地开发模式（最简单）

适合：快速测试、开发调试

```bash
# 1. 安装 Cursor Hook V8
cd "/Users/user/Documents/ cursorgirl/cursor-injector"
./install-v8.sh

# 2. 重启 Cursor（Cmd+Q 完全退出，然后重新打开）

# 3. 测试输入
python3 test-input-complete.py "Hello Ortensia! 🌸"
```

**预期结果**: Cursor AI 聊天输入框显示 "Hello Ortensia! 🌸"

---

### 方式 2: 完整系统模式

适合：生产环境、多客户端协同

#### 步骤 1: 启动中央 Server

**终端 1**:
```bash
cd "/Users/user/Documents/ cursorgirl/bridge"
python3 websocket_server.py
```

#### 步骤 2: 测试 Server

**终端 2**:
```bash
cd "/Users/user/Documents/ cursorgirl/bridge"
python3 test_server.py
```

**预期**: 看到 "✅ 所有测试通过！"

#### 步骤 3: 连接 Cursor

**终端 3**:
```bash
# 设置环境变量
export ORTENSIA_SERVER=ws://localhost:8765

# 重启 Cursor（确保环境变量生效）
# 等待 10 秒

# 查看日志
cat /tmp/cursor_ortensia.log
```

**预期日志**: 看到 "✅ 已连接到中央Server"

#### 步骤 4: 运行 Command Client

**终端 4**:
```bash
cd "/Users/user/Documents/ cursorgirl/examples"
python3 command_client_example.py
```

**预期结果**: 
- Command Client 成功连接
- 找到 Cursor 实例
- 提示词成功发送
- Cursor 输入框显示提示词

---

## 📖 文档导航

| 文档 | 用途 | 适合人群 |
|------|------|----------|
| `QUICK_START.md` (本文档) | 快速上手 | 所有人 |
| `docs/PROTOCOL_USAGE_GUIDE.md` | 协议使用 | 开发者 |
| `docs/END_TO_END_TESTING_GUIDE.md` | 完整测试 | 测试人员 |
| `docs/WEBSOCKET_PROTOCOL.md` | 协议规范 | 架构师 |
| `PROJECT_COMPLETION_SUMMARY.md` | 项目总结 | 管理者 |

---

## 🔧 常见问题

### Q: Server 启动失败 "Address already in use"

**A**: 端口被占用，终止占用进程：
```bash
lsof -i :8765
kill -9 <PID>
```

### Q: Cursor 无法连接到 Server

**A**: 检查环境变量：
```bash
echo $ORTENSIA_SERVER  # 应显示 ws://localhost:8765
```

如果没有，重新设置并重启 Cursor：
```bash
export ORTENSIA_SERVER=ws://localhost:8765
# Cmd+Q 完全退出 Cursor，然后重新打开
```

### Q: 提示词没有出现在 Cursor 输入框

**A**: 
1. 检查 Server 日志，确认消息路由成功
2. 查看 Cursor 日志：`cat /tmp/cursor_ortensia.log`
3. 确认 Cursor ID 正确（在 Server 和 Client 日志中）

### Q: 想切换回本地模式

**A**: 取消环境变量并重启 Cursor：
```bash
unset ORTENSIA_SERVER
# 重启 Cursor
```

---

## 📊 系统架构（一图看懂）

```
┌─────────────────────────────────────────┐
│    中央 Server (port 8765)              │
│    bridge/websocket_server.py           │
│                                         │
│  • 客户端注册管理                        │
│  • 消息路由                              │
│  • 事件广播                              │
│  • 心跳检测                              │
└──────┬──────────────┬──────────────┬───┘
       │              │              │
       v              v              v
   ┌──────┐      ┌──────┐      ┌──────┐
   │Cursor│      │ CC   │      │AITuber│
   │ Hook │      │Client│      │Client│
   └──┬───┘      └──────┘      └──────┘
      │
      v
   ┌──────┐
   │Cursor│
   │  UI  │
   └──────┘
```

**CC** = Command Client（发送自动化命令）

---

## 💡 核心概念

### 双重角色设计

Cursor Hook V8 同时扮演两个角色：

1. **本地 WebSocket Server (端口 9876)**
   - 用途：开发调试
   - 特点：无需中央 Server
   - 使用：直接用 Python 脚本连接

2. **中央 Server 客户端**
   - 用途：生产环境
   - 特点：通过 Server 协调多客户端
   - 使用：设置 `ORTENSIA_SERVER` 环境变量

**自动切换**: 根据环境变量自动选择模式，无需修改代码

### 即时响应 + 事件驱动

```
Command Client  ─[发送命令]→  Server  ─[路由]→  Cursor Hook
                 ↓
                返回成功/失败（即时）

Cursor Hook  ─[任务开始]→  Server  ─[广播]→  所有客户端
             ─[任务完成]→  Server  ─[广播]→  所有客户端
```

**优势**: 不阻塞，支持长任务，易于实现状态机

---

## 🎯 下一步

完成快速开始后：

1. ✅ 阅读 `docs/PROTOCOL_USAGE_GUIDE.md` 了解协议详情
2. ✅ 参考 `examples/command_client_example.py` 开发自己的客户端
3. ✅ 查看 `docs/END_TO_END_TESTING_GUIDE.md` 进行完整测试
4. ✅ 集成到 Ortensia 主系统

---

## 📞 获取帮助

- **协议规范**: `docs/WEBSOCKET_PROTOCOL.md`
- **使用指南**: `docs/PROTOCOL_USAGE_GUIDE.md`
- **测试指南**: `docs/END_TO_END_TESTING_GUIDE.md`
- **项目总结**: `PROJECT_COMPLETION_SUMMARY.md`

---

*祝你使用愉快！🌸*

