#!/usr/bin/env node
/**
 * Node.js 集成注入器
 * 利用 ELECTRON_RUN_AS_NODE 环境变量注入代码
 * 
 * 使用方法：
 * ELECTRON_RUN_AS_NODE=1 /Applications/Cursor.app/Contents/MacOS/Cursor node-integration-injector.js
 */

console.log('🚀 Node.js Integration Injector');
console.log('================================');
console.log('');

// 检查 Node.js 是否可用
try {
    const fs = require('fs');
    const path = require('path');
    const os = require('os');
    
    console.log('✅ Node.js is available');
    console.log(`   Version: ${process.version}`);
    console.log(`   Platform: ${process.platform}`);
    console.log('');
    
    // 1. 创建注入脚本
    const injectCode = `
(function() {
    console.log('🎉 Ortensia injected via Node.js integration!');
    
    // 创建全局 API
    window.ortensiaAPI = {
        version: '1.0.0-node',
        
        sendToAI: function(prompt) {
            console.log('📤 Sending to Cursor AI:', prompt);
            
            // 模拟 Cmd+L 打开 AI
            document.dispatchEvent(new KeyboardEvent('keydown', {
                key: 'l',
                metaKey: true,
                bubbles: true
            }));
            
            setTimeout(() => {
                // 查找输入框
                const inputs = document.querySelectorAll('textarea, input');
                for (const input of inputs) {
                    if (input.offsetWidth > 0 && input.offsetHeight > 0) {
                        input.value = prompt;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        // 发送
                        input.dispatchEvent(new KeyboardEvent('keydown', {
                            key: 'Enter',
                            keyCode: 13,
                            bubbles: true
                        }));
                        
                        console.log('✅ Sent to AI');
                        break;
                    }
                }
            }, 500);
        },
        
        getEditor: function() {
            if (window.monaco && window.monaco.editor) {
                const editors = window.monaco.editor.getEditors();
                return editors[0];
            }
            return null;
        },
        
        insertCode: function(code) {
            const editor = this.getEditor();
            if (editor) {
                const position = editor.getPosition();
                editor.executeEdits('ortensia', [{
                    range: new window.monaco.Range(
                        position.lineNumber,
                        position.column,
                        position.lineNumber,
                        position.column
                    ),
                    text: code
                }]);
                console.log('✅ Code inserted');
                return true;
            }
            console.log('❌ Editor not found');
            return false;
        },
        
        // 创建 WebSocket 服务器（利用 Node.js）
        startServer: function() {
            try {
                const WebSocket = require('ws');
                const wss = new WebSocket.Server({ port: 9223 });
                
                wss.on('connection', (ws) => {
                    console.log('✅ Client connected to injected WebSocket');
                    
                    ws.on('message', (data) => {
                        const msg = JSON.parse(data);
                        console.log('📨 Received:', msg);
                        
                        switch (msg.type) {
                            case 'sendToAI':
                                this.sendToAI(msg.prompt);
                                break;
                            case 'insertCode':
                                this.insertCode(msg.code);
                                break;
                        }
                    });
                });
                
                console.log('✅ WebSocket server started on port 9223');
                return true;
            } catch (e) {
                console.log('❌ Failed to start server:', e.message);
                return false;
            }
        }
    };
    
    console.log('✅ Ortensia API ready!');
    console.log('   Usage:');
    console.log('   - ortensiaAPI.sendToAI("your prompt")');
    console.log('   - ortensiaAPI.insertCode("console.log()")');
    console.log('   - ortensiaAPI.startServer()');
})();
`;
    
    // 2. 将代码保存到 userData 目录
    const userDataDir = path.join(os.homedir(), 'Library/Application Support/Cursor');
    const ortensiaDir = path.join(userDataDir, 'ortensia');
    const injectFile = path.join(ortensiaDir, 'inject.js');
    
    // 创建目录
    if (!fs.existsSync(ortensiaDir)) {
        fs.mkdirSync(ortensiaDir, { recursive: true });
        console.log(`✅ Created directory: ${ortensiaDir}`);
    }
    
    // 写入注入脚本
    fs.writeFileSync(injectFile, injectCode);
    console.log(`✅ Injection script saved to:`);
    console.log(`   ${injectFile}`);
    console.log('');
    
    // 3. 创建启动脚本
    const launchScript = `#!/bin/bash
# Ortensia Cursor Launcher with Node.js integration

# 设置环境变量
export ELECTRON_RUN_AS_NODE=1
export ELECTRON_ENABLE_LOGGING=1

# 启动 Cursor
/Applications/Cursor.app/Contents/MacOS/Cursor &

# 等待 Cursor 启动
sleep 3

# 注入脚本（通过 Node.js）
node -e "
const script = require('fs').readFileSync('${injectFile}', 'utf8');
console.log('Injection script ready');
console.log('To inject, paste the script content in Cursor DevTools');
"

echo ""
echo "🎉 Cursor launched with Node.js integration!"
echo ""
echo "📝 To inject Ortensia API:"
echo "   1. Open DevTools in Cursor (Cmd+Shift+I)"
echo "   2. Paste the injection script from:"
echo "      ${injectFile}"
echo ""
`;
    
    const launchScriptPath = path.join(ortensiaDir, 'launch.sh');
    fs.writeFileSync(launchScriptPath, launchScript);
    fs.chmodSync(launchScriptPath, '755');
    
    console.log(`✅ Launch script created:`);
    console.log(`   ${launchScriptPath}`);
    console.log('');
    
    // 4. 显示使用说明
    console.log('================================');
    console.log('  📚 How to Use');
    console.log('================================');
    console.log('');
    console.log('Method 1: Manual injection');
    console.log('  1. Start Cursor normally');
    console.log('  2. Open DevTools (Cmd+Shift+I)');
    console.log('  3. Paste the script from:');
    console.log(`     ${injectFile}`);
    console.log('');
    console.log('Method 2: Use launch script');
    console.log(`  ${launchScriptPath}`);
    console.log('');
    console.log('Method 3: Integrate with Ortensia');
    console.log('  See: ortensia-integration.py');
    console.log('');
    
} catch (error) {
    console.log('❌ Error:', error.message);
    process.exit(1);
}

