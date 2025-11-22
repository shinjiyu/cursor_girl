#!/usr/bin/env python3
"""
深入探索 VSCode/Cursor API 来查找 conversation_id

通过 window.vscode 访问内部 API
"""

import asyncio
import json
import websockets


async def execute_js(code):
    """通过 inject 执行 JS 代码"""
    try:
        async with websockets.connect('ws://localhost:9876') as ws:
            await ws.send(code)
            response = await ws.recv()
            result = json.loads(response)
            return result
    except Exception as e:
        return {"success": False, "error": str(e)}


async def main():
    print("=" * 80)
    print("🔍 深入探索 VSCode/Cursor API")
    print("=" * 80)
    print()
    
    # ============================================================
    # 1. 详细查看 vscode 对象
    # ============================================================
    print("1️⃣  详细检查 window.vscode 对象")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                if (!window.vscode) return 'No vscode object';
                
                const info = {};
                
                // 遍历 vscode 对象的所有属性
                for (const key in window.vscode) {
                    try {
                        const value = window.vscode[key];
                        const type = typeof value;
                        
                        if (type === 'function') {
                            info[key] = {
                                type: 'function',
                                toString: value.toString().substring(0, 200)
                            };
                        } else if (type === 'object' && value !== null) {
                            info[key] = {
                                type: 'object',
                                keys: Object.keys(value).slice(0, 20),
                                constructor: value.constructor?.name
                            };
                        } else {
                            info[key] = {
                                type: type,
                                value: String(value).substring(0, 200)
                            };
                        }
                    } catch (e) {
                        info[key] = { error: e.message };
                    }
                }
                
                return JSON.stringify(info, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        print(f"结果:\n{result.get('result')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 2. 查找所有 _VSCODE 开头的全局变量
    # ============================================================
    print("2️⃣  查找所有 _VSCODE 相关的全局变量")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const found = {};
                
                for (const key in window) {
                    if (key.includes('VSCODE') || 
                        key.includes('vscode') || 
                        key.includes('cursor') ||
                        key.includes('CURSOR')) {
                        try {
                            const value = window[key];
                            const type = typeof value;
                            
                            if (type === 'object' && value !== null) {
                                // 尝试序列化看看内容
                                try {
                                    const str = JSON.stringify(value);
                                    if (str.length < 1000) {
                                        found[key] = JSON.parse(str);
                                    } else {
                                        found[key] = {
                                            type: 'object',
                                            keys: Object.keys(value),
                                            size: str.length
                                        };
                                    }
                                } catch (e) {
                                    found[key] = {
                                        type: 'object',
                                        keys: Object.keys(value).slice(0, 30),
                                        error: 'Cannot stringify'
                                    };
                                }
                            } else {
                                found[key] = value;
                            }
                        } catch (e) {
                            found[key] = { error: e.message };
                        }
                    }
                }
                
                return JSON.stringify(found, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        print(f"结果:\n{result.get('result', '{}')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 3. 尝试通过 IPC 获取当前状态
    # ============================================================
    print("3️⃣  尝试通过 vscode.ipcRenderer 监听/获取信息")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                if (!window.vscode || !window.vscode.ipcRenderer) {
                    return 'No ipcRenderer';
                }
                
                const ipc = window.vscode.ipcRenderer;
                
                // 获取 ipcRenderer 的所有方法
                const methods = [];
                for (const key in ipc) {
                    if (typeof ipc[key] === 'function') {
                        methods.push(key);
                    }
                }
                
                return JSON.stringify({
                    available: true,
                    methods: methods,
                    note: 'IPC 可用，但需要知道具体的 channel 名称才能发送/接收消息'
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        print(f"结果:\n{result.get('result')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 4. 查找所有包含 UUID 的全局对象
    # ============================================================
    print("4️⃣  查找包含 UUID 的全局对象")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/i;
                const found = {};
                
                // 遍历 window 的所有属性
                for (const key in window) {
                    try {
                        const value = window[key];
                        if (typeof value === 'object' && value !== null) {
                            const str = JSON.stringify(value);
                            if (uuidRegex.test(str)) {
                                // 这个对象包含 UUID
                                found[key] = {
                                    type: typeof value,
                                    preview: str.substring(0, 500),
                                    keys: Object.keys(value).slice(0, 20)
                                };
                            }
                        } else if (typeof value === 'string' && uuidRegex.test(value)) {
                            found[key] = value;
                        }
                    } catch (e) {
                        // 忽略
                    }
                }
                
                return JSON.stringify(found, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        print(f"结果:\n{result.get('result', '{}')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 5. 检查 DOM 中最近的 markdown section 的 ID
    # ============================================================
    print("5️⃣  提取最后一个 markdown section 的 ID（很可能是当前 conversation_id）")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const sections = document.querySelectorAll('[id^="markdown-section-"]');
                
                if (sections.length === 0) {
                    return JSON.stringify({ found: false, message: 'No markdown sections' });
                }
                
                // 获取最后一个 section
                const lastSection = sections[sections.length - 1];
                const uuidMatch = lastSection.id.match(/markdown-section-([a-f0-9-]+)-\\d+/);
                
                if (uuidMatch && uuidMatch[1]) {
                    const uuid = uuidMatch[1];
                    
                    // 验证是否是 UUID 格式
                    if (/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/.test(uuid)) {
                        return JSON.stringify({
                            found: true,
                            conversation_id: uuid,
                            total_sections: sections.length,
                            sample_ids: Array.from(sections).slice(-5).map(s => s.id)
                        }, null, 2);
                    }
                }
                
                return JSON.stringify({
                    found: false,
                    total_sections: sections.length,
                    last_id: lastSection.id
                });
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        print(f"结果:\n{result.get('result')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 6. 检查 Composer Pane 的 DOM 树中是否有隐藏的 conversation 信息
    # ============================================================
    print("6️⃣  检查 Composer 相关 DOM 的所有属性")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 查找 composer 相关的父容器
                const selectors = [
                    '.composer-bar',
                    '.aichat-pane',
                    '.aichat-container',
                    '.editor-instance'
                ];
                
                const found = [];
                
                for (const selector of selectors) {
                    const el = document.querySelector(selector);
                    if (el) {
                        // 获取所有 Object.keys
                        const allKeys = Object.keys(el);
                        
                        // 筛选有趣的键
                        const interestingKeys = allKeys.filter(k => 
                            k.startsWith('__') ||
                            k.includes('react') ||
                            k.includes('vue') ||
                            k.includes('conversation') ||
                            k.includes('chat') ||
                            k.includes('id') ||
                            k.includes('state')
                        );
                        
                        // 尝试访问这些键的值
                        const keyValues = {};
                        for (const key of interestingKeys.slice(0, 10)) {
                            try {
                                const val = el[key];
                                if (val !== null && val !== undefined) {
                                    if (typeof val === 'object') {
                                        keyValues[key] = {
                                            type: typeof val,
                                            keys: Object.keys(val).slice(0, 20)
                                        };
                                    } else {
                                        keyValues[key] = String(val).substring(0, 200);
                                    }
                                }
                            } catch (e) {
                                keyValues[key] = 'Error: ' + e.message;
                            }
                        }
                        
                        found.push({
                            selector: selector,
                            allKeysCount: allKeys.length,
                            interestingKeys: interestingKeys,
                            keyValues: keyValues
                        });
                    }
                }
                
                return JSON.stringify(found, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        print(f"结果:\n{result.get('result', '[]')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    print("=" * 80)
    print("✅ 探索完成")
    print("=" * 80)


if __name__ == "__main__":
    print("\n💡 使用说明:")
    print("1. 确保 Cursor 已启动并打开了一个对话")
    print("2. 确保已安装并运行 Ortensia inject")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

