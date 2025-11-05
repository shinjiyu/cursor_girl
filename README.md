# 🌸 Ortensia - Cursor AI 远程控制系统

> **通过 WebSocket 远程控制 Cursor AI IDE，实现自动化 AI 编程工作流**

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)](./PROJECT_STATUS.md)
[![Version](https://img.shields.io/badge/version-V9-blue)](./QUICK_START_V9.md)
[![License](https://img.shields.io/badge/license-MIT-orange)](./LICENSE)

---

## ✨ 特性

- 🎯 **远程控制** - 通过 WebSocket 控制 Cursor Composer
- 🏗️ **中央服务器** - 支持多客户端连接和消息路由
- 🔧 **完整 DOM 操作** - 输入文字、点击按钮、检测状态
- 💬 **语义化命令** - 高级封装，简单易用
- 🔄 **自动重连** - 断线自动恢复，心跳保持连接
- 📦 **开箱即用** - 一键安装，快速上手

---

## 🚀 快速开始

### 方法 1: 一键启动（推荐）⭐

```bash
./scripts/START_ALL.sh
```

然后启动 Cursor，运行测试：
```bash
cd tests
python3 quick_test_central.py
```

### 方法 2: 手动启动

#### 1. 安装 Cursor Hook

```bash
cd cursor-injector
./install-v9.sh
```

#### 2. 启动中央服务器

```bash
cd bridge
python3 websocket_server.py &
```

#### 3. 启动 Cursor

正常启动 Cursor，Hook 会自动连接到中央服务器。

#### 4. 发送测试命令

```bash
cd tests
python3 quick_test_central.py
```

✅ **成功！** 你会看到 Cursor Composer 收到命令并开始执行。

> 💡 **提示**: 查看 [QUICK_START.md](./QUICK_START.md) 了解详细步骤和故障排除。

---

## 📖 文档

> 📚 **完整文档索引**: [DOCS_INDEX.md](./DOCS_INDEX.md)

### 快速开始
- [📘 快速入门](./QUICK_START.md) - 5 分钟快速上手 ⭐
- [📊 项目状态](./docs/PROJECT_STATUS.md) - 完整功能清单和架构说明

### 技术文档
- [📡 WebSocket 协议](./docs/WEBSOCKET_PROTOCOL.md) - 完整协议规范
- [🏗️ 系统架构](./docs/WEBSOCKET_ARCHITECTURE.md) - 架构设计说明
- [🛠️ 底层实现](./docs/BOTTOM_UP_IMPLEMENTATION.md) - DOM 操作详解
- [🔧 脚本使用](./docs/SCRIPTS_INDEX.md) - 所有脚本说明

### 测试报告
查看 [reports/](./reports/) 目录获取所有测试报告

---

## 🏗️ 系统架构

```
┌──────────────────┐
│ Command Clients  │  发送控制命令
└────────┬─────────┘
         │ WebSocket (Port 8765)
         ↓
┌──────────────────┐
│ Central Server   │  路由消息
│  websocket_      │  管理客户端
│  server.py       │
└────────┬─────────┘
         │ WebSocket
         ↓
┌──────────────────┐
│  Cursor Hook     │  接收命令
│  (Injected JS)   │  执行 DOM 操作
└────────┬─────────┘
         │ executeJavaScript
         ↓
┌──────────────────┐
│ Cursor Composer  │  实际 UI 交互
└──────────────────┘
```

---

## 💻 使用示例

### Python 客户端

```python
import asyncio
import websockets
import json
import time

async def send_prompt_to_cursor(prompt):
    """发送提示词到 Cursor"""
    async with websockets.connect('ws://localhost:8765') as ws:
        # 1. 注册客户端
        await ws.send(json.dumps({
            "type": "register",
            "from": "my-client-001",
            "to": "server",
            "timestamp": int(time.time()),
            "payload": {"client_type": "command_client"}
        }))
        
        response = await ws.recv()
        print(f"✅ 注册成功: {response}")
        
        # 2. 发送命令（需要知道 Cursor Hook ID）
        cursor_id = "cursor-xxxxx"  # 从服务器日志获取
        
        await ws.send(json.dumps({
            "type": "composer_send_prompt",
            "from": "my-client-001",
            "to": cursor_id,
            "timestamp": int(time.time()),
            "payload": {
                "agent_id": "demo-agent",
                "prompt": prompt
            }
        }))
        
        # 3. 接收结果
        result = await ws.recv()
        result_data = json.loads(result)
        
        if result_data['payload']['success']:
            print(f"✅ 成功: {result_data['payload']['message']}")
        else:
            print(f"❌ 失败: {result_data['payload']['error']}")

# 使用
asyncio.run(send_prompt_to_cursor("写一个 Python 快速排序函数"))
```

---

## 📂 项目结构

```
cursorgirl/
├── README.md                    # 本文档
├── PROJECT_STATUS.md            # 项目状态和功能清单
├── QUICK_START_V9.md            # 快速入门指南
│
├── bridge/                      # 中央服务器
│   ├── websocket_server.py     # WebSocket 服务器
│   ├── protocol.py             # 协议定义
│   └── requirements.txt        # Python 依赖
│
├── cursor-injector/             # Cursor Hook
│   ├── install-v9.sh           # V9 注入脚本 ⭐
│   ├── composer_operations.py  # DOM 操作封装
│   └── test_complete_flow.py   # 本地测试
│
├── docs/                        # 技术文档
│   ├── WEBSOCKET_PROTOCOL.md
│   ├── BOTTOM_UP_IMPLEMENTATION.md
│   └── SEMANTIC_OPERATIONS.md
│
├── examples/                    # 示例代码
│   ├── command_client_example.py
│   └── semantic_command_client.py
│
├── tests/                       # 测试脚本
│   └── quick_test_central.py   # 快速测试 ⭐
│
├── scripts/                     # 工具脚本
│   ├── START_ALL.sh
│   └── STOP_ALL.sh
│
└── reports/                     # 测试报告
    ├── CENTRAL_SERVER_SUCCESS_REPORT.md
    └── V9_COMPLETION_REPORT.md
```

---

## 🔧 核心功能

### ✅ 已实现功能

#### 1. Composer 操作
- [x] 发送提示词 (`composer_send_prompt`)
- [x] 检查状态 (`composer_check_status`)
- [x] 获取输入 (`composer_get_input`)
- [x] 清空输入 (`composer_clear_input`)

#### 2. Agent 控制
- [x] 检测 Agent 工作状态
- [x] 检测错误状态
- [x] 等待操作完成

#### 3. UI 操作
- [x] 切换到 Editor tab
- [x] 调用 Composer (Cmd+I)
- [x] 等待 UI 元素就绪

#### 4. 连接管理
- [x] 客户端注册
- [x] 消息路由
- [x] 心跳保持
- [x] 自动重连

---

## 🎯 使用场景

### 1. 自动化编程工作流
```python
# 批量生成代码
for task in tasks:
    await send_prompt(f"实现 {task.name} 功能")
    await wait_completion()
```

### 2. AITuber 直播编程
```python
# 接收观众指令，控制 Cursor 编程
async def handle_chat_command(command):
    await send_prompt(f"根据观众要求: {command}")
```

### 3. 远程协作
```python
# 团队成员远程触发 AI 代码生成
await send_prompt("重构 UserService 使用依赖注入")
```

### 4. 测试和验证
```python
# 自动化测试 Cursor 功能
for test in test_cases:
    result = await send_prompt(test.prompt)
    assert result.success
```

---

## ⚙️ 配置

### 中央服务器配置

编辑 `bridge/websocket_server.py`:

```python
# 服务器地址和端口
HOST = "localhost"  # 改为 "0.0.0.0" 允许远程连接
PORT = 8765

# 心跳间隔（秒）
HEARTBEAT_INTERVAL = 30
HEARTBEAT_TIMEOUT = 90
```

### Cursor Hook 配置

编辑 `cursor-injector/install-v9.sh`:

```javascript
// 中央服务器地址
const CENTRAL_SERVER_URL = 'ws://localhost:8765';

// 本地调试端口
const LOCAL_SERVER_PORT = 9876;
```

---

## 🐛 故障排除

### 问题 1: Cursor Hook 未连接

**检查**:
```bash
cat /tmp/cursor_ortensia.log
```

**解决**:
```bash
# 重新注入
cd cursor-injector
./install-v9.sh

# 重启 Cursor
```

### 问题 2: 命令无响应

**检查服务器日志**:
```bash
tail -f /tmp/ws_server.log
```

**常见原因**:
1. Cursor Hook ID 不正确
2. 服务器未运行
3. 网络连接问题

### 问题 3: 按钮点击失败

**症状**: 提示词未提交

**解决**: 
- 确保使用 V9 版本
- 检查 Composer 是否已打开
- 查看日志了解具体错误

---

## 📊 性能

| 指标 | 数值 |
|------|------|
| 连接建立 | < 100ms |
| 命令传输 | < 10ms |
| Composer 输入 | ~500ms |
| 端到端延迟 | ~700ms |
| 心跳间隔 | 30s |

---

## 🔮 路线图

### 近期 (1-2 周)
- [ ] 客户端列表查询命令
- [ ] 完整语义操作实现
- [ ] 等待 Agent 完成功能
- [ ] Web 控制面板原型

### 中期 (1-2 月)
- [ ] WSS 加密通信
- [ ] 客户端认证机制
- [ ] 多 Cursor 实例支持
- [ ] 命令历史和回放

### 长期 (3+ 月)
- [ ] 完整 Web 控制面板
- [ ] 插件系统
- [ ] 云端部署方案
- [ ] 跨平台支持 (Windows/Linux)

---

## 🤝 贡献

欢迎贡献！项目使用 MIT 许可证。

### 开发环境
- Python 3.13+
- Node.js 18+
- macOS (主要测试平台)
- Cursor IDE

### 贡献流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📜 许可证

MIT License - 详见 [LICENSE](./LICENSE) 文件

---

## 🙏 致谢

- **Cursor Team** - 优秀的 AI IDE
- **WebSocket 协议** - 可靠的实时通信
- **Electron** - 强大的桌面应用框架

---

## 📞 联系

- **项目**: Ortensia Cursor Control System
- **版本**: V9 - Production Ready
- **状态**: ✅ 所有核心功能已实现并测试通过
- **最后更新**: 2025-11-04

---

<div align="center">

**🎉 开始使用 Ortensia，解锁 Cursor 的远程控制能力！**

[快速开始](./QUICK_START_V9.md) · [查看文档](./docs/) · [测试报告](./reports/)

</div>
