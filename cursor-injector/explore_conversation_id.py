#!/usr/bin/env python3
"""
探索 Cursor DOM 中的 conversation_id

使用 inject 的本地 WebSocket 接口（端口 9876）执行 JS 代码
探索 DOM、localStorage、sessionStorage、全局变量等
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
    print("🔍 探索 Cursor 中的 conversation_id")
    print("=" * 80)
    print()
    
    # ============================================================
    # 1. 检查 localStorage
    # ============================================================
    print("1️⃣  检查 localStorage")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key.toLowerCase().includes('conversation') || 
                        key.toLowerCase().includes('chat') ||
                        key.toLowerCase().includes('session')) {
                        items[key] = localStorage.getItem(key).substring(0, 200);
                    }
                }
                return JSON.stringify(items, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        print(f"结果:\n{result.get('result', 'No conversation-related items')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 2. 检查 sessionStorage
    # ============================================================
    print("2️⃣  检查 sessionStorage")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const items = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    if (key.toLowerCase().includes('conversation') || 
                        key.toLowerCase().includes('chat') ||
                        key.toLowerCase().includes('session')) {
                        items[key] = sessionStorage.getItem(key).substring(0, 200);
                    }
                }
                return JSON.stringify(items, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        print(f"结果:\n{result.get('result', 'No conversation-related items')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 3. 检查全局 window 对象
    # ============================================================
    print("3️⃣  检查全局 window 对象")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const found = [];
                
                // 遍历 window 对象的属性
                for (const key in window) {
                    if (key.toLowerCase().includes('conversation') ||
                        key.toLowerCase().includes('chat') ||
                        key.toLowerCase().includes('ai') ||
                        key.toLowerCase().includes('agent')) {
                        try {
                            const value = window[key];
                            const type = typeof value;
                            found.push({
                                key: key,
                                type: type,
                                preview: type === 'object' ? 
                                    Object.keys(value).slice(0, 10).join(', ') :
                                    String(value).substring(0, 100)
                            });
                        } catch (e) {
                            found.push({ key: key, error: e.message });
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
        print(f"结果:\n{result.get('result', '[]')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 4. 检查 DOM 元素的 data 属性
    # ============================================================
    print("4️⃣  检查 DOM 元素的 data-* 属性")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const found = [];
                const elements = document.querySelectorAll('*[data-conversation], *[data-chat], *[data-session], *[data-id]');
                
                elements.forEach((el, idx) => {
                    if (idx < 20) {  // 限制数量
                        const attrs = {};
                        for (const attr of el.attributes) {
                            if (attr.name.startsWith('data-')) {
                                attrs[attr.name] = attr.value.substring(0, 100);
                            }
                        }
                        if (Object.keys(attrs).length > 0) {
                            found.push({
                                tag: el.tagName.toLowerCase(),
                                class: el.className.substring(0, 50),
                                attributes: attrs
                            });
                        }
                    }
                });
                
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
    
    # ============================================================
    # 5. 检查 React Fiber (如果使用 React)
    # ============================================================
    print("5️⃣  检查 React Fiber 内部状态")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 查找包含 React Fiber 的 DOM 元素
                const rootElement = document.querySelector('#root') || 
                                  document.querySelector('[data-reactroot]') ||
                                  document.body;
                
                if (!rootElement) return 'No React root found';
                
                // 尝试访问 Fiber
                const fiberKey = Object.keys(rootElement).find(key => 
                    key.startsWith('__reactFiber') || 
                    key.startsWith('__reactInternalInstance')
                );
                
                if (!fiberKey) return 'No React Fiber found';
                
                const fiber = rootElement[fiberKey];
                
                // 遍历 Fiber 树查找 conversation 相关的 state/props
                const found = [];
                let current = fiber;
                let depth = 0;
                
                while (current && depth < 100) {
                    try {
                        // 检查 memoizedState
                        if (current.memoizedState) {
                            const stateStr = JSON.stringify(current.memoizedState);
                            if (stateStr.includes('conversation') || 
                                stateStr.includes('chat') ||
                                stateStr.includes('session')) {
                                found.push({
                                    type: current.type?.name || current.type,
                                    state: stateStr.substring(0, 200)
                                });
                            }
                        }
                        
                        // 检查 memoizedProps
                        if (current.memoizedProps) {
                            const propsStr = JSON.stringify(current.memoizedProps);
                            if (propsStr.includes('conversation') ||
                                propsStr.includes('chat') ||
                                propsStr.includes('session')) {
                                found.push({
                                    type: current.type?.name || current.type,
                                    props: propsStr.substring(0, 200)
                                });
                            }
                        }
                        
                        current = current.child || current.sibling || current.return;
                    } catch (e) {
                        break;
                    }
                    depth++;
                }
                
                return JSON.stringify(found.slice(0, 10), null, 2);
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
    
    # ============================================================
    # 6. 检查 URL 和路由
    # ============================================================
    print("6️⃣  检查 URL 和路由")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                return JSON.stringify({
                    url: window.location.href,
                    pathname: window.location.pathname,
                    search: window.location.search,
                    hash: window.location.hash
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
    # 7. 检查 Composer/Chat 容器的属性
    # ============================================================
    print("7️⃣  检查 Composer/Chat 容器")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 查找可能的对话容器
                const selectors = [
                    '.composer',
                    '.chat-container',
                    '.conversation',
                    '.aislash-editor',
                    '[class*="composer"]',
                    '[class*="chat"]',
                    '[class*="conversation"]'
                ];
                
                const found = [];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach((el, idx) => {
                        if (idx < 5) {
                            // 获取所有属性
                            const attrs = {};
                            for (const attr of el.attributes) {
                                attrs[attr.name] = attr.value.substring(0, 100);
                            }
                            
                            // 检查所有以 __ 开头的属性（可能是 React/框架内部）
                            const internalKeys = Object.keys(el).filter(k => 
                                k.startsWith('__') || k.startsWith('_react')
                            );
                            
                            found.push({
                                selector: selector,
                                tag: el.tagName,
                                id: el.id,
                                className: el.className.substring(0, 100),
                                attributes: attrs,
                                internalKeys: internalKeys
                            });
                        }
                    });
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
    print("1. 确保 Cursor 已启动")
    print("2. 确保已安装并运行 Ortensia inject (install-v9.sh)")
    print("3. inject 会在端口 9876 启动本地 WebSocket 服务")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

