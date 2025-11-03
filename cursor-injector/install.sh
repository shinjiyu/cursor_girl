#!/bin/bash
# V7: 修复 Promise 处理，支持异步代码执行

MAIN_JS="/Applications/Cursor.app/Contents/Resources/app/out/main.js"
BACKUP_JS="/Applications/Cursor.app/Contents/Resources/app/out/main.js.ortensia.backup"
LOG_FILE="/tmp/cursor_ortensia.log"

# 清理旧日志
rm -f "$LOG_FILE"

# 恢复备份
cp "$BACKUP_JS" "$MAIN_JS"

# 读取原始内容
ORIGINAL=$(cat "$BACKUP_JS")

# 创建新 main.js
cat > "$MAIN_JS" << 'INJECT_END'
// ============================================================================
// ORTENSIA: WebSocket 服务器 V6 - Fixed
// ============================================================================
(async function() {
    const fs = await import('fs');
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
    log('🎉 Ortensia V7 启动中...');
    log(`进程 ID: ${process.pid}`);
    
    // 等待 3 秒
    await new Promise(resolve => setTimeout(resolve, 3000));
    log('⏱️  等待完成，开始加载 WebSocket 模块...');
    
    try {
        const ws = await import('ws');
        log('✅ ws 模块加载成功!');
        log(`   模块导出: ${Object.keys(ws).join(', ')}`);
        
        // 正确的构造函数名称！
        const WebSocketServer = ws.WebSocketServer || ws.Server || ws.default;
        log(`✅ WebSocketServer 类型: ${typeof WebSocketServer}`);
        
        if (typeof WebSocketServer !== 'function') {
            throw new Error('无法找到 WebSocketServer 构造函数');
        }
        
        // 创建服务器
        log('📡 创建 WebSocket 服务器 (端口 9876)...');
        const wss = new WebSocketServer({ port: 9876 });
        
        wss.on('listening', () => {
            log('');
            log('██████████████████████████████████████████████████████████████');
            log('█ ✅ WebSocket 服务器启动成功！');
            log('█ 📍 端口: 9876');
            log('█ 🔑 进程: ' + process.pid);
            log('█ 📡 等待 Ortensia 连接...');
            log('██████████████████████████████████████████████████████████████');
            log('');
        });
        
        wss.on('connection', (ws) => {
            log('🔗 客户端已连接!');
            
            ws.on('message', async (message) => {
                try {
                    const code = message.toString();
                    log(`📥 收到代码: ${code.substring(0, 50)}...`);
                    
                    // 执行代码
                    let result = eval(code);
                    
                    // 如果是 Promise，等待其完成
                    if (result && typeof result.then === 'function') {
                        result = await result;
                    }
                    
                    const response = { success: true, result: String(result) };
                    ws.send(JSON.stringify(response));
                    
                    log(`✅ 执行成功: ${String(result).substring(0, 100)}`);
                } catch (error) {
                    log(`❌ 执行错误: ${error.message}`);
                    ws.send(JSON.stringify({ success: false, error: error.message }));
                }
            });
            
            ws.on('close', () => {
                log('🔌 客户端断开连接');
            });
            
            ws.on('error', (err) => {
                log(`❌ 客户端错误: ${err.message}`);
            });
        });
        
        wss.on('error', (error) => {
            log(`❌ 服务器错误: ${error.message}`);
            if (error.code === 'EADDRINUSE') {
                log('   端口 9876 已被占用，可能 Ortensia 已在运行？');
            }
        });
        
        log('✅ WebSocket 服务器设置完成，等待连接...');
        
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
echo "  ✅ V7 已注入 - 支持异步代码执行！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "V7 新功能:"
echo "  ✅ 自动检测并等待 Promise 完成"
echo "  ✅ 支持访问渲染进程 DOM (通过 executeJavaScript)"
echo "  ✅ 可以执行异步 Electron API 调用"
echo ""
echo "日志文件: $LOG_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📋 测试步骤:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1️⃣  完全退出 Cursor (Cmd+Q)"
echo "  2️⃣  重新启动 Cursor"
echo "  3️⃣  等待 10 秒"
echo "  4️⃣  查看日志: cat /tmp/cursor_ortensia.log"
echo "  5️⃣  测试连接: cd /Users/user/Documents/cursorgirl && ./ortensia-cursor.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

