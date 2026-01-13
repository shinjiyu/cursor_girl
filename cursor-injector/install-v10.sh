#!/bin/bash
# V11.2: 支持广播/单播两种模式，当前使用广播模式 + JS 代码内检查

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
// ORTENSIA V11.2: 支持广播/单播协议，当前使用广播 + JS 代码内检查
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
        const fs = await import('fs');
        const os = await import('os');
        const path = await import('path');

        function readCentralServerFromFile() {
            try {
                const home = os.homedir();

                // macOS GUI 启动时 env 可能不可用，因此提供本地配置文件兜底
                const candidates = [
                    // 1) macOS 推荐路径
                    path.join(home, 'Library', 'Application Support', 'Ortensia', 'central_server.txt'),
                    // 2) 通用隐藏文件
                    path.join(home, '.ortensia_server'),
                    // 3) 通用 config 目录
                    path.join(home, '.config', 'ortensia', 'central_server.txt'),
                    // 4) 项目内（可选）
                    path.join(process.cwd(), '.ortensia', 'central_server.txt'),
                ];

                for (const p of candidates) {
                    try {
                        if (!fs.existsSync(p)) continue;
                        const raw = fs.readFileSync(p, 'utf8');
                        const url = (raw || '').trim();
                        if (url) {
                            return { url, path: p };
                        }
                    } catch (e) {
                        // ignore candidate read errors
                    }
                }
            } catch (e) {
                // ignore
            }
            return null;
        }

        const DEFAULT_CENTRAL_SERVER_URL = 'ws://localhost:8765';
        let CENTRAL_SERVER_URL = null;
        let CENTRAL_SERVER_SOURCE = null;

        if (process.env.ORTENSIA_SERVER && String(process.env.ORTENSIA_SERVER).trim()) {
            CENTRAL_SERVER_URL = String(process.env.ORTENSIA_SERVER).trim();
            CENTRAL_SERVER_SOURCE = 'env:ORTENSIA_SERVER';
        } else {
            const fileCfg = readCentralServerFromFile();
            if (fileCfg && fileCfg.url) {
                CENTRAL_SERVER_URL = fileCfg.url;
                CENTRAL_SERVER_SOURCE = `file:${fileCfg.path}`;
            }
        }

        if (!CENTRAL_SERVER_URL) {
            CENTRAL_SERVER_URL = DEFAULT_CENTRAL_SERVER_URL;
            CENTRAL_SERVER_SOURCE = 'default';
        }

        if (CENTRAL_SERVER_SOURCE.startsWith('env:')) {
            log(`💡 使用环境变量配置的服务器地址: ${CENTRAL_SERVER_URL}`);
        } else if (CENTRAL_SERVER_SOURCE.startsWith('file:')) {
            log(`💡 使用本地配置文件的服务器地址: ${CENTRAL_SERVER_URL}`);
            log(`   配置文件: ${CENTRAL_SERVER_SOURCE.substring(5)}`);
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
        
        // V11: 不再需要设置 ORTENSIA_INJECT_ID
        
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
        
        /**
         * V11.2: 通用 JavaScript 执行器
         * 
         * 支持三种模式：
         *   1. window_index（数字）：单播，直接指定窗口
         *   2. conversation_id（字符串）：单播，自动查找匹配的窗口
         *   3. 都不指定：广播到所有窗口
         * 
         * 注：当前实现使用广播模式 + JS 代码内检查
         */
        async function handleExecuteJs(fromId, payload) {
            const code = payload.code || '';
            const requestId = payload.request_id || 'unknown';
            const windowIndex = payload.window_index;
            const conversationId = payload.conversation_id;
            
            log(`🔧 [ExecuteJS] 收到执行请求: ${requestId.substring(0, 30)}... (from=${fromId}, window_index=${windowIndex}, conversation_id=${conversationId ? conversationId.substring(0, 8) : 'null'})`);
            
            try {
                // 获取 BrowserWindow
                const electron = await import('electron');
                const windows = electron.BrowserWindow.getAllWindows();
                
                if (windows.length === 0) {
                    throw new Error('没有打开的窗口');
                }
                
                let result;
                let targetIndex = null;
                
                // 优先级 1: 如果指定了 window_index，直接使用（单播模式）
                if (windowIndex !== null && windowIndex !== undefined) {
                    if (windowIndex < 0 || windowIndex >= windows.length) {
                        throw new Error('窗口索引超出范围: ' + windowIndex + ' (总共 ' + windows.length + ' 个窗口)');
                    }
                    targetIndex = windowIndex;
                    log('📍 [单播-索引] 使用窗口 [' + targetIndex + ']');
                }
                // 优先级 2: 如果指定了 conversation_id，查找匹配的窗口（单播模式）
                else if (conversationId) {
                    log('🔍 [单播-查找] 查找 conversation_id: ' + conversationId);
                    
                    const extractConvIdCode = '(() => { const el = document.querySelector(\'[id^="composer-bottom-add-context-"]\'); if (!el) return JSON.stringify({ found: false }); const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/); return JSON.stringify({ found: true, conversation_id: match ? match[1] : null }); })()';
                    
                    for (let i = 0; i < windows.length; i++) {
                        try {
                            const convResult = await windows[i].webContents.executeJavaScript(extractConvIdCode);
                            const convData = JSON.parse(convResult);
                            const windowConvId = convData.found && convData.conversation_id ? convData.conversation_id : null;
                            
                            log('  窗口 [' + i + ']: conversation_id = ' + windowConvId);
                            
                            if (windowConvId === conversationId) {
                                targetIndex = i;
                                log('✅ [单播-查找] 找到匹配窗口: [' + i + ']');
                                break;
                            }
                        } catch (err) {
                            log('  ⚠️  窗口 [' + i + '] 查询失败: ' + err.message);
                        }
                    }
                    
                    if (targetIndex === null) {
                        throw new Error('未找到 conversation_id 为 ' + conversationId + ' 的窗口');
                    }
                }
                
                // 执行逻辑
                if (targetIndex !== null) {
                    // 单播模式：只在指定窗口执行
                    log('📍 [单播执行] 窗口 [' + targetIndex + ']');
                    const targetWindow = windows[targetIndex];
                    result = await targetWindow.webContents.executeJavaScript(code);
                } else {
                    // 广播模式：在所有窗口执行，返回字典
                    log('📢 [广播模式] 在所有 ' + windows.length + ' 个窗口执行');
                    const results = {};
                    
                    for (let i = 0; i < windows.length; i++) {
                        try {
                            const windowResult = await windows[i].webContents.executeJavaScript(code);
                            results[i] = windowResult;
                            log('  ✅ 窗口 [' + i + '] 执行成功');
                        } catch (err) {
                            results[i] = { error: err.message };
                            log('  ❌ 窗口 [' + i + '] 执行失败: ' + err.message);
                        }
                    }
                    
                    result = results;
                }
                
                // 尝试解析结果（如果是 JSON 字符串）
                let parsedResult;
                try {
                    parsedResult = JSON.parse(result);
                } catch {
                    parsedResult = result;
                }
                
                // 发送响应
                const response = {
                    type: 'execute_js_result',
                    from: injectId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: true,
                        result: parsedResult,
                        request_id: requestId
                    }
                };
                
                sendToCentral(response);
                log(`✅ [ExecuteJS] 执行成功: ${requestId}`);
                
            } catch (error) {
                log(`❌ [ExecuteJS] 执行错误: ${error.message}`);
                
                const errorResponse = {
                    type: 'execute_js_result',
                    from: injectId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: false,
                        error: error.message,
                        request_id: requestId
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
                    
                    case 'execute_js':
                        await handleExecuteJs(from, payload);
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
echo "V11.2 新功能："
echo "  📡 支持三种窗口定位模式："
echo "     • window_index: 单播，直接指定窗口索引"
echo "     • conversation_id: 单播，inject 自动查找窗口"
echo "     • 都不指定: 广播到所有窗口"
echo "  🎯 当前使用：广播模式 + JS 代码内检查"
echo ""
echo "请重启 Cursor 以使更改生效"
echo ""
echo "日志位置: /tmp/cursor_ortensia.log"
echo "查看日志: tail -f /tmp/cursor_ortensia.log"
echo ""

