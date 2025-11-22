#!/usr/bin/env python3
"""
从 Cursor DOM 中提取 conversation_id

基于探索结果，重点查找：
1. markdown section 的 ID 中的 UUID
2. bubble ID
3. 其他可能的 conversation 标识符
"""

import asyncio
import json
import re
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
    print("🔍 提取 Cursor conversation_id")
    print("=" * 80)
    print()
    
    # ============================================================
    # 1. 提取所有 markdown section ID 中的 UUID
    # ============================================================
    print("1️⃣  提取 markdown section 中的 UUID")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const sections = document.querySelectorAll('[id^="markdown-section-"]');
                const uuids = new Set();
                
                sections.forEach(section => {
                    // 格式：markdown-section-{UUID}-{index}
                    const match = section.id.match(/markdown-section-([a-f0-9-]+)-\\d+/);
                    if (match && match[1]) {
                        // 验证是否是 UUID 格式 (8-4-4-4-12)
                        if (/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/.test(match[1])) {
                            uuids.add(match[1]);
                        }
                    }
                });
                
                return JSON.stringify({
                    count: sections.length,
                    uuids: Array.from(uuids)
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('count', 0)} 个 markdown section")
        print(f"提取到的 UUID:")
        for uuid in data.get('uuids', []):
            print(f"  🔑 {uuid}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 2. 提取 bubble ID
    # ============================================================
    print("2️⃣  提取 bubble ID")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const bubbles = document.querySelectorAll('[id^="bubble-"]');
                const ids = [];
                
                bubbles.forEach(bubble => {
                    ids.push({
                        id: bubble.id,
                        messageIndex: bubble.getAttribute('data-message-index'),
                        className: bubble.className.substring(0, 100)
                    });
                });
                
                return JSON.stringify(ids, null, 2);
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
    # 3. 检查 composer-bar 的所有内部属性
    # ============================================================
    print("3️⃣  深入检查 composer-bar 内部")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const composer = document.querySelector('.composer-bar');
                if (!composer) return 'No composer found';
                
                // 获取所有非标准属性（可能是框架添加的）
                const info = {
                    id: composer.id,
                    className: composer.className,
                    attributes: {},
                    specialKeys: []
                };
                
                // 标准属性
                for (const attr of composer.attributes) {
                    info.attributes[attr.name] = attr.value.substring(0, 100);
                }
                
                // 对象的所有键（包括框架添加的）
                for (const key in composer) {
                    if (key.startsWith('__') || 
                        key.includes('react') || 
                        key.includes('vue') ||
                        key.includes('conversation') ||
                        key.includes('chat') ||
                        key.includes('id')) {
                        info.specialKeys.push(key);
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
    # 4. 检查整个 document 的所有 UUID 格式的内容
    # ============================================================
    print("4️⃣  扫描整个文档中的所有 UUID")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const html = document.documentElement.outerHTML;
                const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/gi;
                const matches = html.match(uuidRegex);
                
                if (!matches) return JSON.stringify({ count: 0, uuids: [] });
                
                // 去重
                const uniqueUuids = [...new Set(matches.map(m => m.toLowerCase()))];
                
                return JSON.stringify({
                    count: matches.length,
                    unique: uniqueUuids.length,
                    uuids: uniqueUuids
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"总共找到 {data.get('count', 0)} 个 UUID（{data.get('unique', 0)} 个唯一）")
        print(f"\n所有唯一的 UUID:")
        for uuid in data.get('uuids', []):
            print(f"  🔑 {uuid}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 5. 检查 aichat-container 内部
    # ============================================================
    print("5️⃣  检查 aichat-container")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const container = document.querySelector('.aichat-container');
                if (!container) return 'No aichat-container found';
                
                // 查找所有包含 UUID 的属性
                const info = {
                    attributes: {},
                    dataAttributes: {},
                    childrenWithIds: []
                };
                
                // 所有属性
                for (const attr of container.attributes) {
                    info.attributes[attr.name] = attr.value.substring(0, 200);
                }
                
                // data-* 属性
                if (container.dataset) {
                    for (const key in container.dataset) {
                        info.dataAttributes[key] = container.dataset[key].substring(0, 200);
                    }
                }
                
                // 子元素的 ID
                const childrenWithId = container.querySelectorAll('[id]');
                childrenWithId.forEach((child, idx) => {
                    if (idx < 20) {
                        info.childrenWithIds.push({
                            id: child.id,
                            tag: child.tagName,
                            className: child.className.substring(0, 100)
                        });
                    }
                });
                
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
    # 6. 尝试访问 VSCode API
    # ============================================================
    print("6️⃣  尝试访问 VSCode/Cursor 内部 API")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 查找可能的全局 API
                const apis = {};
                
                // 检查 window 上的特殊对象
                if (window.vscode) apis.vscode = Object.keys(window.vscode);
                if (window.cursor) apis.cursor = Object.keys(window.cursor);
                if (window.acquireVsCodeApi) {
                    try {
                        const vscodeApi = window.acquireVsCodeApi();
                        apis.acquiredVsCodeApi = Object.keys(vscodeApi);
                    } catch (e) {
                        apis.acquireVsCodeApiError = e.message;
                    }
                }
                
                // 查找 window 上包含 conversation 的属性
                for (const key in window) {
                    if (typeof window[key] === 'object' && window[key] !== null) {
                        try {
                            const objStr = JSON.stringify(window[key]);
                            if (objStr.includes('conversation') || objStr.includes('chat')) {
                                apis[key] = {
                                    type: typeof window[key],
                                    keys: Object.keys(window[key]).slice(0, 20)
                                };
                            }
                        } catch (e) {
                            // 忽略循环引用等错误
                        }
                    }
                }
                
                return JSON.stringify(apis, null, 2);
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
    
    print("=" * 80)
    print("✅ 提取完成")
    print("=" * 80)
    print()
    print("💡 结论:")
    print("   如果在 markdown section 中找到了 UUID，那很可能就是 conversation_id")
    print("   格式为：markdown-section-{conversation_id}-{index}")


if __name__ == "__main__":
    print("\n💡 使用说明:")
    print("1. 确保 Cursor 已启动并打开了一个对话")
    print("2. 确保已安装并运行 Ortensia inject (install-v9.sh)")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

