#!/bin/bash
# V9: 使用正确的选择器和操作流程（Editor tab + Cmd+I + 上箭头按钮）

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
// ORTENSIA V9: 正确的 DOM 操作（Editor tab + Cmd+I + 上箭头按钮）
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
    log('🎉 Ortensia V9 启动中...');
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
        
        // 🌸 中央服务器地址（支持环境变量配置）
        const CENTRAL_SERVER_URL = process.env.ORTENSIA_SERVER || 'ws://localhost:8765';
        
        if (process.env.ORTENSIA_SERVER) {
            log(`💡 使用环境变量配置的服务器地址: ${CENTRAL_SERVER_URL}`);
        } else {
            log(`💡 使用默认服务器地址: ${CENTRAL_SERVER_URL}`);
            log('   提示: 可通过环境变量修改: export ORTENSIA_SERVER=ws://your-server:8765');
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
        
        // ====================================================================
        // V9 新增：DOM 操作辅助函数
        // ====================================================================
        
        // 确保在 Editor tab
        async function ensureEditorTab(window) {
            const code = `
                (function() {
                    const tabs = document.querySelectorAll('.segmented-tab');
                    
                    if (tabs.length === 0) {
                        return JSON.stringify({ success: false, error: '未找到标签' });
                    }
                    
                    let editorTab = null;
                    for (const tab of tabs) {
                        const text = (tab.innerText || tab.textContent || '').toLowerCase();
                        if (text.includes('editor')) {
                            editorTab = tab;
                            break;
                        }
                    }
                    
                    if (!editorTab) {
                        return JSON.stringify({ success: false, error: '未找到 Editor 标签' });
                    }
                    
                    const isActive = editorTab.classList.contains('active') || 
                                   editorTab.getAttribute('aria-selected') === 'true';
                    
                    if (!isActive) {
                        editorTab.click();
                        return JSON.stringify({ success: true, switched: true });
                    }
                    
                    return JSON.stringify({ success: true, switched: false });
                })()
            `;
            
            const result = await window.webContents.executeJavaScript(code);
            return JSON.parse(result);
        }
        
        // 使用 Cmd+I 唤出 Composer
        async function invokeComposer(window) {
            const code = `
                (function() {
                    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
                    
                    const event = new KeyboardEvent('keydown', {
                        key: 'i',
                        code: 'KeyI',
                        keyCode: 73,
                        which: 73,
                        metaKey: isMac,
                        ctrlKey: !isMac,
                        bubbles: true,
                        cancelable: true
                    });
                    
                    document.dispatchEvent(event);
                    
                    return JSON.stringify({ success: true });
                })()
            `;
            
            const result = await window.webContents.executeJavaScript(code);
            return JSON.parse(result);
        }
        
        // 检查输入框是否存在
        async function checkInput(window) {
            const code = `
                (function() {
                    const input = document.querySelector('.aislash-editor-input');
                    return JSON.stringify({ exists: input !== null });
                })()
            `;
            
            const result = await window.webContents.executeJavaScript(code);
            return JSON.parse(result);
        }
        
        // 输入文字
        async function inputText(window, text) {
            const code = `
                (function() {
                    const input = document.querySelector('.aislash-editor-input');
                    if (!input) return JSON.stringify({ success: false, error: '输入框未找到' });
                    
                    input.focus();
                    
                    const sel = window.getSelection();
                    const range = document.createRange();
                    range.selectNodeContents(input);
                    sel.removeAllRanges();
                    sel.addRange(range);
                    document.execCommand('delete', false, null);
                    
                    document.execCommand('insertText', false, ${JSON.stringify(text)});
                    
                    input.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true }));
                    
                    return JSON.stringify({ success: true });
                })()
            `;
            
            const result = await window.webContents.executeJavaScript(code);
            return JSON.parse(result);
        }
        
        // 等待并点击提交按钮（上箭头）
        async function submitByButton(window) {
            // 等待按钮出现（最多 10 秒）
            for (let i = 0; i < 50; i++) {
                const code = `
                    (function() {
                        // ✅ 必须查找子元素 .anysphere-icon-button
                        const button = document.querySelector('.send-with-mode > .anysphere-icon-button');
                        if (!button) return JSON.stringify({ ready: false });
                        
                        const isVisible = button.offsetParent !== null;
                        return JSON.stringify({ ready: isVisible });
                    })()
                `;
                
                const checkResult = await window.webContents.executeJavaScript(code);
                const check = JSON.parse(checkResult);
                
                if (check.ready) {
                    // 按钮已就绪，点击它
                    const clickCode = `
                        (function() {
                            // ✅ 点击子元素，不是父元素
                            const button = document.querySelector('.send-with-mode > .anysphere-icon-button');
                            if (!button) return JSON.stringify({ success: false, error: '按钮未找到' });
                            
                            button.click();
                            return JSON.stringify({ success: true });
                        })()
                    `;
                    
                    const clickResult = await window.webContents.executeJavaScript(clickCode);
                    return JSON.parse(clickResult);
                }
                
                // 等待 200ms 后重试
                await new Promise(resolve => setTimeout(resolve, 200));
            }
            
            return { success: false, error: '提交按钮未在 10 秒内出现' };
        }
        
        // ====================================================================
        // 处理来自中央Server的命令
        // ====================================================================
        
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
                    
                    case 'agent_execute_prompt':
                        await handleAgentExecutePrompt(from, payload);
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
        
        // 处理 Composer 发送提示词命令（V9：完整流程）
        async function handleComposerSendPrompt(fromId, payload) {
            const { agent_id, prompt } = payload;
            
            log(`💬 [Composer] 发送提示词: ${prompt.substring(0, 50)}...`);
            
            try {
                const electron = await import("electron");
                const windows = electron.BrowserWindow.getAllWindows();
                
                if (windows.length === 0) {
                    throw new Error('没有打开的窗口');
                }
                
                const window = windows[0];
                
                // 步骤 1: 确保在 Editor tab
                log('  📍 步骤 1: 确保在 Editor tab...');
                const tabResult = await ensureEditorTab(window);
                if (!tabResult.success) {
                    throw new Error(`Editor tab 错误: ${tabResult.error}`);
                }
                if (tabResult.switched) {
                    log('  ✅ 已切换到 Editor tab');
                    await new Promise(resolve => setTimeout(resolve, 500));
                } else {
                    log('  ✅ 已在 Editor tab');
                }
                
                // 步骤 2: 检查输入框，如需则用 Cmd+I 唤出
                log('  📍 步骤 2: 检查 Composer...');
                let inputCheck = await checkInput(window);
                
                if (!inputCheck.exists) {
                    log('  📢 输入框不可见，发送 Cmd+I...');
                    await invokeComposer(window);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                    inputCheck = await checkInput(window);
                    if (!inputCheck.exists) {
                        throw new Error('Cmd+I 后输入框仍未出现');
                    }
                }
                log('  ✅ Composer 已就绪');
                
                // 步骤 3: 输入文字
                log('  📍 步骤 3: 输入文字...');
                const inputResult = await inputText(window, prompt);
                if (!inputResult.success) {
                    throw new Error(`输入文字失败: ${inputResult.error}`);
                }
                log('  ✅ 文字已输入');
                
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // 步骤 4: 点击上箭头按钮
                log('  📍 步骤 4: 点击上箭头按钮...');
                const submitResult = await submitByButton(window);
                if (!submitResult.success) {
                    throw new Error(`提交失败: ${submitResult.error}`);
                }
                log('  ✅ 已提交');
                
                // 发送成功结果
                const resultMessage = {
                    type: 'composer_send_prompt_result',
                    from: cursorId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: true,
                        agent_id: agent_id,
                        message: '提示词已提交',
                        error: null
                    }
                };
                
                sendToCentral(resultMessage);
                log(`✅ [Composer] 提示词已成功提交！`);
                
            } catch (error) {
                log(`❌ [Composer] 错误: ${error.message}`);
                
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
        
        // 处理 Agent 执行提示词命令（语义操作）
        async function handleAgentExecutePrompt(fromId, payload) {
            // 目前就是调用 handleComposerSendPrompt
            // 未来可以添加更多逻辑（如等待完成）
            await handleComposerSendPrompt(fromId, payload);
        }
        
        // 处理 Composer 查询状态命令（V9：正确的状态检测）
        async function handleComposerQueryStatus(fromId, payload) {
            const { agent_id } = payload;
            
            log(`📊 [Composer] 查询状态: agent_id=${agent_id}`);
            
            try {
                const electron = await import("electron");
                const windows = electron.BrowserWindow.getAllWindows();
                
                if (windows.length === 0) {
                    throw new Error('没有打开的窗口');
                }
                
                const code = `
                    (function() {
                        // 检查 loading 指示器
                        const loadingSelectors = [
                            '[class*="loading" i]',
                            '.cursor-thinking',
                            '.agent-working'
                        ];
                        
                        let isWorking = false;
                        for (const selector of loadingSelectors) {
                            const el = document.querySelector(selector);
                            if (el && el.offsetParent !== null) {
                                isWorking = true;
                                break;
                            }
                        }
                        
                        const status = isWorking ? 'working' : 'idle';
                        return JSON.stringify({ status: status });
                    })()
                `;
                
                const result = await windows[0].webContents.executeJavaScript(code);
                const resultObj = JSON.parse(result);
                
                const resultMessage = {
                    type: 'composer_status_result',
                    from: cursorId,
                    to: fromId,
                    timestamp: Math.floor(Date.now() / 1000),
                    payload: {
                        success: true,
                        agent_id: agent_id,
                        status: resultObj.status,
                        error: null
                    }
                };
                
                sendToCentral(resultMessage);
                log(`✅ [Composer] 状态已返回: ${resultObj.status}`);
                
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
                    log(`  📡 WebSocket readyState: ${centralWs.readyState}`);
                    log('══════════════════════════════════════════════════════════════');
                    log('');
                    
                    reconnectDelay = 1000;
                    
                    // 等待一小段时间，确保连接完全建立
                    await new Promise(resolve => setTimeout(resolve, 100));
                    
                    log(`📡 等待后 readyState: ${centralWs.readyState}`);
                    
                    await register();
                    
                    heartbeatInterval = setInterval(() => {
                        sendHeartbeat();
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
echo "  ✅ V9 已注入 - 正确的 DOM 操作流程"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "V9 新特性:"
echo "  ✅ 自动切换到 Editor tab（不是 Agents）"
echo "  ✅ 使用 Cmd+I 唤出 Composer（如果需要）"
echo "  ✅ 正确的输入框选择器：.aislash-editor-input"
echo "  ✅ 正确的提交按钮：.send-with-mode（上箭头按钮）"
echo "  ✅ 等待按钮出现后再点击"
echo "  ✅ 正确的状态检测：[class*=\"loading\" i]"
echo ""
echo "使用方式:"
echo "  开发模式: python3 test_complete_flow.py"
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
echo "  开发测试（推荐）:"
echo "    python3 test_complete_flow.py"
echo ""
echo "  生产测试:"
echo "    export ORTENSIA_SERVER=ws://localhost:8765"
echo "    重启 Cursor"
echo "    python3 examples/command_client_example.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

