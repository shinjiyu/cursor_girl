# 🚀 Ortensia Cursor Injector - 快速开始

## 📋 前提条件

- ✅ Cursor 已安装
- ✅ Node.js（Windows 注入脚本需要）
- ✅ Python 3（仅用于你的客户端工具，不是注入必须）

---

## ⚙️ 配置（可选）

### 修改中央服务器地址

**默认**: `ws://localhost:8765`

如果需要连接到其他服务器，在启动 Cursor **之前**设置环境变量：

```bash
# 设置服务器地址
export ORTENSIA_SERVER=ws://192.168.1.100:8765

# 添加到配置文件（永久生效）
echo 'export ORTENSIA_SERVER=ws://192.168.1.100:8765' >> ~/.zshrc
source ~/.zshrc
```

**验证配置**：

```bash
# 重启 Cursor 后查看日志
cat /tmp/cursor_ortensia.log | grep "服务器地址"
```

**常用场景**：
- 🏠 本地测试: `ws://localhost:8765` (默认)
- 🌐 局域网: `ws://192.168.1.100:8765`
- ☁️ 远程服务器: `ws://your-domain.com:8765`

---

## 🎯 3 步开始

### 步骤 1: 安装注入器（30 秒）

#### Windows（PowerShell）

```powershell
cd C:\path\to\cursorgirl\cursor-injector
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-win.ps1
```

#### macOS

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
🔗 连接到 Cursor (ws://localhost:9876)...
✅ 已连接

🏓 Ping...
✅ Pong: pong

👋 已断开连接
```

### 方法 2: 查看日志文件

macOS / Linux:

```bash
cat /tmp/cursor_ortensia.log
```

Windows（PowerShell）:

```powershell
Get-Content -Path (Join-Path $env:TEMP "cursor_ortensia.log") -Encoding utf8 -Wait
```

应该看到：

```
██████████████████████████████████████████████████████████████
█ ✅ WebSocket 服务器启动成功！
█ 📍 端口: 9876
█ 🔑 进程: xxxxx
█ 📡 等待 Ortensia 连接...
██████████████████████████████████████████████████████████████
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

