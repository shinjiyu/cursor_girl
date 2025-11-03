#!/bin/bash
# ============================================================================
# Ortensia Cursor Injector v3 - 完全内联版本
# 直接将所有代码内联到 main.js，不使用外部文件
# ============================================================================

set -e

# ========== 颜色 ==========
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ========== 配置 ==========
CURSOR_APP="/Applications/Cursor.app"
CURSOR_RESOURCES="$CURSOR_APP/Contents/Resources/app"
OUT_DIR="$CURSOR_RESOURCES/out"
MAIN_JS="$OUT_DIR/main.js"
BACKUP_JS="$OUT_DIR/main.js.ortensia.backup"

# ========== 检查 ==========
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} Ortensia Cursor Injector v3${NC}"
echo -e "${BLUE} (Fully Inlined)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -d "$CURSOR_APP" ]; then
    echo -e "${RED}❌ Cursor.app not found!${NC}"
    exit 1
fi

if [ ! -f "$MAIN_JS" ]; then
    echo -e "${RED}❌ main.js not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Cursor found${NC}"
echo ""

# ========== 备份 ==========
if [ -f "$BACKUP_JS" ]; then
    echo -e "${YELLOW}⚠️  Using existing backup${NC}"
else
    echo -e "${BLUE}[1/3]${NC} Creating backup..."
    cp "$MAIN_JS" "$BACKUP_JS"
    echo -e "${GREEN}✅ Backup created${NC}"
fi
echo ""

# ========== 注入 ==========
echo -e "${BLUE}[2/3]${NC} Injecting code..."

# 将整个 WebSocket 服务器代码直接内联到 main.js
cat > "$MAIN_JS" << 'ORTENSIA_EOF'
// ============================================================================
// Ortensia Cursor Injector v3 - Fully Inlined
// ============================================================================

(function() {
    console.log('');
    console.log('='.repeat(80));
    console.log('  🎉 Ortensia Cursor Injector v3 (Inlined)');
    console.log('  Loading modules...');
    console.log('='.repeat(80));
    console.log('');

    // 延迟执行，确保 Electron 完全加载
    setTimeout(function() {
        try {
            // 动态加载模块
            Promise.all([
                import('ws'),
                import('electron')
            ]).then(function(modules) {
                const WebSocketModule = modules[0];
                const ElectronModule = modules[1];
                
                const WebSocket = WebSocketModule.default || WebSocketModule.Server || WebSocketModule;
                const BrowserWindow = ElectronModule.BrowserWindow;
                
                console.log('✅ Modules loaded successfully');
                console.log('   ws:', typeof WebSocket);
                console.log('   electron:', typeof BrowserWindow);
                
                // 创建 WebSocket 服务器
                const PORT = 9224;
                const wss = new (WebSocket.Server || WebSocket)({ port: PORT });
                
                console.log('✅ WebSocket server started on port ' + PORT);
                console.log('📡 Waiting for Ortensia to connect...');
                console.log('');
                
                wss.on('connection', function(ws) {
                    console.log('🔗 Ortensia connected!');
                    
                    ws.on('message', function(message) {
                        try {
                            const data = JSON.parse(message.toString());
                            console.log('📥 Received:', data.action);
                            
                            let response = { success: false };
                            
                            if (data.action === 'ping') {
                                response = { success: true, message: 'pong' };
                            } 
                            else if (data.action === 'eval') {
                                const result = eval(data.code);
                                response = { success: true, result: String(result) };
                            }
                            else if (data.action === 'evalr') {
                                const win = BrowserWindow.getFocusedWindow() || 
                                            BrowserWindow.getAllWindows()[0];
                                if (win) {
                                    win.webContents.executeJavaScript(data.code).then(function(result) {
                                        ws.send(JSON.stringify({ 
                                            success: true, 
                                            result: String(result) 
                                        }));
                                    }).catch(function(error) {
                                        ws.send(JSON.stringify({ 
                                            success: false, 
                                            error: error.message 
                                        }));
                                    });
                                    return;
                                } else {
                                    response = { success: false, error: 'No window available' };
                                }
                            }
                            else {
                                response = { success: false, error: 'Unknown action: ' + data.action };
                            }
                            
                            ws.send(JSON.stringify(response));
                            console.log('✅ Response sent');
                            
                        } catch (error) {
                            console.error('❌ Error:', error.message);
                            ws.send(JSON.stringify({ 
                                success: false, 
                                error: error.message 
                            }));
                        }
                    });
                    
                    ws.on('close', function() {
                        console.log('👋 Ortensia disconnected');
                    });
                    
                    ws.on('error', function(error) {
                        console.error('❌ WebSocket client error:', error.message);
                    });
                });
                
                wss.on('error', function(error) {
                    console.error('❌ WebSocket server error:', error.message);
                });
                
                // 暴露全局 API
                globalThis.ortensiaAPI = {
                    version: '3.0.0',
                    wss: wss
                };
                
                console.log('');
                console.log('✅ Ortensia Injector v3 ready!');
                console.log('💡 Test: ./ortensia-cursor.sh ping');
                console.log('');
                
            }).catch(function(error) {
                console.error('');
                console.error('❌ Failed to load modules:');
                console.error('   ', error.message);
                console.error('   ', error.stack);
                console.error('');
            });
            
        } catch (error) {
            console.error('');
            console.error('❌ FATAL ERROR in Ortensia Injector:');
            console.error('   ', error.message);
            console.error('   ', error.stack);
            console.error('');
        }
    }, 5000); // 延迟 5 秒，确保 Cursor 完全加载

})();

// ============================================================================
// 原始 main.js 代码
// ============================================================================

ORTENSIA_EOF

cat "$BACKUP_JS" >> "$MAIN_JS"

echo -e "${GREEN}✅ Injection complete${NC}"
echo ""

# ========== 重签名 ==========
echo -e "${BLUE}[3/3]${NC} Re-signing..."

codesign --force --deep --sign - "$CURSOR_APP" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Signing failed (OK)${NC}"
}

echo -e "${GREEN}✅ Done${NC}"
echo ""

# ========== 完成 ==========
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN} ✅ Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. ${YELLOW}Quit Cursor${NC} (Cmd+Q)"
echo "  2. ${YELLOW}Restart Cursor${NC}"
echo "  3. ${YELLOW}Wait ~5 seconds${NC} for injector to load"
echo "  4. Open DevTools Console - should see:"
echo "     ${GREEN}✅ Ortensia Injector v3 ready!${NC}"
echo ""
echo "  5. Test:"
echo "     ${BLUE}./ortensia-cursor.sh ping${NC}"
echo ""

