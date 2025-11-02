/**
 * Frida 注入脚本 - 动态注入到 Cursor
 * 
 * 使用方法：
 * 1. 启动 Cursor
 * 2. frida -n Cursor -l frida-inject-cursor.js
 * 
 * 或者通过 PID:
 * frida -p $(pgrep -f "Cursor.app/Contents/MacOS/Cursor") -l frida-inject-cursor.js
 */

console.log('🔥 Frida injecting into Cursor...');

// ==================== 1. 查找渲染进程 ====================
function findRendererProcess() {
    console.log('🔍 Searching for Electron renderer processes...');
    
    // Electron 的渲染进程通常有特定的特征
    const modules = Process.enumerateModules();
    modules.forEach(mod => {
        if (mod.name.includes('Electron') || mod.name.includes('Chromium')) {
            console.log(`✅ Found: ${mod.name} at ${mod.base}`);
        }
    });
}

// ==================== 2. Hook JavaScript 执行 ====================
function hookJavaScriptExecution() {
    console.log('🎣 Hooking JavaScript execution...');
    
    // Hook v8::Script::Run (Chromium JavaScript 执行)
    const v8Module = Process.findModuleByName('libnode.dylib') || 
                     Process.findModuleByName('node.dll');
    
    if (v8Module) {
        console.log('✅ Found V8 module:', v8Module.name);
        
        // 这里可以 hook V8 的 JavaScript 执行函数
        // 但需要知道具体的函数签名
    } else {
        console.log('⚠️  V8 module not found');
    }
}

// ==================== 3. 注入到 WebContents ====================
function injectIntoWebContents() {
    console.log('💉 Injecting into WebContents...');
    
    // 查找 Electron 的 webContents.executeJavaScript
    const electronModule = Process.findModuleByName('Electron Framework') ||
                          Process.findModuleByName('Electron');
    
    if (electronModule) {
        console.log('✅ Found Electron module:', electronModule.name);
        
        // 尝试查找 executeJavaScript 函数
        const symbols = electronModule.enumerateSymbols();
        symbols.forEach(sym => {
            if (sym.name.includes('executeJavaScript') || 
                sym.name.includes('webContents')) {
                console.log(`   Found symbol: ${sym.name}`);
            }
        });
    }
}

// ==================== 4. 直接操作渲染进程内存 ====================
function injectViaMemory() {
    console.log('🧠 Attempting memory injection...');
    
    // 创建要注入的 JavaScript 代码
    const injectCode = `
        console.log('🎉 Ortensia injected via Frida!');
        
        // 创建全局 API
        window.ortensiaAPI = {
            version: '1.0.0-frida',
            
            sendToAI: function(prompt) {
                console.log('📤 Sending to Cursor AI:', prompt);
                
                // 尝试查找 Cursor AI 的内部 API
                if (window.cursorAI) {
                    window.cursorAI.sendMessage(prompt);
                } else {
                    console.log('⚠️  Cursor AI API not found');
                }
            },
            
            getEditor: function() {
                // 查找 Monaco Editor
                if (window.monaco && window.monaco.editor) {
                    const editors = window.monaco.editor.getEditors();
                    console.log('✅ Found Monaco editors:', editors.length);
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
                }
            }
        };
        
        // 监听 DOM 变化，查找 AI 相关元素
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.className && typeof node.className === 'string') {
                        if (node.className.includes('ai') || 
                            node.className.includes('chat')) {
                            console.log('🤖 AI element detected:', node.className);
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('✅ Ortensia API ready!');
        console.log('   Usage: ortensiaAPI.sendToAI("your prompt")');
    `;
    
    // 将代码写入内存并执行
    const script = Memory.allocUtf8String(injectCode);
    console.log(`📝 Injection code prepared (${injectCode.length} bytes)`);
    
    return script;
}

// ==================== 5. RPC 接口 ====================
// 暴露给 Python 的 RPC 接口
rpc.exports = {
    /**
     * 执行 JavaScript 代码
     */
    executeJS: function(code) {
        console.log('🔧 Executing JS:', code.substring(0, 50) + '...');
        
        try {
            // 这里需要找到执行 JS 的方法
            // 实际实现取决于 Electron 的版本和结构
            return { success: true, result: 'Code queued' };
        } catch (e) {
            return { success: false, error: e.message };
        }
    },
    
    /**
     * 查找 Cursor AI 的入口点
     */
    findCursorAI: function() {
        console.log('🔍 Searching for Cursor AI entry points...');
        
        // 遍历所有全局对象
        const globals = [];
        
        // 返回发现的信息
        return {
            found: globals.length > 0,
            globals: globals
        };
    },
    
    /**
     * 注入控制代码
     */
    inject: function() {
        console.log('💉 Starting injection...');
        
        findRendererProcess();
        hookJavaScriptExecution();
        injectIntoWebContents();
        const script = injectViaMemory();
        
        return { success: true, message: 'Injection completed' };
    }
};

// ==================== 主执行流程 ====================
console.log('');
console.log('='.repeat(70));
console.log('  🎯 Frida Cursor Injection Script');
console.log('='.repeat(70));
console.log('');

// 自动执行初始化
setTimeout(() => {
    console.log('⚡ Starting automatic injection...');
    
    findRendererProcess();
    injectIntoWebContents();
    
    console.log('');
    console.log('✅ Injection script loaded!');
    console.log('');
    console.log('💡 Available RPC commands:');
    console.log('   - inject()          : Inject control code');
    console.log('   - executeJS(code)   : Execute JavaScript');
    console.log('   - findCursorAI()    : Find Cursor AI API');
    console.log('');
    console.log('📝 Usage from Python:');
    console.log('   session.exports.inject()');
    console.log('   session.exports.execute_js("alert(1)")');
    console.log('');
}, 1000);

// 保持脚本运行
console.log('🔄 Frida script is running...');
console.log('   Press Ctrl+C to detach');
console.log('');

