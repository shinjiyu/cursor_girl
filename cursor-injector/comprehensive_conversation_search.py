#!/usr/bin/env python3
"""
全面搜索 conversation_id 的所有相关内容

包括：
1. DOM 元素（所有出现的地方）
2. 全局变量和函数
3. Tab 切换相关
4. 对话列表
5. 事件处理
6. localStorage/sessionStorage
7. 可能的 API 调用
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
    target_uuid = "2d8f9386-9864-4a51-b089-a7342029bb41"
    
    print("=" * 80)
    print(f"🔍 全面搜索 conversation_id: {target_uuid}")
    print("=" * 80)
    print()
    
    # ============================================================
    # 1. 搜索所有包含这个 UUID 的 DOM 元素
    # ============================================================
    print("1️⃣  搜索所有包含 UUID 的 DOM 元素")
    print("-" * 80)
    
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetUuid = '{target_uuid}';
                const found = [];
                const allElements = document.querySelectorAll('*');
                
                allElements.forEach((el, idx) => {{
                    let hasMatch = false;
                    const info = {{
                        tag: el.tagName.toLowerCase(),
                        index: idx
                    }};
                    
                    // 检查 ID
                    if (el.id && el.id.includes(targetUuid)) {{
                        info.id = el.id;
                        hasMatch = true;
                    }}
                    
                    // 检查所有属性
                    const matchedAttrs = {{}};
                    for (const attr of el.attributes) {{
                        if (attr.value.includes(targetUuid)) {{
                            matchedAttrs[attr.name] = attr.value.substring(0, 300);
                            hasMatch = true;
                        }}
                    }}
                    if (Object.keys(matchedAttrs).length > 0) {{
                        info.attributes = matchedAttrs;
                    }}
                    
                    // 检查 className
                    if (el.className && typeof el.className === 'string') {{
                        info.className = el.className.substring(0, 200);
                    }}
                    
                    // 检查文本内容（只检查直接文本，不包括子元素）
                    if (el.childNodes.length > 0) {{
                        for (const node of el.childNodes) {{
                            if (node.nodeType === 3 && node.textContent.includes(targetUuid)) {{
                                info.textContent = node.textContent.substring(0, 200);
                                hasMatch = true;
                                break;
                            }}
                        }}
                    }}
                    
                    // 检查特殊属性
                    const specialProps = ['value', 'placeholder', 'title', 'alt', 'aria-label', 'data-id'];
                    specialProps.forEach(prop => {{
                        const val = el[prop] || el.getAttribute(prop);
                        if (val && val.includes && val.includes(targetUuid)) {{
                            if (!info.attributes) info.attributes = {{}};
                            info.attributes[prop] = val.substring(0, 300);
                            hasMatch = true;
                        }}
                    }});
                    
                    if (hasMatch) {{
                        found.push(info);
                    }}
                }});
                
                return JSON.stringify({{
                    total: found.length,
                    elements: found
                }}, null, 2);
            }})()
        `);
        
        return result;
    }})()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个包含 UUID 的元素:\n")
        for el in data.get('elements', []):
            print(f"标签: {el['tag']}")
            if 'id' in el:
                print(f"  ID: {el['id']}")
            if 'className' in el:
                print(f"  Class: {el['className']}")
            if 'attributes' in el:
                print(f"  匹配的属性:")
                for k, v in el['attributes'].items():
                    print(f"    {k}: {v}")
            if 'textContent' in el:
                print(f"  文本: {el['textContent']}")
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 2. 搜索所有对话 Tab 相关的元素
    # ============================================================
    print("2️⃣  搜索对话 Tab 标签（Composer Tab）")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 查找可能是对话 tab 的元素
                const possibleSelectors = [
                    // Composer 相关
                    '[class*="composer"]',
                    '[id*="composer"]',
                    // Chat/Conversation 相关
                    '[class*="chat"]',
                    '[id*="chat"]',
                    '[class*="conversation"]',
                    '[id*="conversation"]',
                    // Tab 相关
                    '[role="tab"]',
                    '[class*="tab"][class*="chat"]',
                    '[class*="tab"][class*="conversation"]',
                    // Panel 相关
                    '[role="tabpanel"]',
                    '[class*="panel"][class*="chat"]'
                ];
                
                const found = [];
                const processed = new Set();
                
                for (const selector of possibleSelectors) {
                    try {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach((el, idx) => {
                            // 避免重复
                            const key = el.tagName + (el.id || '') + (el.className || '');
                            if (processed.has(key)) return;
                            processed.add(key);
                            
                            // 只保留前 50 个
                            if (found.length >= 50) return;
                            
                            // 获取所有属性
                            const attrs = {};
                            for (const attr of el.attributes) {
                                attrs[attr.name] = attr.value.substring(0, 200);
                            }
                            
                            // 检查是否包含 UUID
                            const htmlStr = el.outerHTML.substring(0, 500);
                            const hasUuid = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/i.test(htmlStr);
                            
                            found.push({
                                selector: selector,
                                tag: el.tagName.toLowerCase(),
                                id: el.id || '',
                                className: (el.className || '').substring(0, 200),
                                attributes: attrs,
                                hasUuid: hasUuid,
                                htmlPreview: htmlStr
                            });
                        });
                    } catch (e) {
                        // 忽略无效选择器
                    }
                }
                
                return JSON.stringify({
                    total: found.length,
                    tabs: found
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个可能的对话 Tab 元素:\n")
        
        for tab in data.get('tabs', [])[:20]:  # 只显示前 20 个
            print(f"选择器: {tab['selector']}")
            print(f"  标签: {tab['tag']}")
            if tab['id']:
                print(f"  ID: {tab['id']}")
            if tab['className']:
                print(f"  Class: {tab['className']}")
            if tab['hasUuid']:
                print(f"  🔑 包含 UUID!")
            
            # 检查是否是我们的目标 UUID
            if target_uuid in tab.get('htmlPreview', ''):
                print(f"  🎯 包含目标 conversation_id!")
            
            # 显示关键属性
            key_attrs = ['role', 'aria-label', 'data-id', 'data-conversation-id', 'onclick']
            for attr in key_attrs:
                if attr in tab.get('attributes', {}):
                    print(f"  {attr}: {tab['attributes'][attr]}")
            
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 3. 查找全局变量中包含 conversation_id 的对象
    # ============================================================
    print("3️⃣  查找全局变量中的 conversation 相关内容")
    print("-" * 80)
    
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetUuid = '{target_uuid}';
                const found = [];
                
                // 遍历 window 对象
                for (const key in window) {{
                    if (key.startsWith('_') || 
                        key.includes('conversation') || 
                        key.includes('chat') ||
                        key.includes('composer') ||
                        key.includes('ai')) {{
                        try {{
                            const value = window[key];
                            if (value !== null && value !== undefined) {{
                                const str = JSON.stringify(value);
                                
                                // 检查是否包含我们的 UUID
                                const hasTargetUuid = str.includes(targetUuid);
                                
                                // 检查是否包含任何 UUID
                                const hasAnyUuid = /[a-f0-9]{{8}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{12}}/i.test(str);
                                
                                if (hasTargetUuid || (hasAnyUuid && str.length < 5000)) {{
                                    found.push({{
                                        key: key,
                                        type: typeof value,
                                        hasTargetUuid: hasTargetUuid,
                                        hasAnyUuid: hasAnyUuid,
                                        preview: str.substring(0, 500),
                                        size: str.length
                                    }});
                                }}
                            }}
                        }} catch (e) {{
                            // 忽略循环引用等错误
                        }}
                    }}
                }}
                
                return JSON.stringify({{
                    total: found.length,
                    variables: found
                }}, null, 2);
            }})()
        `);
        
        return result;
    }})()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个相关的全局变量:\n")
        
        for var in data.get('variables', []):
            print(f"变量: window.{var['key']}")
            print(f"  类型: {var['type']}")
            print(f"  大小: {var['size']} 字符")
            if var['hasTargetUuid']:
                print(f"  🎯 包含目标 UUID!")
            elif var['hasAnyUuid']:
                print(f"  🔑 包含其他 UUID")
            print(f"  预览: {var['preview']}")
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 4. 查找对话列表/历史记录
    # ============================================================
    print("4️⃣  查找对话列表和历史记录")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const selectors = [
                    '.conversations',
                    '[class*="conversation-list"]',
                    '[class*="conversation-item"]',
                    '[class*="chat-list"]',
                    '[class*="chat-item"]',
                    '[class*="history"]',
                    '[class*="sidebar"]',
                    '[role="list"]',
                    '[role="listitem"]'
                ];
                
                const found = [];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach((el, idx) => {
                        if (found.length >= 30) return;
                        
                        // 获取属性
                        const attrs = {};
                        for (const attr of el.attributes) {
                            attrs[attr.name] = attr.value.substring(0, 200);
                        }
                        
                        // 查找子元素中的 UUID
                        const uuids = [];
                        const text = el.textContent || '';
                        const html = el.innerHTML.substring(0, 2000);
                        const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/gi;
                        const matches = html.match(uuidRegex);
                        if (matches) {
                            uuids.push(...new Set(matches.map(u => u.toLowerCase())));
                        }
                        
                        if (uuids.length > 0 || selector.includes('conversation') || selector.includes('chat')) {
                            found.push({
                                selector: selector,
                                tag: el.tagName.toLowerCase(),
                                id: el.id,
                                className: el.className.substring(0, 150),
                                attributes: attrs,
                                uuids: uuids.slice(0, 5),
                                textPreview: text.substring(0, 100),
                                childCount: el.children.length
                            });
                        }
                    });
                }
                
                return JSON.stringify({
                    total: found.length,
                    lists: found
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个对话列表相关元素:\n")
        
        for lst in data.get('lists', []):
            print(f"选择器: {lst['selector']}")
            print(f"  标签: {lst['tag']} | ID: {lst['id']}")
            if lst['className']:
                print(f"  Class: {lst['className']}")
            if lst['uuids']:
                print(f"  🔑 包含 {len(lst['uuids'])} 个 UUID:")
                for uuid in lst['uuids']:
                    if uuid == target_uuid.lower():
                        print(f"    🎯 {uuid} (目标!)")
                    else:
                        print(f"    - {uuid}")
            if lst['textPreview']:
                print(f"  文本: {lst['textPreview']}")
            print(f"  子元素数: {lst['childCount']}")
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 5. 查找事件监听器和可点击元素
    # ============================================================
    print("5️⃣  查找与 conversation 相关的可交互元素")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const clickableSelectors = [
                    'button',
                    '[role="button"]',
                    '[onclick]',
                    'a',
                    '[class*="clickable"]'
                ];
                
                const found = [];
                
                for (const selector of clickableSelectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach((el) => {
                        if (found.length >= 40) return;
                        
                        // 检查是否与 conversation 相关
                        const text = (el.textContent || '').toLowerCase();
                        const className = (el.className || '').toLowerCase();
                        const id = (el.id || '').toLowerCase();
                        const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                        
                        const isRelated = 
                            text.includes('conversation') ||
                            text.includes('chat') ||
                            text.includes('history') ||
                            className.includes('conversation') ||
                            className.includes('chat') ||
                            id.includes('conversation') ||
                            id.includes('chat') ||
                            ariaLabel.includes('conversation') ||
                            ariaLabel.includes('chat');
                        
                        if (isRelated) {
                            found.push({
                                tag: el.tagName.toLowerCase(),
                                id: el.id,
                                className: el.className.substring(0, 150),
                                text: el.textContent.substring(0, 100),
                                ariaLabel: el.getAttribute('aria-label'),
                                onclick: el.onclick ? 'function defined' : el.getAttribute('onclick')
                            });
                        }
                    });
                }
                
                return JSON.stringify({
                    total: found.length,
                    interactive: found
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个可交互元素:\n")
        
        for item in data.get('interactive', []):
            print(f"标签: {item['tag']}")
            if item['id']:
                print(f"  ID: {item['id']}")
            if item['className']:
                print(f"  Class: {item['className']}")
            if item['ariaLabel']:
                print(f"  Aria Label: {item['ariaLabel']}")
            if item['text']:
                print(f"  文本: {item['text']}")
            if item['onclick']:
                print(f"  Onclick: {item['onclick']}")
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 6. 检查 localStorage 和 sessionStorage
    # ============================================================
    print("6️⃣  检查 localStorage 和 sessionStorage")
    print("-" * 80)
    
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetUuid = '{target_uuid}';
                const found = {{
                    localStorage: [],
                    sessionStorage: []
                }};
                
                // 检查 localStorage
                for (let i = 0; i < localStorage.length; i++) {{
                    const key = localStorage.key(i);
                    const value = localStorage.getItem(key);
                    
                    const hasTarget = value.includes(targetUuid);
                    const hasAnyUuid = /[a-f0-9]{{8}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{12}}/i.test(value);
                    
                    if (hasTarget || (hasAnyUuid && (
                        key.includes('conversation') ||
                        key.includes('chat') ||
                        key.includes('history')
                    ))) {{
                        found.localStorage.push({{
                            key: key,
                            hasTarget: hasTarget,
                            valuePreview: value.substring(0, 300),
                            size: value.length
                        }});
                    }}
                }}
                
                // 检查 sessionStorage
                for (let i = 0; i < sessionStorage.length; i++) {{
                    const key = sessionStorage.key(i);
                    const value = sessionStorage.getItem(key);
                    
                    const hasTarget = value.includes(targetUuid);
                    const hasAnyUuid = /[a-f0-9]{{8}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{12}}/i.test(value);
                    
                    if (hasTarget || (hasAnyUuid && (
                        key.includes('conversation') ||
                        key.includes('chat') ||
                        key.includes('history')
                    ))) {{
                        found.sessionStorage.push({{
                            key: key,
                            hasTarget: hasTarget,
                            valuePreview: value.substring(0, 300),
                            size: value.length
                        }});
                    }}
                }}
                
                return JSON.stringify(found, null, 2);
            }})()
        `);
        
        return result;
    }})()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        
        print("localStorage:")
        if data.get('localStorage'):
            for item in data['localStorage']:
                print(f"  Key: {item['key']}")
                if item['hasTarget']:
                    print(f"    🎯 包含目标 UUID!")
                print(f"    大小: {item['size']}")
                print(f"    预览: {item['valuePreview']}")
                print()
        else:
            print("  未找到相关项")
        
        print("\nsessionStorage:")
        if data.get('sessionStorage'):
            for item in data['sessionStorage']:
                print(f"  Key: {item['key']}")
                if item['hasTarget']:
                    print(f"    🎯 包含目标 UUID!")
                print(f"    大小: {item['size']}")
                print(f"    预览: {item['valuePreview']}")
                print()
        else:
            print("  未找到相关项")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 7. 查找包含切换/导航功能的函数
    # ============================================================
    print("7️⃣  查找可能的切换对话函数")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const found = [];
                
                // 查找全局函数
                for (const key in window) {
                    if (typeof window[key] === 'function') {
                        const funcStr = window[key].toString();
                        
                        // 检查函数名和内容是否与对话切换相关
                        const isRelated = 
                            key.toLowerCase().includes('conversation') ||
                            key.toLowerCase().includes('chat') ||
                            key.toLowerCase().includes('switch') ||
                            key.toLowerCase().includes('navigate') ||
                            key.toLowerCase().includes('open') && (
                                funcStr.includes('conversation') ||
                                funcStr.includes('chat')
                            );
                        
                        if (isRelated) {
                            found.push({
                                name: key,
                                preview: funcStr.substring(0, 300)
                            });
                        }
                    }
                }
                
                return JSON.stringify({
                    total: found.length,
                    functions: found
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个相关函数:\n")
        
        for func in data.get('functions', []):
            print(f"函数: {func['name']}")
            print(f"  预览: {func['preview']}")
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    print("=" * 80)
    print("✅ 全面搜索完成")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

