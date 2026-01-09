# Cursor Agent Hooks - 详细安装指南

## 📋 目录

- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [配置选项](#配置选项)
- [验证安装](#验证安装)
- [故障排查](#故障排查)
- [卸载](#卸载)

## 系统要求

### 必需

- **Cursor IDE** >= 0.42.0
- **Python** >= 3.7
- **macOS / Linux / Windows** (推荐 macOS/Linux)

### 依赖

- `websockets` - WebSocket 客户端库
- `asyncio` - 异步 I/O（Python 标准库）

安装依赖：

```bash
pip3 install websockets
```

或使用项目的 requirements.txt：

```bash
cd /path/to/cursorgirl/cursor-hooks
pip3 install -r requirements.txt
```

## 安装步骤

### 方法 1: 自动安装（推荐）

#### 步骤 1: 启动 Ortensia 中央服务器

```bash
cd /path/to/cursorgirl
./scripts/START_ALL.sh
```

验证服务器运行：
```bash
lsof -i :8765
```

应该看到：
```
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3   xxx user   x    IPv4 xxxxxx      0t0  TCP localhost:8765 (LISTEN)
```

#### 步骤 2: 运行部署脚本

##### Windows（PowerShell）

```powershell
cd C:\path\to\cursorgirl\cursor-hooks
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy.ps1
```

> 如需无提示覆盖已安装版本：`.\deploy.ps1 -Force`
>
> 需要本机已安装 Python 3.7+ 且 `python` 在 PATH；或使用 `.\deploy.ps1 -PythonPath "C:\Path\to\python.exe"`。

##### macOS / Linux

```bash
cd /path/to/cursorgirl/cursor-hooks
./deploy.sh
```

脚本会：
1. 检查 `~/.cursor-agent/` 是否已存在
2. 询问是否覆盖（如果存在）
3. 复制所有 Agent Hooks 到全局目录
4. 设置执行权限
5. 创建 Cursor 配置文件
6. 显示部署摘要

#### 步骤 3: 重启 Cursor（通常不需要）

一般情况下 Hook 配置生效不需要重启 Cursor；如果你发现 Hook 没有触发，再尝试完全退出 Cursor 后重新打开。

```bash
# macOS
osascript -e 'quit app "Cursor"'
open -a Cursor

# Linux
killall cursor
cursor &
```

### 方法 2: 手动安装

#### 步骤 1: 创建目录

```bash
mkdir -p ~/.cursor-agent/hooks
mkdir -p ~/.cursor-agent/lib
mkdir -p ~/.cursor
```

#### 步骤 2: 复制文件

```bash
cd /path/to/cursorgirl/cursor-hooks

# 复制 hooks
cp hooks/*.py ~/.cursor-agent/hooks/

# 复制库文件
cp lib/*.py ~/.cursor-agent/lib/
cp lib/*.sh ~/.cursor-agent/lib/ 2>/dev/null || true

# 复制配置
cp hooks.json ~/.cursor-agent/
cp run_hook.sh ~/.cursor-agent/
```

#### 步骤 3: 设置权限

```bash
chmod +x ~/.cursor-agent/hooks/*.py
chmod +x ~/.cursor-agent/lib/*.py
chmod +x ~/.cursor-agent/lib/*.sh 2>/dev/null || true
chmod +x ~/.cursor-agent/run_hook.sh
```

#### 步骤 4: 创建 Cursor 配置

```bash
ln -sf ~/.cursor-agent/hooks.json ~/.cursor/hooks.json
```

#### 步骤 5: 验证配置

```bash
ls -la ~/.cursor-agent/
ls -la ~/.cursor/hooks.json
```

#### 步骤 6: 重启 Cursor

完全退出并重新打开 Cursor。

## 配置选项

### 修改 WebSocket 服务器地址

编辑 `~/.cursor-agent/lib/agent_hook_handler.py`：

```python
# 第 37 行
self.ws_server = "ws://localhost:8765"
```

#### 场景 1: 本地开发（默认）

```python
self.ws_server = "ws://localhost:8765"
```

#### 场景 2: 局域网服务器

```python
self.ws_server = "ws://192.168.1.100:8765"
```

#### 场景 3: 远程服务器

```python
self.ws_server = "ws://your-domain.com:8765"
```

**注意**：修改后需要重启 Cursor。

### 自定义日志路径

编辑 `~/.cursor-agent/lib/agent_hook_handler.py`：

```python
# 默认：系统临时目录下的 cursor-agent-hooks.log
# 如需自定义路径，设置环境变量：
#   CURSOR_AGENT_HOOKS_LOG=/your/custom/path/hooks.log
```

### 启用/禁用特定 Hook

编辑 `~/.cursor/hooks.json`：

```json
{
  "beforeShellExecution": {
    "command": "~/.cursor-agent/run_hook.sh beforeShellExecution",
    "enabled": true  // 改为 false 禁用
  }
}
```

## 验证安装

### 1. 检查文件结构

```bash
tree ~/.cursor-agent/
```

期望输出：
```
~/.cursor-agent/
├── hooks/
│   ├── afterAgentResponse.py
│   ├── afterFileEdit.py
│   ├── afterMCPExecution.py
│   ├── afterShellExecution.py
│   ├── beforeMCPExecution.py
│   ├── beforeReadFile.py
│   ├── beforeShellExecution.py
│   ├── beforeSubmitPrompt.py
│   └── stop.py
├── lib/
│   ├── agent_hook_handler.py
│   └── websocket_sender.sh
├── hooks.json
└── run_hook.sh
```

### 2. 检查配置链接

```bash
ls -la ~/.cursor/hooks.json
```

应该是符号链接：
```
~/.cursor/hooks.json -> /Users/xxx/.cursor-agent/hooks.json
```

### 3. 手动测试 Hook

```bash
echo '{"command":"ls -la"}' | python3 ~/.cursor-agent/hooks/beforeShellExecution.py
```

期望输出：
```
[2025-11-22 12:00:00] [INFO] 🎣 [beforeShellExecution] Agent Hook 启动
[2025-11-22 12:00:00] [INFO] ✅ Hook 执行成功
```

### 4. 查看日志

```bash
tail -f /tmp/cursor-agent-hooks.log
```

Windows（PowerShell）可以这样查看：

```powershell
Get-Content -Path (Join-Path $env:TEMP "cursor-agent-hooks.log") -Wait
```

### 5. 在 Cursor 中触发

在 Cursor 中：
1. 按 `Cmd+K` 打开 Composer
2. 输入："创建一个 hello.py 文件"
3. 观察日志文件是否有新内容

## 故障排查

### 问题 1: Hook 没有触发

**症状**：Agent 执行操作但日志没有更新

**解决方案**：

1. **检查 Cursor 版本**：
   ```
   Cursor -> About Cursor
   ```
   确保版本 >= 0.42.0

2. **检查配置文件**：
   ```bash
   cat ~/.cursor/hooks.json
   ```
   应该有内容，而不是空文件

3. **检查权限**：
   ```bash
   ls -la ~/.cursor-agent/hooks/
   ```
   所有 `.py` 文件应该有 `x`（可执行）权限

4. **重启 Cursor**：
   完全退出（Cmd+Q）后重新打开

### 问题 2: Ortensia 没有反应

**症状**：Hook 触发了但 Ortensia 没有说话

**解决方案**：

1. **检查中央服务器**：
   ```bash
   lsof -i :8765
   ```
   如果没有进程，启动服务器：
   ```bash
   cd /path/to/cursorgirl
   ./scripts/START_ALL.sh
   ```

2. **检查服务器日志**：
   ```bash
   tail -f /tmp/ws_server.log
   ```
   应该看到 Hook 的消息

3. **检查服务器地址**：
   ```bash
   grep "ws_server" ~/.cursor-agent/lib/agent_hook_handler.py
   ```
   确保地址正确

4. **手动测试连接**：
   ```bash
   cd /path/to/cursorgirl
   python3 tests/test_aituber_integration.py
   ```

### 问题 3: 权限错误

**症状**：`Permission denied` 错误

**解决方案**：

```bash
chmod +x ~/.cursor-agent/hooks/*.py
chmod +x ~/.cursor-agent/lib/*.py
chmod +x ~/.cursor-agent/run_hook.sh
```

### 问题 4: Python 模块找不到

**症状**：`ModuleNotFoundError: No module named 'websockets'`

**解决方案**：

```bash
pip3 install websockets
```

或者：

```bash
cd /path/to/cursorgirl/cursor-hooks
pip3 install -r requirements.txt
```

### 问题 5: 日志文件没有创建

**症状**：日志文件不存在

**解决方案**：

1. **确认你有权限写入系统临时目录**
2. **使用自定义路径**：设置 `CURSOR_AGENT_HOOKS_LOG` 指向一个你确定可写的文件路径

## 卸载

### 完全卸载

```bash
# 删除 Agent Hooks
rm -rf ~/.cursor-agent/

# 删除 Cursor 配置
rm ~/.cursor/hooks.json

# 清理日志
rm /tmp/cursor-agent-hooks.log
```

### 重启 Cursor

完全退出并重新打开 Cursor。

### 验证卸载

```bash
ls ~/.cursor-agent/    # 应该不存在
ls ~/.cursor/hooks.json # 应该不存在
```

## 高级选项

### 多项目配置

Agent Hooks 是**全局安装**的，所有 Cursor 项目都会使用同一套 Hooks。

如果需要为不同项目使用不同配置：

1. 在 Hook 脚本中检测项目路径：
   ```python
   workspace_roots = self.input_data.get("workspace_roots", [])
   if "/path/to/special/project" in workspace_roots:
       # 特殊处理
   ```

2. 使用环境变量：
   ```bash
   export ORTENSIA_SERVER="ws://special-server:8765"
   cursor /path/to/special/project
   ```

### 自定义 Hook

参考 [README.md 的开发指南](README.md#开发指南)。

## 相关文档

- [README.md](README.md) - 完整文档
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [Cursor Agent Hooks 官方文档](https://cursor.com/en-US/docs/agent/hooks)

## 技术支持

如有问题，请在项目中提交 Issue。
