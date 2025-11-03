# 🚀 Ortensia Cursor Injector - 快速开始

## 📋 前提条件

- ✅ macOS
- ✅ Cursor 已安装
- ✅ Python 3（系统自带即可）

---

## 🎯 3 步开始

### 步骤 1: 安装注入器（30 秒）

```bash
cd "/Users/user/Documents/ cursorgirl/cursor-injector"
./install.sh
```

### 步骤 2: 重启 Cursor

完全退出 Cursor（Cmd+Q），然后重新打开。

### 步骤 3: 测试连接

```bash
./ortensia-cursor.sh ping
```

如果看到 "✅ Pong"，说明成功了！🎉

---

## 🎮 交互模式

```bash
./ortensia-cursor.sh interactive
```

然后试试这些命令：

```
> ping
> version
> commands
> evalr console.log("Hello from Ortensia!")
> exit
```

---

## 🔍 验证安装

### 方法 1: 命令行测试（推荐）

```bash
./ortensia-cursor.sh ping
```

**期望输出**：
```
🔗 连接到 Cursor (ws://localhost:9224)...
✅ 已连接

🏓 Ping...
✅ Pong: pong

👋 已断开连接
```

### 方法 2: 查看 DevTools

1. 在 Cursor 中按 `Cmd+Shift+P`
2. 输入 "Toggle Developer Tools"
3. 切换到 Console 标签
4. 应该看到：

```
================================================================================
  🎉 Ortensia Cursor Injector
  Version: 1.0.0 (Minimal)
================================================================================

✅ WebSocket server started on port 9224
📡 Waiting for Ortensia to connect...
```

---

## 🐛 故障排除

### 问题 1: 连接失败

**症状**：
```
❌ 连接失败: [Errno 61] Connection refused
```

**解决**：
1. 确认 Cursor 已启动
2. 打开 DevTools 查看 Console 是否有错误
3. 如果看到 JavaScript 错误，可能需要重新安装：
   ```bash
   ./uninstall.sh
   ./install.sh
   ```

### 问题 2: JavaScript 错误（ES Module）

**症状**：
```
ReferenceError: require is not defined in ES module scope
```

**解决**：
说明你使用了旧版本的注入脚本，重新安装即可：
```bash
./uninstall.sh
./install.sh
```

### 问题 3: Python 模块缺失

**症状**：
```
ModuleNotFoundError: No module named 'websockets'
```

**解决**：
使用提供的启动脚本（它会自动使用正确的 Python 环境）：
```bash
./ortensia-cursor.sh ping
```

---

## 💻 Python API 快速示例

```python
#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/Users/user/Documents/ cursorgirl/bridge')
from ortensia_cursor_client import OrtensiaCursorClient

async def main():
    client = OrtensiaCursorClient()
    
    if await client.connect():
        # 测试
        await client.ping()
        
        # 在渲染进程执行代码
        result = await client.eval_in_renderer('''
            vscode.window.showInformationMessage('Hello from Ortensia!');
        ''')
        
        await client.close()

asyncio.run(main())
```

---

## 🗑️ 卸载

```bash
./uninstall.sh
```

然后重启 Cursor。

---

## ✅ 下一步

成功运行后，可以：
1. 查看 `README.md` 了解更多功能
2. 尝试 `ortensia_cursor_client.py` 中的示例
3. 集成到 Ortensia 系统

