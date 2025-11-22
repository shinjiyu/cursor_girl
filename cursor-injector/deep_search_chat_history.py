#!/usr/bin/env python3
"""
深入搜索 Chat History 和对话切换机制
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
    print(f"🔍 深入搜索 Chat History 和对话切换机制")
    print(f"目标 conversation_id: {target_uuid}")
    print("=" * 80)
    print()
    
    # ============================================================
    # 1. 详细分析 Chat History 按钮和相关元素
    # ============================================================
    print("1️⃣  分析 Chat History 按钮")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 查找所有可能是 Chat History 的元素
                const historyElements = [];
                
                // 通过 aria-label 查找
                const allElements = document.querySelectorAll('[aria-label*="Chat History"], [aria-label*="History"]');
                
                allElements.forEach(el => {
                    // 获取所有属性
                    const attrs = {};
                    for (const attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    
                    // 查找父元素和子元素
                    const parent = el.parentElement;
                    const parentInfo = parent ? {
                        tag: parent.tagName,
                        id: parent.id,
                        className: parent.className
                    } : null;
                    
                    historyElements.push({
                        tag: el.tagName.toLowerCase(),
                        id: el.id,
                        className: el.className,
                        attributes: attrs,
                        parent: parentInfo,
                        text: el.textContent?.substring(0, 100)
                    });
                });
                
                return JSON.stringify({
                    total: historyElements.length,
                    elements: historyElements
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个 History 相关元素:\n")
        
        for el in data.get('elements', []):
            print(f"标签: {el['tag']}")
            print(f"  ID: {el['id']}")
            print(f"  Class: {el['className']}")
            print(f"  Aria Label: {el['attributes'].get('aria-label')}")
            if el['parent']:
                print(f"  父元素: {el['parent']['tag']} | {el['parent']['className']}")
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 2. 模拟点击 Chat History 按钮并观察变化
    # ============================================================
    print("2️⃣  尝试打开 Chat History 面板")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 查找 Chat History 按钮
                const historyButton = document.querySelector('[aria-label*="Show Chat History"]');
                
                if (!historyButton) {
                    return JSON.stringify({ error: 'History button not found' });
                }
                
                // 记录点击前的状态
                const beforeClick = {
                    buttonExists: true,
                    ariaLabel: historyButton.getAttribute('aria-label')
                };
                
                // 点击按钮
                historyButton.click();
                
                // 等待一小段时间让 UI 更新
                return new Promise(resolve => {
                    setTimeout(() => {
                        // 查找可能新出现的面板
                        const panels = [];
                        const possiblePanels = document.querySelectorAll(
                            '[class*="history"], [class*="panel"], [class*="sidebar"], [class*="modal"]'
                        );
                        
                        possiblePanels.forEach(panel => {
                            // 检查是否可见
                            const style = window.getComputedStyle(panel);
                            const isVisible = style.display !== 'none' && style.visibility !== 'hidden';
                            
                            if (isVisible) {
                                panels.push({
                                    tag: panel.tagName.toLowerCase(),
                                    id: panel.id,
                                    className: panel.className.substring(0, 200),
                                    visible: isVisible,
                                    children: panel.children.length
                                });
                            }
                        });
                        
                        resolve(JSON.stringify({
                            clicked: true,
                            beforeClick: beforeClick,
                            panelsFound: panels.length,
                            panels: panels
                        }, null, 2));
                    }, 500);
                });
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        if 'error' in data:
            print(f"⚠️  {data['error']}")
        else:
            print(f"✅ 点击了 History 按钮")
            print(f"找到 {data.get('panelsFound', 0)} 个可能的面板:\n")
            
            for panel in data.get('panels', []):
                print(f"标签: {panel['tag']}")
                print(f"  ID: {panel['id']}")
                print(f"  Class: {panel['className']}")
                print(f"  子元素数: {panel['children']}")
                print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 3. 查找 History 面板中的对话列表
    # ============================================================
    print("3️⃣  查找 History 面板中的对话项")
    print("-" * 80)
    
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetUuid = '{target_uuid}';
                
                // 查找所有可能是对话项的元素
                const selectors = [
                    '[class*="history-item"]',
                    '[class*="chat-item"]',
                    '[class*="conversation-item"]',
                    '[role="listitem"]',
                    '[class*="history"] [role="button"]',
                    '[class*="history"] a',
                    '[class*="panel"] [class*="item"]'
                ];
                
                const items = [];
                
                for (const selector of selectors) {{
                    const elements = document.querySelectorAll(selector);
                    
                    elements.forEach((el, idx) => {{
                        if (items.length >= 50) return;
                        
                        // 获取所有属性
                        const attrs = {{}};
                        for (const attr of el.attributes) {{
                            attrs[attr.name] = attr.value.substring(0, 200);
                        }}
                        
                        // 检查是否包含 UUID
                        const html = el.outerHTML.substring(0, 1000);
                        const hasTargetUuid = html.includes(targetUuid);
                        const uuidMatches = html.match(/[a-f0-9]{{8}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{12}}/gi);
                        
                        // 检查是否可见
                        const style = window.getComputedStyle(el);
                        const isVisible = style.display !== 'none' && style.visibility !== 'hidden';
                        
                        if (isVisible && (hasTargetUuid || uuidMatches)) {{
                            items.push({{
                                selector: selector,
                                tag: el.tagName.toLowerCase(),
                                id: el.id,
                                className: el.className.substring(0, 150),
                                attributes: attrs,
                                hasTargetUuid: hasTargetUuid,
                                uuids: uuidMatches ? [...new Set(uuidMatches.map(u => u.toLowerCase()))] : [],
                                text: el.textContent?.substring(0, 100),
                                isVisible: isVisible
                            }});
                        }}
                    }});
                }}
                
                return JSON.stringify({{
                    total: items.length,
                    items: items
                }}, null, 2);
            }})()
        `);
        
        return result;
    }})()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个可见的对话项:\n")
        
        for item in data.get('items', []):
            print(f"选择器: {item['selector']}")
            print(f"  标签: {item['tag']} | ID: {item['id']}")
            print(f"  Class: {item['className']}")
            
            if item['hasTargetUuid']:
                print(f"  🎯 包含目标 conversation_id!")
            
            if item['uuids']:
                print(f"  🔑 包含 {len(item['uuids'])} 个 UUID:")
                for uuid in item['uuids'][:3]:
                    print(f"    - {uuid}")
            
            if item['text']:
                print(f"  文本: {item['text']}")
            
            # 显示关键属性
            key_attrs = ['onclick', 'href', 'data-id', 'data-conversation-id']
            for attr in key_attrs:
                if attr in item.get('attributes', {}):
                    print(f"  {attr}: {item['attributes'][attr]}")
            
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 4. 查找所有侧边栏和面板
    # ============================================================
    print("4️⃣  查找所有侧边栏和面板结构")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const selectors = [
                    '[class*="sidebar"]',
                    '[class*="panel"]',
                    '[class*="pane"]',
                    '[role="complementary"]',
                    '[class*="split-view"]'
                ];
                
                const panels = [];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    
                    elements.forEach(el => {
                        if (panels.length >= 30) return;
                        
                        // 检查是否可见
                        const style = window.getComputedStyle(el);
                        const isVisible = style.display !== 'none' && style.visibility !== 'hidden';
                        
                        if (isVisible) {
                            // 查找子元素中是否有对话相关内容
                            const text = el.textContent || '';
                            const hasConversation = 
                                text.toLowerCase().includes('chat') ||
                                text.toLowerCase().includes('conversation') ||
                                text.toLowerCase().includes('history');
                            
                            panels.push({
                                selector: selector,
                                tag: el.tagName.toLowerCase(),
                                id: el.id,
                                className: el.className.substring(0, 150),
                                isVisible: isVisible,
                                hasConversation: hasConversation,
                                textPreview: text.substring(0, 100),
                                childCount: el.children.length,
                                width: style.width,
                                height: style.height
                            });
                        }
                    });
                }
                
                return JSON.stringify({
                    total: panels.length,
                    panels: panels
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个可见的面板:\n")
        
        for panel in data.get('panels', []):
            print(f"选择器: {panel['selector']}")
            print(f"  标签: {panel['tag']} | ID: {panel['id']}")
            print(f"  Class: {panel['className']}")
            print(f"  尺寸: {panel['width']} x {panel['height']}")
            print(f"  子元素数: {panel['childCount']}")
            
            if panel['hasConversation']:
                print(f"  💬 包含对话相关内容")
                print(f"  文本预览: {panel['textPreview']}")
            
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 5. 查找包含 conversation_id 的所有可点击元素
    # ============================================================
    print("5️⃣  查找包含 conversation_id 的可点击元素")
    print("-" * 80)
    
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetUuid = '{target_uuid}';
                const clickable = [];
                
                // 查找所有可能可点击的元素
                const allElements = document.querySelectorAll('button, a, [role="button"], [onclick], [class*="clickable"]');
                
                allElements.forEach(el => {{
                    // 检查元素本身或其属性是否包含 UUID
                    const html = el.outerHTML.substring(0, 1000);
                    const hasUuid = html.includes(targetUuid) || /[a-f0-9]{{8}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{12}}/i.test(html);
                    
                    if (hasUuid) {{
                        const attrs = {{}};
                        for (const attr of el.attributes) {{
                            attrs[attr.name] = attr.value.substring(0, 200);
                        }}
                        
                        clickable.push({{
                            tag: el.tagName.toLowerCase(),
                            id: el.id,
                            className: el.className.substring(0, 150),
                            attributes: attrs,
                            text: el.textContent?.substring(0, 100),
                            hasTargetUuid: html.includes(targetUuid)
                        }});
                    }}
                }});
                
                return JSON.stringify({{
                    total: clickable.length,
                    clickable: clickable
                }}, null, 2);
            }})()
        `);
        
        return result;
    }})()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        print(f"找到 {data.get('total', 0)} 个包含 UUID 的可点击元素:\n")
        
        for item in data.get('clickable', []):
            print(f"标签: {item['tag']}")
            if item['id']:
                print(f"  ID: {item['id']}")
            if item['className']:
                print(f"  Class: {item['className']}")
            if item['hasTargetUuid']:
                print(f"  🎯 包含目标 conversation_id!")
            if item['text']:
                print(f"  文本: {item['text']}")
            
            # 显示 href 或 onclick
            if 'href' in item.get('attributes', {}):
                print(f"  href: {item['attributes']['href']}")
            if 'onclick' in item.get('attributes', {}):
                print(f"  onclick: {item['attributes']['onclick']}")
            
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    print("=" * 80)
    print("✅ 深入搜索完成")
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

