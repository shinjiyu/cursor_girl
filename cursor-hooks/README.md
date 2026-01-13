# Cursor Agent Hooks - 全局安装工具

## 🤖 什么是 Agent Hooks？

Agent Hooks 允许你监控和控制 **Cursor AI Agent** 的行为，在 Agent 执行各种操作时自动触发自定义脚本。

### ✨ 与 Ortensia 集成

所有 Agent Hooks 事件都会自动发送到 **Ortensia 中央服务器**，触发虚拟角色（オルテンシア）的实时反馈：
- 🎤 **语音反馈** - AI 说话告诉你发生了什么
- 🎭 **表情动作** - 根据情绪显示表情和动作
- 📊 **详细日志** - 完整的执行日志记录

## 📋 支持的 Agent Hooks（9个）

| Hook名称 | 类型 | 触发时机 | 功能 |
|---------|------|---------|------|
| `beforeShellExecution` | 权限 | Agent 执行命令前 | 安全检查，拦截危险命令 |
| `afterShellExecution` | 审计 | Agent 执行命令后 | 审计命令执行结果 |
| `beforeMCPExecution` | 权限 | Agent 调用工具前 | 检查敏感工具 |
| `afterMCPExecution` | 审计 | Agent 调用工具后 | 审计工具执行结果 |
| `afterFileEdit` | 审计 | Agent 编辑文件后 | 自动格式化，审计修改 |
| `beforeReadFile` | 权限 | Agent 读取文件前 | 敏感文件保护 |
| `beforeSubmitPrompt` | 审计 | Agent 提交提示前 | 检测敏感信息 |
| `afterAgentResponse` | 审计 | Agent 响应后 | 审计 Agent 响应 |
| `stop` | 控制 | Agent 任务完成 | 任务完成通知 |

## 🚀 快速开始

## 🌐 配置中央服务器地址（推荐）

优先级（从高到低）：
1. 环境变量 `WS_SERVER`（hooks 专用）
2. 环境变量 `ORTENSIA_SERVER`
3. 本地配置文件（适合 GUI 启动/无环境变量场景）
4. 默认 `ws://localhost:8765`

### 本地配置文件（macOS 推荐路径）

把中央服务器地址写入：

```
~/Library/Application Support/Ortensia/central_server.txt
```

内容示例：

```
wss://mazda-commissioners-organised-perceived.trycloudflare.com/
```

### 前提条件

1. **启动 Ortensia 中央服务器**（必须）：
   ```bash
   cd <your-cursorgirl-project>
   ./scripts/START_ALL.sh
   ```
   
2. **确认服务器运行**：
   ```bash
   lsof -i :8765  # 应该看到 python3 进程监听 8765 端口
   ```

### 一键安装

#### macOS / Linux

```bash
cd /path/to/cursorgirl/cursor-hooks
./deploy.sh
```

#### Windows（PowerShell）

在 `cursor-hooks/` 目录下运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy.ps1 -Runtime node
```

> 如需无提示覆盖已安装版本：`.\deploy.ps1 -Force`
>
> 默认推荐 `-Runtime node`（Windows 免 Python）。如需继续使用 Python：`-Runtime python -PythonPath "C:\Path\to\python.exe"` 或确保 `python` 在 PATH。

脚本会自动：
1. ✅ 复制所有 Agent Hooks 到 `~/.cursor-agent/`
2. ✅ 设置正确的执行权限
3. ✅ 创建 `hooks.json` 配置文件
4. ✅ 在 `~/.cursor/` 创建符号链接
5. ✅ 复制必要的库文件

### 重启 Cursor（通常不需要）

一般情况下 Hook 配置生效不需要重启 Cursor；如果你发现 Hook 没有触发，再尝试完全退出并重新打开 Cursor。

## 📊 验证安装

### 1. 检查文件部署

```bash
ls -la ~/.cursor-agent/
ls -la ~/.cursor/hooks.json
```

应该看到：
```
~/.cursor-agent/
├── hooks/          # 9 个 Agent Hook 脚本
├── lib/            # 支持库
├── hooks.json      # 配置文件
└── run_hook.sh     # 包装脚本
```

### 2. 查看日志

日志文件默认写入**系统临时目录**下的 `cursor-agent-hooks.log`（也可以用环境变量 `CURSOR_AGENT_HOOKS_LOG` 自定义）。

- macOS / Linux（默认临时目录通常是 `/tmp`）

```bash
tail -f /tmp/cursor-agent-hooks.log
```

- Windows（PowerShell）

```powershell
Get-Content -Path (Join-Path $env:TEMP "cursor-agent-hooks.log") -Encoding utf8 -Wait
```

### 3. 测试 Hook

```bash
echo '{"command":"ls -la"}' | python3 ~/.cursor-agent/hooks/beforeShellExecution.py
```

应该看到日志输出，并且 Ortensia 会说话（如果中央服务器运行中）。

### 4. 触发真实 Agent 事件

在 Cursor 中：
1. 打开任意项目
2. 按 `Cmd+K` 打开 AI Composer
3. 输入提示，如："创建一个 hello.py 文件"
4. 观察：
   - Cursor Agent 开始工作
   - Agent Hooks 被触发
   - 日志文件有新日志（见上面的日志路径说明）
   - Ortensia 说话和做动作

## 🔧 配置

### 修改中央服务器地址

如果你的 Ortensia 服务器不在 `localhost:8765`：

编辑 `~/.cursor-agent/lib/agent_hook_handler.py`：

```python
# 找到这一行
self.ws_server = "ws://localhost:8765"

# 修改为你的服务器地址
self.ws_server = "ws://192.168.1.100:8765"
```

然后重启 Cursor。

### 自定义 Hook 行为

编辑 `~/.cursor-agent/hooks/<hook_name>.py` 来自定义 Hook 行为。

例如，修改 `stop.py` 来改变任务完成时的消息：

```python
# 修改文本和情绪
await self.send_to_ortensia(
    text="太棒了！任务圆满完成！🎉",
    emotion="excited",
    event_type="stop"
)
```

## 🗑️ 卸载

```bash
rm -rf ~/.cursor-agent/
rm ~/.cursor/hooks.json
```

然后重启 Cursor。

## 📁 目录结构

```
cursor-hooks/
├── deploy.sh           # 部署脚本
├── hooks/              # Agent Hook 脚本（9个）
│   ├── afterAgentResponse.py
│   ├── afterFileEdit.py
│   ├── afterMCPExecution.py
│   ├── afterShellExecution.py
│   ├── beforeMCPExecution.py
│   ├── beforeReadFile.py
│   ├── beforeShellExecution.py
│   ├── beforeSubmitPrompt.py
│   └── stop.py
├── lib/                # 支持库
│   ├── agent_hook_handler.py  # Hook 处理器基类
│   └── websocket_sender.sh    # WebSocket 发送工具
├── hooks.json          # Cursor 配置文件
├── run_hook.sh         # Hook 包装脚本
├── requirements.txt    # Python 依赖
└── README.md           # 本文件
```

## 🐛 故障排查

### Agent Hooks 没有触发

1. **检查 Cursor 版本**：
   - Agent Hooks 需要 Cursor >= 0.42.0
   - 检查：Cursor -> About Cursor

2. **检查配置文件**：
   ```bash
   cat ~/.cursor/hooks.json
   ```
   应该存在且是符号链接到 `~/.cursor-agent/hooks.json`

3. **检查日志**：
   ```bash
   tail -f /tmp/cursor-agent-hooks.log
   ```

### Ortensia 没有说话

1. **检查中央服务器**：
   ```bash
   lsof -i :8765  # 应该有进程监听
   tail -f /tmp/ws_server.log  # 查看服务器日志
   ```

2. **检查服务器地址**：
   ```bash
   grep "ws_server" ~/.cursor-agent/lib/agent_hook_handler.py
   ```
   应该是 `ws://localhost:8765`

3. **手动测试连接**：
   ```bash
   cd /path/to/cursorgirl
   python3 tests/test_aituber_integration.py
   ```

### 权限问题

如果 Hook 脚本无法执行：

```bash
chmod +x ~/.cursor-agent/hooks/*.py
chmod +x ~/.cursor-agent/lib/*.py
chmod +x ~/.cursor-agent/run_hook.sh
```

## 🔗 相关文档

- [Cursor Agent Hooks 官方文档](https://cursor.com/en-US/docs/agent/hooks)
- [Ortensia 中央服务器](../bridge/README.md)
- [Ortensia 协议](../bridge/protocol.py)

## 📝 开发指南

### 创建自定义 Hook

1. 在 `hooks/` 目录创建新的 `.py` 文件
2. 继承 `AgentHookHandler` 基类
3. 实现 `handle_hook()` 方法
4. 在 `hooks.json` 中注册

示例：

```python
#!/usr/bin/env python3
from agent_hook_handler import AgentHookHandler

class MyCustomHook(AgentHookHandler):
    def __init__(self):
        super().__init__("myCustomHook")
    
    async def handle_hook(self):
        # 你的逻辑
        await self.send_to_ortensia(
            text="自定义 Hook 被触发了！",
            emotion="neutral"
        )
        
        # 返回响应（如果需要）
        return self.format_response(allow=True)

if __name__ == "__main__":
    import asyncio
    hook = MyCustomHook()
    asyncio.run(hook.run())
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请在项目中提交 Issue。
