# Ortensia Cursor Injector

**最小化注入方案**：只注入 WebSocket 服务器，动态执行 Python 发送的 JavaScript 代码。

---

## 🎯 核心思路

```
1. 注入最小化代码到 Cursor
   ↓
2. 启动 WebSocket 服务器 (端口 9224)
   ↓
3. Python 连接并发送 JS 代码
   ↓
4. Cursor 动态执行代码
   ↓
5. 返回执行结果
```

**优势**：
- ✅ 注入的代码极少
- ✅ 功能可以动态更新
- ✅ 不需要重新注入就能改变行为

---

## 📦 文件说明

```
cursor-injector/
├── ortensia-injector.js      # 注入代码（WebSocket 服务器）
├── install.sh                 # 安装脚本
├── uninstall.sh               # 卸载脚本
├── ortensia_cursor_client.py  # Python 客户端
└── README.md                  # 本文档
```

---

## 🚀 安装

### 步骤 1: 运行安装脚本

```bash
cd "/Users/user/Documents/ cursorgirl/cursor-injector"
chmod +x install.sh uninstall.sh
./install.sh
```

### 步骤 2: 重启 Cursor

完全退出 Cursor，然后重新打开。

### 步骤 3: 验证安装

1. 打开 DevTools: `Cmd+Shift+P` → `Toggle Developer Tools`
2. 切换到 Console 标签
3. 应该看到：

```
================================================================================
  🎉 Ortensia Cursor Injector
  Version: 1.0.0 (Minimal)
================================================================================

✅ WebSocket server started on port 9224
📡 Waiting for Ortensia to connect...
```

---

## 🎮 使用

### 基础测试

```bash
# 测试连接
python3 ortensia_cursor_client.py ping
```

### 交互模式

```bash
# 启动交互模式
python3 ortensia_cursor_client.py interactive
```

然后可以输入命令：

```
> ping                                    # 测试连接
> version                                 # 获取版本
> commands                                # 列出所有 VSCode 命令
> eval console.log("Hello!")              # 在主进程执行代码
> evalr console.log("In renderer!")       # 在渲染进程执行代码
> cmd workbench.action.files.save         # 执行 VSCode 命令
> exit                                    # 退出
```

---

## 💻 Python API

```python
import asyncio
from ortensia_cursor_client import OrtensiaC​ursorClient

async def main():
    client = OrtensiaC​ursorClient()
    await client.connect()
    
    try:
        # 1. 测试连接
        await client.ping()
        
        # 2. 在主进程执行代码
        result = await client.eval_code('2 + 2')
        print(f'Result: {result}')  # 4
        
        # 3. 在渲染进程执行代码（可以访问 vscode API）
        commands = await client.eval_in_renderer(
            'vscode.commands.getCommands(true)'
        )
        print(f'Found {len(commands)} commands')
        
        # 4. 获取所有 Cursor 命令
        cursor_commands = await client.get_vscode_commands()
        
        # 5. 执行 VSCode 命令
        await client.execute_vscode_command('workbench.action.files.save')
        
    finally:
        await client.close()

asyncio.run(main())
```

---

## 🔧 高级用法

### 动态发送函数

```python
# 定义一个函数（在 Python 中）
js_function = '''
async function insertCode(code) {
    const editor = await vscode.window.activeTextEditor;
    if (editor) {
        await editor.edit(builder => {
            builder.insert(editor.selection.active, code);
        });
        return true;
    }
    return false;
}
'''

# 先在渲染进程中定义函数
await client.eval_in_renderer(js_function)

# 然后调用
await client.eval_in_renderer('insertCode("console.log(\\'Hello\\');")')
```

### 创建持久化功能

```python
# 一次性定义，以后都能用
setup_code = '''
window.ortensiaTools = {
    insertCode: async (code) => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return false;
        await editor.edit(b => b.insert(editor.selection.active, code));
        return true;
    },
    
    getContent: () => {
        const editor = vscode.window.activeTextEditor;
        return editor ? editor.document.getText() : '';
    },
    
    openFile: async (path) => {
        const doc = await vscode.workspace.openTextDocument(path);
        await vscode.window.showTextDocument(doc);
        return true;
    }
};
'''

await client.eval_in_renderer(setup_code)

# 以后直接调用
await client.eval_in_renderer('ortensiaTools.insertCode("test")')
await client.eval_in_renderer('ortensiaTools.getContent()')
```

---

## 🗑️ 卸载

```bash
./uninstall.sh
```

然后重启 Cursor。

---

## 📊 与 Ortensia 集成

在 `bridge/websocket_server.py` 中添加：

```python
from ortensia_cursor_client import OrtensiaC​ursorClient

class OrtensiaB​ridge:
    def __init__(self):
        self.cursor_client = None
    
    async def connect_to_cursor(self):
        """连接到 Cursor"""
        self.cursor_client = OrtensiaC​ursorClient()
        await self.cursor_client.connect()
    
    async def on_git_commit(self, commit_info):
        """Git 提交时，自动发送到 Cursor AI"""
        prompt = f"请审查这次提交: {commit_info['message']}"
        
        # 发送到 Cursor AI
        await self.cursor_client.eval_in_renderer(f'''
            vscode.commands.executeCommand('cursor.aichat', {{
                prompt: "{prompt}"
            }});
        ''')
    
    async def insert_code(self, code):
        """插入代码"""
        await self.cursor_client.eval_in_renderer(f'''
            const editor = vscode.window.activeTextEditor;
            if (editor) {{
                await editor.edit(b => b.insert(editor.selection.active, `{code}`));
            }}
        ''')
```

---

## ⚠️ 注意事项

### 1. Cursor 更新

Cursor 更新后需要重新安装：

```bash
./install.sh
```

### 2. 代码签名

安装后 Cursor 的签名会变化，但不影响使用。

### 3. 安全性

注入的代码只监听 `localhost:9224`，外部无法访问。

---

## 🐛 故障排除

### 问题 1: Python 无法连接

**检查**：
1. Cursor 是否已启动
2. DevTools Console 是否显示 "WebSocket server started"
3. 端口 9224 是否被占用

```bash
# 检查端口
lsof -i :9224
```

### 问题 2: 安装失败

**检查**：
1. 是否有权限修改 `/Applications/Cursor.app`
2. Cursor 是否正在运行（需要先关闭）

```bash
# 确保 Cursor 已关闭
killall Cursor
```

### 问题 3: 执行代码失败

**检查**：
1. JavaScript 语法是否正确
2. 是否在正确的上下文中执行（main vs renderer）
3. DevTools Console 是否有错误信息

---

## 📚 更多示例

查看 `ortensia_cursor_client.py` 中的示例。

---

## 🎉 完成！

现在你可以：
- ✅ 从 Python 动态执行任何 JavaScript 代码
- ✅ 访问所有 Cursor 内部 API
- ✅ 控制编辑器、文件、AI
- ✅ 集成到 Ortensia 系统

