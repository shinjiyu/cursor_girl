# ⚙️ Ortensia Cursor Injector - 配置指南

## 🌐 修改中央服务器地址

### 默认配置

Cursor Hook 默认连接到本地服务器：

```
ws://localhost:8765
```

### 修改方法
优先级（从高到低）：
1. 环境变量 `ORTENSIA_SERVER`
2. 本地配置文件（推荐给“直接双击启动 Cursor”的场景）
3. 默认值 `ws://localhost:8765`

---

## ✅ 本地配置文件（推荐给 macOS 双击启动）

当你从 Finder / Dock / Spotlight 直接启动 Cursor 时，shell 环境变量经常不会注入到 App 进程。
此时可以使用本地配置文件来指定中央服务器地址。

### 推荐路径（macOS）

把中央服务器地址写入：

```
~/Library/Application Support/Ortensia/central_server.txt
```

文件内容示例（只写一行 URL）：

```
wss://mazda-commissioners-organised-perceived.trycloudflare.com/
```

### 备选路径（也会自动尝试）

- `~/.ortensia_server`
- `~/.config/ortensia/central_server.txt`
- `<workspace>/.ortensia/central_server.txt`

---

## 🌿 环境变量（终端启动时可用）

通过环境变量 `ORTENSIA_SERVER` 配置服务器地址。

#### 方法 1：临时设置（仅当前终端会话）

```bash
export ORTENSIA_SERVER=ws://192.168.1.100:8765
```

**然后启动 Cursor**。

#### 方法 2：永久设置（推荐）

添加到 shell 配置文件：

```bash
# 对于 zsh (macOS 默认)
echo 'export ORTENSIA_SERVER=ws://192.168.1.100:8765' >> ~/.zshrc
source ~/.zshrc

# 对于 bash
echo 'export ORTENSIA_SERVER=ws://192.168.1.100:8765' >> ~/.bashrc
source ~/.bashrc
```

**然后启动 Cursor**。

---

## 📋 配置场景

### 1. 本地开发（默认）

不需要任何配置，使用默认值：

```bash
# 无需设置，默认就是这个
ws://localhost:8765
```

### 2. 局域网服务器

连接到同一网络内的另一台机器：

```bash
export ORTENSIA_SERVER=ws://192.168.1.100:8765
```

**注意**：确保：
- 服务器在 `192.168.1.100` 上运行
- 端口 `8765` 未被防火墙阻止
- 两台机器在同一局域网

### 3. 远程服务器

连接到互联网上的服务器：

```bash
export ORTENSIA_SERVER=ws://your-domain.com:8765
```

**注意**：
- 确保服务器可以通过公网访问
- 考虑使用 WSS (安全 WebSocket) 而不是 WS
- 配置适当的防火墙规则

### 4. 自定义端口

如果中央服务器使用非标准端口：

```bash
export ORTENSIA_SERVER=ws://localhost:9999
```

---

## ✅ 验证配置

### 1. 检查环境变量

```bash
echo $ORTENSIA_SERVER
```

应该输出你设置的地址。

### 2. 查看 Cursor 日志

启动 Cursor 后查看日志：

```bash
cat /tmp/cursor_ortensia.log | grep "服务器地址"
```

**使用环境变量配置时**，应该看到：
```
💡 使用环境变量配置的服务器地址: ws://192.168.1.100:8765
```

**使用默认配置时**，应该看到：
```
💡 使用默认服务器地址: ws://localhost:8765
   提示: 可通过环境变量修改: export ORTENSIA_SERVER=ws://your-server:8765
```

### 3. 测试连接

使用 Python 测试客户端：

```bash
cd /Users/user/Documents/cursorgirl/bridge
python3 websocket_server.py &

cd /Users/user/Documents/cursorgirl/tests
python3 quick_test_central.py
```

如果配置正确，应该能成功发送命令到 Cursor。

---

## 🔄 更改配置

### 修改后需要：

1. **重启 Cursor**：
   ```bash
   # 完全退出 Cursor (Cmd+Q)
   # 然后重新打开
   ```

2. **验证新配置**：
   ```bash
   cat /tmp/cursor_ortensia.log | grep "服务器地址"
   ```

### 恢复默认配置

```bash
unset ORTENSIA_SERVER

# 如果添加到了配置文件，需要删除那一行
# 编辑 ~/.zshrc 或 ~/.bashrc，删除包含 ORTENSIA_SERVER 的行
```

---

## 🐛 故障排除

### 问题 1：无法连接到服务器

**症状**：日志显示连接失败或超时

**检查**：
```bash
# 1. 验证环境变量
echo $ORTENSIA_SERVER

# 2. 验证服务器是否运行
# 在服务器机器上：
ps aux | grep websocket_server

# 3. 验证端口是否可达
nc -zv <server-ip> 8765
```

**解决**：
- 确保中央服务器正在运行
- 检查防火墙设置
- 验证 IP 地址和端口正确

### 问题 2：配置未生效

**症状**：仍然连接到 localhost

**检查**：
```bash
# 1. 确认环境变量在 Cursor 启动前设置
echo $ORTENSIA_SERVER

# 2. 查看 Cursor 日志
cat /tmp/cursor_ortensia.log | grep "服务器地址"
```

**解决**：
- 确保在启动 Cursor **之前**设置环境变量
- 如果从 Dock/Spotlight 启动 Cursor，环境变量可能不生效
- 尝试从终端启动：`/Applications/Cursor.app/Contents/MacOS/Cursor`

### 问题 3：局域网连接失败

**症状**：本地可以，但局域网其他机器无法连接

**检查**：
```bash
# 1. 服务器是否监听所有接口
# 在 bridge/websocket_server.py 中检查：
# HOST = "0.0.0.0"  # 不是 "localhost"

# 2. 防火墙是否允许
sudo pfctl -sr | grep 8765  # macOS
```

**解决**：
- 修改服务器监听地址为 `0.0.0.0`
- 添加防火墙规则允许端口 8765
- 确保两台机器在同一网络

---

## 📚 相关文档

- [README.md](./README.md) - 完整功能说明
- [QUICK_START.md](./QUICK_START.md) - 快速开始指南
- [../bridge/README.md](../bridge/README.md) - 中央服务器文档

---

## 💡 最佳实践

### 开发环境

```bash
# 使用默认 localhost
# 无需配置
```

### 生产环境

```bash
# 添加到 ~/.zshrc
export ORTENSIA_SERVER=ws://production-server:8765

# 设置日志级别（如果需要）
export ORTENSIA_LOG_LEVEL=INFO
```

### 多环境切换

使用 shell 函数：

```bash
# 添加到 ~/.zshrc

# 切换到开发环境
ortensia_dev() {
    unset ORTENSIA_SERVER
    echo "✅ 切换到开发环境: ws://localhost:8765"
}

# 切换到生产环境
ortensia_prod() {
    export ORTENSIA_SERVER=ws://production-server:8765
    echo "✅ 切换到生产环境: $ORTENSIA_SERVER"
}
```

使用：

```bash
ortensia_dev   # 切换到开发环境
ortensia_prod  # 切换到生产环境
```

---

<div align="center">

**需要帮助？** 查看 [QUICK_START.md](./QUICK_START.md) 或提交 Issue

</div>

