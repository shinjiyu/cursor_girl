#!/bin/bash
# V10: 添加 get_conversation_id 协议，支持通过 conversation_id 关联 inject 和 hook

MAIN_JS="/Applications/Cursor.app/Contents/Resources/app/out/main.js"
BACKUP_JS="/Applications/Cursor.app/Contents/Resources/app/out/main.js.ortensia.backup"
LOG_FILE="/tmp/cursor_ortensia.log"

# 清理旧日志
rm -f "$LOG_FILE"

# 创建备份（如果不存在）
if [ ! -f "$BACKUP_JS" ]; then
    echo "创建备份..."
    cp "$MAIN_JS" "$BACKUP_JS"
else
    echo "使用现有备份..."
fi

# 恢复备份
cp "$BACKUP_JS" "$MAIN_JS"

# 读取原始内容
ORIGINAL=$(cat "$BACKUP_JS")

# 创建新 main.js
cat > "$MAIN_JS" << 'INJECT_END'
// ============================================================================
// ORTENSIA V10: 添加 get_conversation_id 协议
// ============================================================================
(async function() {
    const fs = await import('fs');
    const path = await import('path');
    const LOG = '/tmp/cursor_ortensia.log';
    
    function log(msg) {
        const line = `[${new Date().toISOString()}] [PID:${process.pid}] ${msg}\n`;
        try {
            fs.appendFileSync(LOG, line);
            console.log(`[ORTENSIA] ${msg}`);
        } catch (e) {
            console.error('[ORTENSIA] Log error:', e);
        }
    }
    
    log('========================================');
    log('🎉 Ortensia V10 启动中...');
    log(`进程 ID: ${process.pid}`);
    
    // 等待 Electron 初始化
    await new Promise(resolve => setTimeout(resolve, 3000));
    log('⏱️  等待完成，开始初始化...');
    
    try {
        const ws_module = await import('ws');
        const WebSocketServer = ws_module.WebSocketServer || ws_module.Server;
        const WebSocketClient = ws_module.default || ws_module.WebSocket || ws_module;
        
        log('✅ WebSocket 模块加载成功');
        
        // ====================================================================
        // 第一部分：本地 WebSocket Server (用于开发调试)
        // ====================================================================
        
        log('📡 启动本地 WebSocket Server (端口 9876)...');
        const localServer = new WebSocketServer({ port: 9876 });
        
        localServer.on('listening', () => {
            log('');
            log('══════════════════════════════════════════════════════════════');
            log('  ✅ 本地 WebSocket Server 启动成功！');
            log('  📍 端口: 9876');
            log('  💡 用途: 开发调试 (test_complete_flow.py 等工具)');
            log('══════════════════════════════════════════════════════════════');
            log('');
        });
        
        localServer.on('connection', (ws) => {
            log('🔗 [本地] 客户端已连接');
            
            ws.on('message', async (message) => {
                try {
                    const code = message.toString();
                    log(`📥 [本地] 收到代码: ${code.substring(0, 50)}...`);
                    
                    let result = eval(code);
                    
                    // 自动等待 Promise
                    if (result && typeof result.then === 'function') {
                        result = await result;
                    }
                    
                    const response = { success: true, result: String(result) };
                    ws.send(JSON.stringify(response));
                    
                    log(`✅ [本地] 执行成功: ${String(result).substring(0, 100)}`);
                } catch (error) {
                    log(`❌ [本地] 执行错误: ${error.message}`);
                    ws.send(JSON.stringify({ success: false, error: error.message }));
                }
            });
            
            ws.on('close', () => {
                log('🔌 [本地] 客户端断开连接');
            });
        });
        
        localServer.on('error', (error) => {
            if (error.code === 'EADDRINUSE') {
                log('⚠️  [本地] 端口 9876 已被占用，跳过本地Server');
            } else {
                log(`❌ [本地] Server 错误: ${error.message}`);
            }
        });
        
        // ====================================================================
        // 第二部分：作为 Client 连接到中央Server
        // ====================================================================
        
        const CENTRAL_SERVER_URL = process.env.ORTENSIA_SERVER || 'ws://localhost:8765';
        
        if (process.env.ORTENSIA_SERVER) {
            log(`💡 使用环境变量配置的服务器地址: ${CENTRAL_SERVER_URL}`);
        } else {
            log(`💡 使用默认服务器地址: ${CENTRAL_SERVER_URL}`);
        }
        
        log('');
        log('══════════════════════════════════════════════════════════════');
        log('  🌐 连接到中央Server...');
        log(`  📍 地址: ${CENTRAL_SERVER_URL}`);
        log('══════════════════════════════════════════════════════════════');
        log('');
        
        let centralWs = null;
        let injectId = `inject-${process.pid}`;
        let heartbeatInterval = null;
        let reconnectTimeout = null;
        let reconnectDelay = 1000;
        const MAX_RECONNECT_DELAY = 60000;
        
        // 获取工作区路径
        async function getWorkspacePath() {
            try {
                const electron = await import('electron');
                const windows = electron.BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    return process.cwd();
                }
            } catch (e) {
                // 忽略错误
            }
            return process.cwd();
        }
        
        // ====================================================================
        // V10 新增：获取当前 conversation_id
        // ====================================================================
        
        async function getCurrentConversationId() {
            try {
                const electron = await import('electron');
                const windows = electron.BrowserWindow.getAllWindows();
                
                if (windows.length === 0) {
                    return null;
                }
                
                const code = `
                    (() => {
                        const el = document.querySelector('[id^="composer-bottom-add-context-"]');
                        if (!el) return JSON.stringify({ found: false });
                        
                        const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
                        return JSON.stringify({
                            found: true,
                            conversation_id: match ? match[1] : null
                        });
                    })()
                `;
                
                const result = await windows[0].webContents.executeJavaScript(code);
                const data = JSON.parse(result);
                
                if (data.found && data.conversation_id) {
                    return data.conversation_id;
                }
                
                return null;
            } catch (error) {
                log(`❌ [ConversationID] 提取失败: ${error.message}`);
                return null;
            }
        }
        
        // ====================================================================
        // V10 新增：处理 get_conversation_id 命令
        // ====================================================================
        
        async function handleGetConversationId(fromId, payload) {
            log(`🔍 [ConversationID] 收到查询请求: from=${fromId}`);
            
            try {
                const conversationId = await getCurrentConversationId();
                
                const response = {
                    type: 'get_conversation_id_result',
                    from: injectId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: conversationId !== null,
                        conversation_id: conversationId,
                        inject_id: injectId,
                        workspace: await getWorkspacePath()
                    }
                };
                
                sendToCentral(response);
                
                if (conversationId) {
                    log(`✅ [ConversationID] 返回: ${conversationId}`);
                } else {
                    log(`⚠️  [ConversationID] 未找到当前对话`);
                }
                
            } catch (error) {
                log(`❌ [ConversationID] 处理错误: ${error.message}`);
                
                const errorResponse = {
                    type: 'get_conversation_id_result',
                    from: injectId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: false,
                        conversation_id: null,
                        error: error.message
                    }
                };
                
                sendToCentral(errorResponse);
            }
        }
        
        // 发送消息到中央Server
        function sendToCentral(message) {
            if (centralWs && centralWs.readyState === 1) {
                try {
                    const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
                    centralWs.send(messageStr);
                    log(`📤 [中央] 发送: ${messageStr.substring(0, 100)}...`);
                    return true;
                } catch (error) {
                    log(`❌ [中央] 发送失败: ${error.message}`);
                    return false;
                }
            } else {
                log(`⚠️  [中央] WebSocket 未连接 (readyState: ${centralWs ? centralWs.readyState : 'null'})`);
                return false;
            }
        }
        
        // 注册到中央Server
        async function register() {
            const workspace = await getWorkspacePath();
            
            const registerMessage = {
                type: 'register',
                from: injectId,
                to: 'server',
                timestamp: Math.floor(Date.now() / 1000),
                payload: {
                    client_type: 'cursor_inject',
                    inject_id: injectId,
                    workspace: workspace,
                    platform: process.platform,
                    pid: process.pid,
                    ws_port: 9876,
                    capabilities: ['composer', 'editor', 'terminal', 'conversation_id']
                }
            };
            
            sendToCentral(registerMessage);
        }
        
        // ====================================================================
        // 命令处理函数（省略其他命令的实现，仅添加新命令）
        // ====================================================================
        
        async function handleCommand(message) {
            const { type, from, to, payload } = message;
            
            log(`📨 [中央] 收到命令: ${type}`);
            
            try {
                switch (type) {
                    case 'register_ack':
                        log(`✅ [中央] 注册成功`);
                        break;
                    
                    case 'get_conversation_id':
                        await handleGetConversationId(from, payload);
                        break;
                    
                    case 'heartbeat_ack':
                        // 心跳响应
                        break;
                    
                    default:
                        log(`⚠️  [中央] 未知命令类型: ${type}`);
                }
            } catch (error) {
                log(`❌ [中央] 命令处理错误: ${error.message}`);
            }
        }
        
        // ====================================================================
        // 连接和重连逻辑
        // ====================================================================
        
        function scheduleReconnect() {
            if (reconnectTimeout) {
                clearTimeout(reconnectTimeout);
            }
            
            log(`⏱️  ${reconnectDelay/1000} 秒后尝试重连...`);
            
            reconnectTimeout = setTimeout(() => {
                reconnectTimeout = null;
                connectToCentral();
            }, reconnectDelay);
            
            reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
        }
        
        async function connectToCentral() {
            try {
                log('🔗 [中央] 正在连接...');
                
                centralWs = new WebSocketClient(CENTRAL_SERVER_URL);
                
                centralWs.on('open', () => {
                    log('✅ [中央] 连接成功！');
                    reconnectDelay = 1000;
                    
                    register();
                    
                    if (heartbeatInterval) {
                        clearInterval(heartbeatInterval);
                    }
                    
                    heartbeatInterval = setInterval(() => {
                        if (centralWs && centralWs.readyState === 1) {
                            const heartbeat = {
                                type: 'heartbeat',
                                from: injectId,
                                to: 'server',
                                timestamp: Math.floor(Date.now() / 1000),
                                payload: {}
                            };
                            sendToCentral(heartbeat);
                        }
                    }, 30000);
                });
                
                centralWs.on('message', (data) => {
                    try {
                        const message = JSON.parse(data.toString());
                        handleCommand(message);
                    } catch (error) {
                        log(`❌ [中央] 消息解析错误: ${error.message}`);
                    }
                });
                
                centralWs.on('close', () => {
                    log('🔌 [中央] 连接已断开');
                    
                    if (heartbeatInterval) {
                        clearInterval(heartbeatInterval);
                        heartbeatInterval = null;
                    }
                    
                    scheduleReconnect();
                });
                
                centralWs.on('error', (error) => {
                    log(`❌ [中央] 连接错误: ${error.message}`);
                });
                
            } catch (error) {
                log(`❌ [中央] 连接失败: ${error.message}`);
                scheduleReconnect();
            }
        }
        
        // 启动连接
        connectToCentral();
        
        log('');
        log('══════════════════════════════════════════════════════════════');
        log('  🎉 Ortensia V10 初始化完成！');
        log('  ✅ 本地 Server: ws://localhost:9876');
        log(`  ✅ 中央 Server: ${CENTRAL_SERVER_URL}`);
        log(`  ✅ Inject ID: ${injectId}`);
        log('  🆕 支持 conversation_id 查询');
        log('══════════════════════════════════════════════════════════════');
        log('');
        
    } catch (error) {
        log(`❌ 初始化失败: ${error.message}`);
        log(error.stack);
    }
})();

// 原始 main.js 内容
INJECT_END

# 追加原始内容
cat "$BACKUP_JS" >> "$MAIN_JS"

echo ""
echo "✅ Ortensia V10 安装完成！"
echo ""
echo "新功能："
echo "  🆕 支持 get_conversation_id 协议"
echo "  🆕 Hook 可以使用 conversation_id 作为 ID"
echo "  🆕 服务器可以通过 conversation_id 关联 inject 和 hook"
echo ""
echo "请重启 Cursor 以使更改生效"
echo ""
echo "日志位置: /tmp/cursor_ortensia.log"
echo "查看日志: tail -f /tmp/cursor_ortensia.log"
echo ""

