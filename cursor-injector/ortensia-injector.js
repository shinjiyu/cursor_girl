// ============================================================================
// Ortensia Cursor Injector - Minimal Version
// 注入最小化的代码：只有 WebSocket 服务器 + 动态执行能力
// ============================================================================

(async function() {
    // ES Module 兼容：动态导入
    const { default: WebSocket } = await import('ws');
    const { BrowserWindow } = await import('electron');
    
    console.log('');
    console.log('='.repeat(80));
    console.log('  🎉 Ortensia Cursor Injector');
    console.log('  Version: 1.0.0 (Minimal)');
    console.log('='.repeat(80));
    console.log('');
    
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
                        console.log('📥 Received:', data.action || 'eval');
                        
                        let result;
                        
                        // 如果是纯 JS 代码，直接执行
                        if (typeof data === 'string' || data.code) {
                            const code = typeof data === 'string' ? data : data.code;
                            result = await executeCode(code, data.context || 'main');
                        } 
                        // 如果是命令对象
                        else if (data.action) {
                            result = await handleAction(data);
                        }
                        
                        ws.send(JSON.stringify({ 
                            success: true, 
                            result: result 
                        }));
                        
                        console.log('✅ Executed successfully');
                        
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
        }
    }
    
    // ========== 代码执行 ==========
    
    /**
     * 在指定上下文中执行代码
     * @param {string} code - 要执行的 JavaScript 代码
     * @param {string} context - 执行上下文: 'main' | 'renderer'
     */
    async function executeCode(code, context = 'main') {
        if (context === 'renderer') {
            // 在渲染进程中执行
            return await executeInRenderer(code);
        } else {
            // 在主进程中执行
            return eval(code);
        }
    }
    
    /**
     * 在渲染进程中执行代码
     */
    async function executeInRenderer(code) {
        const win = BrowserWindow.getFocusedWindow() || 
                    BrowserWindow.getAllWindows()[0];
        
        if (!win) {
            throw new Error('No window available');
        }
        
        return await win.webContents.executeJavaScript(code);
    }
    
    // ========== 内置命令 ==========
    
    async function handleAction(data) {
        const { action, params } = data;
        
        switch (action) {
            case 'ping':
                return 'pong';
                
            case 'getVersion':
                return '1.0.0';
                
            case 'eval':
                return await executeCode(params.code, params.context);
                
            case 'evalInRenderer':
                return await executeInRenderer(params.code);
                
            case 'getWindows':
                return BrowserWindow.getAllWindows().map(win => ({
                    id: win.id,
                    title: win.getTitle(),
                    focused: win.isFocused()
                }));
                
            case 'executeVSCodeCommand':
                // 在渲染进程中执行 VSCode 命令
                return await executeInRenderer(
                    `vscode.commands.executeCommand('${params.command}', ${JSON.stringify(params.args || [])})`
                );
                
            case 'getVSCodeCommands':
                // 获取所有 VSCode 命令
                return await executeInRenderer(
                    `vscode.commands.getCommands(true)`
                );
                
            default:
                throw new Error(`Unknown action: ${action}`);
        }
    }
    
    // ========== 暴露全局 API ==========
    
    global.ortensiaAPI = {
        version: '1.0.0',
        executeCode,
        executeInRenderer,
        getWebSocketServer: () => wss
    };
    
    // ========== 启动 ==========
    
    // 延迟启动，等待 Cursor 完全加载
    setTimeout(() => {
        startWebSocketServer();
        console.log('✅ Ortensia Injector ready');
        console.log('💡 You can now connect from Python using:');
        console.log('   python ortensia_cursor_client.py');
        console.log('');
    }, 3000);
    
})();

