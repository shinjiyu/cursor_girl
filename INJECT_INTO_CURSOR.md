# 直接注入 Cursor 代码

**核心思路**: 修改 Cursor 的启动脚本，注入我们自己的代码

---

## 🎯 为什么这个方案最好？

### ✅ 优势
- **完全控制**: 可以访问 Cursor 的所有内部 API
- **无沙箱限制**: 不受扩展 API 限制
- **启动时加载**: 自动运行，无需手动激活
- **简单直接**: 不需要打包扩展

### ⚠️ 注意事项
- **更新会覆盖**: Cursor 更新后需要重新注入
- **代码签名**: 可能破坏签名（macOS 可能需要重新签名）
- **备份重要**: 修改前必须备份

---

## 🔍 注入点分析

### 最佳注入点: `main.js`

```
/Applications/Cursor.app/Contents/Resources/app/out/main.js
```

这是 Electron 主进程入口，最早执行的代码。

### 或者: `bootstrap.js`

```
/Applications/Cursor.app/Contents/Resources/app/out/bootstrap.js
```

启动引导代码。

### 或者: `workbench.desktop.main.js`

```
/Applications/Cursor.app/Contents/Resources/app/out/vs/workbench/workbench.desktop.main.js
```

Workbench（UI）主入口。

---

## 💉 注入方法

### 方法 1: 在 main.js 头部注入 ⭐⭐⭐⭐⭐

```bash
#!/bin/bash

# 备份原文件
cp /Applications/Cursor.app/Contents/Resources/app/out/main.js \
   /Applications/Cursor.app/Contents/Resources/app/out/main.js.backup

# 创建注入代码
cat > /tmp/ortensia-inject.js << 'EOF'
// ============================================================================
// Ortensia Cursor Injector
// 注入时间: $(date)
// ============================================================================

(function() {
    console.log('🎉 Ortensia Injector loaded!');
    
    // 创建全局 API
    global.ortensiaAPI = {
        version: '1.0.0',
        
        // WebSocket 服务器（与 Ortensia 通信）
        startWebSocketServer: function(port = 9224) {
            const WebSocket = require('ws');
            const wss = new WebSocket.Server({ port });
            
            console.log(`✅ Ortensia WebSocket server started on port ${port}`);
            
            wss.on('connection', (ws) => {
                console.log('🔗 Ortensia connected');
                
                ws.on('message', (message) => {
                    try {
                        const cmd = JSON.parse(message);
                        console.log('📥 Received command:', cmd);
                        
                        // 处理命令
                        global.ortensiaAPI.handleCommand(cmd).then(result => {
                            ws.send(JSON.stringify({ success: true, result }));
                        }).catch(error => {
                            ws.send(JSON.stringify({ success: false, error: error.message }));
                        });
                        
                    } catch (error) {
                        console.error('❌ Error:', error);
                        ws.send(JSON.stringify({ success: false, error: error.message }));
                    }
                });
            });
            
            global.ortensiaWebSocketServer = wss;
            return wss;
        },
        
        // 命令处理器
        handleCommand: async function(cmd) {
            const { action, data } = cmd;
            
            switch (action) {
                case 'ping':
                    return 'pong';
                    
                case 'getVersion':
                    return global.ortensiaAPI.version;
                    
                case 'executeVSCodeCommand':
                    // 需要在渲染进程中执行
                    return await this.executeInRenderer(
                        `vscode.commands.executeCommand('${data.command}', ...${JSON.stringify(data.args || [])})`
                    );
                    
                case 'getCommands':
                    return await this.executeInRenderer(
                        `vscode.commands.getCommands(true)`
                    );
                    
                default:
                    throw new Error(`Unknown action: ${action}`);
            }
        },
        
        // 在渲染进程中执行代码
        executeInRenderer: async function(code) {
            // 获取当前焦点窗口
            const { BrowserWindow } = require('electron');
            const win = BrowserWindow.getFocusedWindow() || BrowserWindow.getAllWindows()[0];
            
            if (!win) {
                throw new Error('No window available');
            }
            
            // 执行代码
            return await win.webContents.executeJavaScript(code);
        }
    };
    
    // 自动启动 WebSocket 服务器
    setTimeout(() => {
        try {
            global.ortensiaAPI.startWebSocketServer(9224);
        } catch (error) {
            console.error('❌ Failed to start Ortensia WebSocket:', error);
        }
    }, 5000); // 延迟 5 秒，等 Cursor 完全启动
    
    console.log('✅ Ortensia API ready');
    console.log('📡 WebSocket server will start in 5 seconds on port 9224');
    
})();

// ============================================================================
// 原始 main.js 代码从这里开始
// ============================================================================

EOF

# 将注入代码添加到 main.js 开头
cat /tmp/ortensia-inject.js \
    /Applications/Cursor.app/Contents/Resources/app/out/main.js.backup \
    > /Applications/Cursor.app/Contents/Resources/app/out/main.js

echo "✅ 注入完成！"
echo "📝 备份文件: main.js.backup"
echo "🚀 重启 Cursor 生效"
```

---

### 方法 2: 使用独立文件注入 ⭐⭐⭐⭐⭐ (推荐)

更优雅的方式：创建独立的注入文件，然后在 `main.js` 中 require。

```bash
#!/bin/bash

# 1. 创建注入文件
cat > /Applications/Cursor.app/Contents/Resources/app/out/ortensia-injector.js << 'EOF'
// Ortensia Injector
// 完整的注入代码（同上）
EOF

# 2. 备份 main.js
cp /Applications/Cursor.app/Contents/Resources/app/out/main.js \
   /Applications/Cursor.app/Contents/Resources/app/out/main.js.backup

# 3. 在 main.js 头部添加 require
echo "require('./ortensia-injector.js');" | \
    cat - /Applications/Cursor.app/Contents/Resources/app/out/main.js.backup \
    > /Applications/Cursor.app/Contents/Resources/app/out/main.js

echo "✅ 注入完成！"
```

**优势**：
- 代码分离，易于维护
- 修改注入代码不需要重新处理 main.js
- 容易卸载（删除文件 + 恢复 main.js）

---

## 🚀 完整注入脚本

我现在就帮你创建完整的注入脚本！

### 功能列表

注入后 Cursor 会有：

1. **WebSocket 服务器** (端口 9224)
   - 与 Ortensia Python 通信
   
2. **命令执行**
   - 执行任何 VSCode 命令
   - 在渲染进程中执行 JavaScript
   
3. **编辑器控制**
   - 插入代码
   - 获取内容
   - 打开文件
   
4. **AI 集成**
   - 发送提示到 Cursor AI
   - 获取 AI 响应

---

## ⚠️ 重要注意事项

### 1. 代码签名

修改后 Cursor 的签名会失效。需要重新签名或允许运行未签名应用：

```bash
# 移除签名（允许修改后的代码运行）
sudo codesign --remove-signature /Applications/Cursor.app

# 或者重新签名（需要开发者证书）
codesign --force --deep --sign - /Applications/Cursor.app
```

### 2. SIP (System Integrity Protection)

**好消息**: 修改 `/Applications/Cursor.app` **不受 SIP 保护**！

只有系统目录（如 `/System/`）才受保护。

### 3. Cursor 更新

每次 Cursor 更新后，修改会被覆盖，需要重新注入。

**解决方案**: 创建自动注入脚本，更新后重新运行。

---

## 🔧 自动化脚本

### 安装脚本

```bash
#!/bin/bash
# install-ortensia-injector.sh

set -e

CURSOR_APP="/Applications/Cursor.app"
CURSOR_RESOURCES="$CURSOR_APP/Contents/Resources/app"
MAIN_JS="$CURSOR_RESOURCES/out/main.js"
INJECTOR_JS="$CURSOR_RESOURCES/out/ortensia-injector.js"

echo "🔧 安装 Ortensia Injector"
echo ""

# 检查 Cursor 是否存在
if [ ! -d "$CURSOR_APP" ]; then
    echo "❌ 找不到 Cursor.app"
    exit 1
fi

# 备份 main.js（如果还没备份）
if [ ! -f "$MAIN_JS.backup" ]; then
    echo "📦 备份 main.js..."
    cp "$MAIN_JS" "$MAIN_JS.backup"
fi

# 创建注入文件
echo "📝 创建注入文件..."
cat > "$INJECTOR_JS" << 'INJECT_EOF'
// Ortensia Injector
// 完整代码...
INJECT_EOF

# 修改 main.js
echo "💉 注入 main.js..."
echo "require('./ortensia-injector.js');" | \
    cat - "$MAIN_JS.backup" > "$MAIN_JS"

# 重新签名
echo "🔏 重新签名..."
codesign --remove-signature "$CURSOR_APP" 2>/dev/null || true
codesign --force --deep --sign - "$CURSOR_APP"

echo ""
echo "✅ 安装完成！"
echo ""
echo "📝 文件位置:"
echo "  - 注入代码: $INJECTOR_JS"
echo "  - 备份文件: $MAIN_JS.backup"
echo ""
echo "🚀 重启 Cursor 生效"
echo ""
```

### 卸载脚本

```bash
#!/bin/bash
# uninstall-ortensia-injector.sh

CURSOR_APP="/Applications/Cursor.app"
CURSOR_RESOURCES="$CURSOR_APP/Contents/Resources/app"
MAIN_JS="$CURSOR_RESOURCES/out/main.js"
INJECTOR_JS="$CURSOR_RESOURCES/out/ortensia-injector.js"

echo "🗑️  卸载 Ortensia Injector"
echo ""

# 恢复 main.js
if [ -f "$MAIN_JS.backup" ]; then
    echo "♻️  恢复 main.js..."
    mv "$MAIN_JS.backup" "$MAIN_JS"
fi

# 删除注入文件
if [ -f "$INJECTOR_JS" ]; then
    echo "🗑️  删除注入文件..."
    rm "$INJECTOR_JS"
fi

# 重新签名
echo "🔏 重新签名..."
codesign --remove-signature "$CURSOR_APP" 2>/dev/null || true
codesign --force --deep --sign - "$CURSOR_APP"

echo ""
echo "✅ 卸载完成！"
echo "🚀 重启 Cursor 生效"
echo ""
```

---

## 🎯 与测试扩展对比

| 特性 | 注入代码 | VSCode 扩展 |
|------|---------|------------|
| **访问内部 API** | ✅ 完全访问 | ❌ 受限 |
| **控制主进程** | ✅ 可以 | ❌ 不能 |
| **Electron API** | ✅ 完全访问 | ❌ 有限 |
| **更新后** | ❌ 需要重新注入 | ✅ 无需修改 |
| **安装** | ⚠️ 需要修改应用 | ✅ 简单安装 |
| **安全性** | ⚠️ 破坏签名 | ✅ 安全 |
| **维护** | ⚠️ 需要管理 | ✅ 自动 |

---

## 💡 推荐策略

### 混合方案 ⭐⭐⭐⭐⭐

**同时使用两种方法**：

1. **代码注入**: 底层控制，访问内部 API
2. **VSCode 扩展**: 上层逻辑，易于维护

```
Ortensia (Python)
       ↓ WebSocket
注入代码 (主进程)
   ↓         ↓
Cursor    VSCode 扩展
内部 API   标准 API
```

---

## 🚀 现在就试试

### 选项 A: 先测试扩展

先用测试扩展看看有哪些命令可用，再决定是否需要注入。

### 选项 B: 直接注入

如果你想要完全控制，立即创建注入脚本。

### 选项 C: 两个都做

测试扩展了解 API，注入代码实现深度控制。

---

**要我创建完整的注入脚本吗？** 

包括：
- ✅ 自动安装脚本
- ✅ 完整注入代码
- ✅ WebSocket 服务器
- ✅ Python 客户端
- ✅ 自动卸载脚本
- ✅ 更新后自动重新注入

预计 30 分钟完成！🚀

