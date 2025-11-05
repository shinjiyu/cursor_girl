# 中央 Server 模式测试指南

**当前状态**: 
- ✅ 中央 Server 已启动 (ws://localhost:8765)
- ✅ 环境变量已设置 (ORTENSIA_SERVER=ws://localhost:8765)
- ✅ V9 已重新注入（将连接到中央 Server）
- ⏳ **等待 Cursor 重启**

---

## 📋 测试步骤

### 1. 重启 Cursor

**重要**: 必须完全退出再重启，不能只是关闭窗口！

```bash
# Mac 上完全退出
按 Cmd+Q

# 或者命令行
killall Cursor

# 等待 2 秒

# 重新启动 Cursor
打开 Applications/Cursor.app
```

### 2. 等待连接（10 秒）

Cursor 启动后，等待约 10 秒让注入代码初始化并连接到中央 Server。

### 3. 检查连接状态

```bash
# 查看 Cursor 日志
cat /tmp/cursor_ortensia.log | grep "中央"

# 应该看到类似：
#   🌐 连接到中央Server...
#   📍 地址: ws://localhost:8765
#   ✅ 已连接到中央Server！
#   🔑 Cursor ID: cursor-xxxxxxxx
```

### 4. 获取 Cursor Hook ID

```bash
# 从日志中提取 Cursor ID
cat /tmp/cursor_ortensia.log | grep "Cursor ID:"

# 记下这个 ID，例如: cursor-abc12345
```

### 5. 运行测试脚本

```bash
cd cursor-injector
python3 test_central_server.py
```

测试脚本会：
1. 连接到中央 Server
2. 注册为 Command Client
3. 要求你输入 Cursor Hook ID
4. 发送测试命令
5. 等待响应

---

## 🔍 验证清单

### 检查中央 Server

在启动 Server 的终端中，应该看到：

```
✅ WebSocket 服务器已启动: ws://localhost:8765
等待客户端连接...
```

Cursor 连接后会显示：

```
✅ 新客户端连接
🔑 Client ID: cursor-xxxxxxxx
📝 客户端类型: cursor_hook
```

### 检查 Cursor 日志

```bash
cat /tmp/cursor_ortensia.log
```

**成功的标志**:
```
🎉 Ortensia V9 启动中...
✅ WebSocket 模块加载成功
📡 启动本地 WebSocket Server (端口 9876)...
✅ 本地 WebSocket Server 启动成功！
🌐 连接到中央Server...
✅ 已连接到中央Server！
🔑 Cursor ID: cursor-xxxxxxxx
```

**失败的情况**:
- 如果没有 "连接到中央Server"，检查环境变量
- 如果有 "连接错误"，检查中央 Server 是否运行
- 如果日志完全为空，Cursor 可能没有重启

---

## 🧪 完整测试流程

### 终端 1: 中央 Server（已运行）

```bash
# 已启动，应该在后台运行
# PID 已保存在 /tmp/ortensia_server.pid

# 查看是否在运行
ps aux | grep websocket_server
```

### 终端 2: Cursor 重启和日志监控

```bash
# 1. 完全退出 Cursor
killall Cursor

# 2. 重启 Cursor
open /Applications/Cursor.app

# 3. 实时监控日志
tail -f /tmp/cursor_ortensia.log
```

### 终端 3: 运行测试

```bash
# 等待 Cursor 连接成功后（终端 2 看到 "已连接到中央Server"）
cd cursor-injector
python3 test_central_server.py
```

---

## 📊 预期结果

### 成功的测试输出

```
======================================================================
  🌸 Ortensia 中央 Server 模式测试
======================================================================

🔗 连接到中央 Server: ws://localhost:8765
✅ 已连接

📝 注册为 Command Client...
✅ 注册成功
   Client ID: cmd-client-xxxxxxxx

📋 查询 Cursor Hook 列表...
请输入 Cursor Hook ID: cursor-abc12345

📤 发送提示词到 cursor-abc12345...
   内容: "用 Python 实现冒泡排序算法"

✅ 命令已发送，等待响应...

📬 收到响应:
   类型: composer_send_prompt_result
   来自: cursor-abc12345
   ✅ 成功: 提示词已提交

✅ 测试成功！

说明:
  1. ✅ 中央 Server 正常运行
  2. ✅ Command Client 成功连接
  3. ✅ Cursor Hook 成功接收命令
  4. ✅ 命令执行成功
```

---

## 🐛 故障排查

### 问题 1: Cursor 日志为空

**原因**: Cursor 没有重启

**解决**:
```bash
# 确保完全退出
killall Cursor
sleep 2

# 重新启动
open /Applications/Cursor.app
```

### 问题 2: 没有连接到中央Server

**原因**: 环境变量未生效

**解决**:
```bash
# 重新设置环境变量
export ORTENSIA_SERVER=ws://localhost:8765

# 重新注入
cd cursor-injector
./install-v9.sh

# 重启 Cursor
```

### 问题 3: 连接被拒绝

**原因**: 中央 Server 没有运行

**解决**:
```bash
# 检查 Server 是否在运行
ps aux | grep websocket_server

# 如果没有，重新启动
cd bridge
python3 websocket_server.py
```

### 问题 4: 测试脚本无响应

**原因**: Cursor Hook ID 不正确

**解决**:
```bash
# 从日志获取正确的 ID
cat /tmp/cursor_ortensia.log | grep "Cursor ID:"

# 或者查看 Server 输出
```

---

## 📝 注意事项

1. **环境变量**: 设置后必须重新注入才能生效
2. **完全重启**: 必须 Cmd+Q 完全退出，不能只关闭窗口
3. **等待时间**: 重启后等待 10 秒让系统初始化
4. **日志查看**: 有问题时先查看 `/tmp/cursor_ortensia.log`
5. **Server 状态**: 确保中央 Server 一直在运行

---

## 🎯 快速命令

```bash
# 检查所有组件状态
echo "=== 中央 Server ==="
ps aux | grep websocket_server

echo ""
echo "=== Cursor 进程 ==="
ps aux | grep Cursor.app

echo ""
echo "=== 环境变量 ==="
echo $ORTENSIA_SERVER

echo ""
echo "=== 最新日志 ==="
tail -10 /tmp/cursor_ortensia.log
```

---

*准备好后运行 `python3 test_central_server.py` 开始测试！*







