# Cursor Agent Hooks - 快速开始

## ⚡ 5 分钟快速安装

### 1️⃣ 启动 Ortensia 中央服务器

```bash
cd /path/to/cursorgirl
./scripts/START_ALL.sh
```

### 2️⃣ 安装 Agent Hooks（全局）

```bash
cd /path/to/cursorgirl/cursor-hooks
./deploy.sh
```

按 `y` 确认安装。

### 3️⃣ 重启 Cursor

**完全退出** Cursor（Cmd+Q），然后重新打开。

### 4️⃣ 测试

在 Cursor 中：
1. 打开任意项目
2. 按 `Cmd+K`
3. 输入："创建一个 test.py 文件"
4. 观察 Ortensia 的反应！🎉

## 📊 验证安装

### 查看已安装的 Hooks

```bash
ls -la ~/.cursor-agent/hooks/
```

应该看到 9 个 `.py` 文件。

### 查看配置

```bash
cat ~/.cursor/hooks.json
```

### 实时查看日志

```bash
tail -f /tmp/cursor-agent-hooks.log
```

### 查看中央服务器日志

```bash
tail -f /tmp/ws_server.log
```

## 🎯 Agent Hooks 会触发什么？

| 你的操作 | Agent Hook | Ortensia 反应 |
|---------|-----------|--------------|
| Agent 执行命令 | `beforeShellExecution` | "要执行命令了，让我检查一下..." 🤔 |
| Agent 编辑文件 | `afterFileEdit` | "文件已编辑！看起来不错~" 😊 |
| Agent 任务完成 | `stop` | "太棒了！任务完成！" 🎉 |
| Agent 读取文件 | `beforeReadFile` | "正在读取文件..." 📖 |
| Agent 调用工具 | `beforeMCPExecution` | "要使用工具了..." 🔧 |

## 🔧 常见问题

### Q: Ortensia 没有说话？

**A:** 检查中央服务器是否运行：
```bash
lsof -i :8765
```

如果没有运行：
```bash
cd /path/to/cursorgirl
./scripts/START_ALL.sh
```

### Q: Agent Hooks 没有触发？

**A:** 
1. 确认 Cursor 版本 >= 0.42.0
2. 检查配置：`cat ~/.cursor/hooks.json`
3. 重启 Cursor（完全退出后重开）

### Q: 如何卸载？

**A:**
```bash
rm -rf ~/.cursor-agent/
rm ~/.cursor/hooks.json
```

然后重启 Cursor。

### Q: 如何修改服务器地址？

**A:** 编辑 `~/.cursor-agent/lib/agent_hook_handler.py`：
```python
self.ws_server = "ws://your-server:port"
```

## 📚 下一步

- 查看完整文档：[README.md](README.md)
- 了解详细安装选项：[INSTALL.md](INSTALL.md)
- 自定义 Hook 行为：编辑 `~/.cursor-agent/hooks/*.py`

## 🎉 完成！

现在你的 Cursor AI Agent 已经和 Ortensia 连接了！

每次 Agent 执行操作时，Ortensia 都会：
- 🎤 语音反馈
- 🎭 表情动作
- 📊 详细日志

享受和虚拟角色一起编程的乐趣吧！✨
