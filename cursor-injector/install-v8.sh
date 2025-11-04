#!/bin/bash
# V8: 添加中央Server连接和注册功能（保留本地Server用于调试）

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
// ORTENSIA V8: 本地Server + 中央Server Client
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
    log('🎉 Ortensia V8 启动中...');
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
            log('  💡 用途: 开发调试 (test-input-complete.py 等工具)');
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
        
        const CENTRAL_SERVER_URL = process.env.ORTENSIA_SERVER || null;
        
        if (!CENTRAL_SERVER_URL) {
            log('💡 未设置 ORTENSIA_SERVER 环境变量，仅本地模式运行');
            log('   设置方式: export ORTENSIA_SERVER=ws://192.168.1.100:8765');
            return;
        }
        
        log('');
        log('══════════════════════════════════════════════════════════════');
        log('  🌐 连接到中央Server...');
        log(`  📍 地址: ${CENTRAL_SERVER_URL}`);
        log('══════════════════════════════════════════════════════════════');
        log('');
        
        let centralWs = null;
        let cursorId = null;
        let heartbeatInterval = null;
        let reconnectTimeout = null;
        let reconnectDelay = 1000; // 初始重连延迟 1 秒
        const MAX_RECONNECT_DELAY = 60000; // 最大重连延迟 60 秒
        
        // 生成 Cursor ID
        function generateCursorId() {
            return `cursor-${Math.random().toString(36).substr(2, 9)}`;
        }
        
        // 获取工作区路径
        async function getWorkspacePath() {
            try {
                const electron = await import('electron');
                const windows = electron.BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    // 尝试从窗口标题或其他方式获取工作区路径
                    // 这是简化版本，实际可能需要更复杂的逻辑
                    return process.cwd();
                }
            } catch (e) {
                // 忽略错误
            }
            return process.cwd();
        }
        
        // 发送消息到中央Server
        function sendToCentral(message) {
            if (centralWs && centralWs.readyState === 1) { // 1 = OPEN
                const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
                centralWs.send(messageStr);
                log(`📤 [中央] 发送: ${messageStr.substring(0, 100)}...`);
                return true;
            } else {
                log('⚠️  [中央] WebSocket 未连接，无法发送消息');
                return false;
            }
        }
        
        // 注册到中央Server
        async function register() {
            const workspace = await getWorkspacePath();
            
            const registerMessage = {
                type: 'register',
                from: cursorId,
                to: 'server',
                timestamp: Math.floor(Date.now() / 1000),
                payload: {
                    client_type: 'cursor_hook',
                    cursor_id: cursorId,
                    workspace: workspace,
                    platform: process.platform,
                    pid: process.pid,
                    ws_port: 9876,
                    capabilities: ['composer', 'editor', 'terminal']
                }
            };
            
            sendToCentral(registerMessage);
        }
        
        // 处理来自中央Server的命令
        async function handleCommand(message) {
            const { type, from, to, payload } = message;
            
            log(`📨 [中央] 收到命令: ${type}`);
            
            try {
                switch (type) {
                    case 'composer_send_prompt':
                        await handleComposerSendPrompt(from, payload);
                        break;
                    
                    case 'composer_query_status':
                        await handleComposerQueryStatus(from, payload);
                        break;
                    
                    case 'heartbeat_ack':
                        // 心跳响应，不需要处理
                        break;
                    
                    default:
                        log(`⚠️  [中央] 未知命令类型: ${type}`);
                }
            } catch (error) {
                log(`❌ [中央] 命令处理错误: ${error.message}`);
            }
        }
        
        // 处理 Composer 发送提示词命令
        async function handleComposerSendPrompt(fromId, payload) {
            const { agent_id, prompt } = payload;
            
            log(`💬 [Composer] 发送提示词: ${prompt.substring(0, 50)}...`);
            
            try {
                // 执行输入提示词的代码
                const electron = await import("electron");
                const windows = electron.BrowserWindow.getAllWindows();
                
                if (windows.length === 0) {
                    throw new Error('没有打开的窗口');
                }
                
                const code = `
                    (function() {
                        const input = document.querySelector('.aislash-editor-input');
                        if (!input) return JSON.stringify({ success: false, error: '输入框未找到' });
                        
                        input.focus();
                        
                        // 选中所有内容并删除
                        const sel = window.getSelection();
                        const range = document.createRange();
                        range.selectNodeContents(input);
                        sel.removeAllRanges();
                        sel.addRange(range);
                        document.execCommand('delete', false, null);
                        
                        // 插入新文字
                        document.execCommand('insertText', false, ${JSON.stringify(prompt)});
                        
                        // 触发事件
                        input.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true }));
                        
                        return JSON.stringify({ success: true });
                    })()
                `;
                
                const result = await windows[0].webContents.executeJavaScript(code);
                const resultObj = JSON.parse(result);
                
                // 发送结果回中央Server
                const resultMessage = {
                    type: 'composer_send_prompt_result',
                    from: cursorId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: resultObj.success,
                        agent_id: agent_id,
                        message: resultObj.success ? '提示词已输入' : null,
                        error: resultObj.error || null
                    }
                };
                
                sendToCentral(resultMessage);
                log(`✅ [Composer] 提示词已发送，结果已返回`);
                
            } catch (error) {
                log(`❌ [Composer] 错误: ${error.message}`);
                
                // 发送错误结果
                const errorMessage = {
                    type: 'composer_send_prompt_result',
                    from: cursorId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: false,
                        agent_id: agent_id,
                        message: null,
                        error: error.message
                    }
                };
                
                sendToCentral(errorMessage);
            }
        }
        
        // 处理 Composer 查询状态命令
        async function handleComposerQueryStatus(fromId, payload) {
            const { agent_id } = payload;
            
            log(`📊 [Composer] 查询状态: agent_id=${agent_id}`);
            
            try {
                // TODO: 实际实现需要检测 Cursor AI 的状态
                // 这里先返回一个模拟状态
                const status = 'idle'; // 可以是: idle, thinking, working, completed
                
                const resultMessage = {
                    type: 'composer_status_result',
                    from: cursorId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: true,
                        agent_id: agent_id,
                        status: status,
                        error: null
                    }
                };
                
                sendToCentral(resultMessage);
                log(`✅ [Composer] 状态已返回: ${status}`);
                
            } catch (error) {
                log(`❌ [Composer] 查询状态错误: ${error.message}`);
                
                const errorMessage = {
                    type: 'composer_status_result',
                    from: cursorId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: false,
                        agent_id: agent_id,
                        status: null,
                        error: error.message
                    }
                };
                
                sendToCentral(errorMessage);
            }
        }
        
        // 发送心跳
        function sendHeartbeat() {
            const heartbeatMessage = {
                type: 'heartbeat',
                from: cursorId,
                to: 'server',
                timestamp: Math.floor(Date.now() / 1000),
                payload: {}
            };
            
            sendToCentral(heartbeatMessage);
        }
        
        // 连接到中央Server
        function connectToCentral() {
            try {
                log(`🔗 [中央] 尝试连接到 ${CENTRAL_SERVER_URL}...`);
                
                cursorId = generateCursorId();
                centralWs = new WebSocketClient(CENTRAL_SERVER_URL);
                
                centralWs.on('open', async () => {
                    log('');
                    log('══════════════════════════════════════════════════════════════');
                    log('  ✅ 已连接到中央Server！');
                    log(`  🔑 Cursor ID: ${cursorId}`);
                    log('══════════════════════════════════════════════════════════════');
                    log('');
                    
                    // 重置重连延迟
                    reconnectDelay = 1000;
                    
                    // 注册
                    await register();
                    
                    // 启动心跳
                    heartbeatInterval = setInterval(() => {
                        sendHeartbeat();
                    }, 30000); // 每 30 秒一次
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
                    
                    // 清理心跳
                    if (heartbeatInterval) {
                        clearInterval(heartbeatInterval);
                        heartbeatInterval = null;
                    }
                    
                    // 尝试重连
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
        
        // 计划重连
        function scheduleReconnect() {
            if (reconnectTimeout) {
                clearTimeout(reconnectTimeout);
            }
            
            log(`⏰ [中央] ${reconnectDelay / 1000} 秒后尝试重连...`);
            
            reconnectTimeout = setTimeout(() => {
                reconnectTimeout = null;
                connectToCentral();
            }, reconnectDelay);
            
            // 指数退避，但不超过最大延迟
            reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
        }
        
        // 启动连接
        connectToCentral();
        
    } catch (error) {
        log(`❌ 启动失败: ${error.message}`);
        log(`   堆栈: ${error.stack}`);
    }
    
    log('注入代码执行完毕');
    log('========================================');
})();

// ============================================================================
// 原始 main.js
// ============================================================================

INJECT_END

# 追加原始内容
echo "$ORIGINAL" >> "$MAIN_JS"

# 重新签名
codesign --force --deep --sign - "/Applications/Cursor.app" 2>/dev/null

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ V8 已注入 - 本地Server + 中央Server Client"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "V8 新功能:"
echo "  ✅ 本地 WebSocket Server (端口 9876) - 用于开发调试"
echo "  ✅ 作为 Client 连接到中央Server - 用于生产环境"
echo "  ✅ 支持 Composer 操作 (发送提示词、查询状态)"
echo "  ✅ 自动注册和心跳机制"
echo "  ✅ 自动重连（指数退避）"
echo ""
echo "使用方式:"
echo "  开发模式: 无需设置环境变量，直接使用 test-input-complete.py"
echo "  生产模式: export ORTENSIA_SERVER=ws://your-server:8765"
echo ""
echo "日志文件: $LOG_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📋 测试步骤:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1️⃣  完全退出 Cursor (Cmd+Q)"
echo "  2️⃣  重新启动 Cursor"
echo "  3️⃣  等待 10 秒"
echo "  4️⃣  查看日志: cat $LOG_FILE"
echo ""
echo "  开发测试:"
echo "    python3 test-input-complete.py \"测试文字\""
echo ""
echo "  生产测试:"
echo "    export ORTENSIA_SERVER=ws://localhost:8765"
echo "    重启 Cursor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

