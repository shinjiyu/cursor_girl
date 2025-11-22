#!/usr/bin/env python3
"""
深入分析 Chat History 面板的完整结构
查找对话切换机制和当前活跃对话
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
    print(f"🔍 深入分析 Chat History 面板结构")
    print(f"目标 conversation_id: {target_uuid}")
    print("=" * 80)
    print()
    
    # ============================================================
    # 1. 分析 auxiliarybar (右侧边栏 - History 面板所在位置)
    # ============================================================
    print("1️⃣  分析 auxiliarybar 完整结构")
    print("-" * 80)
    
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetUuid = '{target_uuid}';
                
                // 查找 auxiliarybar
                const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                
                if (!auxiliarybar) {{
                    return JSON.stringify({{ error: 'auxiliarybar not found' }});
                }}
                
                // 递归遍历所有子元素
                function analyzeElement(el, depth = 0, maxDepth = 10) {{
                    if (depth > maxDepth) return null;
                    
                    const info = {{
                        tag: el.tagName.toLowerCase(),
                        id: el.id || '',
                        className: el.className.substring(0, 200),
                        depth: depth,
                        children: []
                    }};
                    
                    // 检查是否包含 UUID
                    const html = el.innerHTML.substring(0, 2000);
                    if (html.includes(targetUuid)) {{
                        info.hasTargetUuid = true;
                    }}
                    
                    // 检查文本内容
                    if (el.childNodes.length > 0) {{
                        for (const node of el.childNodes) {{
                            if (node.nodeType === 3 && node.textContent.trim()) {{
                                info.textContent = node.textContent.substring(0, 100);
                                break;
                            }}
                        }}
                    }}
                    
                    // 获取关键属性
                    const keyAttrs = ['role', 'aria-label', 'data-id', 'onclick', 'href'];
                    info.attributes = {{}};
                    keyAttrs.forEach(attr => {{
                        const val = el.getAttribute(attr);
                        if (val) {{
                            info.attributes[attr] = val.substring(0, 200);
                        }}
                    }});
                    
                    // 遍历子元素（只遍历重要的）
                    if (depth < 8 && el.children.length > 0 && el.children.length < 50) {{
                        for (const child of el.children) {{
                            const childInfo = analyzeElement(child, depth + 1, maxDepth);
                            if (childInfo) {{
                                info.children.push(childInfo);
                            }}
                        }}
                    }} else if (el.children.length > 0) {{
                        info.childCount = el.children.length;
                    }}
                    
                    return info;
                }}
                
                const structure = analyzeElement(auxiliarybar, 0, 8);
                
                return JSON.stringify({{
                    found: true,
                    structure: structure
                }}, null, 2);
            }})()
        `);
        
        return result;
    }})()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        if 'error' in data:
            print(f"⚠️  {data['error']}")
        else:
            print("✅ 找到 auxiliarybar 结构")
            print()
            
            # 递归打印结构
            def print_structure(node, indent=0):
                prefix = "  " * indent
                tag_info = f"{node['tag']}"
                if node['id']:
                    tag_info += f" #{node['id']}"
                if node['className']:
                    tag_info += f" .{node['className'][:50]}"
                
                print(f"{prefix}{tag_info}")
                
                if node.get('hasTargetUuid'):
                    print(f"{prefix}  🎯 包含目标 conversation_id")
                
                if node.get('textContent'):
                    print(f"{prefix}  📝 {node['textContent']}")
                
                if node.get('attributes'):
                    for k, v in node['attributes'].items():
                        print(f"{prefix}  {k}: {v}")
                
                if node.get('childCount'):
                    print(f"{prefix}  ⤷ {node['childCount']} 个子元素")
                
                for child in node.get('children', []):
                    print_structure(child, indent + 1)
            
            print_structure(data['structure'])
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 2. 查找所有包含 UUID 的对话项（更详细）
    # ============================================================
    print("\n" + "=" * 80)
    print("2️⃣  查找所有对话历史项（详细分析）")
    print("-" * 80)
    
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetUuid = '{target_uuid}';
                
                // 查找 auxiliarybar 中的所有对话项
                const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                if (!auxiliarybar) return JSON.stringify({{ error: 'auxiliarybar not found' }});
                
                const items = [];
                const uuidRegex = /[a-f0-9]{{8}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{12}}/gi;
                
                // 查找所有包含 UUID 的元素
                const allElements = auxiliarybar.querySelectorAll('*');
                
                allElements.forEach(el => {{
                    const html = el.outerHTML.substring(0, 5000);
                    const uuids = html.match(uuidRegex);
                    
                    if (uuids && uuids.length > 0) {{
                        // 检查是否是对话项容器（通过类名或结构判断）
                        const className = el.className || '';
                        const isLikelyItem = 
                            className.includes('item') ||
                            className.includes('row') ||
                            className.includes('entry') ||
                            className.includes('conversation') ||
                            className.includes('chat') ||
                            el.children.length > 0;
                        
                        if (isLikelyItem) {{
                            const attrs = {{}};
                            for (const attr of el.attributes) {{
                                attrs[attr.name] = attr.value.substring(0, 300);
                            }}
                            
                            // 获取文本（不包括子元素）
                            let directText = '';
                            for (const node of el.childNodes) {{
                                if (node.nodeType === 3) {{
                                    directText += node.textContent;
                                }}
                            }}
                            
                            // 获取所有文本
                            const allText = el.textContent || '';
                            
                            items.push({{
                                tag: el.tagName.toLowerCase(),
                                id: el.id,
                                className: className.substring(0, 200),
                                attributes: attrs,
                                uuids: [...new Set(uuids.map(u => u.toLowerCase()))],
                                hasTargetUuid: uuids.some(u => u.toLowerCase() === targetUuid.toLowerCase()),
                                directText: directText.substring(0, 150).trim(),
                                allText: allText.substring(0, 150).trim(),
                                childCount: el.children.length,
                                // 检查父元素
                                parentTag: el.parentElement?.tagName.toLowerCase(),
                                parentClass: el.parentElement?.className.substring(0, 100),
                                // 检查是否可点击
                                isClickable: el.onclick !== null || 
                                             el.tagName === 'A' || 
                                             el.tagName === 'BUTTON' ||
                                             el.getAttribute('role') === 'button' ||
                                             el.hasAttribute('onclick')
                            }});
                        }}
                    }}
                }});
                
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
        print(f"找到 {data.get('total', 0)} 个包含 UUID 的对话项:\n")
        
        for idx, item in enumerate(data.get('items', [])):
            print(f"[{idx + 1}] {item['tag']}")
            if item['id']:
                print(f"  ID: {item['id']}")
            if item['className']:
                print(f"  Class: {item['className']}")
            
            if item['hasTargetUuid']:
                print(f"  🎯 包含目标 conversation_id!")
            
            print(f"  🔑 包含 {len(item['uuids'])} 个 UUID:")
            for uuid in item['uuids'][:3]:
                marker = "🎯" if uuid == target_uuid.lower() else "  "
                print(f"    {marker} {uuid}")
            
            if item['isClickable']:
                print(f"  🖱️  可点击")
            
            if item['allText']:
                print(f"  📝 文本: {item['allText']}")
            
            print(f"  👨‍👩‍👧 父元素: {item['parentTag']} | {item['parentClass']}")
            print(f"  👶 子元素数: {item['childCount']}")
            
            # 显示关键属性
            key_attrs = ['role', 'aria-label', 'onclick', 'href', 'data-id']
            for attr in key_attrs:
                if attr in item.get('attributes', {}):
                    print(f"  {attr}: {item['attributes'][attr]}")
            
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 3. 查找当前活跃的对话标识
    # ============================================================
    print("\n" + "=" * 80)
    print("3️⃣  查找当前活跃的对话")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 方法 1: 从 composer-bottom-add-context 获取
                const composerEl = document.querySelector('[id^="composer-bottom-add-context-"]');
                const fromComposer = composerEl ? composerEl.id.match(/composer-bottom-add-context-([a-f0-9-]+)/)?.[1] : null;
                
                // 方法 2: 查找带有 active/selected/current 类名的元素
                const activeSelectors = [
                    '[class*="active"]',
                    '[class*="selected"]',
                    '[class*="current"]',
                    '[aria-selected="true"]',
                    '[aria-current="true"]'
                ];
                
                const activeElements = [];
                
                for (const selector of activeSelectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        const html = el.outerHTML.substring(0, 1000);
                        const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/gi;
                        const uuids = html.match(uuidRegex);
                        
                        if (uuids) {
                            activeElements.push({
                                selector: selector,
                                tag: el.tagName.toLowerCase(),
                                id: el.id,
                                className: el.className.substring(0, 150),
                                uuids: [...new Set(uuids.map(u => u.toLowerCase()))],
                                text: el.textContent?.substring(0, 100)
                            });
                        }
                    });
                }
                
                return JSON.stringify({
                    fromComposer: fromComposer,
                    activeElements: activeElements
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        data = json.loads(result.get('result', '{}'))
        
        print(f"从 Composer 提取的 conversation_id:")
        print(f"  🎯 {data.get('fromComposer', 'Not found')}")
        print()
        
        print(f"找到 {len(data.get('activeElements', []))} 个带有 active/selected 标识的元素:")
        for el in data.get('activeElements', [])[:10]:
            print(f"\n  选择器: {el['selector']}")
            print(f"    标签: {el['tag']} | ID: {el['id']}")
            print(f"    Class: {el['className']}")
            print(f"    UUIDs: {', '.join(el['uuids'][:3])}")
            if el['text']:
                print(f"    文本: {el['text']}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    print("=" * 80)
    print("✅ 分析完成")
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

