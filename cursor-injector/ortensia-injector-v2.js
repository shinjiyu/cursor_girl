// ============================================================================
// Ortensia Cursor Injector v2 - CommonJS Version
// 使用 require() 而不是 import() 以确保兼容性
// ============================================================================

console.log('');
console.log('='.repeat(80));
console.log('  🎉 Ortensia Cursor Injector v2');
console.log('  Loading...');
console.log('='.repeat(80));
console.log('');

try {
    // 使用 require 而不是 import（更兼容 Electron 主进程）
    const WebSocket = require('ws');
    const { BrowserWindow } = require('electron');
    
    console.log('✅ Modules loaded successfully');
    
    // ========== WebSocket 服务器 ==========
    
    const PORT = 9224;
    let wss = null;
    
    function startWebSocketServer() {
        try {
            wss = new WebSocket.Server({ port: PORT });
            
            console.log(`✅ WebSocket server started on port ${PORT}`);
            console.log('📡 Waiting for Ortensia to connect...');
            console.log('');
            
            wss.on('connection', (ws) => {
                console.log('🔗 Ortensia connected');
                
                ws.on('message', async (message) => {
                    try {
                        const data = JSON.parse(message.toString());
                        console.log('📥 Received:', data.action || 'unknown');
                        
                        let response = { success: false };
                        
                        // 处理不同的 action
                        if (data.action === 'ping') {
                            response = { success: true, message: 'pong' };
                        } 
                        else if (data.action === 'eval') {
                            // 在主进程执行
                            const result = eval(data.code);
                            response = { success: true, result: JSON.stringify(result) };
                        }
                        else if (data.action === 'evalr') {
                            // 在渲染进程执行
                            const win = BrowserWindow.getFocusedWindow() || 
                                        BrowserWindow.getAllWindows()[0];
                            if (win) {
                                const result = await win.webContents.executeJavaScript(data.code);
                                response = { success: true, result: JSON.stringify(result) };
                            } else {
                                response = { success: false, error: 'No window available' };
                            }
                        }
                        else if (data.action === 'getCommands') {
                            // 在渲染进程获取命令
                            const win = BrowserWindow.getFocusedWindow() || 
                                        BrowserWindow.getAllWindows()[0];
                            if (win) {
                                const commands = await win.webContents.executeJavaScript(
                                    'vscode.commands.getCommands(true)'
                                );
                                response = { success: true, result: JSON.stringify(commands) };
                            } else {
                                response = { success: false, error: 'No window available' };
                            }
                        }
                        else {
                            response = { success: false, error: `Unknown action: ${data.action}` };
                        }
                        
                        ws.send(JSON.stringify(response));
                        console.log('✅ Response sent');
                        
                    } catch (error) {
                        console.error('❌ Error:', error.message);
                        ws.send(JSON.stringify({ 
                            success: false, 
                            error: error.message,
                            stack: error.stack
                        }));
                    }
                });
                
                ws.on('close', () => {
                    console.log('👋 Ortensia disconnected');
                });
                
                ws.on('error', (error) => {
                    console.error('❌ WebSocket error:', error);
                });
            });
            
            wss.on('error', (error) => {
                console.error('❌ Server error:', error);
            });
            
        } catch (error) {
            console.error('❌ Failed to start WebSocket server:', error);
            console.error('Stack:', error.stack);
        }
    }
    
    // ========== 暴露全局 API ==========
    
    global.ortensiaAPI = {
        version: '2.0.0',
        getWebSocketServer: () => wss,
        restart: () => {
            if (wss) {
                wss.close();
            }
            startWebSocketServer();
        }
    };
    
    // ========== 启动 ==========
    
    console.log('⏳ Starting in 3 seconds...');
    
    setTimeout(() => {
        startWebSocketServer();
        console.log('');
        console.log('✅ Ortensia Injector v2 is ready!');
        console.log('💡 Connect from Python:');
        console.log('   ./ortensia-cursor.sh ping');
        console.log('');
    }, 3000);
    
} catch (error) {
    console.error('');
    console.error('❌ FATAL ERROR in Ortensia Injector:');
    console.error('   ', error.message);
    console.error('   ', error.stack);
    console.error('');
}

