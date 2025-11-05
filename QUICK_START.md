# 🚀 Ortensia 快速入门

**版本**: V9  
**5 分钟快速上手**

---

## 📋 前置要求

- Python 3.13+
- Cursor IDE
- macOS (主要测试平台)

---

## 🎯 三步启动

### 1️⃣ 安装 Cursor Hook

```bash
cd cursor-injector
./install-v9.sh
```

这会将 WebSocket 客户端注入到 Cursor 中。

### 2️⃣ 启动中央服务器

```bash
# 方法 1: 一键启动（推荐）
./scripts/START_ALL.sh

# 方法 2: 手动启动
cd bridge
python3 websocket_server.py
```

服务器会监听端口 8765。

### 3️⃣ 启动 Cursor 并测试

启动 Cursor IDE，然后运行测试：

```bash
cd tests
python3 quick_test_central.py
```

✅ **成功！** 你会看到 Cursor Composer 收到命令并开始执行。

---

## 📝 发送你的第一个命令

### Python 客户端示例

```python
import asyncio
import websockets
import json
import time

async def send_command():
    async with websockets.connect('ws://localhost:8765') as ws:
        # 1. 注册
        await ws.send(json.dumps({
            "type": "register",
            "from": "my-client",
            "to": "server",
            "timestamp": int(time.time()),
            "payload": {"client_type": "command_client"}
        }))
        
        await ws.recv()  # 等待确认
        
        # 2. 发送命令 (需要知道 Cursor ID)
        cursor_id = "cursor-xxxxx"  # 从日志获取
        
        await ws.send(json.dumps({
            "type": "composer_send_prompt",
            "from": "my-client",
            "to": cursor_id,
            "timestamp": int(time.time()),
            "payload": {
                "agent_id": "test",
                "prompt": "写一个 Python 快速排序"
            }
        }))
        
        # 3. 接收结果
        result = await ws.recv()
        print(result)

asyncio.run(send_command())
```

---

## 🔍 如何获取 Cursor ID

### 方法 1: 查看服务器日志

```bash
tail -f /tmp/ws_server.log | grep "已注册"
```

你会看到类似：
```
✅ 客户端已注册: cursor-4rod28v0h (cursor_hook)
```

### 方法 2: 使用测试脚本

测试脚本会自动发现 Cursor ID：

```bash
cd tests
python3 quick_test_central.py
```

---

## 📊 查看日志

### Cursor Hook 日志

```bash
tail -f /tmp/cursor_ortensia.log
```

### 服务器日志

```bash
tail -f /tmp/ws_server.log
```

---

## 🛑 停止服务

```bash
./scripts/STOP_ALL.sh
```

---

## 🐛 故障排除

### 问题 1: Hook 未连接

**症状**: 测试脚本找不到 Cursor 客户端

**解决**:
```bash
# 1. 检查 Hook 日志
tail -30 /tmp/cursor_ortensia.log

# 2. 重新注入
cd cursor-injector
./uninstall.sh
./install-v9.sh

# 3. 重启 Cursor
```

### 问题 2: 端口被占用

**症状**: 服务器启动失败，提示端口 8765 已被占用

**解决**:
```bash
# 停止现有服务
./scripts/STOP_ALL.sh

# 或手动查找并杀死进程
lsof -i :8765
kill -9 <PID>
```

### 问题 3: 命令无响应

**症状**: 发送命令后没有反应

**检查**:
```bash
# 1. 确认服务器运行
lsof -i :8765

# 2. 确认 Cursor Hook 已连接
grep "已连接" /tmp/cursor_ortensia.log

# 3. 确认 Cursor ID 正确
tail -f /tmp/ws_server.log
```

---

## 📚 下一步

### 查看文档
- [README.md](./README.md) - 项目主页和详细说明
- [docs/PROJECT_STATUS.md](./docs/PROJECT_STATUS.md) - 完整功能清单
- [docs/WEBSOCKET_PROTOCOL.md](./docs/WEBSOCKET_PROTOCOL.md) - 协议规范

### 查看示例
```bash
cd examples
cat command_client_example.py
cat semantic_command_client.py
```

### 开发自己的客户端
参考 `examples/` 目录中的示例代码，使用 Ortensia Protocol 与 Cursor 通信。

---

## 🎯 常用命令速查

```bash
# 安装
cd cursor-injector && ./install-v9.sh

# 启动服务器
./scripts/START_ALL.sh

# 测试
cd tests && python3 quick_test_central.py

# 查看日志
tail -f /tmp/cursor_ortensia.log    # Cursor
tail -f /tmp/ws_server.log           # 服务器

# 停止
./scripts/STOP_ALL.sh

# 重新安装
cd cursor-injector && ./uninstall.sh && ./install-v9.sh
```

---

## 💡 提示

1. **首次使用**: 确保先运行 `install-v9.sh` 安装 Hook
2. **每次使用**: 先启动服务器，再启动 Cursor
3. **开发调试**: 保持日志窗口打开以便实时查看
4. **出现问题**: 先查看日志，再重启服务

---

## ✅ 验证安装

运行以下命令确保一切正常：

```bash
# 1. 检查文件
ls cursor-injector/install-v9.sh
ls bridge/websocket_server.py
ls tests/quick_test_central.py

# 2. 检查权限
ls -l scripts/*.sh

# 3. 检查 Python 依赖
python3 -c "import websockets; print('✅ websockets 已安装')"
```

---

**准备就绪！开始使用 Ortensia 控制 Cursor！** 🎉
